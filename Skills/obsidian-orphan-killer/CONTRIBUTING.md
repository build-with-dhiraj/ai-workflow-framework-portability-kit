# Contributing

Thanks for your interest in `obsidian-orphan-killer`. The project is small, the bar to contribute is low, and the trust model is "every guard ships with a test that locks it in".

## Development setup

```bash
git clone https://github.com/build-with-dhiraj/obsidian-orphan-killer
cd obsidian-orphan-killer
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Or with stdlib `venv`:

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

For embedding-mode tests (anchor + mint), add the `embed` extra:

```bash
.venv/bin/pip install -e ".[dev,embed]"
```

## Running the tool against a real vault

```bash
# ALWAYS dry-run on a real vault first.
.venv/bin/obsidian-orphan-killer resolve --vault /path/to/your/vault --dry-run
.venv/bin/obsidian-orphan-killer anchor  --vault /path/to/your/vault --dry-run
```

## Filing issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For bugs, please include:

- Output of `obsidian-orphan-killer --version`
- The full CLI command you ran
- The stats output (sample lines are fine)
- A minimal vault that reproduces the issue, if possible (10-30 notes is plenty)

Label safety bugs `safety` and we'll triage them as release blockers.

## Adding a new mode

The bar for a new mode (the third orthogonal action after resolve / anchor / mint) is high. It should:

1. Be a **fundamentally different remediation strategy**, not a parameter tweak on an existing mode.
2. Ship with **every existing safety guard** (frontmatter-only, atomic, idempotent, dangling-link guard, per-hub cap if it touches multiple notes).
3. Have a **dry-run path** that writes an audit TSV.
4. Be **gated behind `--experimental`** if it writes new notes (the mint precedent).
5. Document the failure mode it addresses in `docs/RUBRIC.md`.

## Adding a new safety guard

The bar is LOW. Guards should:

1. Be **testable**.
2. Address a **specific real-world failure mode** (cite an example).
3. Add a **single H2 section** to `docs/RUBRIC.md` with statement / mechanism / test / verify recipe.
4. Update `docs/SAFETY.md` with a user-facing version.
5. Update `README.md`'s safety table.

PRs welcome. The bar for REMOVING a guard is "explicit user discussion + a release-note paragraph explaining the new failure mode".

## Style

- Match the existing code style. The repo runs `ruff check` in CI.
- No emoji in code or docs unless specifically requested.
- No em-dashes in prose (humanizer rule).
- Safety BEFORE features in user-facing docs.
- Every safety claim cites the test that enforces it.
- Cite your sources. Every claim in `docs/RUBRIC.md` and `docs/COMPARISON.md` has a basis; new ones must too.
- Run the test suite (`pytest`) and the linter (`ruff check`) before opening a PR.

## Code of conduct

Be kind. The PKM community has strong opinions and that's a feature, not a bug. Strong opinions, weakly held, is the bar.
