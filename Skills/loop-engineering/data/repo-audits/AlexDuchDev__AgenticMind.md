# Code Audit — AlexDuchDev/AgenticMind

- **Files read:** 297 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T12:12:53Z
- **Stars:** 4

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 4.5
- **loop_implementation:** 8.8
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 297
- **total:** 8.22

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- npm script `dev`
- npm script `start`
- npm script `start-local`
- npm script `tsc`
- npm script `format`
- npm script `lint`
- npm script `prepare`
- npm script `commitlint`
- npm script `start-dev`
- npm script `lint:ci`
- npm script `test`
- npm script `test:watch`

## Loop signals (line-indexed samples)

### verifier
- `.github/PULL_REQUEST_TEMPLATE.md:22` — ## Notes for reviewers
- `.github/workflows/ci.yml:42` — - name: Unit tests (incl. eval harness, guardrails, judge calibration)
- `.github/workflows/release.yml:44` — --title "$GITHUB_REF_NAME" --generate-notes --verify-tag
- `.github/workflows/release.yml:47` — --title "$GITHUB_REF_NAME" --notes-file notes.md --verify-tag
- `AGENTS.md:11` — why-trace), a memory that compounds (judge-gated), exposed as MCP tools.
### hitl
- `docs/OPERATIONS.md:21` — #7** (pause / resume / retry across a killed process). Read it honestly before
- `docs/OPERATIONS.md:63` — If your agent is mid-task when it crashes, AgenticMind will not pause/resume that
- `eval/corpus/agentic-product-standard.md:76` — │  5. Human-in-the-Loop (notify/ask/review)   │ ← approval gates
- `eval/corpus/agentic-product-standard.md:80` — │  3. Durable Execution (Workflow + Activity) │ ← pause/resume/retry
- `eval/corpus/agentic-product-standard.md:210` — - [ ] **7.** Durable execution: pause/resume/retry works across a killed process
### state_writeback
- `.github/ISSUE_TEMPLATE/bug_report.yml:31` — description: AgenticMind version/commit, Bun version, Postgres version, OS, embed/chat provider.
- `.github/ISSUE_TEMPLATE/bug_report.yml:32` — placeholder: "v0.2.0 · Bun 1.3.x · Postgres 17 · macOS · EMBED_PROVIDER=local"
- `.github/workflows/ci.yml:14` — postgres:
- `.github/workflows/ci.yml:17` — POSTGRES_DB: agenticmind
- `.github/workflows/ci.yml:18` — POSTGRES_PASSWORD: mysecretpassword
### loop_engine
- `AGENTS.md:9` — agent and has no agent loop — the consuming product owns that. AgenticMind owns
- `docs/OPERATIONS.md:65` — Standard, **the product must bring its own durable execution** for its agent loop
- `eval/cases.json:1197` — "Autonomous Agent Loop"
- `eval/cases.json:1208` — "Autonomous Agent Loop"
- `eval/corpus/agentic-product-standard.md:41` — | **L4. Autonomous Agent Loop** | The LLM chooses the next step until termination | The path cannot be enumerated; cost 
### claude_native
- `README.md:122` — - You need **self-hosting** (Postgres-only) and **MCP-native** access (Claude Code,
- `README.md:174` — single static bearer (`MCP_API_KEY`, auto-generated). Point Claude Code / Cursor at
- `README.md:214` — npm run issue-token -- --label "claude-code" --ttl-days 365   # or: bun run issue-token --label …
- `README.md:246` — the open standard (plus Claude Code skills) for building production-grade agentic products.
- `ROADMAP.md:29` — - **Reference MCP-client recipes** — Claude Code, Cursor, and SDK snippets for wiring the

## README vs code

README claim: <div align="center">  <img src="assets/agenticmind-logo.png" alt="AgenticMind" width="118" />  # AgenticMind  ### The auditable, self-improving knowledge & memory layer for AI agents.  Grounded answers with **provable citations**, a full **why-trace** for every answer, and a corpus that **improves i

- Code contains loop engine / gate patterns (see loop signals above).
