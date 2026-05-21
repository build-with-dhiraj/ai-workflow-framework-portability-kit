---
name: ner-content-pipeline
description: Extract named entities, relationships, and topics from unstructured text into knowledge graphs or taxonomies. Triggers on "NER pipeline", "extract entities", "tag content".
dispatch_to: data-engineer
---

# NER Content Pipeline

This skill covers NLP entity extraction and structured knowledge pipelines using spaCy, scoped to UPSC exam-prep article processing. The pipeline runs inside Prefect flows and outputs to Pinecone (vector search) and Postgres (taxonomy).

## Core Principles

1. Always use `nlp.pipe()` for batch processing — never call `nlp(text)` in a loop over large corpora.
2. Custom UPSC entity types (SCHEME, AMENDMENT, HISTORICAL_EVENT, GEOGRAPHIC_ENTITY) must be defined before any training run — do not rely on out-of-box labels for domain content.
3. NER output is the Bronze layer. Validated, deduplicated entities go to Silver. Aggregated topic graphs go to Gold.
4. Every entity record must carry: `article_id`, `entity_text`, `entity_label`, `start_char`, `end_char`, `confidence`, `extracted_at`.

## 1. spaCy Pipeline Anatomy

```
tokenizer → tagger → parser → ner → custom_components
```

```python
import spacy

nlp = spacy.load("en_core_web_lg")
print(nlp.pipe_names)
# ['tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer']

# Disable unused components for throughput gains
nlp = spacy.load("en_core_web_lg", disable=["parser", "tagger"])
```

Add a custom component after NER:

```python
from spacy.language import Language

@Language.component("upsc_classifier")
def upsc_classifier(doc):
    for ent in doc.ents:
        # map spaCy labels to UPSC content types
        ent._.upsc_type = LABEL_MAP.get(ent.label_, "OTHER")
    return doc

nlp.add_pipe("upsc_classifier", after="ner")
```

## 2. Model Selection

| Model | Size | WER on UPSC text | Use when |
|---|---|---|---|
| `en_core_web_sm` | 12 MB | High miss rate on Indian proper nouns | Dev/testing only |
| `en_core_web_lg` | 560 MB | Acceptable for org/geo entities | Production baseline |
| `en_core_web_trf` | 440 MB (+ torch) | Best accuracy, 4x slower | Fine-tuning target |

Install: `python -m spacy download en_core_web_lg`

For UPSC content, start with `en_core_web_lg` and fine-tune on annotated UPSC articles. The transformer model (`en_core_web_trf`) is the fine-tuning base of choice when GPU is available.

## 3. Out-of-Box NER Labels and UPSC Mapping

| spaCy label | Meaning | Maps to UPSC type |
|---|---|---|
| `PERSON` | People | HISTORICAL_FIGURE, LEADER |
| `ORG` | Organizations | MINISTRY, BODY, NGO |
| `GPE` | Countries, cities, states | GEOGRAPHIC_ENTITY |
| `DATE` | Dates and periods | HISTORICAL_DATE |
| `EVENT` | Named events | HISTORICAL_EVENT |
| `LAW` | Named laws/acts | CONSTITUTIONAL_PROVISION |
| `MONEY` | Monetary values | ECONOMIC_INDICATOR |

`LAW` is the most useful out-of-box label for UPSC — it catches "Article 370", "73rd Amendment", "MGNREGA" with moderate recall.

## 4. Custom NER Training for UPSC Entities

Define new entity types not covered by the default model:

```python
# config.cfg excerpt — add to [nlp] components
[components.ner]
source = "en_core_web_lg"

# In training script
LABELS = ["SCHEME", "AMENDMENT", "HISTORICAL_EVENT", "GEOGRAPHIC_ENTITY", "COMMITTEE"]

# Annotation format (spaCy v3 .spacy binary or via Prodigy)
# Example training record
TRAIN_DATA = [
    ("PM Kisan Samman Nidhi was launched in 2019",
     {"entities": [(0, 22, "SCHEME"), (39, 43, "DATE")]}),
    ("The 42nd Constitutional Amendment added the word socialist",
     {"entities": [(4, 30, "AMENDMENT")]}),
]
```

Recommended annotation workflow:
1. Export 500 UPSC articles from Postgres.
2. Pre-annotate with `en_core_web_lg` to get bootstrapped labels.
3. Correct in Prodigy (`prodigy ner.correct`) or Label Studio.
4. Train: `python -m spacy train config.cfg --output ./models/upsc-ner`

Minimum viable training set: 300 annotated sentences per new label.

## 5. Batch Processing with nlp.pipe()

```python
from typing import Iterator
import spacy

nlp = spacy.load("en_core_web_lg", disable=["parser", "tagger"])

def extract_entities_batch(texts: list[str], batch_size: int = 64) -> list[dict]:
    results = []
    for doc in nlp.pipe(texts, batch_size=batch_size):
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "kb_id": ent.kb_id_ or None,
            }
            for ent in doc.ents
        ]
        results.append({"entities": entities, "text": doc.text})
    return results
```

Throughput rule of thumb on CPU: `en_core_web_lg` processes ~200 articles/min at batch_size=64. For 1,000 daily articles, a single worker is sufficient.

## 6. Prefect Flow Integration

```python
from prefect import flow, task
import spacy, psycopg2, json

@task
def load_articles_from_postgres(conn_str: str, limit: int = 500) -> list[dict]:
    # returns [{"id": ..., "content": ...}]
    ...

@task
def run_ner(articles: list[dict]) -> list[dict]:
    nlp = spacy.load("en_core_web_lg", disable=["parser", "tagger"])
    texts = [a["content"] for a in articles]
    entity_docs = extract_entities_batch(texts)
    for article, entity_doc in zip(articles, entity_docs):
        entity_doc["article_id"] = article["id"]
    return entity_docs

@task
def upsert_to_pinecone(entity_docs: list[dict], index_name: str) -> None:
    # embed entity.text, upsert with metadata
    ...

@task
def write_to_postgres(entity_docs: list[dict], conn_str: str) -> None:
    # INSERT INTO silver_entities (article_id, entity_text, label, ...) ON CONFLICT DO UPDATE
    ...

@flow(name="upsc-ner-pipeline")
def ner_pipeline_flow(conn_str: str, pinecone_index: str):
    articles = load_articles_from_postgres(conn_str)
    entity_docs = run_ner(articles)
    upsert_to_pinecone(entity_docs, pinecone_index)
    write_to_postgres(entity_docs, conn_str)
```

Schedule this flow after the article ingestion flow in Prefect to ensure fresh content is processed daily.

## 7. Relationship Extraction (SVO Triples)

Use the dependency parser to extract subject-verb-object triples for knowledge graph edges:

```python
nlp_with_parser = spacy.load("en_core_web_lg")  # parser enabled

def extract_svo(text: str) -> list[dict]:
    doc = nlp_with_parser(text)
    triples = []
    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            subj = [t for t in token.lefts if t.dep_ in ("nsubj", "nsubjpass")]
            obj  = [t for t in token.rights if t.dep_ in ("dobj", "pobj", "attr")]
            if subj and obj:
                triples.append({
                    "subject": subj[0].text,
                    "predicate": token.lemma_,
                    "object": obj[0].text,
                })
    return triples
```

SVO triples become directed edges in the knowledge graph: `(SCHEME) --launched_by--> (MINISTRY)`.

## 8. Output Formats

### JSON-L (Bronze/Storage)
```python
import jsonlines
with jsonlines.open("entities_2024_01_15.jsonl", mode="w") as writer:
    for doc in entity_docs:
        writer.write(doc)
```

### Pinecone Upsert (Vector Search)
```python
# One vector per unique entity mention; metadata carries article_id and label
vectors = [
    {
        "id": f"{doc['article_id']}_{i}",
        "values": embed(ent["text"]),
        "metadata": {"article_id": doc["article_id"], "label": ent["label"], "text": ent["text"]},
    }
    for doc in entity_docs
    for i, ent in enumerate(doc["entities"])
]
index.upsert(vectors=vectors)
```

### Postgres (Taxonomy / Silver Layer)
```sql
CREATE TABLE silver_entities (
    id            BIGSERIAL PRIMARY KEY,
    article_id    TEXT NOT NULL,
    entity_text   TEXT NOT NULL,
    entity_label  TEXT NOT NULL,
    upsc_type     TEXT,
    start_char    INT,
    end_char      INT,
    confidence    FLOAT,
    extracted_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (article_id, entity_text, entity_label)
);
CREATE INDEX ON silver_entities (entity_label);
CREATE INDEX ON silver_entities (upsc_type);
```

## Failure Modes to Watch

- **Silent label drift**: if upstream article format changes (HTML tags leaking in), entity boundaries break silently. Add a pre-NER text-cleaning assertion.
- **`en_core_web_lg` missing Indian proper nouns**: Niti Aayog, Pradhan Mantri schemes, and state names often miss. Supplement with a `PhraseMatcher` gazetteer of known UPSC terms.
- **Parser cost**: SVO extraction adds ~3x latency. Run it only for Gold-layer relationship graph builds, not daily entity tagging.
