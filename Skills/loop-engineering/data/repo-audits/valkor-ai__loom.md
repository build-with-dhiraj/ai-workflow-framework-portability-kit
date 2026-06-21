# Code Audit — valkor-ai/loom

- **Files read:** 295 text/source files (every line indexed)
- **Pushed at:** 2026-06-18T07:09:37Z
- **Stars:** 347

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 10
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 295
- **total:** 9.62

## Entrypoints (from code)

- skill_md: plugins/claude-code/skills/loom/SKILL.md, plugins/claude-code/skills/loom-deploy/SKILL.md, plugins/codex/skills/loom/SKILL.md, plugins/codex/skills/loom-deploy/SKILL.md
- hooks: plugins/claude-code/hooks/hooks.json
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- bins: loom
- npm script `test`
- npm script `clean`
- npm script `build`
- npm script `check`
- npm script `verify:phase2-repository-context`
- npm script `verify:phase-handoff-git-advisory`
- npm script `verify:next-phase-preview-routing`
- npm script `verify:layered-self-validation`
- npm script `verify:review-scope-declared-changed-files`
- npm script `verify:submit-routing-coverage`
- npm script `verify:long-operation-observability`
- npm script `verify:optional-empty-aac-repair-sections`

## Loop signals (line-indexed samples)

### stop_condition
- `scripts/verify-agent-facing-request-protocol.js:181` — "Brainstorm stopConditions must stop only after a block was presented to the user",
- `scripts/verify-auto-runnable-transition-contract.js:94` — assert.equal(data.instruction?.groupBoundaryIsNotStopCondition, undefined, `${label}: group scheduling details must stay
- `scripts/verify-layered-self-validation.js:257` — request?.agentAction?.stopConditions?.some((condition) => condition.includes("after presenting the next required Brainst
- `scripts/verify-layered-self-validation.js:258` — `${label}: Brainstorm stopConditions must stop only after presenting the current user-facing block`,
- `scripts/verify-layered-self-validation.js:263` — "agentAction.stopConditions",
### verifier
- `README.md:32` — Loom is an open-source delivery harness for existing coding agents. It does not replace the model or editor you already 
- `README.md:36` — Instead of a one-shot prompt chain, Loom treats delivery as a loop: route the next step, execute, verify, record evidenc
- `README.md:44` — Website and app generation is becoming table stakes. The harder problem is reliable delivery: keeping the agent aligned 
- `README.md:52` — Self-check bias | Review, verification, repair requests, and evidence records separate implementation from validation.
- `README.md:56` — The hard part is the harness around the model: durable state, scoped work, routing, verification, recovery, and human-re
### hitl
- `scripts/audit-claude-loom-session.js:195` — addIssue(issues, "warning", "stop_guard_intervened", stopGuardBlocks);
- `src/core/operations/brainstorm.ts:1734` — phaseStatus: ["scope_confirmed", "proposed", "delivered", "paused", "skipped", "revised"],
- `src/core/operations/repository-context.ts:1487` — phaseStatus: ["scope_confirmed", "proposed", "delivered", "paused", "skipped", "revised"],
- `src/core/schemas.ts:318` — "paused",
- `src/core/schemas.ts:337` — "pause",
### state_writeback
- `README.md:34` — Loom uses dynamic workflows to choose the right delivery path for each goal, then makes that path durable: project conte
- `README.md:79` — Token-saving context | Persist project summaries, task graphs, backend/runtime state, tests, and deployment results so a
- `benchmarks/agent-run/cases/analytics-funnel-continuation/seed/docs/phase-1-analytics.md:10` — - Do not add external analytics, persistence, batching, or package dependencies.
- `benchmarks/agent-run/cases/analytics-funnel-continuation.json:8` — "Events have userId, type, occurredAt, and optional properties. Do not add persistence, batching, or external analytics 
- `benchmarks/agent-run/cases/backend-readiness-continuation/seed/benchmark-verify.js:8` — DATABASE_URL: "postgres://example",
### loop_engine
- `plugins/claude-code/commands/loom-deploy.md:18` — If the first Bash command is a long-running `deploy run`, keep waiting on that same Bash session. After one short "deplo
- `plugins/claude-code/commands/loom.md:27` — If the first Bash command is a long-running deploy command, keep waiting on that same Bash session. After one short "dep
- `plugins/claude-code/skills/loom/SKILL.md:37` — For deploy commands, keep waiting on the first Bash session while it is active. After one short "deploy is running" upda
- `plugins/claude-code/skills/loom/SKILL.md:85` — - `observe_active_deploy_operation`: obey `instruction.observationPolicy`; prefer waiting on the original deploy command
- `plugins/claude-code/skills/loom-deploy/SKILL.md:61` — If a returned instruction has `mode: observe_active_deploy_operation`, obey `instruction.observationPolicy`. `operationA
### claude_native
- `README.md:4` — <p>An open delivery harness that turns Claude Code, Codex, OpenCode and other coding agents into repeatable software del
- `README.md:85` — Multi-agent protocol | Bring the same delivery process to Claude Code, Codex, OpenCode and other agents.
- `README.md:93` — (Codex, Claude Code, OpenCode, future adapters...)
- `README.md:121` — - The coding agent CLI for the adapter you install: Codex CLI for Codex, Claude Code CLI for Claude Code, or OpenCode CL
- `README.md:137` — # Claude Code: installs the Claude Code plugin package, skills, hooks, and launcher.

## README vs code

README claim: <div align="center">   <img src="./assets/loom-logo.svg" alt="Loom" width="560">   <p><strong>Loop engineering for agentic software delivery.</strong></p>   <p>An open delivery harness that turns Claude Code, Codex, OpenCode and other coding agents into repeatable software delivery systems.</p>   <p

- Code contains loop engine / gate patterns (see loop signals above).
