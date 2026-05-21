---
name: rag-patterns
description: "Build RAG pipelines — vector DB + LLM, document Q&A, chunking/embedding strategies. Triggers on 'build RAG', 'document Q&A', 'retrieval pipeline', 'embed and search'."
metadata:
  author: the-operator
  version: "0.1.0"
---

# RAG Patterns with LlamaIndex

## Core Principle

**Check the LlamaIndex docs before writing code.** APIs shift between minor versions.
- Docs: https://docs.llamaindex.ai/en/stable/
- Integrations hub: https://llamahub.ai/

Primary stack: `llama-index-core` + `llama-index-vector-stores-pinecone` + Pinecone MCP.

---

## 1. RAG Decision Tree

| Situation | Approach |
|---|---|
| Documents > 20 pages, answers must cite sources | RAG |
| Knowledge changes weekly or is private | RAG |
| Task needs specialized style/format learned from examples | Fine-tuning |
| Total context fits in <100k tokens and is static | Context-stuffing (simpler, cheaper) |
| Need both grounding AND behavioral change | RAG + fine-tuning together |

**For UPSC article pipelines:** always RAG. Articles are dense, frequently updated, and answers must be traceable to source text.

---

## 2. Document Loading

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import BeautifulSoupWebReader

# PDFs, txt, md from a directory
docs = SimpleDirectoryReader(
    input_dir="./articles",
    required_exts=[".pdf", ".txt", ".md"],
    recursive=True,
).load_data()

# HTML / web articles
loader = BeautifulSoupWebReader()
docs = loader.load_data(urls=["https://example.com/article"])

# Structured JSON (article pipeline pattern)
from llama_index.core import Document

docs = [
    Document(
        text=article["body"],
        metadata={
            "title": article["title"],
            "source": article["url"],
            "date": article["published_at"],
            "category": article["category"],   # e.g. "polity", "economy"
        },
        excluded_embed_metadata_keys=["date"],   # don't embed date noise
    )
    for article in articles
]
```

---

## 3. Chunking Strategy

| Strategy | When to use | LlamaIndex class |
|---|---|---|
| Fixed-size | Uniform docs, simple retrieval | `SentenceSplitter(chunk_size=512)` |
| Sentence-window | Dense prose, need surrounding context | `SentenceWindowNodeParser` |
| Hierarchical | Long docs where sections matter | `HierarchicalNodeParser` |

**UPSC articles:** use sentence-window (window=3). Dense factual text; surrounding sentences add critical context for exam Q&A.

```python
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter

# Sentence-window (recommended for UPSC)
parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text",
)

# Fixed-size fallback
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = splitter.get_nodes_from_documents(docs)
```

---

## 4. Embedding Model Selection

| Model | Latency | Cost | Quality | Use when |
|---|---|---|---|---|
| `text-embedding-3-small` (OpenAI) | ~50ms | $0.02/1M tokens | High | Production default |
| `text-embedding-3-large` (OpenAI) | ~80ms | $0.13/1M tokens | Highest | Critical retrieval |
| `embed-english-v3.0` (Cohere) | ~60ms | $0.10/1M tokens | High | Multilingual or rerank |
| `BAAI/bge-small-en-v1.5` (local) | varies | Free | Good | Offline/privacy |

```python
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
# Dimension: 1536. Set Pinecone index dimension to match.
```

---

## 5. Pinecone Integration (native MCP connector)

Use the Pinecone MCP tools (`mcp__pinecone__*`) for index introspection, then LlamaIndex for ingestion and query.

```python
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("upsc-articles")   # must match embedding dimension

vector_store = PineconeVectorStore(pinecone_index=index, namespace="v1")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Ingest
llama_index = VectorStoreIndex.from_documents(
    docs,
    storage_context=storage_context,
    show_progress=True,
)

# Query (no re-ingestion needed — Pinecone is the store)
llama_index = VectorStoreIndex.from_vector_store(vector_store)
```

Always set a `namespace` per pipeline version so you can do blue-green index swaps without downtime.

---

## 6. Query Pipeline: Retrieval → Reranking → Synthesis

```python
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import get_response_synthesizer

# Step 1 — retrieve more candidates than you need
retriever = llama_index.as_retriever(similarity_top_k=10)

# Step 2 — rerank down to top-3 (use Cohere or cross-encoder)
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=3,
)

# Step 3 — synthesize with source citations
synthesizer = get_response_synthesizer(response_mode="compact")

from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[reranker],
    response_synthesizer=synthesizer,
)

response = query_engine.query("What are the powers of the Rajya Sabha?")
# response.source_nodes contains the cited chunks
```

---

## 7. Evaluation: Retrieval Quality Metrics

```python
# deepeval (recommended — integrates with LlamaIndex)
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input=question,
    actual_output=str(response),
    expected_output=ground_truth,
    retrieval_context=[n.text for n in response.source_nodes],
)

# Run with: deepeval test run test_rag.py
```

Key metrics to track per pipeline version:

| Metric | Target | Measures |
|---|---|---|
| Answer Relevancy | > 0.80 | Does answer address the question |
| Faithfulness | > 0.85 | Is answer grounded in retrieved chunks |
| Contextual Recall | > 0.75 | Did retrieval surface the right chunks |
| MRR@10 | > 0.60 | Mean reciprocal rank of first relevant chunk |

---

## 8. Production Patterns

**Async ingestion** — for `ask-ai-daily-automation`:
```python
import asyncio
from llama_index.core import VectorStoreIndex

async def ingest_batch(docs_batch):
    index = VectorStoreIndex.from_vector_store(vector_store)
    await index.ainsert_nodes(nodes)   # non-blocking

asyncio.run(ingest_batch(new_articles))
```

**Incremental updates** — avoid re-embedding unchanged docs:
```python
from llama_index.core.ingestion import IngestionPipeline, DocstoreStrategy
from llama_index.storage.docstore.redis import RedisDocumentStore

pipeline = IngestionPipeline(
    transformations=[parser, Settings.embed_model],
    vector_store=vector_store,
    docstore=RedisDocumentStore.from_host_and_port("localhost", 6379),
    docstore_strategy=DocstoreStrategy.UPSERTS,  # skip unchanged docs
)
pipeline.run(documents=docs)
```

**Query caching** — for repeated UPSC question patterns:
```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.storage.kvstore.redis import RedisKVStore

# Cache query results in Redis with TTL=3600s
# Wire this between query_engine.query() and the response return
```

**Blue-green namespace swap:**
1. Ingest new batch into `namespace="v2"`
2. Evaluate v2 metrics vs v1
3. Switch `vector_store` namespace to `"v2"` in app config
4. Delete `namespace="v1"` after 24h stability window
