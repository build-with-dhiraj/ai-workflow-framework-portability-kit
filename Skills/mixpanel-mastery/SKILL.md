---
name: mixpanel-mastery
description: Deep, tool-verified Mixpanel expertise for the JoVE org, covering how to actually build and audit dashboards, funnels, Insights queries, and tracking plans through the Mixpanel MCP (Get-Business-Context, Run-Query, Create-Dashboard, Create-Metric, Get-Events, Get-Report, etc). Every claim here was checked against the live MCP, not asserted from docs, and it exists specifically because docs and the live tool schemas disagree in several places that produce a confidently wrong dashboard. ALWAYS use this skill whenever the user mentions Mixpanel, a dashboard, a funnel, a tracking plan, an activation or completion metric, Insights, cohorts, JVA-30536, the JoVE Labs analytics, or asks to build, audit, fix, or debug anything analytics-related for JoVE, even if they don't say "Mixpanel" by name. Load it before writing a single Run-Query call.
---

> **Project root:** every relative path in this skill (`knowledge/...`, `tools/...`, `.claude/skills/...`) resolves against `~/dev/jove-hq`, never the current working directory. This skill is invocable from any cwd, so prefix accordingly: `~/dev/jove-hq/knowledge/jove-labs/STATUS.md`.

# Mixpanel mastery

Full evidence trail: `knowledge/jove-labs/mixpanel-mastery.md` in jove-hq (1,481 lines; schema claims re-verified live 7 Sep 2026). This skill is the operational distillation of that document. When the two disagree, the mastery doc is the source of truth, update this skill from it, not the other way round.

## Before any tool call

1. Call `Get-Business-Context` first, every session, before any other Mixpanel tool. It resolves project nicknames and org vocabulary you can't infer from tool names.
2. **Know which project you're in.** Production is `2857603` ("www.jove.com - LIVE"). The dev/preview project, where PREVIEW-LYHRM and any pre-launch testing lands, is `2875597` ("New Website - Dev team (new)"). Stage and QA have their own separate projects. A wrong project pick returns confidently empty results, it doesn't error.
3. **The one construct everything else hangs on:** counting something across two different people (a lab touched by a trainer, then by a trainee) is
   ```json
   {"type": "aggregate-property", "math": "unique_values", "propertyName": "lab_id"}
   ```
   inside an Insights `Run-Query`. The UI calls this "Distinct Count of lab_id". It is not a funnel, not Hold Property Constant, and not a saved Metric: `Create-Metric`'s `math` enum is `unique | total | session | dau | wau | mau` and has no `aggregate-property` option at all (re-verified live 7 Sep 2026), so this measurement can never be centralized, it must be repeated in every report that needs it.

## The eleven traps, read every one before building or reviewing a tile

Ordered by how likely each is to ship unnoticed. Full detail and live evidence for each is in `references/traps-detail.md`.

1. **Building a cross-user tile as a funnel.** Two different actors in one funnel returns a near-zero number, and it doesn't error. Check: read the two events, name who fires each. Different people means no funnel, use Distinct Count instead.
2. **Reaching for Hold Property Constant to "fix" trap 1.** It requires *one user* to carry the value through every step, it narrows the funnel, it doesn't re-key it across users. Legitimate only when every step really is the same person in one session.
3. **Summing distinct counts.** Not additive across breakdown segments (live proof: 4,552 unbroken vs 4,556 broken-down, a lab in two buckets counts in both) and not additive across time on line charts either. Headline totals come from their own unbroken `metric`/`bar` tile, never from summing a column or a line.
4. **Right-censoring a rolling-window denominator.** A relative "last 30 days" window on a "did X happen within 7 days" tile counts things too young to possibly qualify, understating the rate worst exactly when growth is fastest. The window must end at least N days in the past, and say why on the board.
5. **Shipping a formula tile with no denominator.** A formula call in `Run-Query` suppresses its input metrics entirely, verified live, so a 98.9% over n=4,552 and a 98.9% over n=3 render identically. Every formula tile needs a companion tile showing its denominator.
6. **Sending a number as a string.** A numeric-filter-driving property (`days_since_lab_created` etc.) arriving as `"3"` instead of `3` is silently excluded from numeric filters, no error anywhere, and Mixpanel infers type with no schema declaration and no documented retroactive fix. Assert the JSON type at the source.
7. **Trusting an institution/property breakdown at face value.** Missing values arrive in at least 3-5 disguises simultaneously (`""`, `"undefined"`, `"-"`, absent, null, all rendering `(not set)`), and values are case-sensitive with zero folding (`"jove"` and `"JoVE"` are different buckets). One canonical missing representation, one canonical casing, both enforced server-side, plus a coverage companion tile.
8. **Assuming super properties reach server-emitted events.** Super properties are a client-SDK-only concept with no server-side equivalent, documented explicitly. A server event not stamped with the property by hand is simply undefined for it, which looks like an adoption problem rather than a tracking bug.
9. **Reading today's number.** Late-arriving data means today's figure for today's date range is always provisional and always low; caching adds up to an hour of staleness on top. Every tile's window ends yesterday.
10. **Omitting or reusing `$insert_id` on server events.** Without it, ingestion succeeds but dedup never applies, so every retry double-counts permanently. Reusing a business key (e.g. `lab_id`) as the insert id silently deletes legitimate repeat events instead.
11. **Assuming a never-fired event renders as a zero.** It does not render at all. A `Run-Query` naming only never-fired events returns an empty result, and in a **mixed** tile the missing metric is dropped in silence: a three-metric tile whose middle event has never fired comes back with A and C, no row and no gap where B belongs. A table captioned "AC7 usage events" then reads as a short list and nobody can tell a missing row from an unbuilt tile. **The only honest way to state that an event never fired is a text card.** Verified live 7 Sep 2026 on project 2875597.

## Building a dashboard, the actual mechanics

1. `Run-Query` once per tile, `skip_results: true` for every call you intend to chain (the tool description: "Only use skip_results=true when building a dashboard or you won't use the results"). Collect each `query_id`.
2. One `Create-Dashboard` call, assembling those `query_id`s into `rows` (max 4 cells per row, max 30 rows), `text` cards (max 2000 chars, a small allowed-tag set) as section headers between groups of tiles.
3. Order matters beyond looks: **a board subscription (email/Slack, daily/weekly/monthly) only carries the top 8 reports.** Put the most important tiles first.
4. **You cannot read a report's query definition back.** `Get-Report` returns metadata and a URL, never the query (verified on two report types). This means:
   - Never assume you can "clone" an existing board's tile by inspecting it through the MCP, you can't. Author from a written spec.
   - The written tile spec (see `jove-labs-mixpanel`'s `references/tile-spec.md` for JoVE Labs specifically) is the only durable record of what a tile means. Keep it current when a tile changes, in the same edit, not as a follow-up.
   - Deleting a board deletes its linked reports. There is no separate undo.
5. For edits to an existing dashboard, `Update-Dashboard` needs the real row/cell ids from `Get-Dashboard(include_layout: true)` first; new rows/cells use temp string ids like `"temp-row-1"`.

### Board mechanics that break the board rather than the number

- **Operation ordering on an update:** metadata, then cell creates, then `rows_order`, then cell updates, then cell deletes, then row deletes. Wrong order fails partway.
- **A cell changing type (report to text, or back) is a cross-type change** and needs delete-then-create. The API rejects a `content_type` change on an update action.
- **The field named `markdown` accepts HTML only.** Markdown syntax renders as literal text. Allowed tags: `a, blockquote, br, code, em, h1, h2, h3, hr, li, mark, ol, p, s, strong, u, ul`. `mark` is the only highlight primitive. Strip newlines before sending; they mangle the editor's content.
- **Character limits:** title 255, description 400, text card 2,000.
- **Cells per row is the only size control.** There is no width, height, colour or theme field: one cell is full width, four is quarter width.
- **A new or duplicated dashboard is invisible to the team until it is pinned.**
- **`add_report_to_dashboard` clones**, creating a "Duplicate of..." copy. Put reports in `rows` at create time instead.
- **Adding an existing report to a board always creates a linked copy, and deleting a board deletes its saved and linked reports.** So never share one report between two boards, and take a `Duplicate-Dashboard` backup before restructuring anything. There is no undo.
- Rate limits: 60 queries/hour, 5 concurrent.

## Report-type cheat sheet

| Need | Use | Not |
|---|---|---|
| Count distinct `lab_id` / any entity across different users | Insights, `aggregate-property` / `unique_values` | Funnels, Retention (both are user-keyed, no exception) |
| One user's steps in one session (e.g. the lab-creation flow) | Funnels | fine as-is |
| Exclusion steps, any-order steps, hold-property-constant, cohort filters | UI only | Not in the `Run-Query` schema for any report type, verified |
| A percentage/ratio | Insights formula (`+ - * /` and parens only, no functions, no conditionals) | Custom property `display_formula` is a different, richer language for row-level property values, not for combining metric results |
| Reusable saved metric | Not really available | `Create-Metric`'s `math` enum is the six basic maths (`unique`, `total`, `session`, `dau`, `wau`, `mau`), no `aggregate-property`, so the core Distinct Count construct can't be saved as a Metric |

Full schema detail (filters, breakdowns, date ranges, chart types, what's absent from each schema) is in `references/query-schemas.md`.

## JoVE Labs specifics live in a different skill

**This skill holds no JoVE Labs project facts.** Event names, property names, project and board ids, ticket state and the tile spec rot on a different clock from Mixpanel's schemas, and mixing them is why a property name that exists in no repo survived in here for five weeks.

Load **`jove-labs-mixpanel`** for any Labs work. It owns the fired and never-fired event inventory, the real property names, the board ids and the tile spec, and it regenerates them rather than trusting what is typed.

The one structural fact worth repeating here, because it is a Mixpanel fact rather than a Labs fact: when two identifiers describe an attempt and an entity and only one event carries both, **no report can join them at query time.** Any tile spanning the two worlds is two numbers related by hand.

## Governance, ingestion, and plan-tier gotchas

Identity merge (Simplified vs Original, and mixing the two is a silent no-op not an error), Lexicon hide-vs-block semantics, the CSV tracking-plan-template-is-not-the-import-format trap, timezone effects on every "day" boundary, and which features are Enterprise-only and unverified for this org, are in `references/governance-and-ingestion.md`. Check this before promising a client any feature that sounds like it needs a paid tier (Verified Data, saved formulas, Group Analytics, Data Views).

## Where docs and the live MCP disagree

Full table in `references/docs-vs-mcp-disagreements.md`. The rule in every case: **the live tool schema and a direct test win over docs prose.** If you're about to state a Mixpanel capability from memory or from a docs page, check this table first, several plausible-sounding things (funnel exclusion steps, retention criteria, reading back a saved report) are documented in detail and simply absent from what the MCP actually exposes.
