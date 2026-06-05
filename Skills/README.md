# Skills — Roster, Layers & Precedence

107 active skills live in this folder. They are the **process tier**, **implementation-pattern tier**, and **governance tier** of the architecture described in [../CLAUDE.md](../CLAUDE.md). Skills don't write code by themselves — they tell agents *how* to work.

> **Where they live on the live Mac:** `~/.claude/skills/` (some as real dirs, some as symlinks to `~/.agents/skills/`).
> Restoration: copy every subdirectory in this folder back to `~/.claude/skills/`. Each skill is self-contained — its `SKILL.md` is auto-discovered. The symlink targets have already been resolved here, so no external library is needed.

---

## 1. The four kinds of skills

| Kind | Examples | When invoked |
|---|---|---|
| **Process** | `brainstorming`, `tdd`, `diagnose`, `gepetto`, `grill-me`, `prototype`, `zoom-out`, `verification-before-completion` | Before / around implementation — decides the workflow |
| **Implementation patterns** | `supabase`, `threejs-animation`, `flutter-*`, `langfuse`, `framer-motion-animator`, `r3f-best-practices` | Inside an implementation specialist — loads domain knowledge |
| **Governance** | `evaluating-skill-necessity`, `managing-skills-library`, `evaluating-agent-behavior`, `find-skills` | Around library hygiene & evals |
| **Workflow artifacts** | `to-prd`, `to-issues`, `triage`, `edit-article`, `write-a-skill`, `setup-pre-commit`, `setup-matt-pocock-skills`, `git-guardrails-claude-code` | Producing deliverables outside the code itself |

A few skills span layers — `context-kernel` is part process (when to write/read kernel) and part implementation pattern (the schema). `improve-codebase-architecture` is part diagnostic, part planning.

---

## 2. Precedence rules — what to use when two skills overlap

The same precedence is in [../CLAUDE.md §4](../CLAUDE.md); kept here in compact form for quick lookup.

### 2a. Provider priority (highest first)

| Tier | Provider | Examples |
|---|---|---|
| 1 | **Mattpocock** (local) | `tdd`, `diagnose`, `to-prd`, `to-issues`, `gepetto`, `grill-me`, `write-a-skill`, `setup-pre-commit`, `git-guardrails-claude-code`, `triage`, `prototype`, `zoom-out`, `edit-article`, `scaffold-exercises` |
| 2 | **Superpowers plugin** | `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:subagent-driven-development`, `superpowers:dispatching-parallel-agents`, `superpowers:verification-before-completion`, `superpowers:brainstorming`, `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review` |
| 3 | **Skills Master / governance** | `gepetto` (also Mattpocock-class), `evaluating-skill-necessity`, `managing-skills-library`, `evaluating-agent-behavior`, `find-skills` |
| 4 | **Plugin-provided domain skills** | `vercel-plugin:*` (29 skills), `figma:*` (5 skills), `anthropic-skills:*` (6 skills), `andrej-karpathy-skills:karpathy-guidelines`, `superpowers-chrome:browsing`, `superpowers-developing-for-claude-code:*`, `superpowers-lab:*` |

### 2b. Concrete contradictions and their resolution

| Job | ✅ Use | ❌ Don't use |
|---|---|---|
| TDD | `tdd` (Mattpocock) | `superpowers:test-driven-development` |
| Debugging | `diagnose` (Mattpocock) | `superpowers:systematic-debugging` |
| Writing a new skill | `write-a-skill` (Mattpocock) | `superpowers:writing-skills` |
| PRD / spec | `to-prd` (Mattpocock) | `product-management:write-spec` only for non-tracker output |
| Tracker ticket creation | `to-issues` (Mattpocock) | spec-kit `/speckit.tasks` for tracker work |
| Upfront feature planning | `gepetto` | `superpowers:writing-plans` (use AFTER gepetto if needed) |
| Implementation plan after planning | `superpowers:writing-plans` → `superpowers:executing-plans` | direct dispatch without a plan |
| Parallel subagent dispatch | `superpowers:dispatching-parallel-agents` | sequential when independent |
| Pre-merge verification | `superpowers:verification-before-completion` + `evaluating-agent-behavior` | skipping verification |
| Vercel deployment | `vercel-plugin:deployments-cicd`, `vercel-plugin:vercel-cli`, `vercel-plugin:env`, `vercel-plugin:deploy` | local `vercel-deployment` (deprecated, archived) |

### 2c. Narrowest-match-wins clusters

| Cluster | Cascade |
|---|---|
| **Grilling sessions** | `grill-with-docs` (project has `docs/adr/` or `CONTEXT.md`) → `grill-me` (otherwise) |
| **3D web** | `threejs-animation` (animation/GLTF/skeletal/morph) → `r3f-best-practices` (non-animation R3F) → `3d-web-experience` (general "how should I build a 3D site") |
| **Postgres/Supabase** | `supabase` (Supabase named) → chain `supabase-postgres-best-practices` for SQL perf inside Supabase → `postgresql-code-review` for pure PostgreSQL (no Supabase context) |
| **Architecture** | `improve-codebase-architecture` (diagnostic — existing code) ≠ `gepetto` (prescriptive — new feature planning) |
| **PM brainstorming** | `product-management:product-brainstorming` (product/feature ideation) → `superpowers:brainstorming` (technical/process ideation) |
| **Skill governance (strict ordering)** | `evaluating-skill-necessity` (gate BEFORE adding) → `find-skills` (discovery) → `managing-skills-library` (monthly audit) |

### 2d. User instruction always wins

Per `superpowers:using-superpowers`:

1. **User's explicit instructions** (this CLAUDE.md, conversation directives) — highest
2. **Skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest

---

## 3. Skills by category — what's in this folder

### Process skills (workflow shapers)

| Skill | What it does |
|---|---|
| `tdd` | Red-green-refactor loop. Use before writing implementation. |
| `diagnose` | Reproduce → minimize → hypothesize → instrument → fix loop |
| `gepetto` | Multi-step planning: Research → Interview → Spec → Plan → External Review |
| `grill-me` | Interview-style stress test of your plan |
| `grill-with-docs` | Same as grill-me but writes decisions back to `docs/adr/` and `CONTEXT.md` |
| `prototype` | Build a throwaway prototype to flush out design — terminal or UI variations |
| `zoom-out` | Step back from current code to evaluate the bigger picture |
| `idea-researcher` | Reddit + Chrome + WebSearch cross-source idea validation; produces a 9-section report |
| `edit-article` | Restructure + tighten article drafts |
| `triage` | State machine for issue triage (bugs, feature requests) |
| `to-prd` | Convert current conversation into a PRD on the project issue tracker |
| `to-issues` | Break a plan/spec into independently-grabbable tracker tickets |
| `caveman` | Ultra-compressed response mode (~75% token reduction); persists until "stop caveman" |
| `setup-pre-commit` | Husky + lint-staged + Prettier + typecheck + tests |
| `git-guardrails-claude-code` | Hooks to block dangerous git commands |
| `setup-matt-pocock-skills` | Installs the AGENTS.md `## Agent skills` block + `docs/agents/` scaffolding (precondition for `to-prd`, `to-issues`, `triage`) |
| `write-a-skill` | Author a new skill with proper structure + bundled resources |
| `scaffold-exercises` | Exercise directory scaffolding (course/content authoring) |
| `building-claude-portability-kit` | Build a self-contained Mac-replacement-proof snapshot of an entire Claude Code setup (agents + skills + plugins + MCP + connectors + tooling + restore script). Encodes the exact workflow used to build the canonical kit at `/Users/pw/Claude Agents and Skills/` |

### Implementation-pattern skills (domain knowledge)

**Web / frontend:**

| Skill | Domain |
|---|---|
| `framer-motion-animator` | Framer Motion — page transitions, gestures, scroll, micro-interactions |
| `r3f-best-practices` | React Three Fiber + Poimandres |
| `threejs-animation` | Keyframe, skeletal, morph targets, animation mixing |
| `3d-web-experience` | High-level 3D-web architectural patterns |
| `cra-to-next-migration` | Create React App → Next.js migration |
| `tanstack-start-best-practices` | TanStack Start full-stack patterns |
| `typescript-react-reviewer` | TS + React 19 code review |
| `migrate-to-shoehorn` | Replace `as` assertions in tests with `@total-typescript/shoehorn` |

**Backend / data:**

| Skill | Domain |
|---|---|
| `supabase` | Supabase umbrella (Database, Auth, Edge Functions, Realtime, Storage, Vectors) |
| `supabase-postgres-best-practices` | Postgres perf in a Supabase context |
| `postgresql-code-review` | Pure PostgreSQL review |
| `langfuse` | Langfuse CLI + concepts |
| `gws-forms` | Google Forms read/write |
| `obsidian-vault` | Obsidian vault management (notes, wikilinks, index notes) |

**Code review / governance:**

| Skill | Use |
|---|---|
| `code-review-excellence` | Constructive review practices |
| `security-review` | Comprehensive security checklist for sensitive features |
| `improve-codebase-architecture` | Diagnostic — find refactor opportunities given existing CONTEXT.md + ADRs |
| `context-kernel` | Read/write project context kernel for forked sessions |

**Mobile (Flutter):** 20 `flutter-*` skills covering setup (macOS/Windows/Linux), building (forms, layouts, plugins, widgets), animation, navigation, state, theming, testing, localization, accessibility, native interop, concurrency, caching, databases, HTTP, size reduction.

**Product:**

| Skill | Use |
|---|---|
| `product-management` | Founder/PM toolkit (discovery, roadmaps, prioritization, PMF) |
| `find-skills` | User-facing skill discovery |

### Governance / meta

| Skill | Use |
|---|---|
| `evaluating-skill-necessity` | Run **before** adding any skill |
| `managing-skills-library` | Monthly drift / duplication audit |
| `evaluating-agent-behavior` | Eval agents on tool choice, steerability, behavioral correctness (chained after `verification-before-completion`) |

---

## 4. Plugin-provided skills (NOT mirrored here)

The following skills come from installed plugins — they auto-reappear when plugins are re-installed on the new Mac (see [../BOOTSTRAP.md](../BOOTSTRAP.md)). They live in `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/skills/` and aren't copied here because the plugin source controls them.

| Plugin | Skill count | Highlights |
|---|---|---|
| `vercel-plugin` | 29 | `ai-sdk`, `chat-sdk`, `nextjs`, `nextjs-app-router`, `deploy`, `env`, `workflow`, `ai-elements`, `shadcn`, `runtime-cache`, `routing-middleware`, `vercel-functions`, `cron-jobs`, etc. |
| `figma` | 5 | `figma-use`, `figma-generate-design`, `figma-implement-design`, `figma-code-connect-components`, `figma-create-design-system-rules`, `figma-generate-library` |
| `superpowers` | ~14 | `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch`, `systematic-debugging` (use Mattpocock `diagnose` instead), `test-driven-development` (use Mattpocock `tdd` instead), `writing-skills` (use Mattpocock `write-a-skill` instead) |
| `superpowers-chrome` | 1 | `browsing` (Chrome DevTools Protocol via `use_browser`) |
| `superpowers-developing-for-claude-code` | 2 | `working-with-claude-code`, `developing-claude-code-plugins` |
| `superpowers-lab` | 5 | `slack-messaging`, `windows-vm`, `mcp-cli`, `finding-duplicate-functions`, `using-tmux-for-interactive-commands` |
| `andrej-karpathy-skills` | 1 | `karpathy-guidelines` |
| `anthropic-skills` *(built-in default plugin)* | 7 | `docx`, `pptx`, `pdf`, `xlsx`, `skill-creator`, `setup-cowork`, `consolidate-memory` |
| Claude Code built-ins | several | `init`, `review`, `security-review`, `loop`, `schedule`, `claude-api`, `update-config`, `simplify`, `fewer-permission-prompts`, `keybindings-help` |

---

## 5. File inventory — what's actually in this folder

82 skill directories, alphabetically:

```
3d-web-experience              flutter-handling-concurrency      postgresql-code-review
brand-guidelines               flutter-handling-http-and-json    product-management
building-claude-portability-kit flutter-implementing-navigation-…  prototype
caveman                        flutter-improving-accessibility   r3f-best-practices
claude-seo                     flutter-interoperating-with-…     scaffold-exercises
code-review-excellence         flutter-localizing-apps           security-review
context-kernel                 flutter-managing-state            setup-matt-pocock-skills
cra-to-next-migration          flutter-reducing-app-size         setup-pre-commit
deep-research                  flutter-setting-up-on-linux       supabase
diagnose                       flutter-setting-up-on-macos       supabase-postgres-best-practices
edit-article                   flutter-setting-up-on-windows     tanstack-start-best-practices
evaluating-agent-behavior      flutter-testing-apps              tdd
evaluating-skill-necessity     flutter-theming-apps              threejs-animation
fact-check                     flutter-working-with-databases    to-issues
find-skills                    framer-motion-animator            to-prd
fleet-auditor                  frontend-design                   token-coach
flutter-adding-home-screen-…   gepetto                           token-dashboard
flutter-animating-apps         git-guardrails-claude-code        token-optimizer
flutter-architecting-apps      grill-me                          triage
flutter-building-forms         grill-with-docs                   typescript-react-reviewer
flutter-building-layouts       gws-forms                         write-a-skill
flutter-building-plugins       humanizer                         zoom-out
flutter-caching-data           idea-researcher
flutter-embedding-native-views improve-codebase-architecture
                               langfuse
                               managing-skills-library
                               migrate-to-shoehorn
                               obsidian-vault
                               office-hours
```

### Added 2026-05-14 (post-snapshot import)
| Skill | Source | Notes |
|---|---|---|
| `frontend-design` | `anthropics/skills` | Anti-AI-aesthetic UI generation; bans Inter/Roboto/Space Grotesk defaults |
| `brand-guidelines` | `anthropics/skills` | Anthropic-official brand application; complements figma/shadcn skills |
| `deep-research` | `199-biotechnologies/claude-deep-research-skill` | 8-phase multi-source pipeline; deeper than `idea-researcher` |
| `humanizer` | `blader/humanizer` | Strips 29 Wikipedia-documented "signs of AI writing" patterns |
| `office-hours` | `garrytan/gstack` | YC-partner-style brutal teardown; 6 forcing questions |
| `fact-check` | `petar-nauka/fact-check-skill` | SIFT+CRAAP claim verification; produces HTML Fact-Check Cards |
| `token-optimizer` | `alexgreensh/token-optimizer` | Context-side ghost-token audit (NOT PDF extraction) |
| `token-coach` | (same package) | Proactive token-efficiency guidance during sessions |
| `token-dashboard` | (same package) | Browser dashboard for token usage trends |
| `fleet-auditor` | (same package) | Cross-tool token-waste audit (CC, Codex, OpenClaw, Hermes, OpenCode) |
| `claude-seo` | `AgriciDaniel/claude-seo` | **Plugin, not flat skill** — has agents/hooks/extensions; needs `./install.sh` to fully wire up 18 sub-agents |

Skipped duplicates: *Skill creator* (covered by `anthropic-skills:skill-creator` + `write-a-skill`), *Find skill* (covered by local `find-skills`).

Each directory contains a `SKILL.md` with the activation logic, plus optional bundled resources (scripts, templates, references).

### Added 2026-05-27 (design layer + drift catch-up)

**3 new design skills (the headline of this update):**

| Skill | Source | License | Notes |
|---|---|---|---|
| `impeccable` | `pbakaus/impeccable` | Apache 2.0 | Anti-pattern auto-detection + 23 slash-commands (`/audit`, `/polish`, `/critique`, `/animate`, etc.). Active upstream (30k stars). |
| `design-taste-frontend` | `Leonxlnx/taste-skill` | MIT | Anti-slop frontend for landing pages, portfolios, redesigns. **Supersedes the archived local `frontend-design`.** Active upstream (22k stars). |
| `emil-design-eng` | `emilkowalski/skill` | **None (no LICENSE upstream)** — risk accepted by operator. Documented for audit trail. | Emil Kowalski's philosophy on motion polish, easing, micro-interactions. Narrow scope. |

**Companion agent:** `engineering-design-specialist.md` added — visual-judgment dispatch parallel to `engineering-frontend-developer`. See `Agents/README.md` for full role.

**Deprecated/archived:**
- Local `frontend-design` moved to `~/.claude/skills/.archive/frontend-design/` (replaced by `design-taste-frontend`).
- Local `brand-guidelines` moved to `~/.claude/skills/.archive/brand-guidelines/` (was a duplicate of harness-bundled `anthropic-skills:brand-guidelines`; bundled version is authoritative).

Both are locally restorable; neither is visible in the public kit.

---

### Connecting-Dots planning round (same 2026-05-27 push)

While planning a personal-content "second brain" tool ("Connecting Dots"), the `evaluating-skill-necessity` gate was run against marketplace candidates for each project gap. After concrete `npx skills find` results were re-gated, **2 marketplace installs passed and 1 custom skill was authored** via `write-a-skill`:

| Skill | Source | License | Use |
|---|---|---|---|
| `baoyu-youtube-transcript` | `jimliu/baoyu-skills` (skills.sh) | MIT-ish (per skill repo) | Download YouTube transcripts/subtitles/cover images by URL or video ID. 11.4k installs, category leader. |
| `integrate-whatsapp` | `gokapso/agent-skills` (skills.sh) | Per skill repo | WhatsApp Cloud API integration — onboarding flow, webhooks, message-send, Flows. 2k installs. |
| `personal-content-resurface` | **Local custom (authored via `write-a-skill`)** | MIT (kit-default) | Decide which saved content (YT/IG/WA/LI) should re-surface today. Encodes SM-2, FSRS, and a custom context-aware hybrid algorithm — implementer picks at build time. Decision math only; no UX. This is the Connecting-Dots moat. |

**Gate results for the other gaps (documented for audit trail):**
- LinkedIn scraper → REJECT (no skill installed; manual export flow specified in PRD instead — ToS-safer)
- Personal knowledge graph skill → REJECT (existing `obsidian-vault` + `memory-router` + `ner-content-pipeline` cover 85%)
- Browser extension scaffold → REJECT (out of MVP scope)
- Playwright skill / Neo4j skill / Prefect skill → DEFERRED (revisit after `gepetto` architectural decisions)
- Instagram scraper → DEFERRED (install only if `deep-research` confirms IG platform-feasibility)

**Unrelated drift (9 skills appeared between 2026-05-20 and 2026-05-27, lumped into this same push):** `defuddle`, `wrap-up`, `user-research`, `obsidian-markdown`, `research-synthesis`, `memory-router`, `obsidian-bases`, `obsidian-cli`, `json-canvas`. These are personal-knowledge / research / utility skills (Obsidian + Pinecone memory routing pattern), unrelated to the design layer. Documented here for the next monthly `managing-skills-library` audit.

**Governance gate override:** `evaluating-skill-necessity` would likely have flagged Emil (no license) and Taste (overlap with `frontend-design`). Operator overrode the gate explicitly: Emil installed with risk accepted; Taste replaces `frontend-design` rather than coexisting. Logged here for the audit trail.
