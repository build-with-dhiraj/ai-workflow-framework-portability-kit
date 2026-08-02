---
name: idea-to-build
description: The global 4-stage idea→shipped pipeline (Sonnet brainstorms → tracker tickets with dependencies → Fable plans in-repo → Fable orchestrates Opus 4.8 implementers). Invoke when the user says "run the pipeline", "idea to build", "take this brainstorm and build it", "plan the build from Linear/Jira tickets", "execute the tickets", or arrives in a project session pointing at tickets produced by a chat brainstorm. Also invoke at Stage-4 time when the user asks to "execute the plan with 4.8 agents".
---

# Idea → Build Pipeline (global, model-tiered)

A cross-surface pipeline that separates **ideation, specification, architecture, and implementation** by model tier and surface. The durable state between stages is the **ticket tracker** — never a chat transcript. Any new session (any device) resumes by reading the tracker.

**Why tiers:** Sonnet is a cheap, fast divergent thinker — ideal brainstorm partner. Fable is the scarce, expensive judgment — spend it ONLY on architecture, planning, review gating, and orchestration. Opus 4.8 agents are strong implementers at a fraction of Fable's cost. Fable never writes the code; it instructs agents who do. Same output quality, fraction of the price.

## The four stages

| # | Stage | Surface | Model | State it produces |
|---|-------|---------|-------|-------------------|
| 1 | **Brainstorm** | Anywhere — claude.ai chat, phone, or Claude Code | **Sonnet** | A fleshed-out idea (scope, constraints, decisions) |
| 2 | **Ticketize** | Same surface as 1 (needs tracker MCP) | Sonnet | Tickets with dependencies, blockers, human/agent tags |
| 3 | **Plan** | **MUST be in the project repo** (Claude Code) | **Fable** | Build plan grounded in tickets + actual repo state |
| 4 | **Execute** | Project repo (Claude Code) | **Fable orchestrates; Opus 4.8 agents implement** | Shipped, reviewed code; tickets closed |

**Hard gate:** Stages 3–4 never happen in a plain chat. They require the project file — Fable must see the real repo (what already exists, conventions, migrations half-done) alongside the tickets.

## Stage 1 — Brainstorm (Sonnet, anywhere)
- Role: thought partner. Ask probing questions, run WebSearch/research on demand, surface trade-offs, converge on scope. Brain-dump friendly.
- In Claude Code: switch with `/model sonnet`, then use `superpowers:brainstorming` (or `product-management:product-brainstorming` for product/feature ideation, per global precedence).
- On claude.ai/phone: plain chat works — no repo needed. Ensure the tracker connector is enabled on claude.ai so Stage 2 can run from the same conversation.
- Done when: the idea's scope, non-goals, and key decisions are settled enough that ticketizing wouldn't invent anything.

## Stage 2 — Ticketize (same surface; tracker required)
Convert everything decided into tickets. **Every ticket must carry:**
1. **Dependencies / blockers** — what it relies on, linked explicitly (blocked-by relations).
2. **Executor tag** — `agent-ok` (an AI agent can complete it end-to-end) or `human-in-loop` (needs a human decision, credential, purchase, or irreversible action). Be honest; when unsure, tag `human-in-loop`.
3. **Acceptance criteria** — verifiable, so a Stage-4 agent knows "done".
4. Enough self-contained context to be executed without the brainstorm transcript.

**Tracker resolution order (use the first available):**
1. **Linear MCP** (`mcp__linear__*` / the claude.ai Linear connector) — the canonical choice; supports blocked-by relations + labels natively.
2. **Jira** (Atlassian MCP: `createJiraIssue`, `createIssueLink` for blocks/is-blocked-by).
3. **Notion** (a tickets database with Relation property for dependencies).
4. **Claude Code native tasks** (`TaskCreate` + `TaskUpdate addBlockedBy`) — fine for solo/single-machine projects; not readable from phone chats.
5. **mattpocock `to-issues`** (files in `docs/agents/`) — repo-native fallback; requires the `setup-matt-pocock-skills` precondition per global CLAUDE.md.

## Stage 3 — Plan (Fable, in the project repo)
1. Pull **all** relevant tickets from the tracker (list them; read every one).
2. Read the actual repo state — Fable must understand what already exists before planning (greenfield vs brownfield changes everything).
3. Produce the build plan: sequencing from the dependency graph, per-ticket dispatch strategy, what runs in parallel, where the human gates are. Use plan mode / `superpowers:writing-plans`; use `gepetto` first for deep upstream architectural research when the build is large/greenfield.
4. **Fable's architectural judgment overrides Stage-1/2 choices** where they conflict — but it must (a) say so explicitly, (b) write the deviation back to the affected tickets (comment or edit), so the tracker stays the single source of truth. User-locked *product* decisions are never overridden, only technical approach.

## Stage 4 — Execute (Fable = EM; Opus 4.8 agents = hands)
- Fable stays the Engineering Manager (global EM mode applies): it NEVER implements; it dispatches, reviews, integrates.
- **Every implementation dispatch pins the worker model:** `Agent(..., model: "opus")` — Opus 4.8. Do NOT let workers silently inherit the session model (inheriting = agents run as Fable = quality-identical but several× the cost). Combine with the right specialist `subagent_type` from `~/.claude/agents/`.
- Reviews are **maker≠checker**: independent reviewer agent (also `model:"opus"`, fresh context/worktree) per meaningful unit. `superpowers:subagent-driven-development` + `dispatching-parallel-agents` govern the mechanics; `verification-before-completion` closes it.
- Work ticket-by-ticket along the dependency graph; parallelize independent tickets. **Commit+push per ticket** (durable checkpoints — background agents die; commits don't).
- `human-in-loop` tickets: STOP and ask the user; never auto-complete them.
- Close/update each ticket in the tracker as it lands (status + link to commit/PR). The tracker must end truthful.

## Resumability & hygiene
- The tracker is the memory. A dead session, a new machine, or a phone follow-up all resume by reading tickets — never by reconstructing chat history.
- If the session model isn't Fable at Stage 3/4, tell the user to switch (`/model claude-fable-5`) rather than proceeding with a weaker architect.
- Cost sanity: Sonnet for volume ideation, Fable tokens only for judgment, Opus for production code. If a Stage-4 task is trivial/mechanical, `model:"haiku"` is permitted for it.
