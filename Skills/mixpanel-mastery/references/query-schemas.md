# Run-Query schema contracts, verified against the live tool definitions

Call `Get-Query-Schema(report_type: ...)` to get the exact live schema before building anything nonstandard; this file records what it returned as of 29 Jul 2026 and should not be treated as a permanent substitute for that call.

## Insights (`report_type: "insights"`)

`required` for the whole report: only `metrics` and `name`. Everything else defaults.

### Measurement types (discriminated union on `type`)

- **`basic`**, `math` one of `unique` (default, "count of users who did the event") | `total` ("count of event occurrences") | `session` ("count of sessions containing the event") | `dau`/`wau`/`mau`.
- **`aggregate-property`**, `math` one of `unique_values` | `total` | `average` | `median` | `p25` | `p75` | `p90` | `p99` | `min` | `max`. Requires `propertyName`. `unique_values` is **the core construct**: "count of distinct values" of a property across all instances of the event. UI label: "Distinct Count of `<property>`". Works on string properties (proven live on `video id`), the docs wording deliberately omits the "numeric property" qualifier that the other aggregate-property maths carry.
- **`frequency-per-user`**, `math` one of `histogram` | `average` | `median` | `p25` | `p75` | `p90` | `min` | `max`. "Statistic over the per-user event count."
- **`aggregate-property-per-user`**: two-stage, `mathPerUser` then `math` across users. **Trap:** aggregates per user first, so two users touching the same entity produce two contributions. Never use this for lab-level counts, use plain `aggregate-property` instead.

### Formulas

`{label, value}`. `value` uses only `+ - / *`, parentheses, and numeric constants. **No functions, no conditionals, no date arithmetic.** Metrics are referenced positionally by letter (A = first metric in the array, B = second, ...), so **reordering the metrics array silently rewires every formula.** A formula can freely mix measurement types (verified: `aggregate-property/unique_values` divided by `basic/total` computed without complaint). Percentage needs an explicit `* 100`, there's no percent-format flag.

### Filters

Seven types: `string` (equals/contains/does not equal/does not contain, or is-set/is-not-set), `number` (is at least/is equal to/is not equal to/is greater than/is less than/is at most), `number_array` (is between, array value), `boolean` (true/false), `datetime` (was on/was before/was since), `list-of-objects` (nested `listItemFilters` + quantifier/inclusion). Every filter carries `resource: event` (default) or `user`. Two scopes: report-level `filters` (all metrics) and per-metric `filters` (that metric only) — a ratio tile whose numerator and denominator differ by one condition is two metrics with different per-metric filters, then a formula.

### Breakdowns

`{metric, buckets?, useAsBaseSegment?}`. Breakdown `metric` is one of four: `property` (event or user property, `propertyType` string/number/boolean/datetime/list), `list-of-objects`, `frequency-per-user`, `aggregate-property-per-user`. Multiple breakdowns are ordered ("must be specified in the order they should be applied"). `buckets` is `NumericBucketConfiguration` (min/max/size/intervals) or `CustomGroupConfiguration` (exact-match groups, `equals` only in Insights). For a strict "<= N days" cut, prefer a `number` filter `is at most N` over bucketing, it's exact and simpler.

### Chart types and the counting trap

`bar` (default) | `stacked-bar` | `line` | `stacked-line` | `pie` | `table` | `metric`. Schema itself warns: `bar`/`metric` give "a single deduplicated count across the full date range"; `line` gives per-period values and explicitly says **do not sum rows to get a total, unique counts are not additive across time periods.** `unit` (hour/day/week/month) required when chartType is line/stacked-line. Every headline number tile: `metric` or `bar`. Every trend tile: `line` with explicit `unit`, never summed.

### Date ranges

`RelativeDateRange`: preset `today`/`yesterday`, or `{unit: day|week|month, value: int}` (quarters/years must be converted to 3/12 months, the schema only accepts these three units). `AbsoluteDateRange`: `{from, to, type: "absolute"}` — **send both `from` and `to`**, the schema's `required` array lists both even though the description implies start-only is allowed. `timeComparison`: relative (previous day/week/month/quarter/year) or absolute-start/absolute-end.

### What's absent from Insights entirely

No sampling control, no percent/currency formatting, no sort/limit on breakdown values, **no cohort field anywhere** (cohorts can't be reached through `Run-Query` at all, despite being readable via `List-Cohorts`/`Get-Cohort`).

## Funnels (`report_type: "funnels"`)

`required`: `metrics`, `name`.

- `metrics`: `minItems: 2`, each step is `{eventName, filters[]}` only.
- `conversionTime`: `{unit: second|minute|hour|day|week|month, value}` or `{unit: "session"}`. **Default is 7 days if omitted** — never omit it on a tile whose meaning depends on the window (a 5-minute flow should not inherit a 7-day window).
- `countType`, default `unique`: `unique` (one entry per user in the window) | `total` (user can re-enter after conversion/timeout/exclusion) | `session`. **For a per-attempt creation funnel, use `total`**, `unique` hides repeat attempts.
- `chartType`, default `steps`: `steps` (drop-off between steps) | `trends` (conversion over time) | `ttc` (time-to-convert distribution) | `frequency` (times a step repeats before converting/dropping).
- `breakdowns`: only `PropertyBreakdown`, narrower than Insights' four kinds.
- `CustomGroupOperator` here allows `contains` **and** `equals` (Insights restricts the same-named object to `equals` only — don't assume grouping behavior carries across report types).

### What's completely absent from the Funnels schema, despite existing in the UI

1. **No exclusion steps** ("did not do X between step 2 and 3").
2. **No step-order control** (Specific Order vs Any Order).
3. **No Hold Property Constant.** This is the decisive one, since it's the standard UI way to make a funnel follow one entity rather than one user, and it simply isn't reachable through `Run-Query`.
4. **No counting unit besides user/session** — no group key, no custom entity. Cross-user funnels need Group Analytics (a paid add-on, see governance-and-ingestion.md), full stop.

**Conclusion:** a Mixpanel funnel through the MCP is always counted per user or session. It cannot follow an entity like `lab_id` across a trainer and a trainee — this is a schema-level impossibility, not a preference. If a tile genuinely needs exclusion/ordering/hold-constant, it must be built by hand in the UI; note that per-tile rather than discovering it mid-build.

## Retention (`report_type: "retention"`)

`required`: `metrics` (exactly 2: `{eventName, filters}` for initial action and return action), `name`. `chartType` default `curve` (per-cohort curve) or `trend` (rate over time). `retentionUnit` default `day` | `week` | `month`.

### What's absent

No retention-criteria control (UI has On / On or After / On or Before, custom brackets like "Days 1-3"; the schema exposes none of it, so an MCP-built retention report silently gets the unbounded "On or After" default). No period-count control, no birth-window control. Day retention capped at 60 days (docs). **It does support** `filters`, `breakdowns` (with buckets and `useAsBaseSegment`) and `timeComparison`, same shapes as Insights, so a retention report is filterable and segmentable even though its criteria are not settable.

**Retention counts users, not any other entity**, same limitation as Funnels. It's the wrong tool for "lab created by trainer, first started by a different trainee within 7 days" for the identical reason Funnels is wrong. It's the right tool for genuinely same-user questions (e.g. trainee stickiness across weeks), which isn't one of the JoVE Labs tiles today.

## Cross-schema notes worth keeping

- Insights `line`/Funnels line-chart both warn: a line view runs a separate calculation per period, so an entity present in two periods is counted in both. Table/bar/metric views run the calc once across the whole range. **These will never tie out with each other, by design.**
- `Run-Query` does not persist anything, verified by comparing `report_url`s: a `Run-Query` result is `view/<id>#<opaque-hash>` (different hash every call); a genuinely saved report from `Get-Report` is `#report/<numeric-bookmark-id>`. Safe to probe freely.
- Result caching: 1 hour for sub-day query spans, up to ~14 days for year-plus spans. A tile checked the same day it's built may serve a stale cached result, manual refresh exists at report/board/card level.
- Query API rate limit: 60 queries/hour, 5 concurrent (separate from the MCP's own 600 requests/hour/user).
