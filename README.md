# AI Workflow Framework & Portability Kit

A portable, self-contained snapshot of a working **Claude Code** setup — agents, skills, plugins, MCP servers, host-side tooling, and the orchestration logic that ties them together. Drop the folder on a fresh Mac, run one script, and the entire stack is restored in about twenty minutes.

This is the master config behind a multi-layer "Engineering Manager" AI workflow: a top-level orchestrator that never writes code itself, dispatching work down to 35 specialist agents who do. The kit captures that architecture as files anyone can audit, fork, or rebuild from.

---

## What's inside

| Folder / file | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The master orchestration logic — 7-layer architecture, skill precedence rules, when to dispatch which specialist. Start here if you want the deep model. |
| [`BOOTSTRAP.md`](BOOTSTRAP.md) | Step-by-step new-Mac install runbook. Numbered phases for the manual path; one-script "fast path" pointer at the top. |
| [`MEMORY.md`](MEMORY.md) | Memory-system design — auto-memory (per-project), context kernel (cross-session), how state survives forked conversations. |
| [`SPEC-KIT-global.md`](SPEC-KIT-global.md) | Greenfield-only Spec-Driven Development phase map; explicit override rule (never run `/speckit.implement`). |
| [`Agents/`](Agents/) | **35 custom specialist agents** — 31 engineering implementers (frontend, backend, AI, Solidity, WeChat, Feishu, design-specialist, etc.), 1 cross-session continuity advisor, 3 consultative expert advisors. Each is dispatched by the orchestrator via the `Task` tool. |
| [`Skills/`](Skills/) | **104 active skills** — process discipline (TDD, debugging, brainstorming), implementation patterns (Supabase, Three.js, Flutter, design / impeccable / taste, etc.), and governance (skill-necessity gating, library hygiene). Symlinks already resolved into real content — zero external dependencies. |
| [`MCP/`](MCP/) | Local MCP server registry template, with all secrets redacted to placeholders. |
| [`Plugins/`](Plugins/) | Installed-plugins manifest, known-marketplaces registry, plus the local-directory marketplace cache (without it, Vercel-style plugins fail to reinstall). |
| [`Connectors/`](Connectors/) | Inventory of 43 account-bound MCP integrations (Gmail, Drive, Supabase, Slack, Atlassian, Notion, etc.). These auto-reattach on `claude login` — the README documents what's wired up. |
| [`Tooling/`](Tooling/) | Brewfile, npm-globals snapshot, and **`restore.sh`** — the one-prompt end-to-end restore script. |
| [`settings.json`](settings.json) | Mirror of `~/.claude/settings.json` — permissions, env vars, plugin allowlist. |

---

## The mental model in one diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — ORCHESTRATION                                    │
│  Top-level Claude Code session, Engineering Manager mode     │
│  • Dispatches, never implements                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2 — PROCESS SKILLS (the "how")                        │
│  brainstorming · tdd · diagnose · gepetto · grill-me         │
└──────────────────────────┬──────────────────────────────────┘
                           │ produces plan / spec / test
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — SPECIALIST AGENTS (the "who")                     │
│  35 custom specialists, dispatched in parallel when work     │
│  is independent. THIS is where code gets written.            │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4 — IMPLEMENTATION SKILLS (the "what patterns")       │
│  supabase · threejs · flutter-* · vercel-plugin:* · langfuse │
└──────────────────────────┬──────────────────────────────────┘
                           │ exercises capabilities through
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4½ — TOOLS & INTEGRATIONS  (orthogonal to layers)     │
│  Local MCPs · plugin-bundled MCPs · account connectors       │
└──────────────────────────┬──────────────────────────────────┘
                           │ persists state to
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 5 — MEMORY & STATE (cross-conversation continuity)    │
│  auto-memory · context-kernel                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ audited by
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 6 — GOVERNANCE  (library hygiene)                     │
│  evaluating-skill-necessity → find-skills → managing-skills  │
└─────────────────────────────────────────────────────────────┘
```

The top-priority directive: **the orchestrator never writes code.** All implementation work is dispatched to a specialist who owns that domain. See [`CLAUDE.md`](CLAUDE.md) for the full rule set, including how skill precedence resolves when two skills could do the same job.

---

## Restore on a fresh Mac

```bash
# 1. Clone this repo
git clone https://github.com/build-with-dhiraj/ai-workflow-framework-portability-kit.git
cd ai-workflow-framework-portability-kit

# 2. Run the one-prompt restore script
./Tooling/restore.sh
```

The script is idempotent — safe to re-run. It installs Homebrew packages, npm globals, copies the kit into `~/.claude/`, registers marketplaces, and reinstalls plugins. The only manual step at the end: paste live secrets into `MCP/mcp.template.json` (placeholders point at where each value lives in your password manager).

For the piece-by-piece manual path with troubleshooting, see [`BOOTSTRAP.md`](BOOTSTRAP.md).

---

## Why this exists

LLM coding agents got powerful enough that the bottleneck stopped being "can the model do it" and started being "does my setup let it do the right thing without me babysitting." That setup — agents + skills + integrations + memory + orchestration rules — is a real artifact, but it lives scattered across `~/.claude/`, hidden plugin caches, and ad-hoc config files. Lose your Mac and you lose months of compounding tuning.

This kit treats that setup as code: version-controlled, reproducible, restorable in one command, and forkable by anyone who wants a starting point for their own.

---

## License

[MIT](LICENSE) — fork it, modify it, use it commercially. Just keep the copyright line.
