---
name: obsidian-brain-eval
description: |
  Test your Obsidian RAG, measure your second brain's retrieval quality, and score your vault on Recall@10 against a gold-set generated from your own notes. Pluggable retrieval backends (BM25 zero-infra, LanceDB hybrid FTS+vector). Pure Python CLI, read-only. The skill is the only tool that publishes a methodology and a default 0.85 pass/fail threshold for "is your vault chat actually working". Use when the user asks any of: test my obsidian rag, measure my second brain, is my pkm answering well, obsidian retrieval quality, test my obsidian search, recall at 10 my vault, evaluate my obsidian rag, obsidian rag benchmark, score my obsidian retrieval, is my second brain working, obsidian search quality, pkm retrieval eval, obsidian eval framework, gold set obsidian, smart connections eval, obsidian copilot eval, rag over my vault, does my vault chat work, vault retrieval test. Works on any markdown vault using wikilinks (Obsidian, Logseq, Foam, Quartz). Complements obsidian-graph-auditor (measures graph topology); brain-eval measures retrieval quality.
license: MIT
author: Dhiraj Singh Pawar (build-with-dhiraj)
homepage: https://github.com/build-with-dhiraj/obsidian-brain-eval
version: 0.1.0
---

# Obsidian Brain Eval

Measure whether your Obsidian RAG actually works. Generate a gold-set from your vault, score any retrieval backend on Recall@10, and get a PASS or BELOW TARGET grade against a 0.85 default threshold.

## When to use this skill

Trigger this skill whenever the user wants to:

1. **Test their vault's RAG.** "test my obsidian rag", "is my second brain answering well", "does my vault chat work", "rag over my vault test".
2. **Measure retrieval quality.** "obsidian retrieval quality", "score my obsidian retrieval", "recall at 10 my vault", "obsidian search quality".
3. **Benchmark a retrieval system.** "obsidian rag benchmark", "compare BM25 vs hybrid in my vault", "evaluate Smart Connections", "Obsidian Copilot eval", "vault retrieval test".
4. **Generate a gold-set.** "make a gold-set for my vault", "create eval questions from my notes", "gold set obsidian".
5. **Establish a CI gate.** Run `score --backend ...` in CI to block retrieval regressions.
6. **Decide what to improve next.** When Recall@10 < 0.85, the misses tell you where the retrieval layer fails (paraphrase, rare vocab, chunking).

## What it does

- **`generate`** — Sample N representative notes from your vault, ask GPT-4.1 to write ONE natural question per note that the note answers, and write a JSONL gold-set. Each record pins the source note plus any notes it strongly links via frontmatter (`entities`, `topics`, `related`). Costs roughly $1-2 of OpenAI for 40 questions. Idempotent: skips notes already in the gold-set unless `--force`.
- **`score`** — Run each gold question through a pluggable retrieval backend and check whether a known-relevant note appears in the top-k. Reports Recall@k, hit/miss per question, and a rank distribution. No GPT cost.

## How to run

After installation (see `## Install` below):

```bash
# Step 1 (optional): generate a 40-question gold-set with GPT-4.1.
# Skip this and use the shipped sample if you don't want to spend GPT.
export OPENAI_API_KEY=...
obsidian-brain-eval generate --vault ~/Documents/MyVault --out gold.jsonl --n 40

# Step 2: score with the zero-infra BM25 backend.
obsidian-brain-eval score --vault ~/Documents/MyVault --gold gold.jsonl --backend naive

# Or score with the LanceDB hybrid backend, against a table you already populated.
obsidian-brain-eval score --vault ~/Documents/MyVault --gold gold.jsonl \
    --backend lancedb --db ~/Documents/MyVault/.lancedb

# CI gate: exit 1 if Recall@10 < 0.85.
obsidian-brain-eval score --vault ~/Documents/MyVault --gold gold.jsonl \
    --backend naive --quiet --json-out result.json

# Try it instantly on the shipped 10-note demo vault.
obsidian-brain-eval score --vault examples/demo-vault \
    --gold examples/sample-gold-set.jsonl --backend naive
```

Default exit codes:

- `0`: score met or exceeded the target (default 0.85)
- `1`: score below target
- `2`: vault or gold-set missing/unreadable

## How to read the output

```
================================================================
  RECALL@10 - obsidian-brain-eval
================================================================
  questions   40
  hits        37
  Recall@10   0.9250   (target >= 0.85)
  status      PASS
----------------------------------------------------------------
  MISSES
    x  Where do I find notes that compare cloud providers?
       want: vault/concepts/cloud-comparison.md
----------------------------------------------------------------
  HITS (first-relevant rank distribution)
    rank  1: 24
    rank  2: 8
    rank  3: 3
    rank  5: 1
    rank  7: 1
================================================================
```

Read it in three passes:

1. **The headline.** Recall@10 + PASS/BELOW TARGET. Done if PASS.
2. **The misses.** Each miss is a concrete repair: either the gold-set question is too vague, or your retrieval is missing a real signal. Walk these.
3. **The rank distribution.** Hits clustered at rank 1-2 = retrieval is sharp. Hits drifting to ranks 5-10 = retrieval is finding the right thing but ranking it poorly. The fix is reranking, not more candidates.

## Install

### Claude Code

```bash
pip install "obsidian-brain-eval[naive]"
mkdir -p ~/.claude/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.claude/skills/obsidian-brain-eval
```

Then ask Claude Code: "test my obsidian rag at ~/Documents/MyVault using the shipped gold set", or "generate a 40-question gold-set for ~/Documents/MyVault and score it with the naive backend".

### Cursor

```bash
pip install "obsidian-brain-eval[naive]"
mkdir -p ~/.cursor/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.cursor/skills/obsidian-brain-eval
```

### Gemini CLI

```bash
pip install "obsidian-brain-eval[naive]"
mkdir -p ~/.gemini/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.gemini/skills/obsidian-brain-eval
```

### Codex CLI

```bash
pip install "obsidian-brain-eval[naive]"
mkdir -p ~/.codex/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.codex/skills/obsidian-brain-eval
```

## Pluggable backends

Two backends ship by default. Both implement the same `topk(question, k) -> list[str]` protocol so you can drop in your own (see `obsidian_brain_eval.backends` for the protocol definition).

| Backend | Install extra | What it does | When to use |
|---|---|---|---|
| `naive` (BM25) | `pip install "obsidian-brain-eval[naive]"` | BM25 over title + body, ASCII fold + stopword strip, no embeddings, no API | Baseline. Run this first. If your fancy stack does not beat it, your fancy stack is wrong. |
| `lancedb` (hybrid) | `pip install "obsidian-brain-eval[lancedb]"` | Hybrid FTS + BAAI/bge-small vector search over a LanceDB `items` table you already populated | Benchmark production vault-RAG stacks. The exact backend the upstream engine ships against. |

Custom backends are a 10-line class:

```python
from obsidian_brain_eval.eval import score, load_gold

class MyBackend:
    def __init__(self, vault):
        # Index whatever you want.
        ...

    def topk(self, question: str, k: int) -> list[str]:
        # Return the top-k vault paths, in the canonical 'vaultname/folder/file.md' shape.
        ...

result = score(load_gold("gold.jsonl"), MyBackend("/path/to/vault"), k=10)
```

## What it does NOT do

- It does **not** modify your vault. Read-only by design.
- It does **not** run an LLM for the `score` step. The default target is the pure retrieval-layer Recall@10.
- It does **not** require an Obsidian plugin install. Pure CLI.
- It does **not** require Obsidian to be installed at all. Works on any markdown directory with wikilinks.
- It does **not** measure answer quality. That is a different problem (LLM-as-judge, harness like ragas, etc.). This skill isolates the retrieval gate so when an answer is bad you can tell whether the right note was even retrieved.

## Related

- The 30-50 question methodology, gold-set sizing rationale, and pass-threshold defence: `docs/RUBRIC.md`
- Comparison vs Smart Connections / Obsidian Copilot / vault chat / LangChain eval pipelines / obsidian-graph-auditor: `docs/COMPARISON.md`
- Companion skill that measures graph topology (orphan rate, modularity, top-hub force-star): [obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor)
