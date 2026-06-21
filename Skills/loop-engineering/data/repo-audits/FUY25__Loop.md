# Code Audit — FUY25/Loop

- **Files read:** 14 text/source files (every line indexed)
- **Pushed at:** 2026-06-10T06:47:26Z
- **Stars:** 8

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 9.0
- **file_coverage:** 14
- **total:** 6.97

## Entrypoints (from code)

- skill_md: skills/loop-generate/SKILL.md, skills/loop-list/SKILL.md, skills/loop-run/SKILL.md, skills/loop-scan/SKILL.md, skills/loop-status/SKILL.md, skills/loop-verify/SKILL.md
- hooks: (none)
- loop_scripts: skills/loop-scan/scripts/digest.py
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `README.md:15` — | `loop-generate` | Design | Interviews you (or takes a scan finding) and scaffolds a complete loop: spec with verifiabl
- `README.md:58` — | Loop | Trigger | What it does | Verification / stop condition |
- `README.md:69` — | Loop | Trigger | What it does | Verification / stop condition |
- `README.md:78` — | Loop | Trigger | What it does | Verification / stop condition |
- `README.md:100` — ├── loop.md         # the spec: purpose, trigger, stop condition, verification, budget, escalation
### verifier
- `README.md:7` — verification + memory**, assembled from five building blocks (automations, worktrees, skills,
- `README.md:15` — | `loop-generate` | Design | Interviews you (or takes a scan finding) and scaffolds a complete loop: spec with verifiabl
- `README.md:16` — | `loop-verify` | Verification layer | Encodes your *manual* verification steps (browser clicks, endpoint checks) into a
- `README.md:28` — loop-scan ──> loop-generate ──> loop-verify
- `README.md:33` — loop from scratch without a scan; run loop-verify before or after generation to harden one
### hitl
- `skills/loop-generate/assets/loop-template.md:3` — > One-line purpose. Created <date> · Status: draft | active | paused | retired
- `skills/loop-list/SKILL.md:47` — - Do not hide draft, paused, or broken loops; users list loops specifically to find what exists.
- `skills/loop-status/SKILL.md:29` — | ⚪ paused/retired | as recorded — verify the scheduler entry is actually gone |
### state_writeback
- `README.md:97` — ├── LOOPS.md            # registry: one row per loop (status, mechanism, cadence, last run)
- `skills/loop-generate/assets/LOOPS-template.md:1` — # Loops registry
- `skills/loop-list/SKILL.md:8` — This is a read-only inventory pass. Do not start loops, modify registry files, or diagnose
- `skills/loop-list/SKILL.md:13` — 1. Find the project loop registry:
- `skills/loop-list/SKILL.md:38` — - If registry and folder disagree, show both and mark `registry drift` in the table.
### loop_engine
- `README.md:18` — | `loop-run` | Start | Fuzzy-matches a loop by name/purpose and prints or invokes the exact `/goal`, `/loop`, schedule, 
- `README.md:126` — name Claude Code uses (`/loop-scan`, `/loop-generate`, `/loop-verify`, `/loop-list`,
- `README.md:127` — `/loop-run`, `/loop-status`). The frontmatter `name` matches the directory name so skill
- `README.md:132` — swapping the mechanism wiring (Claude: /goal, /loop, cron/schedule, hooks, GH Actions ↔
- `skills/loop-generate/SKILL.md:3` — description: Design and scaffold a complete autonomous loop for a recurring task — spec with a machine-verifiable stop c
### claude_native
- `.gitignore:4` — .claude/
- `README.md:5` — This repo is the **development home** for a family of Claude Code skills that help you move from
- `README.md:14` — | `loop-scan` | Discover | Mines Claude Code + Codex session history for repeated work, babysat sessions, and re-explain
- `README.md:105` — ## Install (Claude Code first; Codex port later)
- `README.md:108` — ./scripts/install.sh        # copies skills/* to ~/.claude/skills/

## README vs code

README claim: # Loops — skill family for loop engineering  > "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."  This repo is the **development home** for a family of Claude Code skills that help you move from prompting agents turn-by-turn to designing self-

- Code contains loop engine / gate patterns (see loop signals above).
