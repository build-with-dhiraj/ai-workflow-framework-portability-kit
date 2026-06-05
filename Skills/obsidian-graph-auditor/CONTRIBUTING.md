# Contributing

Thanks for your interest in `obsidian-graph-auditor`. The project is small and the bar to contribute is low. Issues, doc fixes, new tests, and well-justified new rubric dimensions are all welcome.

## Development setup

```bash
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor
cd obsidian-graph-auditor
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Or with stdlib `venv`:

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

## Running the auditor against a real vault

```bash
.venv/bin/obsidian-graph-audit --vault /path/to/your/vault
```

## Filing issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For bugs, please include:

- Output of `obsidian-graph-audit --version`
- The full CLI command you ran
- The error / surprising output, with logs (`--quiet` off so you see the human table)
- A minimal vault that reproduces the issue, if possible (10-30 notes is plenty)

## Proposing new rubric dimensions

The rubric is intentionally minimal. New dimensions should:

1. Be **purely structural**, computable from the link graph alone, no LLM in the loop.
2. Have **literature backing** for the threshold. "Feels right" is not sufficient.
3. Be **independent** of the existing 8. Strongly correlated dimensions don't add information.
4. Have a **concrete fix path** documented in `docs/GRAPH-ANALYSIS.md`.

If you want a dimension that requires LLM judgment (recall, semantic coherence, personal usefulness), it's probably a *different tool*, not a new dimension here. The auditor's contract is "pure local Python, no API keys".

## Style

- Match the existing code style. The repo runs `ruff` in CI.
- No emoji in code or docs unless specifically requested.
- No em-dashes in prose (humanizer rule).
- Cite your sources. Every threshold in `docs/RUBRIC.md` has a citation; new ones must too.
- Run the test suite (`pytest`) before opening a PR.

## Code of conduct

Be kind. The PKM community is full of thoughtful people with strong opinions; that's a feature. Strong opinions, weakly held, is the bar.
