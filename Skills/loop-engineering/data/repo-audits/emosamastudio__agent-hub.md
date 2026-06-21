# Code Audit — emosamastudio/agent-hub

- **Files read:** 121 text/source files (every line indexed)
- **Pushed at:** 2026-06-18T10:07:13Z
- **Stars:** 2

## Code-backed scores

- **direct_install:** 10
- **claude_code_native:** 0.6
- **loop_implementation:** 4.0
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 121
- **total:** 6.25

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- bins: agent-hub, agent-hub-mcp, agent-hub-demo-worker
- npm script `dev`
- npm script `build`
- npm script `regression:gemini`
- npm script `regression:openclaw`
- npm script `typecheck`
- npm script `start`
- npm script `db:generate`
- npm script `db:migrate`
- npm script `test`
- npm script `lint`
- npm script `preview`
- npm script `hub`

## Loop signals (line-indexed samples)

### verifier
- `README.md:176` — Executor registry sync is fail-fast: `syncRegistry()` and `start()` verify that
- `README.md:352` — `ops recovery-plan --project <name-or-id>` generates backup, upgrade, rollback, and verification commands without exposi
- `apps/server/src/services/scheduler.ts:205` — await runStep("timeoutChecker", () => timeoutChecker(ctx));
- `apps/server/src/services/scheduler.ts:340` — // ─── TimeoutChecker ───
- `apps/server/src/services/scheduler.ts:341` — async function timeoutChecker(ctx: SchedulerContext) {
### hitl
- `apps/web/src/App.css:680` — .action-button--pause {
- `docs/superpowers/plans/2026-05-25-dashboard-redesign.md:1007` — Current scheduler data already available via `/api/scheduler/status` and `/api/metrics`. Scheduler health card shows: ru
- `docs/superpowers/specs/2026-05-18-agent-cron-hub-design.md:388` — A background maintenance job purges expired rows daily. Deletion is batched (LIMIT 10000 per iteration with short pauses
- `docs/superpowers/specs/2026-05-18-agent-cron-hub-design.md:481` — │       LIMIT 10000; (repeat with pauses)
- `docs/superpowers/specs/2026-05-18-agent-cron-hub-design.md:566` — - Scheduling pauses briefly (one tick at most — the next instance acquires the lock on its next tick attempt)
### state_writeback
- `.gitignore:7` — apps/server/*.sqlite
- `README.md:9` — - `apps/server`: Fastify + PostgreSQL + Drizzle control plane
- `README.md:58` — - agent registry
- `README.md:73` — DATABASE_URL=postgres://agent_hub:agent_hub_dev@localhost:5433/agent_hub
- `README.md:96` — curl -X PUT http://127.0.0.1:8788/api/registry/agents \
### loop_engine
- `apps/server/src/http/llm-proxy.ts:304` — while (true) {
- `deploy/deploy-compose.sh:135` — while true; do
- `docs/superpowers/specs/2026-05-18-agent-cron-hub-design.md:172` — -- Safety guards (agent_loop / ReAct agents)
- `docs/superpowers/specs/2026-05-18-agent-cron-hub-design.md:220` — Note: `agent_loop` was considered but removed. Long-running loops (like consumer-a steward) decompose into individual cr
- `packages/sdk/src/index.ts:1413` — while (true) {
### claude_native
- `docs/superpowers/plans/2026-05-19-agent-cron-hub-phase1.md:821` — - Remove: `apps/server/src/services/claude-code-runtime.ts`
- `docs/superpowers/plans/2026-05-19-agent-cron-hub-phase1.md:841` — rm services/claude-code-runtime.ts

## README vs code

README claim: # Agent Hub  Independent local-first Agent Cron / Job control plane for scheduling, dispatching, monitoring, and tracing AI agent tasks across projects.  Agent Hub is the platform. Business repositories are consumers: they register agents through the SDK/API, poll for work, execute in their own code

- Code contains loop engine / gate patterns (see loop signals above).
