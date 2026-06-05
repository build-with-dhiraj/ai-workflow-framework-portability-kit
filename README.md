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
| [`Skills/`](Skills/) | **110 active skills** — process discipline (TDD, debugging, brainstorming), implementation patterns (Supabase, Three.js, Flutter, design / impeccable / taste, YouTube transcript, WhatsApp Cloud API, etc.), and governance (skill-necessity gating, library hygiene). Symlinks already resolved into real content — zero external dependencies. |
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

## Skill precedence — decision trees

When two or more skills could handle the same task, these trees decide which one fires. Read top-down, stop at first match. Same logic lives terser as bullet lists in `CLAUDE.md` §4c.

### Design / visual quality

```
You say: "design / make / polish / animate / audit something"
                │
                ▼
        Is it static visual art? (poster, PDF, PNG, single-image)
                │
        ┌───────┴───────┐
       YES              NO  (it's app UI)
        │               │
   anthropic-skills:    ▼
   canvas-design   Figma file involved? (read / generate / implement)
   ───STOP──             │
                  ┌──────┴──────┐
                 YES            NO
                  │             │
              figma:* cluster   ▼
              (see Figma        3D / WebGL?
               workflow         │
               below)     ┌─────┴─────┐
              ───STOP──  YES          NO
                          │           │
                   3D web stack       ▼
                   cluster       Brand-locked Anthropic work?
                   (see below)        │
                   ───STOP──    ┌─────┴─────┐
                               YES          NO
                                │           │
                       anthropic-skills:    ▼
                       brand-guidelines NEW UI or EXISTING UI?
                       (local archived)     │
                       ───STOP──      ┌─────┴─────┐
                                    NEW         EXISTING
                                     │           │
                         design-taste-frontend   impeccable
                         (greenfield landing /   (anti-pattern audit:
                          portfolio / redesign)  /audit /polish /critique
                                                 /animate /typeset /spacing
                         THEN run impeccable     /motion /clarify /distill
                         /audit as polish pass   /harden ...)
                                     │           │
                                     └─────┬─────┘
                                           ▼
                                    Need motion?
                                           │
                                    ┌──────┼──────────┐
                                 FRAMER  OTHER     Three.js
                                  │     (taste)       │
                       framer-motion- emil-design-  3D cluster
                       animator       eng (taste;   (above)
                                      pair with
                                      framer for
                                      actual code)
                                           │
                                           ▼
                                    Theme overlay?
                                    (apply preset)
                                           │
                                    anthropic-skills:theme-factory

  Orthogonal layers (always available, never conflict):
    AI-feature UX (LLM streaming, fallback, multi-turn) → ai-product-ux
    shadcn component library                            → vercel-plugin:shadcn

  Full design-task dispatch ("make this beautiful" not "build this feature"):
    → engineering-design-specialist (parallel to engineering-frontend-developer)
```

---

### Grilling — stress-testing a plan

```
Need to stress-test a plan or design decision?
                │
                ▼
   Does the project have docs/adr/ or CONTEXT.md?
                │
        ┌───────┴───────┐
       YES              NO
        │               │
   grill-with-docs      grill-me
   (writes decisions    (no doc writes;
    back to docs/adr/)  pure interview)
```

---

### 3D web stack (narrowest-match-wins)

```
3D / WebGL task?
        │
        ▼
Is it animation? (keyframe, GLTF, skeletal, morph targets, mixing)
        │
   ┌────┴─────┐
  YES         NO
   │          │
threejs-      ▼
animation  Is it React Three Fiber specifically?
───STOP──     │
         ┌────┴────┐
        YES        NO
         │         │
   r3f-best-       ▼
   practices  3d-web-experience
   ───STOP──  (catch-all — "how do I build a 3D site",
              Spline integration, immersive scenes,
              product configurators)
```

---

### Postgres / Supabase

```
Postgres / SQL task?
        │
        ▼
Does the task involve Supabase explicitly?
(Database, Auth, Storage, Edge Functions, Vectors, supabase-js, RLS, ...)
        │
   ┌────┴─────┐
  YES         NO
   │          │
   ▼          ▼
Is this   postgresql-code-review
SQL       (pure PostgreSQL, no
performance Supabase context;
specifically? schema, queries, RLS,
   │          functions)
┌──┴───┐
YES    NO
 │     │
supabase- supabase
postgres- (umbrella — any
best-     Supabase task,
practices product-wide)
```

---

### Vercel deployment

```
Vercel deployment / CI / env-var work?
        │
        ▼
  Use vercel-plugin:* skills (all authoritative)
        │
   ┌────┴────┬─────────┬──────────────┐
   ▼         ▼         ▼              ▼
deployments- vercel-cli  deploy        env
cicd                                   (env-var management)
(workflows,  (CLI usage, (the deploy   (list/pull/add/
 promote,     env, link,  command       remove, diff
 rollback,    logs)       itself)       between envs)
 prebuild)

  ⚠️ Local vercel-deployment skill is DEPRECATED
  Archived in ~/.claude/skills/.archive/. Do not use.
```

---

### Architecture work

```
Architecture / refactoring task?
        │
        ▼
Is there existing code to analyze?
        │
   ┌────┴─────┐
  YES         NO  (new feature; nothing to scan yet)
   │          │
   ▼          ▼
improve-     gepetto
codebase-    (prescriptive — multi-step plan,
architecture  multi-LLM review via stakeholder
(diagnostic   interviews. Use BEFORE
— scans       superpowers:writing-plans)
docs/adr/ +
CONTEXT.md +
code; flags
refactor
opportunities)
```

---

### Figma workflow (sequential steps, not competing alternatives)

```
                  ┌─────────────────┐
                  │ figma:figma-use │  ◄── PREREQUISITE for most others
                  │ (read / inspect /│      (Figma must be reachable
                  │  interact with   │       before any other op)
                  │  a Figma file)   │
                  └────────┬────────┘
                           │
   ┌────────────┬──────────┼──────────────┬─────────────────┐
   ▼            ▼          ▼              ▼                 ▼
figma:        figma:     figma:        figma:             figma:
figma-        figma-     figma-        figma-create-      figma-code-
implement-    generate-  generate-     design-system-     connect-
design        design     library       rules              components

(Figma →      (code /    (codebase →   (author per-       (bidirectional
 production    page →     Figma         project DS         mapping
 code, 1:1     Figma —    design        rules / tokens)    Figma ↔ code
 visual        build a    system)                          components for
 fidelity)     screen in                                   Code Connect)
               Figma from
               an app view)
```

Use the leftmost path (read → implement) when you have a Figma design that needs to ship as code. Use the rightmost paths (generate-library, code-connect) when you have a codebase and want to maintain a design system in Figma alongside it.

---



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
