# Skills — Roster, Layers & Precedence

115 active skills live in this folder. They are the **process tier**, **implementation-pattern tier**, and **governance tier** of the architecture described in [../CLAUDE.md](../CLAUDE.md). Skills don't write code by themselves — they tell agents *how* to work.

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
| `building-claude-portability-kit` | Build a self-contained Mac-replacement-proof snapshot of an entire Claude Code setup (agents + skills + plugins + MCP + connectors + tooling + restore script). Encodes the exact workflow used to build this canonical kit (the folder you're reading now) |

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

115 skill directories — the authoritative on-disk set as of the 2026-06-11 re-sync, alphabetically:

```
3d-web-experience                           ai-product-ux
arize-experiment                            arize-prompt-optimization
baoyu-youtube-transcript                    build-review-interface
building-claude-portability-kit             caveman
claude-seo                                  code-review-excellence
context-kernel                              cra-to-next-migration
creating-financial-models                   deep-research
defuddle                                    design-taste-frontend
diagnose                                    dspy-gepa-reflective
edit-article                                emil-design-eng
error-analysis                              eval-audit
evaluate-rag                                evaluating-agent-behavior
evaluating-skill-necessity                  fact-check
find-skills                                 fleet-auditor
flutter-adding-home-screen-widgets          flutter-animating-apps
flutter-architecting-apps                   flutter-building-forms
flutter-building-layouts                    flutter-building-plugins
flutter-caching-data                        flutter-embedding-native-views
flutter-handling-concurrency                flutter-handling-http-and-json
flutter-implementing-navigation-and-routing flutter-improving-accessibility
flutter-interoperating-with-native-apis     flutter-localizing-apps
flutter-managing-state                      flutter-reducing-app-size
flutter-setting-up-on-linux                 flutter-setting-up-on-macos
flutter-setting-up-on-windows               flutter-testing-apps
flutter-theming-apps                        flutter-working-with-databases
framer-motion-animator                      generate-synthetic-data
gepetto                                     git-guardrails-claude-code
github-actions                              grill-me
grill-with-docs                             gws-forms
humanizer                                   idea-researcher
impeccable                                  improve-codebase-architecture
integrate-whatsapp                          jove-youtube-feed-pipeline
json-canvas                                 langfuse
langsmith-evaluator                         llm-eval
managing-skills-library                     master-resume
memory-router                               migrate-to-shoehorn
ner-content-pipeline                        obsidian-bases
obsidian-brain-eval                         obsidian-cli
obsidian-graph-auditor                      obsidian-markdown
obsidian-orphan-rescue                      obsidian-vault
obsidian-vault-architect                    office-hours
personal-content-resurface                  postgresql-code-review
product-management                          prompt-engineering
prototype                                   python-pipelines
r3f-best-practices                          rag-patterns
research-synthesis                          scaffold-exercises
security-review                             setup-matt-pocock-skills
setup-pre-commit                            stock-onboarding-pipeline
stock-pick-ranker                           supabase
supabase-postgres-best-practices            tanstack-start-best-practices
tdd                                         threejs-animation
to-issues                                   to-prd
token-coach                                 token-dashboard
token-optimizer                             triage
typescript-react-reviewer                   user-research
validate-evaluator                          wrap-up
write-a-skill                               write-judge-prompt
zoom-out
```

> `frontend-design` and `brand-guidelines` are **not** in this list — both were archived to `~/.claude/skills/.archive/` (superseded by `design-taste-frontend` and `anthropic-skills:brand-guidelines` respectively) and are intentionally absent from the public kit. The dated subsections below narrate how the library grew to these 115; this fenced block is the source of truth for *what is on disk right now*.

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

---

### Added 2026-06-05: Obsidian PKM trilogy (operator-authored, vendored from `~/builds/`)

Three Python-CLI skills authored by the operator (Dhiraj / `build-with-dhiraj`), each its own published GitHub repo. Vendored here as **lean runnable source** — `SKILL.md` + package source + `pyproject.toml` + `docs/`/`examples/` — with `.venv`, `.git`, caches, and social-card assets excluded (~0.5–0.7 MB each).

| Skill | Source repo | License | What it does |
|---|---|---|---|
| `obsidian-graph-auditor` | `build-with-dhiraj/obsidian-graph-auditor` | MIT | Grades a vault's graph health on an 8-dimension rubric (read-only, pure Python) |
| `obsidian-brain-eval` | `build-with-dhiraj/obsidian-brain-eval` | MIT | Scores vault RAG on Recall@10 vs a 0.85 threshold (BM25 / LanceDB backends) |
| `obsidian-orphan-rescue` | `build-with-dhiraj/obsidian-pkm-skills` | MIT | Auto-links orphan notes (resolve / anchor / mint; frontmatter-only safe writes). *Lives in the `obsidian-pkm-skills` monorepo under `skills/`. Renamed from `obsidian-orphan-killer`; the standalone `obsidian-orphan-killer` repo is now archived and its URL redirects.* |

**These are tool-backed skills, not prompt-only** — unlike the rest of the library, they need a Python install to actually run:
- **Not yet on PyPI** (as of 2026-06-05). After restore, activate with `pip install ~/.claude/skills/<name>` (installs from the vendored source) or `pip install "git+https://github.com/build-with-dhiraj/<name>"`. Once published, the bare `pip install <name>` in each `SKILL.md` resolves from PyPI directly.
- Pulls standard PyPI deps (`networkx`, `python-louvain`, `rank-bm25`, `lancedb`, `fastembed`, `openai`) — the one external dependency the kit can't eliminate for these.
- The vendored copies are **snapshots**; re-sync from `~/builds/` when the upstream repos advance.

Together they form a pipeline: **audit** graph topology → **eval** retrieval quality → **fix** orphans.

---

### Added 2026-06-08: finance / investment-analysis pair (re-sync to live → 112 skills)

Two finance skills appeared in the live `~/.claude/skills/` since the last snapshot and are vendored here. This is the re-sync that brings the kit to full parity with the live app — **110 → 112 skills**.

| Skill | License | What it does |
|---|---|---|
| `creating-financial-models` | MIT (kit-default) | Advanced financial-modeling suite — DCF analysis, sensitivity testing, Monte Carlo simulation, and scenario planning for investment decisions. Method/concept toolkit; use for standalone models of private/unlisted companies. |
| `stock-pick-ranker` | MIT (kit-default) | End-to-end equity quality + valuation ranking pipeline: scrapes investor newsletters, enriches live (Indian-listed) financials, scores each stock on a 7-factor principles rubric, runs forward + reverse DCF, reliability-weights the valuation, re-ranks the universe, and appends/refreshes `Substack_Stock_Picks.xlsx`. Workbook-driven; distinct from `creating-financial-models` (which is for standalone private-company models). |

Same `obsidian-orphan-killer` → `obsidian-orphan-rescue` rename landed in this re-sync (see the 2026-06-05 table above — the local directory and CLI are now `obsidian-orphan-rescue`; the upstream GitHub repo has since been renamed to `obsidian-orphan-rescue` as well, and the old `obsidian-orphan-killer` repo URL now redirects).

---

### Added 2026-06-11: live re-sync → 115 skills

Three skills appeared in the live `~/.claude/skills/` since the last snapshot and are vendored here (operator-authored / personal). Re-sync brings the kit to parity with the live app — **112 → 115 skills**.

| Skill | License | What it does |
|---|---|---|
| `master-resume` | MIT (kit-default) | Research-grade resume/CV/cover-letter tailoring from a persistent experience library to specific JDs — provenance-checked anti-fabrication, confidence-scored matching, 8-dimension critique, LaTeX/Overleaf output. **Runtime dep:** `tectonic` (Homebrew) for PDF compilation — not yet captured in `Tooling/Brewfile`; `brew install tectonic` after restore. |
| `obsidian-vault-architect` | MIT (kit-default) | Higher-level Obsidian vault structuring/architecture guidance (complements the `obsidian-graph-auditor` / `obsidian-brain-eval` / `obsidian-orphan-rescue` trilogy). |
| `stock-onboarding-pipeline` | MIT (kit-default) | End-to-end onboarding of new Indian stocks into the "Paise se Paisa" Action Dashboard (deep dossier → advisor board with FOREVER gate → deterministic D-Engine re-rank → publish). Embeds a personal workspace path (`/Users/pw/invest`) and a Google Sheet fileId — adjust on a new machine. |

`hooks` + `statusLine` (token-optimizer) remain intentionally **out** of the kit's `settings.json` — they hardcode a machine-specific `.archive-token-optimizer-pkg` path and the token-optimizer plugin re-establishes them on restore.
