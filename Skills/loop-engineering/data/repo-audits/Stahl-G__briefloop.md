# Code Audit — Stahl-G/briefloop

- **Files read:** 650 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T06:11:42Z
- **Stars:** 7

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 6.800000000000001
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 650
- **total:** 6.33

## Entrypoints (from code)

- skill_md: .agents/hermes-skills/multi-agent-brief-hermes/SKILL.md, .agents/skills/analyst/SKILL.md, .agents/skills/auditor/SKILL.md, .agents/skills/brief-onboarding/SKILL.md, .agents/skills/briefloop/SKILL.md, .agents/skills/claim-ledger/SKILL.md, .agents/skills/draft-audit-harness/SKILL.md, .agents/skills/editor/SKILL.md
- hooks: (none)
- loop_scripts: tests/test_briefloop_operator_skill.py
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `.agents/skills/briefloop/references/runtime-workspace.md:29` — ## Stop Conditions
### verifier
- `.agents/hermes-skills/multi-agent-brief-hermes/references/delegate-task-sequence.md:28` — 8. Verify each expected artifact exists and is non-empty before selecting the next decision.
- `.agents/skills/briefloop/references/experiment-080-090.md:40` — - Python checks visibility and hashes; it does not judge semantic leakage by
- `.agents/skills/briefloop/references/public-claims.md:24` — - Python judged prose quality, semantic manifestation, or factual regression.
- `.agents/skills/briefloop/references/version-matrix.md:4` — Last verified against BriefLoop runtime: `v0.9.1` plus post-v0.9.1 mainline support-record surfaces
- `.agents/skills/orchestrator/SKILL.md:80` — - After `multi-agent-brief finalize` writes reader-facing artifacts, run `multi-agent-brief gates check --workspace <wor
### hitl
- `docs/agent-dev-guide.zh-CN.md:131` — - human-in-the-loop：需要用户确认方向、范围、修复意图或交付边界。
- `docs/agent-dev-prompt.zh-CN.md:164` — - `human-in-the-loop`：用户确认方向、范围、修复意图或交付边界。
- `docs/mabw-architecture-reference-v0.1.2.md:465` — | Applicability | Deterministic agent benchmarks (ALFWorld, WebShop, OS, DB, τ-bench) | Enterprise briefing (policy-driv
- `docs/roadmap.md:165` — - Classify stage gates as machine-only, human-in-the-loop, or mixed where that distinction affects Orchestrator decision
- `docs/roadmap.zh-CN.md:165` — - 在影响 司乐师 决策的地方，标明 stage gate 是 machine-only、human-in-the-loop 还是 mixed。
### state_writeback
- `.agents/hermes-skills/multi-agent-brief-hermes/SKILL.md:27` — Runtime state files: `output/intermediate/runtime_manifest.json`, `output/intermediate/workflow_state.json`, `output/int
- `.agents/hermes-skills/multi-agent-brief-hermes/SKILL.md:76` — 6. Read `agent_handoff.md`, `workflow_state.json`, `artifact_registry.json`, and optional feedback state references, the
- `.agents/hermes-skills/multi-agent-brief-hermes/SKILL.md:115` — `finalize` is not a quality-gate executor. Blocking gate findings must route to feedback plus deterministic repair, `req
- `.agents/hermes-skills/multi-agent-brief-hermes/references/delegate-task-sequence.md:140` — After repair-complete, rerun downstream stages from must_rerun_from. For non-repair blocks, choose `request_human_review
- `.agents/skills/briefloop/SKILL.md:95` — - Do not edit `workflow_state.json`, `artifact_registry.json`,
### loop_engine
- `docs/briefloop-architecture-reference-v0.3.0.md:133` — | Scheduled discovery | `/loop` 定时触发 | 每周/每月简报调度 |
- `docs/briefloop-architecture-reference-v0.3.0.md:868` — | Osmani | Loop Engineering | Addy Osmani | 2026-06-08 | addyo.substack.com/p/loop-engineering | Engineering article | L
- `docs/mabw-architecture-reference-v0.1.3-related-work.md:25` — **Convergence and divergence.** LIFE-HARNESS and MABW arrived at the same thesis—adapt the interface, not the model—from
- `docs/mabw-architecture-reference-v0.1.3-related-work.md:106` — **Anti-Goodhart design principle (elevated).** The paper empirically demonstrates Goodhart's law applied to evaluation: 
- `docs/mabw-architecture-reference-v0.1.3.md:477` — **Convergence and divergence.** LIFE-HARNESS and MABW arrived at the same thesis—adapt the interface, not the model—from
### claude_native
- `.agents/AGENTS.md:7` — `skills/*/SKILL.md` files are capability contracts, not platform-specific subagent definitions.
- `.agents/AGENTS.md:11` — - `.claude/agents/*.md` for Claude Code
- `.agents/AGENTS.md:17` — When editing skills, keep each `SKILL.md` focused on:
- `.agents/AGENTS.md:25` — Follow Claude Skills progressive disclosure: keep `SKILL.md` concise, use specific frontmatter descriptions for routing,
- `.agents/skills/analyst/SKILL.md:12` — It is not the platform-specific subagent definition. Claude Code subagents live in `.claude/agents/`; OpenCode subagents

## README vs code

README claim: # 🧾 BriefLoop  **Open-source loop engineering for auditable business briefings.** Formerly **MABW — Multi-Agent Brief Workflow**.  <p align="center">   <a href="README.md">English</a> |   <a href="README.zh-CN.md">简体中文</a> </p>  Current version: **v0.9.1** Public framing: **BriefLoop / MABW compatib

- Code contains loop engine / gate patterns (see loop signals above).
