# 🧰 AI Workflow Framework & Portability Kit

> Your entire Claude Code stack — **35 agents, 123 skills, plugins, MCP & tooling** — portable across Macs. Clone, `claude login`, run one script, working in **~20 min**.

<p>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/build-with-dhiraj/ai-workflow-framework-portability-kit?color=yellow"></a>
  <img alt="last commit" src="https://img.shields.io/github/last-commit/build-with-dhiraj/ai-workflow-framework-portability-kit">
  <img alt="agents" src="https://img.shields.io/badge/agents-35-blue">
  <img alt="skills" src="https://img.shields.io/github/directory-file-count/build-with-dhiraj/ai-workflow-framework-portability-kit/Skills?type=dir&label=skills&color=blue">
  <img alt="platform" src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-orchestration-D97757">
</p>

A portable, self-contained snapshot of a working **Claude Code** setup — the specialist agents, the skill library, the plugins, the MCP servers, the host-side tooling, and the orchestration logic that ties them all together. Drop the folder on a fresh Mac, run one script, and the entire stack is restored in about twenty minutes.

This is the master config behind a multi-layer **"Engineering Manager"** AI workflow: a top-level orchestrator that never writes code itself, dispatching work down to 35 specialist agents who do. The kit captures that architecture as plain files anyone can audit, fork, or rebuild from.

> **Want the deep model?** This README is the landing page. [`CLAUDE.md`](CLAUDE.md) is the full deep-dive — the layered architecture, every skill-precedence rule, and the agent org chart.

---

## 🤔 Why this exists

LLM coding agents got powerful enough that the bottleneck stopped being *"can the model do it"* and started being *"does my setup let it do the right thing without me babysitting."*

That setup — agents + skills + integrations + memory + orchestration rules — is a real, compounding artifact. But it lives scattered across `~/.claude/`, hidden plugin caches, and ad-hoc config files. **Lose your Mac and you lose months of tuning.** Standing it back up by hand is hours of careful, error-prone work: re-authoring agents, re-installing plugins from the right marketplaces, resolving symlinked skills, re-wiring MCP servers, remembering which Homebrew and npm globals were load-bearing.

This kit treats that setup as code: **version-controlled, reproducible, restorable in one command, and forkable** by anyone who wants a starting point for their own. New Mac → `claude login` → one script → ~20 minutes → the whole orchestration stack is back.

---

## 📦 What's inside

| Folder / file | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The master orchestration logic — the layered architecture, skill-precedence rules, agent org chart, the Engineering-Manager directive. **Start here for the deep model.** |
| [`BOOTSTRAP.md`](BOOTSTRAP.md) | Step-by-step new-Mac install runbook. Numbered phases for the manual path; one-script "fast path" up top. |
| [`MEMORY.md`](MEMORY.md) | Memory-system design + restoration guide — auto-memory (per-project), context kernel (cross-session), what survives a Mac swap. |
| [`Agents/`](Agents/) | **35 custom specialist agents** + dispatch logic — frontend, backend, AI, Solidity, WeChat, Feishu, design-specialist, and more. Each is dispatched by the orchestrator via the `Task` tool. ([README inside](Agents/README.md)) |
| [`Skills/`](Skills/) | **123 active skills** — process discipline (TDD, debugging, brainstorming), implementation patterns (Supabase, Three.js, Flutter, the design layer, YouTube transcript, WhatsApp Cloud API, finance modeling), and governance (skill-necessity gating, library hygiene). Symlinks already resolved into real content — zero external dependencies. ([README inside](Skills/README.md)) |
| [`MCP/`](MCP/) | Local MCP server template (secrets redacted to placeholders) + the full MCP roster. ([README inside](MCP/README.md)) |
| [`Plugins/`](Plugins/) | Installed-plugins snapshot + known-marketplaces registry + the local-directory Vercel marketplace cache + reinstall guide. ([README inside](Plugins/README.md)) |
| [`Connectors/`](Connectors/) | Inventory of account-bound MCP integrations (Gmail, Drive, Supabase, Slack, Atlassian, Notion, …). These auto-reattach on `claude login`. ([README inside](Connectors/README.md)) |
| [`Automations/`](Automations/) | The **loop-heartbeat** layer ([Loop Engineering](https://addyosmani.com/blog/loop-engineering/)) — the harness scheduling stack (`/loop`, `/goal`, `/schedule`), hooks/statusLine policy, and a human-in-the-loop kit-maintenance loop. ([README inside](Automations/README.md)) |
| [`Tooling/`](Tooling/) | Brewfile + npm-globals snapshot + **`restore.sh`** — the one-prompt end-to-end restore script. ([README inside](Tooling/README.md)) |
| [`CLAUDE-global.md`](CLAUDE-global.md) | Verbatim mirror of the source machine's global `~/.claude/CLAUDE.md`. Source of truth for the orchestrator directive. |
| [`SPEC-KIT-global.md`](SPEC-KIT-global.md) | Greenfield-only Spec-Driven Development phase map; explicit override rule (never run `/speckit.implement`). |
| [`settings.json`](settings.json) | Mirror of `~/.claude/settings.json` — permissions, env vars, plugin allowlist. |

---

## 🧠 The mental model

Claude operates as a **conductor, not a soloist.** Work flows down through layers — the orchestrator at the top *dispatches but never implements*; the specialists in the middle do the actual building; governance at the bottom keeps the library lean.

```
┌──────────────────────────────────────────────────────────────┐
│  L1 — ORCHESTRATION   Engineering-Manager mode                 │
│       Reads intent → picks specialist → reviews. Never codes.  │
└───────────────────────────────┬──────────────────────────────┘
                                │  dispatches via Task tool
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L2 — PROCESS SKILLS  the "how"                                │
│       brainstorming · tdd · diagnose · gepetto · grill-me      │
└───────────────────────────────┬──────────────────────────────┘
                                │  produces plan / spec / test
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L3 — SPECIALIST AGENTS  the "who"  ← code gets written HERE   │
│       35 domain experts, dispatched in parallel when possible  │
└───────────────────────────────┬──────────────────────────────┘
                                │  uses
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L4 — IMPLEMENTATION SKILLS  the "what patterns"               │
│       supabase · threejs · flutter-* · vercel-plugin:* · …     │
└───────────────────────────────┬──────────────────────────────┘
                                │  exercises capabilities via
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L4½ — TOOLS & INTEGRATIONS  (orthogonal — every layer calls)  │
│        local MCP servers · plugin-bundled MCP · connectors     │
└───────────────────────────────┬──────────────────────────────┘
                                │  persists state to
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L5 — MEMORY & STATE   auto-memory · context-kernel            │
└───────────────────────────────┬──────────────────────────────┘
                                │  audited by
                                ▼
┌──────────────────────────────────────────────────────────────┐
│  L6 — GOVERNANCE   evaluating-skill-necessity → find-skills →  │
│       managing-skills-library → evaluating-agent-behavior      │
└──────────────────────────────────────────────────────────────┘
```

**The top-priority directive: the orchestrator never writes code.** Every implementation task is dispatched to the specialist who owns that domain; the orchestrator only plans, selects, reviews, and integrates. The one exception is meta-config that touches only `~/.claude/*`.

👉 Full rule set — including how skill precedence resolves when two skills could do the same job — lives in [`CLAUDE.md`](CLAUDE.md). The decision trees that encode it are reproduced [further down this page](#-skill-precedence--decision-trees).

---

## 🚀 Quick start

```bash
# 1. Clone
git clone https://github.com/build-with-dhiraj/ai-workflow-framework-portability-kit.git
cd ai-workflow-framework-portability-kit

# 2. Authenticate Claude Code (install it first if needed: brew install claude-code)
claude login

# 3. Run the one-prompt restore script (it prompts before doing anything)
bash "Tooling/restore.sh"
```

That's it. The script is **idempotent** — safe to re-run if it fails partway. In 7 steps it installs Homebrew packages, installs npm globals, copies the global config + agents + skills into `~/.claude/`, registers plugin marketplaces, and reinstalls plugins. The **only** manual step at the end: paste live secrets into `MCP/mcp.template.json` (each placeholder points at where the real value lives in your password manager).

> Prefer the piece-by-piece path with troubleshooting notes? See [`BOOTSTRAP.md`](BOOTSTRAP.md) — it walks every phase by hand and explains the recovery options (e.g. the local-directory Vercel marketplace).

---

## ✅ What it restores

| | |
|---|---|
| 🤖 **35** specialist agents | the full dispatch roster, copied into `~/.claude/agents/` |
| 🧩 **123** skills | process + implementation + governance, symlinks pre-resolved (zero external deps) |
| 🔌 **8** plugins | re-installed from their marketplaces (incl. the local-directory Vercel cache) |
| 🛰️ MCP template | full server roster with secrets redacted to placeholders |
| 🍺 Host tooling | Brewfile (leaf packages + VS Code extensions + `uv` tools) + npm globals |
| 🧠 Memory design | auto-memory + context-kernel restoration guide (state survives if repos are pushed) |

Total time on a fresh Mac: **~20 minutes** (dominated by `brew bundle`).

---

## 🧭 Skill precedence — decision trees

When two or more skills could handle the same task, these trees decide which one fires. **Read top-down, stop at first match.** The same logic lives in compact bullet form in [`CLAUDE.md` §4](CLAUDE.md) and [`Skills/README.md` §2](Skills/README.md).

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

## 📄 License

[MIT](LICENSE) — fork it, modify it, use it commercially. Just keep the copyright line.

**Further reading:** [`BOOTSTRAP.md`](BOOTSTRAP.md) (new-Mac runbook) · [`CLAUDE.md`](CLAUDE.md) (full architecture & precedence deep-dive) · [`MEMORY.md`](MEMORY.md) (memory-system design).
