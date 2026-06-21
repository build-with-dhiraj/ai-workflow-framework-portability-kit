# Code Audit — xpriment626/pi-factory

- **Files read:** 68 text/source files (every line indexed)
- **Pushed at:** 2026-06-13T01:51:31Z
- **Stars:** 3

## Code-backed scores

- **direct_install:** 7.5
- **claude_code_native:** 0.0
- **loop_implementation:** 4.0
- **registry_memory:** 7.5
- **verification:** 7.5
- **file_coverage:** 68
- **total:** 5.12

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: src/conductor/factory-loop.ts, tests/factory-loop.test.ts
- main_files: (none)

## Install facts (from manifests)

- npm script `check:node`
- npm script `predev`
- npm script `dev`
- npm script `prebuild`
- npm script `build`
- npm script `pretest`
- npm script `test`
- npm script `presmoke`
- npm script `smoke`
- npm script `precoral:test`
- npm script `coral:test`
- npm script `prepi:ping`

## Loop signals (line-indexed samples)

### verifier
- `README.md:12` — - `agents/*/coral-agent.toml`: local Coral agent manifests for planner, architect, implementer, reviewer.
- `README.md:119` — ## Verification
- `README.md:130` — `npm run smoke` does not call a model. It initializes SQLite, inserts placeholder kanban tickets, verifies the board/com
- `agents/architect/playbook.md:38` — - Reject server processes that remain running after verification.
- `agents/reviewer/coral-agent.toml:4` — name = "factory-reviewer"
### state_writeback
- `.gitignore:6` — *.sqlite
- `.gitignore:7` — *.sqlite-*
- `README.md:3` — Local-only first-pass wiring demo for a Pi + Coral + SQLite software-factory harness. This is not packaged for a marketp
- `README.md:7` — - `src/blackboard`: SQLite schema and API helpers for projects, kanban tickets, ticket events, agent touches, and Coral 
- `README.md:35` — The dev launcher creates `.factory/runs/<runId>/blackboard.sqlite`, writes `.factory/runs/<runId>/coral/config.toml`, st

## README vs code

README claim: # pi-factory  Local-only first-pass wiring demo for a Pi + Coral + SQLite software-factory harness. This is not packaged for a marketplace and does not mutate `~/.coral/agents`.  ## Shape  - `src/blackboard`: SQLite schema and API helpers for projects, kanban tickets, ticket events, agent touches, a

- Code contains loop engine / gate patterns (see loop signals above).
