# Contributing

Thanks for your interest in `obsidian-brain-eval`. The project is small and the bar to contribute is low. Issues, doc fixes, new tests, new retrieval backends, and well-justified methodology changes are all welcome.

## Development setup

```bash
git clone https://github.com/build-with-dhiraj/obsidian-brain-eval
cd obsidian-brain-eval
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Or with stdlib `venv`:

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Running the evaluator against a real vault

```bash
# Score with the shipped naive BM25 baseline (no GPT needed):
.venv/bin/obsidian-brain-eval score \
    --vault /path/to/your/vault \
    --gold /path/to/gold.jsonl \
    --backend naive

# Generate a gold-set if you don't have one yet (needs OPENAI_API_KEY):
export OPENAI_API_KEY=...
.venv/bin/obsidian-brain-eval generate \
    --vault /path/to/your/vault \
    --out /path/to/gold.jsonl \
    --n 40
```

## Filing issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For bugs, please include:

- Output of `obsidian-brain-eval --version`
- The full CLI command you ran
- The error / surprising output, with logs
- A minimal vault + 2-3 gold records that reproduces the issue, if possible

## Proposing new retrieval backends

We are happy to take PRs that add new backends. A new backend must:

1. Implement the `RetrievalBackend` protocol from `obsidian_brain_eval.eval`
   (a single `topk(question, k) -> list[str]` method).
2. Return paths in the canonical `<vault.name>/<relative-path>.md` shape so they
   match what `generate()` writes into `relevant_paths`.
3. Declare its install extra in `pyproject.toml` (e.g. `[smart_connections]`)
   and import its dependencies lazily inside `__init__` so the package stays
   light by default.
4. Ship at least one test using a synthetic fixture vault.

If your backend wraps a commercial API (Smart Connections, vector DB
providers, etc.), please make the dependency optional and document the
credentials it needs.

## Proposing methodology changes

The defaults (Recall@10, target 0.85, 30-50 question gold-sets) are anchored in
`docs/RUBRIC.md` with citations. Methodology changes need a cited rationale.
"Feels right" is not sufficient.

If you want a different metric (MRR, NDCG, answer-quality), it's probably a
*different tool*, not a methodology change here. obsidian-brain-eval's contract
is "Recall@k against a vault-aware gold-set, $0 to score, no LLM in the loop
for the gate".

## Style

- Match the existing code style. The repo runs `ruff` in CI.
- No emoji in code or docs unless specifically requested.
- No em-dashes in prose (humanizer rule).
- Cite your sources. Every threshold in `docs/RUBRIC.md` has a citation.
- Run the test suite (`pytest`) before opening a PR.

## Code of conduct

Be kind. The PKM and RAG-eval communities are full of thoughtful people with strong opinions; that's a feature. Strong opinions, weakly held, is the bar.
