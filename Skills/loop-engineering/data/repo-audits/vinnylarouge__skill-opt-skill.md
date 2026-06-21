# Code Audit — vinnylarouge/skill-opt-skill

- **Files read:** 200 text/source files (every line indexed)
- **Pushed at:** 2026-06-02T10:51:44Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 200
- **total:** 7.12

## Entrypoints (from code)

- skill_md: playground/seed-skill/SKILL.md, playground/seed-skill-opt/SKILL.md, skill/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### verifier
- `.skill-opt/runs/extract-fields-1/config.yml:2` — feedback_source: user-suite     # programmatic checker => ground-truth scoring
- `.skill-opt/runs/extract-fields-1/report.md:3` — **Target:** `playground/seed-skill/SKILL.md` · **Feedback source:** user-suite (programmatic checker = ground truth) · *
- `.skill-opt/runs/extract-fields-1/report.md:10` — - **Judge calibration:** Spearman ρ = 0.868 (n=16) between LLM-judge (gold-blind) and programmatic ground truth — judge 
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:35` — | `validation_depth` | `self-contained` | `map-only` \| `self-contained` \| `verifiers-env` \| `full-ablation` |
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:47` — SCORE    : judge each trajectory (programmatic if available else LLM-judge subagent) → score.json;
### hitl
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:24` — | `feedback_timing` | `autonomous` | `autonomous` \| `interactive` (pause at each gate) |
- `.skill-opt/runs/skill-opt-1/candidates/iter-02/candidate.md:24` — | `feedback_timing` | `autonomous` | `autonomous` \| `interactive` (pause at each gate) |
- `.skill-opt/runs/skill-opt-1/skill/current.md:24` — | `feedback_timing` | `autonomous` | `autonomous` \| `interactive` (pause at each gate) |
- `.skill-opt/runs/skill-opt-1/skill/packet_v0.md:27` — | `feedback_timing` | `autonomous` | `autonomous` \| `interactive` (pause at each gate) |
- `.skill-opt/runs/skill-opt-1/skill/v0.md:24` — | `feedback_timing` | `autonomous` | `autonomous` \| `interactive` (pause at each gate) |
### state_writeback
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:187` — | **Memory** (rejected-edit memory + slow updates) | Tracks rejected edits; applies slow updates, preventing overfitting
- `.skill-opt/runs/skill-opt-1/candidates/iter-02/candidate.md:188` — | **Memory** (rejected-edit memory + slow updates) | Tracks rejected edits; applies slow updates, preventing overfitting
- `.skill-opt/runs/skill-opt-1/skill/current.md:187` — | **Memory** (rejected-edit memory + slow updates) | Tracks rejected edits; applies slow updates, preventing overfitting
- `.skill-opt/runs/skill-opt-1/skill/packet_v0.md:190` — | **Memory** (rejected-edit memory + slow updates) | Tracks rejected edits; applies slow updates, preventing overfitting
- `.skill-opt/runs/skill-opt-1/skill/packet_v0.md:560` — | **Memory** (rejected-edit memory + slow updates) | Tracks rejected edits; applies slow updates, preventing overfitting
### loop_engine
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:92` — - `references/loop.md` — phase mechanics, defaults, edit-budget enforcement, gate margin, memory/slow-update policy, par
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:200` — - `references/loop.md` — phase mechanics and slow-update policy detail
- `.skill-opt/runs/skill-opt-1/candidates/iter-02/candidate.md:93` — - `references/loop.md` — phase mechanics, defaults, edit-budget enforcement, gate margin, memory/slow-update policy, par
- `.skill-opt/runs/skill-opt-1/candidates/iter-02/candidate.md:201` — - `references/loop.md` — phase mechanics and slow-update policy detail
- `.skill-opt/runs/skill-opt-1/skill/current.md:92` — - `references/loop.md` — phase mechanics, defaults, edit-budget enforcement, gate margin, memory/slow-update policy, par
### claude_native
- `.skill-opt/runs/extract-fields-1/config.yml:1` — target_skill: playground/seed-skill/SKILL.md
- `.skill-opt/runs/extract-fields-1/report.md:3` — **Target:** `playground/seed-skill/SKILL.md` · **Feedback source:** user-suite (programmatic checker = ground truth) · *
- `.skill-opt/runs/extract-fields-1/report.md:41` — Best version **v2** saved (save-as-new) to `playground/seed-skill-opt/SKILL.md`. Original seed skill untouched; `skill/v
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:3` — description: "Use to optimize/improve an existing agent skill against scored tasks. Ports Microsoft SkillOpt: treats the
- `.skill-opt/runs/skill-opt-1/candidates/iter-01/candidate.md:21` — | `target_skill` | — (required) | path to SKILL.md or skill dir |

## README vs code

README claim: # skill-opt  A meta-skill that **optimizes other agent skills.** It ports Microsoft Research's [SkillOpt](https://microsoft.github.io/SkillOpt/) into a single Claude Code skill: the target `SKILL.md` is treated as a *trainable document* and improved against a scored task suite — while the model stay

- Code contains loop engine / gate patterns (see loop signals above).
