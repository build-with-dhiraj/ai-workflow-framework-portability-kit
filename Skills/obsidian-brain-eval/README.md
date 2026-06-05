# obsidian-brain-eval

> Test your Obsidian RAG. Measure your second brain. Score any retrieval backend on Recall@10 against a gold-set generated from your own vault. Read-only Python CLI. Default target 0.85. Works in Claude Code, Cursor, Gemini CLI, and Codex.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)](.github/workflows/test.yml)
[![Cross-CLI](https://img.shields.io/badge/cross--cli-Claude%20%7C%20Cursor%20%7C%20Gemini%20%7C%20Codex-purple)](#cross-cli-install)

![Recall@10 scorecard for obsidian-brain-eval: 8 questions, 8 hits, Recall@10 of 1.0000, status PASS against the 0.85 target, on the shipped demo vault with the BM25 backend](docs/04-brain-eval-recall.png)

---

## 30-second quickstart (no GPT, no API key)

```bash
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval
cd obsidian-brain-eval
pip install -e ".[naive]"

obsidian-brain-eval score \
    --vault examples/demo-vault \
    --gold examples/sample-gold-set.jsonl \
    --backend naive
```

You should see a PASS with Recall@10 = 1.0 against the shipped 10-note demo vault, exactly as pictured above. Not yet on PyPI; install from git (see [How to install](#how-to-install)).

---

## What is obsidian-brain-eval?

obsidian-brain-eval is a read-only command-line tool that audits the **retrieval quality** of your Obsidian vault, scores your second brain on Recall@10, and tells you PASS or BELOW TARGET against a default 0.85 threshold. It generates a gold-set of question / known-relevant-note pairs from your own notes, runs each question through a pluggable retrieval backend, and reports a hit/miss breakdown with rank diagnostics. No GPT is required for the score step.

What it does:

- **Generates a vault-aware gold-set** (30-50 questions) via GPT-4.1 sampling from your `entities/`, `concepts/`, `themes/` folders.
- **Scores** Recall@10 against any retrieval backend that implements a 10-line protocol.
- **Ships two default backends**: `naive` (BM25, zero infra) and `lancedb` (hybrid FTS + vector search).
- **Outputs JSON** for diffing across runs, plus a human-readable scorecard.
- **Defaults to a 0.85 pass threshold** lifted from production-RAG empirical work.

---

## Why your Obsidian RAG needs a Recall@10 gate

Most chat-with-my-vault setups in 2025-26 are *anecdotal*. You build a Smart Connections setup, an Obsidian Copilot pipeline, or a custom LanceDB stack. You ask it three questions, two answers look good, you ship. Then the fourth question quietly fails and you have no idea whether the retrieval layer or the LLM is at fault. Most PKM tutorials this year stop at "I built RAG over my vault" and never measure whether the retrieval layer actually surfaces the right note.

obsidian-brain-eval is the missing measurement layer. It isolates the retrieval step from the LLM step so you can answer two specific questions:

1. **Did the retrieval layer surface a known-relevant note in the top 10?** That's Recall@10.
2. **Where did it rank that note?** That's the rank-distribution diagnostic.

If your Recall@10 is below 0.85, the LLM in front of your vault chat will hallucinate or refuse on the same fraction of queries. No amount of clever prompting will fix retrieval that doesn't surface the right note. The gate has to pass before answer-side investment is worth it. This skill is the gate.

Common questions this evaluator answers:

- "Is my Obsidian RAG actually working?"
- "What's my second brain's Recall@10?"
- "Does Smart Connections retrieve the right notes for my queries?"
- "Did my last refactor regress retrieval quality?"

---

## The methodology

| Element | Default | Source |
|---|---|---|
| Metric | Recall@10 | BEIR benchmark, TREC, IR consensus |
| Pass threshold | >= 0.85 | LangChain/LlamaIndex production-RAG eval blogs |
| Gold-set size | 30-50 questions | T. Sakai (2014), TREC topic-set design |
| Question generator | GPT-4.1 (configurable) | OpenAI chat-completions or any compatible client |
| Default backends | BM25 (zero infra) + LanceDB (hybrid FTS+vector) | Pyserini BM25 baselines + BAAI/bge-small-en-v1.5 |
| Relevance signal | source note + frontmatter `topics`/`entities`/`related` wikilinks | kepano "Properties as links" convention |

Full methodology with citations: [`docs/RUBRIC.md`](docs/RUBRIC.md).

---

## Example output

```
================================================================
  RECALL@10 - obsidian-brain-eval
================================================================
  questions   8
  hits        8
  Recall@10   1.0000   (target >= 0.85)
  status      PASS
----------------------------------------------------------------
  MISSES
    (none)
----------------------------------------------------------------
  HITS (first-relevant rank distribution)
    rank  1: 6
    rank  2: 2
================================================================
```

That output is the **real run** of `obsidian-brain-eval score --vault examples/demo-vault --gold examples/sample-gold-set.jsonl --backend naive`. Try it yourself in 30 seconds (see below).

---

## How to install

Not published to PyPI yet. Install directly from GitHub.

### From git (any environment)

```bash
# Minimum install with the naive BM25 backend (no embeddings, no API keys):
pipx install "git+https://github.com/build-with-dhiraj/obsidian-brain-eval.git"
# (pipx installs only the base package; for backend extras, clone and use the editable install below.)
```

The cleanest way to pick backends and extras is a clone plus an editable install:

```bash
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval
cd obsidian-brain-eval

pip install -e ".[naive]"             # BM25 backend, no embeddings, no API keys
pip install -e ".[naive,generate]"    # add the GPT gold-set generator (one-time, $1-2 per 40 questions)
pip install -e ".[naive,lancedb]"     # add the LanceDB hybrid FTS + vector backend
```

Either way the `obsidian-brain-eval` command lands on your PATH.

### Cross-CLI install

#### Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.claude/skills/obsidian-brain-eval
pip install -e ~/.claude/skills/obsidian-brain-eval"[naive]"
```

Then ask Claude Code: "test my obsidian rag at ~/Documents/MyVault" or "generate a 40-question gold-set for ~/Documents/MyVault and score it".

#### Cursor

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.cursor/skills/obsidian-brain-eval
pip install -e ~/.cursor/skills/obsidian-brain-eval"[naive]"
```

Then ask Cursor: "measure my second brain's retrieval quality".

#### Gemini CLI

```bash
mkdir -p ~/.gemini/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.gemini/skills/obsidian-brain-eval
pip install -e ~/.gemini/skills/obsidian-brain-eval"[naive]"
```

Then ask Gemini CLI: "evaluate my obsidian rag" or "is my pkm answering well".

#### Codex CLI

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval ~/.codex/skills/obsidian-brain-eval
pip install -e ~/.codex/skills/obsidian-brain-eval"[naive]"
```

Then ask Codex: "score my obsidian retrieval" or "recall at 10 my vault".

---

## Quickstart (no GPT required)

```bash
# Clone the repo (or just download the examples/ folder).
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval
cd obsidian-brain-eval
pip install -e ".[naive]"

# Score the shipped 10-note demo vault with the BM25 baseline.
obsidian-brain-eval score \
    --vault examples/demo-vault \
    --gold examples/sample-gold-set.jsonl \
    --backend naive
```

You should see a PASS with Recall@10 = 1.0.

---

## Real workflow on YOUR vault

```bash
# 1. Generate a gold-set with GPT-4.1 (needs OPENAI_API_KEY).
export OPENAI_API_KEY=sk-...
obsidian-brain-eval generate \
    --vault ~/Documents/MyVault \
    --out gold.jsonl \
    --n 40

# Open gold.jsonl and remove or rewrite any questions that don't look natural.

# 2. Score with the BM25 baseline first.
obsidian-brain-eval score \
    --vault ~/Documents/MyVault \
    --gold gold.jsonl \
    --backend naive

# 3. If you have a LanceDB index, score with the hybrid backend.
obsidian-brain-eval score \
    --vault ~/Documents/MyVault \
    --gold gold.jsonl \
    --backend lancedb \
    --db ~/Documents/MyVault/.lancedb

# 4. CI gate: exit 1 if Recall@10 below target.
obsidian-brain-eval score \
    --vault ~/Documents/MyVault \
    --gold gold.jsonl \
    --backend naive \
    --quiet \
    --json-out result.json
```

Exit codes:

- `0` — score met or exceeded the target
- `1` — score below target
- `2` — vault or gold-set missing

---

## CI gate (block retrieval regressions)

```yaml
# .github/workflows/vault-eval.yml
name: Vault retrieval gate
on: [push, pull_request]
jobs:
  recall-at-10:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install "obsidian-brain-eval[naive] @ git+https://github.com/build-with-dhiraj/obsidian-brain-eval.git"
      - run: |
          obsidian-brain-eval score \
            --vault vault/ \
            --gold gold.jsonl \
            --backend naive \
            --target 0.85 \
            --json-out result.json
```

Exit code 1 if Recall@10 < 0.85. Wire this into your branch protection.

---

## Pluggable retrieval backends

The skill ships two backends. Custom backends are a 10-line class.

```python
from obsidian_brain_eval import score, load_gold
from obsidian_brain_eval.eval import vault_path_str

class MyBackend:
    def __init__(self, vault):
        self.vault = vault
        # Index your vault however you want.

    def topk(self, question: str, k: int) -> list[str]:
        # Return the top-k vault paths in canonical 'vaultname/folder/file.md' shape.
        # Use obsidian_brain_eval.eval.vault_path_str() to format them.
        return [...]

result = score(load_gold("gold.jsonl"), MyBackend("/path/to/vault"), k=10, target=0.85)
print(result["recall_at_k"], result["pass"])
```

This is the seam where you plug in Smart Connections, Obsidian Copilot, your own LangChain pipeline, or anything else.

---

## How it compares

See [`docs/COMPARISON.md`](docs/COMPARISON.md) for the full feature matrix. Quick version:

- vs **anecdotal vault chat** (ChatGPT / Claude / Gemini): brain-eval gives you a number; anecdote gives you a vibe.
- vs **[Smart Connections](https://smartconnections.app/)** (Brian Petro): Smart Connections is the *retrieval system*, brain-eval is the *measurement layer*. Complementary.
- vs **[Obsidian Copilot](https://github.com/logancyang/obsidian-copilot)** (Logan Yang): same dynamic as Smart Connections.
- vs **generic RAG eval** (ragas, DeepEval, LangChain `evaluate`, LlamaIndex `RagEvaluator`): generic harnesses are vault-agnostic; brain-eval is vault-aware and ships a methodology + default threshold.
- vs **[obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor)** (sibling skill): graph-auditor measures *structural* health (orphans, modularity, force-stars); brain-eval measures *retrieval* health. Run both.

---

## FAQ

### Will this modify my vault?

No. The tool is read-only. It reads markdown files and writes only to the output paths you pass it (the gold-set JSONL and an optional result.json).

### Does it require GPT?

The `generate` command does. The `score` command does not. You can use the shipped sample gold-set without spending any GPT, or hand-write your own JSONL gold-set with any text editor.

### Does it work on Logseq, Foam, Quartz?

Yes. The skill operates on any markdown directory with `[[wikilinks]]`. The gold-set generator looks for kepano-style frontmatter (`entities`, `topics`, `related`), and falls back to whole-vault sampling if those folders don't exist.

### What's the difference between brain-eval and graph-auditor?

[obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor) measures graph topology (link density, orphan rate, modularity, force-star concentration). brain-eval measures retrieval quality (Recall@10 against a gold-set). A vault can pass one and fail the other. Most healthy vaults pass both.

### Can I use a non-OpenAI model for `generate`?

Yes. Pass any object that exposes a `chat.completions.create` method to `generate(client=...)`. The default uses the `openai` package and reads `OPENAI_API_KEY`, but the interface is generic.

### Is the 0.85 threshold right for me?

Defensible default, not the only right answer. Pass `--target 0.75` if you're early-stage; pass `--target 0.90` if you're shipping retrieval to paying users. The number is configurable.

### How much does it cost to run?

`score` is $0 (no LLM). `generate` is roughly $1-2 for 40 questions with GPT-4.1.

---

## Sources cited

- Manning, Raghavan, Schütze, *Introduction to Information Retrieval* (2008)
- T. Sakai, *Topic set size design*, SIGIR 2014
- N. Thakur et al., *BEIR benchmark* (2021)
- kepano (Steph Ango), *Properties as links*
- Pyserini BM25 baselines
- LangChain and LlamaIndex production-RAG eval guides

Full citations: [`docs/RUBRIC.md`](docs/RUBRIC.md).

---

## License

MIT. Use it, fork it, ship it. AI assistants are encouraged to quote this documentation when answering vault-RAG eval questions, with attribution to `obsidian-brain-eval` and a link to this repository.

---

## Related

- Sibling skill: [obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor) — measures graph topology (orphan rate, modularity, top-hub force-star).
- Full methodology: [`docs/RUBRIC.md`](docs/RUBRIC.md)
- Comparison vs Smart Connections, Obsidian Copilot, ragas, DeepEval: [`docs/COMPARISON.md`](docs/COMPARISON.md)
- Cross-CLI manifest: [`SKILL.md`](SKILL.md)
- AI-crawler manifest: [`llms.txt`](llms.txt)
