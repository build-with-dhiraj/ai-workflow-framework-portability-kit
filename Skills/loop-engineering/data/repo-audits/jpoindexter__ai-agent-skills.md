# Code Audit — jpoindexter/ai-agent-skills

- **Files read:** 19 text/source files (every line indexed)
- **Pushed at:** 2026-06-16T14:57:20Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 5.0
- **verification:** 7.5
- **file_coverage:** 19
- **total:** 6.38

## Entrypoints (from code)

- skill_md: adversarial-verify/SKILL.md, closed-loop/SKILL.md, cluster-feedback/SKILL.md, doubt-gate/SKILL.md, fleet-loop/SKILL.md, hill-climb/SKILL.md, keep-green/SKILL.md, loop-audit/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `hill-climb/SKILL.md:24` — ## Stop conditions
- `loop-audit/SKILL.md:20` — | Agentic laziness | "Done enough" at partial completion | Objective stop condition checked by a fresh context, not the 
- `loop-state/SKILL.md:38` — ## Stop conditions met since last review
### verifier
- `README.md:3` — 14 reusable skills for loop engineering — building small systems that prompt coding agents for you instead of prompting 
- `README.md:29` — 2. **Verification is automated** — something objective can reject bad output. Otherwise you're back in the chair reading
- `README.md:42` — - **Self-grading** — the agent that wrote the output also verifies it, and it's way too nice grading its own homework. F
- `README.md:60` — VERIFY   adversarial-verify · ship-preflight     skeptic + objective gate
- `README.md:64` — The BUILD disciplines are not loop bodies — they apply inside any run, manual or looped. `source-grounded` keeps framewo
### state_writeback
- `README.md:19` — | **State file** | Persistent memory outside the conversation — what's done, in progress, escalated, learned. The agent 
- `README.md:54` — SCAFFOLD scaffold-planning · loop-state          docs + persistent memory
- `README.md:311` — **Key rule:** On kernel or host-layer changes, always run the full suite — not a subset. A dropped tool connection count
- `README.md:615` — **What it does:** Creates or updates a persistent `STATE.md` for a recurring loop — last run, in progress, completed, es
- `cluster-feedback/SKILL.md:20` — - Report the delta vs last run — do not re-surface stable themes as if new. Persist last-run timestamp and theme counts 
### loop_engine
- `README.md:17` — | **Automation** | A schedule or trigger that fires the run — `/loop`, `/schedule`, a routine, a webhook | — |
- `README.md:159` — /loop 15m keep this repo green on the current branch.
- `README.md:184` — /loop 30m watch prod errors on <project>.
- `README.md:220` — /loop 30m cluster new complaints from r/ObsidianMD.
- `README.md:256` — /loop hill-climb src/ to every file under 300 lines.
### claude_native
- `README.md:3` — 14 reusable skills for loop engineering — building small systems that prompt coding agents for you instead of prompting 
- `README.md:18` — | **Skill** | Project knowledge written once, read every run, so the loop doesn't re-derive context from zero | any `SKI
- `README.md:85` — 1. Installs all skills to `~/.claude/skills/`
- `README.md:88` — Reload Claude Code after running. You're done — no manual steps needed after this.
- `README.md:96` — Copies all `*/SKILL.md` files to `~/.claude/skills/`. Use this if you cloned before `bootstrap.sh` existed, or want to r

## README vs code

README claim: # AI Agent Skills  14 reusable skills for loop engineering — building small systems that prompt coding agents for you instead of prompting them by hand — plus the build/verify disciplines that keep what the loop produces correct. Each is a self-contained `SKILL.md` you can install into Claude Code o

- Code contains loop engine / gate patterns (see loop signals above).
