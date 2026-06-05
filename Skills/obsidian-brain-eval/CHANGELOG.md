# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-03

### Added
- Initial public release.
- Core eval engine (`obsidian_brain_eval.eval`) with two phases:
  - `generate()` — sample notes from a vault, ask an OpenAI-compatible client
    to write one natural question per note, write JSONL gold-set. Idempotent.
  - `score()` — run each gold question through a pluggable
    `RetrievalBackend` and compute Recall@k with per-question breakdown and a
    rank-distribution diagnostic.
- Default target Recall@10 >= 0.85, configurable via `--target`.
- Two retrieval backends shipped in `obsidian_brain_eval.backends`:
  - `NaiveBM25Backend` — zero-infra BM25 over title + body, via `rank-bm25`.
  - `LanceDBBackend` — hybrid FTS + BAAI/bge-small-en-v1.5 vector search
    against a pre-populated LanceDB `items` table.
- CLI (`obsidian-brain-eval`) with two subcommands:
  - `generate --vault PATH --out gold.jsonl --n 40 [--folders ... --force]`
  - `score    --vault PATH --gold gold.jsonl --backend naive|lancedb [--k 10 --target 0.85 --json-out result.json]`
- Cross-CLI `SKILL.md` for Claude Code, Cursor, Gemini CLI, and Codex.
- Two docs pages: `docs/RUBRIC.md` (methodology + citations), `docs/COMPARISON.md` (vs Smart Connections, Obsidian Copilot, generic RAG eval, obsidian-graph-auditor).
- `llms.txt` for AI crawlers.
- GitHub Actions test workflow (Python 3.10/3.11/3.12 on Ubuntu + macOS).
- Issue templates (bug + feature).
- A 10-note demo vault under `examples/demo-vault/` with sample gold-set so
  users can run the evaluator immediately, no GPT required.
- 22 tests covering scorer math, naive backend on synthetic vaults, CLI exit
  codes, JSONL round-trip, and the shipped demo-vault smoke path.

### Decoupling from upstream prototype
- Lifted from `workers/recall_eval.py` in the Connecting Dots stack and
  rewritten to remove `connecting_dots` imports. The hybrid retrieval logic
  was decoupled from `workers.ask_brain` into the new `LanceDBBackend`.
- Renamed `_get_client` injection point to a public `client=` kwarg on
  `generate()` so users with non-OpenAI clients can plug in any object
  exposing `chat.completions.create`.
- Removed the worker-trace side effect; the package has no side effects on
  import.
- Added the `RetrievalBackend` Protocol as the public extension point.
