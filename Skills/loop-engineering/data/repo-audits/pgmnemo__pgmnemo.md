# Code Audit — pgmnemo/pgmnemo

- **Files read:** 343 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T21:04:57Z
- **Stars:** 4

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 1.2
- **loop_implementation:** 0.8
- **registry_memory:** 7.5
- **verification:** 7.5
- **file_coverage:** 343
- **total:** 2.69

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### verifier
- `.github/PULL_REQUEST_TEMPLATE.md:56` — | process_guardian | Phantom-DONE check: all listed files exist on disk | `[ ]` Verified |
- `.github/PULL_REQUEST_TEMPLATE.md:68` — ### Artifact checklist (process_guardian verification)
- `.github/workflows/ci.yml:25` — - name: Verify extension loads
- `.github/workflows/ci.yml:153` — # without blocking ship while we verify older-version compatibility claims
- `.github/workflows/ci.yml:197` — # Verify ALTER EXTENSION UPDATE chain works end-to-end on PG 17.
### state_writeback
- `.github/ISSUE_TEMPLATE/bug_report.md:24` — - PostgreSQL version:
- `.github/workflows/ci.yml:10` — - name: Install PostgreSQL 17 + pgvector + build deps
- `.github/workflows/ci.yml:12` — sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pg
- `.github/workflows/ci.yml:13` — curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.
- `.github/workflows/ci.yml:15` — sudo apt-get install -y postgresql-17 postgresql-17-pgvector postgresql-server-dev-17 build-essential
### loop_engine
- `AGENTS.md:447` — ### Recipe 1: Memory for an agent loop
### claude_native
- `.gitignore:64` — .claude/
- `POSITIONING.md:138` — | **Install model** | `bun install gbrain` (PGLite embedded) | `pip install memoir` + Claude Code plugin | `npm install 
- `POSITIONING.md:150` — **Use agentmemory if:** you want drop-in memory for a single coding agent (Claude Code, Cursor) with zero-config auto-ca
- `docs/COMPETITIVE_REALITY.md:235` — Ships as Claude Code plugin.

## README vs code

README claim: <div align="center">  <img src="assets/logo.svg" alt="pgmnemo" width="220">  ### Agent memory that learns which lessons worked — inspectable in plain SQL, in your Postgres  <!-- GIF: assets/demo.gif (rendered on host via vhs) -->  [![Release](https://img.shields.io/github/v/release/pgmnemo/pgmnemo?l

- Loop implementation in code is thin or documentation-only.
