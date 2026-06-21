# Code Audit — mikulgohil/se-agent-platform

- **Files read:** 92 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T06:15:32Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 3.5
- **claude_code_native:** 0.8999999999999999
- **loop_implementation:** 0.0
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 92
- **total:** 3.68

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- npm script `dev`
- npm script `build`
- npm script `start`
- npm script `lint`
- npm script `test`
- npm script `test:watch`
- npm script `typecheck`

## Loop signals (line-indexed samples)

### verifier
- `.github/workflows/ci.yml:10` — verify:
- `README.md:59` — - [Notes for reviewers](#notes-for-reviewers)
- `README.md:150` — risks, reviewer checklist, rollback plan — **copyable as Markdown** to paste
- `README.md:443` — - [ ] Real Claude adapter (structured output via Zod) — _needs an API key to verify_
- `README.md:444` — - [ ] Supabase adapter implementation + auth — _needs a live project to verify_
### hitl
- `README.md:27` — human-in-the-loop approval gate before the final artifact is created.
- `README.md:147` — - **Human-in-the-loop** — runs pause at `awaiting_approval`; you approve (→ PR
- `docs/ARCHITECTURE.md:81` — 5. Pauses at `awaiting_approval`.
- `docs/PROMPT.md:45` — 8. Pause for human approval.
- `docs/PROMPT.md:360` — - human-in-the-loop explanation
### state_writeback
- `README.md:154` — - **Settings** — model registry with pricing, the architecture seams, and the env vars
- `README.md:183` — data**: it returns new state and persists nothing, so any storage adapter can drive it.
- `README.md:192` — | **Persistence** | `Repository` | seeded in-memory store | Supabase (`schema.sql` included) |
- `README.md:197` — Supabase `jsonb` columns — the persistence seam costs nothing.
- `README.md:246` — registry maps each step to its owning agent, so the runtime never hard-codes who does
### claude_native
- `docs/PROMPT.md:1` — # Claude Code Prompt: Software Engineering Agent Platform
- `docs/PROMPT.md:3` — You are Claude Code working inside my local development environment.
- `docs/PROMPT.md:434` — ## Final Output Expected From Claude Code

## README vs code

README claim: <div align="center">  # 🛠️ Forge — Software Engineering Agent Platform  **A control center for software-engineering agents.** Submit a feature request and watch a team of specialist agents plan it, simulate the implementation, write a test plan, run quality gates, and produce a pull-request-ready ar

- Loop implementation in code is thin or documentation-only.
