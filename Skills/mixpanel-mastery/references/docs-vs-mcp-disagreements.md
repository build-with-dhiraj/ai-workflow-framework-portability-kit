# Where docs and the live MCP disagree

Source: `knowledge/jove-labs/mixpanel-mastery.md` section 16. Rule in every row: **the live tool schema plus a direct test wins over docs prose.** Re-verify with `Get-Query-Schema` / a probe `Run-Query` before relying on any of these if enough time has passed that Mixpanel may have shipped a schema change.

| Topic | Docs say | Live MCP does | Verdict |
|---|---|---|---|
| Funnel exclusion steps, step ordering, hold-property-constant | All exist, documented in detail | **Absent from the funnels schema entirely** | MCP wins. UI-only; any tile needing them isn't machine-buildable. |
| Retention criteria (On / On or After / On or Before), custom brackets | All documented | **Absent from the retention schema** — only `retentionUnit` and `chartType` exist | MCP wins. An MCP-built retention report silently gets the unbounded default. |
| Reading a saved report's definition | Implied by the existence of saved reports | `Get-Report` returns metadata + URL, **never the query** (verified on two report types) | MCP wins. A written spec is the only durable record of a tile's intent. |
| Creating a board via API | No public REST endpoint exists, and no explicit denial either | `Create-Dashboard` is GA and fully specified | MCP wins, and is the only supported programmatic path. |
| Saved metrics as a KPI-reuse mechanism | Presented as the way to save/reuse a metric | `Create-Metric`'s `math` enum is `unique | total | session | dau | wau | mau`, no `aggregate-property` — the core Distinct Count construct can't be saved | MCP wins. No reuse mechanism exists for this measurement. |
| Lexicon "Drop" vs "Block" naming | Docs say Block was renamed from Drop | MCP still exposes a `dropped` parameter/field, `"dropped": false` | MCP wins on vocabulary; cosmetic but will confuse cross-reading. |
| `AbsoluteDateRange` start-only | Description implies start-only is allowed | Schema `required` lists `from`, `to`, and `type` all as required | MCP wins. Send both dates. |
| `CustomGroupOperator` | Presented as one concept | `equals` only in Insights; `contains` **and** `equals` in Funnels — same object name, different behavior by report type | MCP wins. Don't assume grouping behavior carries across report types. |
| Formulas with breakdowns; formulas mixing aggregation types | **Not documented either way** | Both verified working live by direct test | Live test closes two real docs gaps. |
| Cohorts usable in queries | Documented as usable as a filter/breakdown | **No cohort field in any of the four report schemas** (Insights/Funnels/Retention/Flows-adjacent) | MCP wins. Cohort-based tiles are UI-only, despite cohorts being readable via `List-Cohorts`. |
| Funnel conversion window maximum | 366 days (UI docs) vs 90 days (Query API reference) | Not constrained in the MCP schema itself | Docs contradict docs. Immaterial unless a tile ever needs >30 days. |
| Data Views plan-tier gate | Growth+ (feature page) vs Enterprise (pricing page) | Not independently observable | Unresolved — ask before relying on it for anything. |

## Also worth carrying (not in the section-16 table but load-bearing)

- **`developer.mixpanel.com` now 301-redirects** to `docs.mixpanel.com/reference/*`; old `/docs/reports/apps/*` paths 404. Any bookmark/runbook pointing at the old paths is stale but may still silently resolve somewhere.
- **No public REST API for Boards, Dashboards, or Reports exists at all** — confirmed by enumerating the full reference index (only Ingestion, Query, Raw Data Export, Data Pipelines, Lexicon Schemas, GDPR, Warehouse Connectors, Feature Flags are real API families). The MCP's `Create-Dashboard`/`Update-Dashboard` are the only programmatic path, not a wrapper over a public REST endpoint that could be called directly.
- **`/api/query/insights` (the plain REST Query API) can only run an already-saved report** via `bookmark_id` — there's no REST way to POST an ad-hoc Insights definition. The MCP's `Run-Query` accepting an inline spec is a genuine MCP-only capability, not something replicable via direct API calls.
- **Whether `Distinct Count` is exact or approximate (e.g. HyperLogLog-style) is undocumented anywhere.** Weak live evidence points toward exact (a 4-count discrepancy between an unbroken and broken-down query was fully explained by segment overlap, not estimator noise), but treat as genuinely unresolved. Immaterial at JoVE Labs launch volumes (tens to hundreds of labs); would matter at millions.
