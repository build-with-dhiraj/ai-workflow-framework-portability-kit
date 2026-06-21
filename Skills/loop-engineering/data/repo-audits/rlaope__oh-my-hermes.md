# Code Audit — rlaope/oh-my-hermes

- **Files read:** 331 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T23:34:51Z
- **Stars:** 23

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 331
- **total:** 7.12

## Entrypoints (from code)

- skill_md: skills/agent-ops-review/SKILL.md, skills/ai-slop-cleaner/SKILL.md, skills/ask/SKILL.md, skills/automation-blueprint/SKILL.md, skills/autoresearch-goal/SKILL.md, skills/best-practice-research/SKILL.md, skills/cancel/SKILL.md, skills/code-review/SKILL.md
- hooks: (none)
- loop_scripts: src/commands/loop.py, src/goal_loop.py, src/loopability.py, tests/test_loop_cycle.py
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `docs/SKILL_QUALITY_COMPARISON.md:166` — examples, final checklist, and stop conditions.
- `docs/SKILL_QUALITY_COMPARISON.md:271` — - stop condition
- `docs/WORKFLOWS.md:99` — - Prompt: ralph: handle a execution request that needs explicit evidence boundaries and a clear stop condition.
- `docs/WORKFLOWS.md:100` — - Expected behavior: Run `ralph` only after naming the target, evidence boundary, and stop condition.
- `docs/WORKFLOWS.md:212` — - The goal is too vague to name an observable problem, next artifact, verification signal, or stop condition.
### verifier
- `AGENTS.md:34` — verification, wait for required checks, then merge if authority is clear.
- `AGENTS.md:51` — - What verification was actually observed, including CI, targeted tests,
- `AGENTS.md:57` — the feature's origin, behavior, and evidence obvious to a reviewer reading the
- `AGENTS.md:70` — runs own handoff, dispatch, execution, verification, review, CI, and merge
- `AGENTS.md:86` — ## Verification
### hitl
- `docs/ARCHITECTURE.md:383` — human-in-the-loop executor-choice contract. With `--executor codex`, it also
- `docs/DELEGATION_FIRST_COMPLETENESS.md:101` — - `omh coding delegate --executor choose` returns a human-in-the-loop executor
- `docs/WORKFLOWS.md:506` — - If a worktree or shared-file conflict appears, pause parallel delivery and re-plan ownership before more edits.
- `site/docs/executor-handoff/index.html:80` — <h3>Risky or multi-file work gets a pause.</h3>
- `skills/ultrawork/SKILL.md:52` — - If a worktree or shared-file conflict appears, pause parallel delivery and re-plan ownership before more edits.
### state_writeback
- `AGENTS.md:50` — commands, generated files, persisted state, or wrapper contracts touched.
- `docs/APPLICATION_CASES.md:592` — - The generated router includes the representative harness registry.
- `docs/ARCHITECTURE.md:181` — the same local HUD, target registry, and runtime evidence. It is intentionally
- `docs/ARCHITECTURE.md:215` — `targets.py` owns the deterministic Hermes target registry. It records which
- `docs/ARCHITECTURE.md:281` — `wrapper/sessions.py` owns metadata-only chat session persistence for wrappers.
### loop_engine
- `docs/APPLICATION_CASES.md:566` — | Loopability-gated goal cycle | `./loop make this project a 10k star OSS` | `loop` / `reframe_north_star` | Direct skil
- `docs/PLAYBOOKS.md:55` — | `loopable-goal-cycle` | A user directly starts a long-horizon goal such as `./loop make this a 10k-star quality OSS`. 
- `docs/README.md:163` — `.omh/loops` metadata-only `loop_cycle/v1` state, `loop_runtime/v1` tick
- `docs/ROLES.md:130` — - Primary skills: `ultragoal`, `ultrawork`, `ralph`, `ai-slop-cleaner`
- `docs/SKILL_QUALITY_COMPARISON.md:58` — `plan`, `ralph`, `ralplan`, `skill`, `team`, `ultragoal`, `ultraqa`,
### claude_native
- `README.md:144` — - **Safe handoffs** - coding can go to Codex, Claude Code, Hermes, or another
- `README.md:147` — can show Prepare worktree before Hermes starts Codex, Claude Code, Hermes, or
- `README.md:178` — | `idea-to-deploy` / coding runtime handoff / executor selection | Prepare work for Codex, Claude Code, Hermes, or anoth
- `README.md:239` — | Coding agent paths | Hermes can prepare work for Codex, Claude Code, Hermes itself, or another runtime without pretend
- `docs/APPLICATION_CASES.md:564` — | Executor runtime selection | `Should I use Codex or Claude Code for this coding task?` | `executor-runtime-readiness` 

## README vs code

README claim: # oh-my-hermes  <p align="center">   <img src="assets/hermes-agent-hero.png" alt="Oh My Hermes" width="720"> </p>  <p align="center">   <strong>Install once. Keep your Hermes workflow. Let OMH make the next step safe.</strong>   <br>   <em>Chat-first skills, workflow contracts, status cards, and han

- Code contains loop engine / gate patterns (see loop signals above).
