# Claude Agents and Skills — Master Configuration

This folder is **a portable, self-contained snapshot** of the operator's Claude Code agent + skill setup. Drop it on any new Mac, follow [BOOTSTRAP.md](BOOTSTRAP.md), and the orchestration logic, specialist agents, and skill library are restored exactly as on the source machine.

> **Snapshotted on:** 2026-05-27
> **Source machine settings live at:** `~/.claude/` (mirrored here)

---

## 1. What lives in this folder

| Path | What it is | Source on the Mac |
|---|---|---|
| `CLAUDE.md` *(this file)* | Master orchestration logic, precedence rules, org chart | — |
| `MEMORY.md` | Memory-system design + restoration guide | — |
| `BOOTSTRAP.md` | Step-by-step new-Mac install procedure | — |
| `CLAUDE-global.md` | Snapshot of your global `~/.claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `SPEC-KIT-global.md` | Snapshot of your global `~/.claude/SPEC-KIT.md` (greenfield spec-driven phase mapping) | `~/.claude/SPEC-KIT.md` |
| `settings.json` | Snapshot of `~/.claude/settings.json` (plugins, permissions, env) | `~/.claude/settings.json` |
| `Agents/` | All 35 custom specialist agents + dispatch logic (README inside) | `~/.claude/agents/` |
| `Skills/` | All 107 active skills (symlinks resolved into real content; README inside) | `~/.claude/skills/` |
| `MCP/` | Local MCP server template (secrets redacted) + full MCP roster | `~/.claude/mcp.json` |
| `Plugins/` | Installed-plugins snapshot + marketplace registry + Vercel cache + reinstall guide | `~/.claude/plugins/*` + `~/.cache/plugins/github.com-vercel-vercel-plugin/` |
| `Connectors/` | Account-bound integrations inventory (Gmail, Drive, Supabase, Slack, etc.) | claude.ai → Settings → Connectors (no local file) |
| `Tooling/` | Brewfile + npm globals snapshot + **`restore.sh`** (one-prompt end-to-end restore script) | system-level (Homebrew, npm) |

---

## 2. The Mental Model — Layered Architecture

Claude operates as a **conductor**, not a soloist. Work flows through six layers, each with a distinct job. The orchestrator (top layer) never implements; the specialists (middle layers) do. The governance layer (bottom) keeps the library lean.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 1 — ORCHESTRATION (this Claude Code session, ~/.claude/CLAUDE.md)    │
│  • Engineering Manager mode: dispatches, never implements                    │
│  • Reads user intent → picks specialist → reviews output                     │
│  • EXCEPTIONS: meta-config edits inside ~/.claude/* may be done directly     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ delegates via Task tool
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 2 — PROCESS SKILLS (the "how" — invoked BEFORE implementation)        │
│  • brainstorming, gepetto, grill-me, grill-with-docs, zoom-out, prototype    │
│  • tdd, diagnose, verification-before-completion                             │
│  • Determines workflow, not domain                                            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ produces plan/spec/test
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 3 — SPECIALIST AGENTS (the "who" — domain experts, write code)        │
│  • 35 custom specialist agents in /Agents (see Agents/README.md for org chart)│
│  • Each owns a domain: frontend, backend, Solidity, WeChat, Feishu, etc.     │
│  • Dispatched by Layer 1 in parallel when work is independent                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ uses
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 4 — IMPLEMENTATION SKILLS (the "what patterns" — domain knowledge)    │
│  • supabase, threejs-animation, flutter-*, vercel-plugin:*, langfuse, etc.   │
│  • Loaded inside a specialist when domain depth is needed                    │
│  • Plugin-provided OR local under /Skills                                     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ exercises capabilities through
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 4½ — TOOLS & INTEGRATIONS (the "what can Claude actually DO")         │
│  • Local MCP servers (~/.claude/mcp.json) — see /MCP                         │
│  • Plugin-bundled MCP (figma, vercel, chrome) — see /Plugins                 │
│  • Account Connectors (Gmail, Drive, Supabase, Slack, ...) — see /Connectors │
│  • Orthogonal to agent hierarchy: ALL layers can call these tools            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ persists state to
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 5 — MEMORY & STATE (cross-conversation continuity)                    │
│  • auto-memory: per-project at ~/.claude/projects/<workspace>/memory/        │
│  • context-kernel: <workspace>/.kernel/KERNEL.md for long projects           │
│  • See MEMORY.md for full design                                              │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ audited by
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 6 — GOVERNANCE (library hygiene)                                      │
│  • evaluating-skill-necessity → gate BEFORE adding any skill                 │
│  • find-skills → user-facing discovery                                       │
│  • managing-skills-library → monthly drift/duplication audit                 │
│  • evaluating-agent-behavior → behavioral correctness eval of dispatched runs│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Top-Priority Directive — Engineering Manager Mode

**The orchestrator never writes code.** This is the highest-priority rule, set in `~/.claude/CLAUDE.md` (also mirrored as `CLAUDE-global.md` here).

For ANY code task (writing, modifying, debugging, refactoring, building, configuring project code), the orchestrator MUST:

1. Identify the right specialist from `Agents/`.
2. Dispatch via the `Task` tool with: goal, constraints, files, expected deliverable.
3. For multi-domain work, dispatch in parallel (one message, multiple Task calls).
4. Review specialist output against the original requirements.
5. Integrate and report back.

**The one exception** — meta-configuration touching only `~/.claude/*` (own config, skills, agents, settings) may be done directly without dispatch. This document was written under that exception.

**Subagents are NOT bound by this rule.** When a specialist receives a Task dispatch, it IS expected to run Bash, edit files, and execute the operational work. Self-refusal citing Engineering Manager mode by a dispatched specialist is a bug.

---

## 4. Skill Precedence — Resolving Contradictions

Two or more skills can match the same job. When they do, follow this priority order:

### 4a. Provider tiers (highest first)

| Tier | Provider | When to prefer |
|---|---|---|
| **1** | **Mattpocock skills** (local under `/Skills`) | Engineering work, skill authoring, ticket creation |
| **2** | **Superpowers plugin** | Orchestration workflows not covered by Mattpocock |
| **3** | **Skills Master / governance** | Library audits, upstream planning, evals |
| **4** | **Plugin-provided** (vercel-plugin, figma, karpathy, etc.) | Specific platform domains |

### 4b. Concrete contradiction mappings

| Task | Use | Do NOT use |
|---|---|---|
| Test-driven development | `tdd` (Mattpocock) | `superpowers:test-driven-development` |
| Debugging | `diagnose` (Mattpocock) | `superpowers:systematic-debugging` |
| Authoring a new skill | `write-a-skill` (Mattpocock) | `superpowers:writing-skills` |
| PRD / tracker tickets | `to-prd` or `to-issues` (Mattpocock) | spec-kit `/speckit.tasks` for tracker work |
| Architectural pre-planning | `gepetto` | `superpowers:writing-plans` (use AFTER gepetto) |
| Subagent dispatch | `superpowers:subagent-driven-development`, `superpowers:dispatching-parallel-agents` | — |
| Final verification | `superpowers:verification-before-completion` + `evaluating-agent-behavior` | — |
| Premium / anti-slop UI generation | `design-taste-frontend` (Leonxlnx) | local `frontend-design` (deprecated; archived) |
| Anthropic brand styling | `anthropic-skills:brand-guidelines` (harness-bundled, authoritative) | local `brand-guidelines` (deprecated; archived — was a duplicate of the bundled version) |

### 4c. Local skill clusters (narrowest match wins)

- **Grilling sessions**
  - `grill-with-docs` → project has `docs/adr/` or `CONTEXT.md` (writes decisions back)
  - `grill-me` → otherwise (no doc writes)
- **3D web stack**
  - `threejs-animation` → animation, GLTF, skeletal, morph targets
  - `r3f-best-practices` → R3F authoring or review (non-animation)
  - `3d-web-experience` → catch-all for higher-level "how should I build a 3D site" questions
- **Postgres / Supabase**
  - `supabase` → any task naming Supabase explicitly (the umbrella)
  - `supabase-postgres-best-practices` → SQL performance inside a Supabase project
  - `postgresql-code-review` → pure PostgreSQL, no Supabase context
- **Vercel deployment**
  - `vercel-plugin:deployments-cicd`, `vercel-plugin:vercel-cli`, `vercel-plugin:deploy`, `vercel-plugin:env` are **authoritative**
  - Local `vercel-deployment` skill is **deprecated** (now archived in `~/.claude/skills/.archive/`)
- **Architecture work**
  - `improve-codebase-architecture` → diagnostic: find refactor opportunities in existing code
  - `gepetto` → prescriptive: upfront multi-step plan for a new feature
- **Design / visual quality** (decision tree — read top-down, stop at first match)
  - **Static visual art** (poster, PDF, PNG, single-image deliverable, NOT app UI) → `anthropic-skills:canvas-design`. Stop here.
  - **Figma file involved?** (read, generate, implement, code-connect) → `figma:*` cluster (see "Figma workflow" below). Stop here.
  - **3D / WebGL?** → 3D web stack cluster (above), not this one. Stop here.
  - **Brand-locked Anthropic work** (colors, typography, official identity) → `anthropic-skills:brand-guidelines` (harness-bundled, authoritative). Local `brand-guidelines` is **archived** (was a duplicate).
  - **Greenfield UI generation** (new landing page, portfolio, marketing site, redesign-from-scratch) → `design-taste-frontend` (Leonxlnx/taste-skill). **Supersedes** archived local `frontend-design`. Use FIRST to set direction, THEN run `impeccable /audit` as a polish pass.
  - **Existing UI review / audit / critique / polish** → `impeccable`. 23 slash-commands: `/audit`, `/polish`, `/critique`, `/animate`, `/colorize`, `/typeset`, `/spacing`, `/motion`, `/clarify`, `/distill`, `/harden`, etc. Use `/audit` first to detect anti-patterns, then specific subcommands to fix.
  - **Theme overlay on an existing artifact** (apply one of 10 presets) → `anthropic-skills:theme-factory`. Different layer than design-taste-frontend (skin vs build from scratch).
  - **Motion / animation:**
    - Library-specific: Framer Motion → `framer-motion-animator` · Three.js → `threejs-animation` (3D cluster) · Flutter → `flutter-animating-apps`
    - General motion *taste* / "does this feel alive" / micro-interaction philosophy → `emil-design-eng` (Emil owns judgment, not implementation — pair with `framer-motion-animator` for the actual code)
    - Motion as one aspect of a broader UI audit → `impeccable /animate` or `/motion`
  - **AI-feature UX** (LLM streaming, multi-turn state, fallback states, onboarding for AI features) → `ai-product-ux`. Orthogonal to the above — this is AI-product-shaped UX, not visual design.
  - **shadcn-based product UI** (component library choice) → `vercel-plugin:shadcn` runs alongside whichever generation skill above is firing. Orthogonal — it's about *which library*, not *what design*.
  - **Dispatch agent**: `engineering-design-specialist` owns this entire domain. Dispatched in parallel with `engineering-frontend-developer` when task is "make this beautiful" rather than "build this feature".

- **Figma workflow** (these are sequential steps, not competing alternatives)
  - `figma:figma-use` → read / inspect / interact with a Figma file (prerequisite for several others)
  - `figma:figma-implement-design` → Figma design → production code (1:1 fidelity)
  - `figma:figma-generate-design` → code/page → Figma (build a screen in Figma from an app view)
  - `figma:figma-generate-library` → codebase → Figma design system
  - `figma:figma-create-design-system-rules` → author per-project DS rules
  - `figma:figma-code-connect-components` → bidirectional component mapping

### 4d. Governance trio — strict ordering

`evaluating-skill-necessity` (BEFORE adding a skill) → `find-skills` (user discovery / install path) → `managing-skills-library` (monthly audit).

### 4e. User instructions always override

The `superpowers:using-superpowers` skill makes this explicit:

1. **User's explicit instructions** (CLAUDE.md, AGENTS.md, direct requests) — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If a user instruction says "don't use TDD" and a skill says "always use TDD," follow the user.

---

## 5. The Org Chart — How Agents Stack

The detailed roster lives in [Agents/README.md](Agents/README.md). The dispatch hierarchy:

```
                           ORCHESTRATOR (this session)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   PLANNING TIER             IMPLEMENTATION TIER          SUPPORT TIER
   ─────────────             ───────────────────          ────────────
   software-architect        senior-developer             code-reviewer
   plan (built-in)           frontend-developer           technical-writer
   gepetto (skill)           backend-architect            kernel-steward
   to-prd (skill)            ai-engineer                  codebase-onboarding
                             mobile-app-builder           tabular-data-analyst
                             solidity-smart-contract      explore (built-in)
                             wechat-mini-program          general-purpose
                             feishu-integration
                             devops-automator             OPERATIONS TIER
                             rapid-prototyper             ────────────────
                             minimal-change-engineer      git-workflow-master
                             cms-developer                incident-response
                             embedded-firmware            sre
                             data-engineer                threat-detection
                             database-optimizer           security-engineer
                             ai-data-remediation
                             email-intelligence           SPECIALIZED
                             voice-ai-integration         ───────────
                             filament-optimization        autonomous-optimization
                                                          statusline-setup
                                                          claude-code-guide
```

See [Agents/README.md](Agents/README.md) for the full description of each agent, when to dispatch it, and what its output guarantees are.

---

## 6. The Workflow — Putting it together

A typical multi-domain feature request flows like this:

1. **Brainstorm** the intent (`superpowers:brainstorming` or `product-management:product-brainstorming`).
2. **Plan** the approach (`gepetto` for substantive features → `superpowers:writing-plans` for the executable plan).
3. **Grill** the plan against the codebase (`grill-with-docs` if `docs/adr/` exists, else `grill-me`).
4. **Issue-ize** (`to-issues` if you want independently-grabbable tracker tickets).
5. **Dispatch** specialists in parallel (`superpowers:subagent-driven-development` + `superpowers:dispatching-parallel-agents`).
6. **Verify** before claiming done (`superpowers:verification-before-completion` → `evaluating-agent-behavior` for behavioral correctness).
7. **Memory write-back** (auto-memory captures non-obvious facts, kernel records cross-session state).
8. **Finish** the branch (`superpowers:finishing-a-development-branch`).

For a one-off bug fix, collapse to: `diagnose` → dispatch `minimal-change-engineer` → `verification-before-completion`.

---

## 7. Greenfield exception — Spec-Driven Development

For brand-new projects with no `docs/adr/` or `CONTEXT.md`, the `specify` CLI (github/spec-kit) is installed globally. Mapping:

| spec-kit phase | What it does | Handoff |
|---|---|---|
| `/speckit.constitution` | Writes `.specify/memory/constitution.md` | Project source of truth |
| `/speckit.specify` | Writes spec.md | Hand to `to-prd` if a tracker artifact is needed |
| `/speckit.plan` | Writes plan.md | Hand to `gepetto` for multi-LLM review BEFORE `/speckit.tasks` |
| `/speckit.tasks` | Writes tasks.md | Hand to `to-issues` for tracker tickets |
| `/speckit.implement` | **NEVER RUN** — bypass | Dispatch via Engineering Manager → specialist instead |

The `/speckit.implement` phase is explicitly disabled because spec-kit's generic execution loop bypasses our domain specialists. If a future spec-kit version makes this harder to disable, add an explicit deny in `settings.json`.

---

## 8. Where the source of truth lives

| Concern | File |
|---|---|
| The directive that orchestrator never codes | `CLAUDE-global.md` (mirror of `~/.claude/CLAUDE.md`) |
| Agent roster + dispatch logic | [Agents/README.md](Agents/README.md) |
| Skill roster + precedence detail | [Skills/README.md](Skills/README.md) |
| Local MCP servers + plugin-bundled MCPs | [MCP/README.md](MCP/README.md) (template at `MCP/mcp.template.json`) |
| Installed plugins + marketplaces + reinstall commands | [Plugins/README.md](Plugins/README.md) (snapshots alongside) |
| Account-bound integrations (Gmail, Drive, Supabase, etc.) | [Connectors/README.md](Connectors/README.md) |
| Host-side packages (Homebrew, npm globals) + one-shot restore script | [Tooling/README.md](Tooling/README.md) (Brewfile + npm-globals.json + restore.sh) |
| Memory restoration | [MEMORY.md](MEMORY.md) |
| New-Mac install procedure | [BOOTSTRAP.md](BOOTSTRAP.md) |

When this `CLAUDE.md` and `CLAUDE-global.md` disagree, **`CLAUDE-global.md` wins** — it is the live source-of-truth from the source machine.

When a folder's README and this root `CLAUDE.md` disagree on details (precedence, inventory), **the folder's README wins** — it's closer to the source.
