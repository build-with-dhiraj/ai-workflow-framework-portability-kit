---
name: jove-design-loop
description: Turns Colleague-V's Figma exports + Claude Design + the JoVE Design System into a fast, credential-free loop that cuts the designer-dependency on dev START without touching his visual authority. Builds a designed-vs-owed ledger from CSS/PNG exports, gates any prototype behind a written PM spec, assembles clickable prototypes on the JoVE Design System, and attaches them to Jira tickets as strawmen for the dev lead/Colleague-S/Colleague-P to start from. Invoke when Dhiraj says "design loop", "iterate on designs", "what has Colleague-V designed", "prototype this screen", "cut the design dependency", or /jove-design-loop.
---

> **Project root:** every relative path in this skill (`knowledge/...`, `tools/...`, `.claude/skills/...`) resolves against `~/dev/jove-hq`, never the current working directory. This skill is invocable from any cwd, so prefix accordingly: `~/dev/jove-hq/knowledge/jove-labs/STATUS.md`.

# JoVE design loop (See → Spec → Build → Ship)

Purpose: dev should never be idle waiting on a Figma frame that doesn't exist yet, and Colleague-V should never face a blank canvas. This skill turns Colleague-V's own Figma exports into a designed-vs-owed ledger, then builds clickable strawmen for the owed items on the JoVE Design System so the dev lead/Colleague-S/Colleague-P can start today. Colleague-V keeps full visual authority — the loop removes the *specification* dependency, not the *design* one. Crossing that line reads as "Dhiraj now ships his own designs" and burns the relationship and the CEO's "less is more" bar; every prototype this skill produces is a strawman with an explicit right-of-refusal, never a finished screen.

## Gate (run first)

1. Read `~/.claude/jove-watchdog/jove-design-loop-cache.md` (this skill's own cache). It holds the last CSS-export fingerprint, the last frame-index build, and which JVA tickets already have a prototype attached. Never re-diff or re-catalogue what it already covers; only process what changed.
2. On-demand only, same as jove-labs-sweep. Never scheduled, never run unprompted.
3. There is no Figma Dev-seat dependency for this skill. A View seat hits the Figma MCP's tool-call rate limit almost immediately (confirmed 14 Jul 2026) — don't route through `mcp__figma__*` live reads for this loop. Everything here runs off the exports Dhiraj drags out of Figma's File > Export, which need no seat upgrade and no credential of any kind.

## Station 1 — SEE (build the designed-vs-owed ledger)

Ask Dhiraj to re-export from Figma whenever he says Colleague-V has pushed something: File > Export the CSS (produces a `revamp css` file) and File > Export selected frames as PNG (produces a `Figma PNGs/` folder), both usually landing in `~/Downloads`. The `.fig` file itself is a dead end for reading — it's Figma's binary format, only useful for dragging straight into Claude Design (see Station 3).

1. **Cheap pass — CSS layer diff.** `comm -13` the new export's layer-name comments (`grep -oE "/\* [A-Za-z][^*]{2,70} \*/"`) against `knowledge/jove-labs/figma-revamp.css`. New layer names are what Colleague-V drew since the last export; this alone answers "what's new" in seconds, no image reading needed.
2. **Deep pass — visual catalogue.** If a full re-catalogue is warranted (first run, or the CSS diff shows many new layers), dispatch parallel Agent-tool batches over the PNG folder, ~20-35 images per batch, ALL dispatched in the same turn — not one at a time. Each batch agent maps filename → screen → role → state and returns a compact table, never a transcript. This is not a style preference: cataloguing 182 frames serially in one agent would need ~700k+ tokens and 30+ minutes; split into 6 batches of ~30 it finished in under 10 minutes wall-clock, each batch comfortably inside ~150k tokens (measured 14 Jul 2026). Merge the batch tables into `knowledge/jove-labs/figma-frame-index.md`.
3. **Reconcile against product truth.** Join the layer/frame findings against the design-requirements sheet (`1yg4aHI_MTb_PB0AobTTcip3miLzTgKrhw_FUtoWr73Q`, tab "Design requirements") and the JVA tickets each row points at. Produce three buckets: designed (frame exists, matches locked AC), owed (no frame found), stale (a frame exists but contradicts a newer lock — flag, don't silently trust the older screen).
4. Refresh the vault mirrors so the next session starts from current truth: `cp` the new CSS export over `knowledge/jove-labs/figma-revamp.css` and the PNG folder into `knowledge/jove-labs/figma-frames/`. Both are gitignored (CLAUDE.md rule 8 — large binaries stay on-disk evidence, never pushed); `figma-frame-index.md` is plain markdown and does get committed.

Known owed items as of 14 Jul 2026 (seed data — re-verify before trusting, this list ages fast): no lab settings/pass-mark screen (JVA-29997), no trial-ended/request-access state (JVA-29992), no removed-trainee stop page (JVA-29983), no invite-accept landing page anywhere, progress export has a button but no exported-file mockup (JVA-29978).

## Station 2 — SPEC (hard gate before any prototype)

Do not build a prototype for a ticket unless both are already true on the ticket:
- Final copy is posted (headline/body/button text, not a placeholder).
- The AC is unambiguous about states and edge cases.

If either is missing, stop and write the PM spec first — that's normal PM work, not part of this loop. A prototype built ahead of the spec just produces a second thing to revise.

## Station 3 — BUILD (Claude Design mechanics)

Open claude.ai/design, and set up each prototype run exactly like this:

- **Attach**: the current `.fig` file (drag it in fresh each session — Claude Design reads it directly, which is why the Figma MCP seat limit in Station 1 doesn't matter here).
- **Design system**: the "JoVE Design System" project — already stocked with ~120 real Labs components (`ModuleCard`, `StatusTagsTrainee`, `ProgressStripe`, `Alert`, `Lock`, `Input`, `Select`, `Table`, `ModalActions`, etc.). Never let it default to a generic system.
- **Template**: Prototype (not Slides/Document/Wireframe/Animation).
- **`</>` codebase context → Local codebase → Attach**: point at `~/dev/jove-code/jove.com-ui/src/features/JoveLabs` specifically, not the whole monorepo — small (~1MB), fast to read, and it's exactly the Labs frontend so Claude Design matches real routing/styling patterns. Skip "Connect GitHub" entirely: JoVE's code lives on GitLab, and there is no GitLab-PAT field in this dialog at all (checked 14 Jul 2026) — local attach is both the only option and the credential-free one, so there is nothing to type in and nothing to authorize.
- **Model**: default is fine; escalate to Opus only if a screen's state logic gets genuinely gnarly (e.g. the pass-mark recompute across every trainee).

Write the prompt from the ticket's own copy and AC, verbatim where possible — don't paraphrase locked copy. `knowledge/jove-labs/design-loop-prompts.md` holds the reusable template plus every prompt actually used, growing over time; read it before writing a new prompt so the voice/structure stays consistent, and append the new prompt after using it.

## Station 4 — SHIP (attach, notify, never overstep)

1. Attach the prototype link as a comment on the JVA ticket, explicitly labelled a strawman: dev can start from it today, Colleague-V's Figma link (once it lands) is what design QA signs off on.
2. Notify the dev lead/Colleague-S/Colleague-P via a **staged Slack draft**, never a direct send (standing rule, no exception here) — the message says what's unblocked and where the prototype code lives.
3. **Always** send Colleague-V the same link, framed as "a clickable strawman so dev isn't idle — you own the visual, bin it if you want." Never skip this step and never let a prototype reach a dev ticket without it going to Colleague-V in the same breath. This is the guardrail that keeps the loop from reading as bypassing him.
4. Once a screen is approved (by Colleague-V or by dev picking it up as-is), use `/design-sync` to write the finished component code back into the `JoVE Design System` project in this repo, so the dev lead/Colleague-S are lifting real JSX from the local design system, not re-deriving it from a picture.

## Output

- `knowledge/jove-labs/figma-frame-index.md` — the designed-vs-owed ledger (rebuilt idempotently, Station 1).
- `knowledge/jove-labs/design-loop-prompts.md` — the prompt library (grows, Station 3).
- Design-requirements sheet — Figma-link column filled in as frames are confirmed designed; "Current state" column corrected against the ledger.
- STATUS.md machine block — note what's newly designed vs still owed, same idempotent-merge rule as the other jove-* sweeps.
- JVA ticket comments — prototype links (Station 4).

## Write-back (always)

Rewrite `~/.claude/jove-watchdog/jove-design-loop-cache.md`: last CSS-export fingerprint, last frame-index build date, which JVA tickets have a prototype attached and its link, still-owed list carried forward.

## Composition

Reuses `.claude/skills/_shared/jove-connectors.md` and the standing Slack-draft-only rule. Any Jira comment this skill posts follows the no-eng-internals rule (current-state + outcome, never implementation prescription) — a prototype link is product context, not an engineering directive. Distinct from `jove-labs-sweep` (that's full state reconstruction across every surface); this skill is narrowly the design-to-dev pipeline and should be invoked on top of a sweep, not instead of one.
