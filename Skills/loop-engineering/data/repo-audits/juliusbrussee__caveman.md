# Code Audit — juliusbrussee/caveman

- **Files read:** 131 text/source files (every line indexed)
- **Pushed at:** 2026-06-12T13:51:06Z
- **Stars:** 75222

## Code-backed scores

- **direct_install:** 6.5
- **claude_code_native:** 10
- **loop_implementation:** 0.8
- **registry_memory:** 7.5
- **verification:** 8.5
- **file_coverage:** 131
- **total:** 6.22

## Entrypoints (from code)

- skill_md: plugins/caveman/skills/cavecrew/SKILL.md, plugins/caveman/skills/caveman/SKILL.md, plugins/caveman/skills/caveman-compress/SKILL.md, plugins/caveman/skills/caveman-stats/SKILL.md, skills/cavecrew/SKILL.md, skills/caveman/SKILL.md, skills/caveman-commit/SKILL.md, skills/caveman-compress/SKILL.md
- hooks: .codex/hooks.json
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- bins: caveman, caveman-shrink
- npm script `test`

## Loop signals (line-indexed samples)

### verifier
- `.github/workflows/sync-skill.yml:52` — cp agents/cavecrew-reviewer.md plugins/caveman/agents/cavecrew-reviewer.md
- `.github/workflows/sync-skill.yml:66` — plugins/caveman/agents/cavecrew-reviewer.md \
- `CLAUDE.md:96` — | `agents/cavecrew-reviewer.md` | Diff/file reviewer subagent (haiku). One-line findings with severity emoji. |
- `CLAUDE.md:260` — 1. The profile slug must exist in upstream [vercel-labs/skills](https://github.com/vercel-labs/skills). Verify against t
- `CONTRIBUTING.md:40` — | cavecrew subagent definitions | `agents/cavecrew-investigator.md`, `agents/cavecrew-builder.md`, `agents/cavecrew-revi
### hitl
- `evals/snapshots/results.json:30` — "A debouncer delays firing the search until the user pauses typing (e.g., 300ms of no keystrokes). Without it, every key
- `evals/snapshots/results.json:42` — "A debouncer delays running the search until the user stops typing for a short interval (e.g., 300ms). Benefits:\n\n- **
### state_writeback
- `CLAUDE.md:85` — | `skills/caveman/SKILL.md` | Caveman behavior: intensity levels, rules, wenyan mode, auto-clarity, persistence. Only fi
- `CLAUDE.md:91` — | `skills/caveman-help/SKILL.md` | Quick-reference card. One-shot display, not a persistent mode. |
- `CLAUDE.md:219` — Defined in `skills/caveman/SKILL.md`. Six levels: `lite`, `full` (default), `ultra`, `wenyan-lite`, `wenyan-full`, `weny
- `INSTALL.md:256` — No telemetry. No analytics. The installer's own code makes no network calls. Network requests do happen indirectly throu
- `README.md:143` — | Set up PostgreSQL connection pool | 2347 | 380 | 84% |
### loop_engine
- `README.md:236` — | [**loop-factory**](https://github.com/JuliusBrussee/skills/tree/main/skills/loop-factory) | Spec-driven task loop — in
### claude_native
- `.claude-plugin/marketplace.json:2` — "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
- `.claude-plugin/marketplace.json:4` — "description": "Ultra-compressed communication mode for Claude Code. Cuts ~75% of tokens while keeping full technical ac
- `.github/ISSUE_TEMPLATE/bug_report.md:21` — - [ ] Claude Code
- `.github/workflows/sync-skill.yml:1` — name: Sync SKILL.md and rules
- `.github/workflows/sync-skill.yml:7` — - skills/caveman/SKILL.md

## README vs code

README claim: <p align="center">   <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" /> </p>  <h1 align="center">caveman</h1>  <p align="center">   <strong>why use many token when few do trick</strong> </p>  <p align="center">   <a href="https://github.com/JuliusBrussee/caveman/st

- Loop implementation in code is thin or documentation-only.
