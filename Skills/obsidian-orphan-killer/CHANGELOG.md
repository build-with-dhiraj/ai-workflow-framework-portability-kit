# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-03

### Added
- Initial public release.
- Three modes:
  - `resolve`: deterministic alias-table resolution of plain-string `entities:` / `topics:` to canonical `[[wikilinks]]` (no network, $0).
  - `anchor`: local-embedding (fastembed, `BAAI/bge-small-en-v1.5` @ `max_length=256`) fallback for true-orphan leaves; concepts-only target set by default; cosine floor 0.74; per-hub absorption cap 50.
  - `mint` (experimental): cluster orphans + LLM-name + mint new `concepts/` hubs for coherent clusters >= 5 members; gated behind `--experimental`.
- Safe-writes contract:
  - Frontmatter-only writes (body bytes never modified)
  - Atomic writes via tempfile + os.rename
  - Idempotency stamps (`raw_meta.resolved_at` / `anchored_at` / `clustered_at` + content hash)
  - Dangling-link guard (only links to hubs that exist on disk)
  - Per-hub absorption cap (anti-star)
  - Concepts-only by default (brand-leak guard)
  - DO_NOT_MERGE user-supplied pairs
  - Mint-side topic guards (TOPIC_DENYLIST, URL fragment, generic catch-all, lexical sanity)
  - Mint-mode duplicate-hub redirect
- CLI (`obsidian-orphan-killer`) with three subcommands. Every subcommand supports `--dry-run`.
- Audit TSV dump (per-candidate decision row, sorted by cosine descending) automatically written on `--dry-run` for anchor + mint modes.
- Cross-CLI `SKILL.md` for Claude Code, Cursor, Gemini CLI, and Codex.
- Five docs pages: `README.md`, `SKILL.md`, `docs/SAFETY.md`, `docs/RUBRIC.md`, `docs/COMPARISON.md`.
- `llms.txt` for AI crawlers.
- GitHub Actions test workflow (Linux + macOS, Python 3.10-3.12).
- Issue templates (bug + feature).
- 45 tests across slug, alias-table, resolve, anchor, guards, CLI.
- Demo vault at `examples/demo-vault/` with 10 intentionally-broken notes covering every code path.

### Engine decoupling (from upstream prototype)
- Generic hub-dirs convention. Defaults to `entities,concepts` but the user can pass `--hub-dirs your-dir1,your-dir2`.
- Generic scope-dirs. Defaults to `sources,inbox,context` but the user can pass an empty list for whole-vault.
- Pluggable LLM namer for mint mode. Defaults to OpenAI (reads `OPENAI_API_KEY`); user can supply any callable.
- No `community:` field assumption.
- No `_quarantine/` convention required.
- No mandatory `relationships:` / `related:` field; the orphan detection composes whatever the vault has.

### Known limitations
- Mint mode requires either the `openai` package + `OPENAI_API_KEY` OR a user-supplied `llm_namer` callable. Without one, qualifying clusters are reported but not minted.
- Anchor + mint modes require `fastembed`. Install with `pip install 'obsidian-orphan-killer[embed]'`.
- The default cosine floor (0.74) is calibrated for `BAAI/bge-small-en-v1.5` at `max_length=256`. Different embedders may need a different floor.
- No `de-star` mode in v0.1; deferred to v0.2 (Connecting-Dots-specific in the prototype).
