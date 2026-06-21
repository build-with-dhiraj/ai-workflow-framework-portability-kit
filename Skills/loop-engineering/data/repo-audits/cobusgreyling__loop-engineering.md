# Code Audit — cobusgreyling/loop-engineering

- **Files read:** 201 text/source files (every line indexed)
- **Pushed at:** 2026-06-19T11:57:00Z
- **Stars:** 522

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 201
- **total:** 9.62

## Entrypoints (from code)

- skill_md: skills/loop-budget/SKILL.md, skills/loop-triage/SKILL.md, skills/loop-verifier/SKILL.md, skills/minimal-fix/SKILL.md, starters/changelog-drafter/.claude/skills/changelog-scan/SKILL.md, starters/changelog-drafter/.claude/skills/draft-release-notes/SKILL.md, starters/changelog-drafter/.codex/skills/changelog-scan/SKILL.md, starters/changelog-drafter/.codex/skills/draft-release-notes/SKILL.md
- hooks: (none)
- loop_scripts: tools/loop-audit/src/auditor.ts, tools/loop-audit/src/cli.ts, tools/loop-audit/src/reporter.ts, tools/loop-cost/src/cli.ts, tools/loop-cost/src/estimator.ts, tools/loop-init/src/cli.ts
- main_files: (none)

## Install facts (from manifests)

- bins: loop-audit, loop-cost, loop-init
- npm script `validate:registry`
- npm script `check:loop-init`
- npm script `test:loop-audit`
- npm script `test:loop-init`
- npm script `test:loop-cost`
- npm script `test:tools`
- npm script `build:tools`
- npm script `build`
- npm script `test`
- npm script `prepublishOnly`
- npm script `start`
- npm script `audit`

## Loop signals (line-indexed samples)

### stop_condition
- `docs/failure-modes.md:95` — - No early exit when watchlist empty
- `docs/loop-design-checklist.md:32` — - [ ] `/goal` or equivalent uses a **fresh model** for stop condition (if applicable)
- `docs/primitives-matrix.md:8` — | **Run-until-done** | Keep working until a verifiable condition holds | Goal mode / explicit stopping conditions in loo
- `docs/primitives.md:13` — - `/goal` (run until a verifiable condition is true)
- `examples/claude-code/daily-triage.md:35` — `/goal` uses a fresh model to check the stop condition — maker/checker at the goal layer.
### verifier
- `.github/ISSUE_TEMPLATE/pattern-request.md:19` — **Proposed skills** (triage, fix, verify...):
- `.github/workflows/daily-triage.yml:152` — if git rev-parse --verify "refs/remotes/origin/${BRANCH}" >/dev/null 2>&1; then
- `AGENTS.md:5` — ## Build & verify
- `AGENTS.md:29` — - **Fixes**: only via PR with human review; `minimal-fix` + `loop-verifier` for assisted changes (L2).
- `CONTRIBUTING.md:25` — 6. Verification strategy (maker/checker)
### hitl
- `LOOP.md:59` — - Kill switch: `loop-pause-all` label or flag in `STATE.md`
- `docs/anti-patterns.md:55` — **Anti-pattern**: Loop runs 24/7 with no pause criteria.
- `docs/anti-patterns.md:59` — **Do instead**: Document pause/kill in LOOP.md + `templates/loop-budget.md.template`.
- `docs/concepts.md:92` — - [Operating Loops](./operating-loops.md) — cost, logging, when to pause
- `docs/failure-modes.md:101` — - Daily token budget → pause loop
### state_writeback
- `.github/ISSUE_TEMPLATE/config.yml:18` — description: "loop-audit, registry, starters, templates"
- `.github/ISSUE_TEMPLATE/pattern-request.md:27` — *We will turn accepted requests into full `patterns/*.md` + `registry.yaml` entry + starter + at least one story followi
- `.github/PULL_REQUEST_TEMPLATE.md:5` — - [ ] New pattern or starter (followed `templates/pattern-template.md` + updated `registry.yaml`)
- `.github/workflows/daily-triage.yml:190` — { context: 'validate', description: 'Pattern/registry gates (daily-triage inline)' },
- `.github/workflows/release-loop-audit.yml:21` — registry-url: 'https://registry.npmjs.org'
### loop_engine
- `.github/ISSUE_TEMPLATE/config.yml:4` — url: https://github.com/cobusgreyling/loop-engineering/discussions
- `.github/ISSUE_TEMPLATE/config.yml:7` — url: https://github.com/cobusgreyling/loop-engineering/issues/new?labels=docs
- `.github/PULL_REQUEST_TEMPLATE.md:16` — - [ ] Ran `node tools/loop-audit/dist/cli.js .` (or on the starter) and addressed findings
- `.github/dependabot.yml:4` — directory: "/tools/loop-audit"
- `.github/dependabot.yml:11` — directory: "/tools/loop-init"
### claude_native
- `.github/ISSUE_TEMPLATE/pattern-request.md:15` — **Target tools** (Grok / Claude Code / Codex / GitHub Actions / other):
- `.gitignore:44` — .claude/
- `.gitignore:45` — !starters/**/.claude/
- `.gitignore:46` — !starters/**/.claude/**
- `CONTRIBUTING.md:11` — | Tool example | `examples/{grok,claude-code,codex,github-actions}/` |

## README vs code

README claim: # Loop Engineering   <p align="center">   <a href="https://cobusgreyling.github.io/loop-engineering/">     <img src="https://img.shields.io/badge/✨_Explore_the_Showcase-Design_systems_that_prompt_your_agents-0d1117?style=for-the-badge&labelColor=111a28&color=3ee8c5" alt="Explore the Showcase" />   <

- Code contains loop engine / gate patterns (see loop signals above).
