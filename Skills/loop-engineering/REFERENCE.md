# Loop Engineering Doctrine Brief (v2 — full ingest)

**Generated:** 2026-06-21

## North Star

Replace yourself as the prompter. Design systems that discover work, delegate, verify, persist, and re-trigger — with human gates at the outer scheduler.

## Locked Principles (evidence-backed)

1. **Angus Sewell's Agent Hub centers on PostgreSQL as system-of-record for entities, notes, decisions, and issues, with Claude skills driving plan/build/test/resolve loops under human gates.** — evidence: E001, E002
2. **Loop engineering (Osmani/Cherny/Steinberger, June 2026) reframes the engineer's job from manual prompting to designing recurring systems with automations, worktrees, skills, connectors, and verifier sub-agents.** — evidence: E003, E004, E005
3. **Skills are treated as externalized intent that compounds across loop cycles; without them agents re-derive project context every run.** — evidence: E007, E015
4. **pi-factory (xpriment626, updated 2026-06-13) implements a local Pi + Coral + SQLite blackboard with kanban tickets and planner/architect/implementer/reviewer agents — structurally parallel to Agent Hub's registry + multi-step loop.** — evidence: E008, E009, E018
5. **Multiple June 2026 repos converge on Postgres/SQLite as durable loop state: emosamastudio/agent-hub (job control plane), AgenticMind, pgmnemo, Nabu.** — evidence: E010, E011, E012
6. **Self-improving skills are an active research and product layer: Microsoft SkillOpt optimizes SKILL.md text with validation gates; skills.sh hosts high-install self-improving-agent patterns.** — evidence: E013, E017
7. **Curated indexes and tooling exploded after Osmani's June 2026 naming: cobusgreyling/loop-engineering (522★), Forward-Future/loop-library (483★), awesome-loop-engineering (250+ resources).** — evidence: E016
8. **Reddit r/ClaudeCode thread 1u85zl9 is a community entry point for loop-engineering discourse and pi-factory discovery; full comment corpus could not be scraped in this run.** — evidence: E018
9. **Harness /loop, /goal, and Routines provide the heartbeat primitive for recurring agent work.** — evidence: E021
10. **Verification is architectural: maker/checker sub-agents, mechanical gates, and human-in-the-loop signals prevent self-validating failure.** — evidence: E022
11. **Loop engineering (June 2026 consensus) replaces manual prompting with designed systems: automations, skills, connectors, verifiers, and durable state.** — evidence: E023
12. **Loop engineering replaces manual prompting with designed recurring systems (automations, skills, verifiers, durable state).** — evidence: E023, E039, E040

## Top repos (code audit scores)

- **cobusgreyling/loop-engineering** (score 9.62, 201 files, 11790 lines read)
- **earendil-works/pi** (score 9.62, 843 files, 243355 lines read)
- **valkor-ai/loom** (score 9.62, 295 files, 80117 lines read)
- **agentic-in/inferoa** (score 9.12, 254 files, 101262 lines read)
- **colbymchenry/codegraph** (score 8.25, 326 files, 108754 lines read)
- **AlexDuchDev/AgenticMind** (score 8.22, 297 files, 57072 lines read)
- **rlaope/oh-my-hermes** (score 7.12, 331 files, 116494 lines read)
- **vinnylarouge/skill-opt-skill** (score 7.12, 200 files, 33082 lines read)

## Anti-Patterns

- README claims without code audit confirmation
- Unattended loops without stop conditions
- Self-grading without separate verifier
- Confusing emosamastudio/agent-hub with Sewell Agent Hub
