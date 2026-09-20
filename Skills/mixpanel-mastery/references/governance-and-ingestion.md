# Governance, ingestion, and plan-tier gotchas

Source: `knowledge/jove-labs/mixpanel-mastery.md` sections 10.5-11.10, docs-sourced and cross-checked live where possible.

## Service accounts (the headless-auth mechanism)

- Auth is HTTP Basic, `username:secret`. Query API calls also need `project_id` as a parameter.
- **No expiry by default** — optional ISO-8601 `expires` at creation if you want one. The secret is shown once at creation and is not recoverable after.
- Roles: `owner`, `admin`, `analyst`, `consumer`.
- Created **per project**, from that project's own Project Settings → Service Accounts (not an org-wide list you search by name — each project gets its own newly-created account). A project Admin can self-serve this; org-scoped creation needs org admin/owner.
- Project Secret auth (the older mechanism) is deprecated with a hard retirement date of **March 3, 2027**.
- MCP rate limit: 600 requests/hour/user. Query API: 60 queries/hour, 5 concurrent.

## Lexicon: hide vs block, and neither is retroactive

| | Hide | Block (formerly "Drop") |
|---|---|---|
| Who | Admin or Owner | **Owner only** |
| Ingestion | Still ingests, still counts toward data allowance | Prevents new data from being stored going forward |
| Retroactive | No | **No** — previously-ingested events of that type still show |
| Reversible | Yes | **No** — "cannot recover event data after you block it" |

The MCP's `Get-Events` tool still uses the old vocabulary (`dropped` parameter, `"dropped": false` in responses) even though docs say Block was renamed from Drop. Minor, but confusing when cross-reading old runbooks against the live tool.

Retroactive deletion is a separate feature, **Data Deletion**: last 180 days only, irreversible 7 days after submitting, up to 30 days to purge, capped at 10 deletions/month.

**Merging duplicate events is Owner-only and dangerous:** "After you merge an event into another, it no longer appears in reports or custom events that reference it." Silently breaks any saved report built on the absorbed event name.

## Lexicon CSV import is not the tracking-plan template

Mixpanel's own tracking-plan template spreadsheets (the shape JVA-30536's sheet uses) are **not** the Lexicon CSV import format. There's no documented one-click path from one to the other. Loading a tracking plan into Lexicon is a transformation job (export Lexicon's own CSV, map the plan's rows into that shape, re-import), not a straight upload. Overwrite semantics are also a real hazard: importing can silently flip `hidden`/`blocked`/`sensitive` flags if those columns in the sheet are stale relative to what's live. **Safe procedure: export first, edit the exported file in place, re-import. Never hand-build the CSV.**

## Super properties don't exist server-side

Docs, verbatim: super properties are "mostly applicable to our client-side libraries" — device-local persistence via `register()`. **No server-side equivalent, none documented.** Directly relevant to any "browser vs service" instrumentation decision: whichever side is chosen, choose one side consistently per event, and if server-side, every super property must be explicitly stamped in the payload since nothing does it automatically. See trap 8 in `traps-detail.md`.

## `$insert_id` and the myth of a "dedup window"

Format: max 36 bytes, alphanumeric + hyphens only. There's no dedup window measured in days — the actual mechanism is a timestamp-match rule:
- Same `$insert_id` + same `time`: deduped immediately, query-time.
- Same `$insert_id`, different `time`, same calendar day: not deduped until backend compaction (hours to ~20 days later) — double-counted in the interim.
- Same `$insert_id`, different calendar day: **never deduped, both count forever.**

Omitting `$insert_id` on a server event means it still ingests but never qualifies for dedup at all. Reusing a business key as the insert id causes unintended deletion of legitimate repeats. Dedup is never applied to raw data exports — a Redash/warehouse mirror will diverge from the Mixpanel UI unless dedup is reimplemented downstream. See trap 10.

## Identity management

Mixpanel's actual vocabulary is "Simplified ID Merge" and "Original ID Merge" (docs don't use version numbers; "ID Merge API v3" isn't Mixpanel language).

- **Simplified (recommended):** `$device_id` (anonymous, SDK-generated) + `$user_id` (set via `.identify()`). First co-occurrence creates a merge; retroactively applies `$user_id` to prior `$device_id` events, so pre-login history is recovered.
- **Original (legacy):** `$identify`/`$create_alias`/`$merge`, hard cap 500 IDs/cluster, `.alias()` does **not** retroactively connect past events, canonical `distinct_id` chosen by Mixpanel and not configurable, mappings take up to 24h to propagate.
- **Mixing the two is a silent no-op, not an error** — in Simplified, sending `$identify`/`$create_alias`/`$merge` events just gets them ignored, no error, identity silently fails to stitch.
- Migration between the two is not possible in place, requires a new empty project.

**Practical rule for server-side Labs events:** set both `$user_id` and `$device_id`, never set `distinct_id` manually. If server events carry only `$user_id` and never pair with the browser's `$device_id`, the anonymous pre-login stream never joins the identified stream and every acquisition funnel understates conversion. **Which merge system project 2857603 (or 2875597) is actually on has not been independently verified** — check in Project Settings before instrumenting, don't assume from docs (docs give conflicting default-date claims across pages).

## Event time, late arrival, and why today is always wrong

| | `/track` | `/import` |
|---|---|---|
| Auth | Project Token | Project Secret or Service Account |
| Max event age | **5 days** (older events silently not ingested) | back to 1971 |
| Future events | overwritten with ingestion time | rejected if >1 hour future |

A report re-run tomorrow for the same date range will show a higher number than it did today, for late-arriving data reasons, not a bug. See trap 9.

## Property data types (inferred, not declared)

- String is the fallback default type.
- Boolean is **only** the JSON literals `true`/`false` — the strings `"true"`/`"false"` are Strings.
- Date requires ISO `YYYY-MM-DDTHH:MM:SS` UTC; a Unix timestamp is inferred as **Numeric, not Date**.
- Object: max 255 keys, max 3 nesting levels. List: 8KB on events.
- No documented behavior for mixed types across the same property name (first-seen-wins vs most-common-wins is unstated). What's known: numeric operators only apply to values actually inferred as Numeric, a String-typed value silently drops out rather than erroring. See trap 6.

## Group Analytics: why it's being avoided, and the one real cost of avoiding it

Requires all three: a group key defined in Project Settings, **the group key present as an event property on every event to be attributed** (having it only on the user profile does nothing), and group profiles for group-level properties. It's a paid add-on on Growth/Enterprise, price not published, needs a sales conversation. Limits: 3 group keys standard (6 Enterprise), 1M profiles/key.

**The decisive fact: it is not retroactive, and there is no backfill.** "Mixpanel does not backfill historical data to groups before the group key was implemented." Skipping it costs nothing today and is reversible in capability — but not in history: the day it's turned on, group-level analysis starts from zero for everything before that point.

**The hedge that costs nothing:** emit `lab_id` as an ordinary event property on every Labs event from day one (already the plan). This supports breakdowns/filters/Distinct Count without the add-on. If the add-on is ever purchased later, the same property can be registered as a group key going forward, and the raw property still exists for warehouse-side historical reconstruction even though Mixpanel itself won't backfill.

## Plan-tier gates, unverified for this org — ask before promising

| Feature | Free | Growth | Enterprise |
|---|---|---|---|
| Verified Data badge | no | no | **Enterprise only** |
| Event Approval | no | no | **Enterprise only** |
| Data Standards (naming compliance) | no | no | **Enterprise only** |
| Data Views | no | conflicting docs (Growth+ per feature page, Enterprise per pricing page) | yes |
| Data Classification (sensitive properties) | no | no | **Enterprise only** |
| Group Analytics | no | paid add-on | paid add-on |
| Saved formulas | no | yes | yes |
| Globally saved custom properties | no (report-local only) | yes | yes |
| Cohorts saved | no | yes | yes |

**Confirm JoVE's actual plan tier (ask Colleague-Gu or the Director) before promising any of these.** If the plan is Free, there's no reuse mechanism at all for anything (compounds with the `Create-Metric` limitation below), every tile must be fully self-contained.

Data Views specifically: "the results of a report or Board will change depending on the Data View you have selected," while raw API/export access bypasses Data Views entirely. If Data Views are ever introduced, the same board will show different numbers to different people, a classic "why do we see different numbers" incident waiting to happen.

## `Create-Metric` cannot hold the core measurement

`Create-Metric`'s `math` enum is `unique | total | session | dau | wau | mau` — the `basic` measurement set only. **No `aggregate-property`, therefore no `unique_values`.** The Distinct Count construct this entire dashboard is built on can be used inside `Run-Query` and placed on a dashboard tile, but **cannot** be saved as a reusable Metric. Consequence: the same measurement logic must be repeated verbatim in every report that needs it, and since report definitions can't be read back either (see `docs-vs-mcp-disagreements.md`), drift between tiles that should share a denominator is both likely and invisible. The written tile spec (`the jove-labs-mixpanel skill's tile-spec.md`) is the only defense — update it in the same edit whenever a tile's definition changes.
