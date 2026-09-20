# The eleven traps, in full, with live evidence

Source: `knowledge/jove-labs/mixpanel-mastery.md` section 14, verified against project 2857603 live on 29 Jul 2026.

## 1. Building a cross-user tile as a funnel

`Lab Created` then `Lab Module Started` in a Funnels report returns a number, and that number is near zero, because the trainer who created the lab never performs `Lab Module Started`, a trainee does. Nothing errors, it just returns a confident, wrong percentage.

**Guard:** any tile whose two events have different actors is an Insights `Distinct Count of lab_id`, never a Funnel. The check: read the two events and name who fires each. Different people means no funnel.

## 2. Reaching for Hold Property Constant to "fix" trap 1

Verbatim from docs: "Holding a property constant in a funnel requires that a user retain the same value for a given event property for each step to convert." It has the right name, it accepts `lab_id` as the held property, and it produces a plausible-looking number for a different question. It requires **one user** to carry that value through every step, it makes the funnel narrower, not re-keyed across users.

**Guard:** **hold-constant is UI-only and is not reachable through the MCP at all** (re-verified against the live funnels schema 7 Sep 2026). Do not plan a tile around it. The one case it would have served, separating repeat creation attempts by one trainer, is already solved by `countType: "total"` on the creation funnel. Anywhere a tile spans trainer and trainee, it is the wrong tool regardless of surface.

## 3. Summing distinct counts

Live proof: an unbroken query for `Distinct Count of video id` returned **4,552**. The identical query broken down by institution returned a `"total"` of **4,556**, four higher, because a `video id` seen under two institutions is counted once in each bucket. Distinct counts are per-bucket and buckets overlap; summing them double-counts the overlap. The schema separately warns line charts aren't additive across time either (a value present on two days is counted on both).

**Guard:** headline totals come from their own unbroken `metric` or `bar` tile with no breakdown. Never total a breakdown column, never sum a line chart's rows.

## 4. Right-censoring the activation denominator

A relative "last 30 days" window on a "did X happen within 7 days of creation" tile includes labs created 2 days ago in the denominator, which cannot possibly have activated within 7 days yet. This **understates** the rate, and understates it worst exactly when growth (new lab creation) is fastest, since the newest cohort drags the rate down every single day.

**Guard:** the date range must end at least N days in the past (7 for the 7-day tile, 30 for the 30-day tile), built as an `absolute` date range ending at "today minus N", never a relative rolling window. Put a text card on the board explaining why this tile's window lags the others, it will be the first question asked.

## 5. Shipping a formula tile with no denominator

Verified live: sending a report with metrics A and B plus a `formulas` array returns **only the formula result**. A and B themselves are not returned at all, even though they were computed to produce the formula. A ratio of 98.9% computed over a denominator of 4,552 and one computed over a denominator of 3 render as the exact same number on the tile.

**Guard:** every formula tile ships with a companion tile showing its denominator, as a separate card. This is non-negotiable at JoVE Labs launch volumes where every denominator will genuinely be small.

## 6. Sending a number as a string

Mixpanel infers property type from the JSON value with no schema declaration. `days_since_lab_created` sent as the string `"3"` instead of the number `3` is typed String, and numeric filter operators (`is at most`, `is at least`, etc.) silently exclude String-typed values rather than erroring. There is no documented retroactive way to change an established property's type.

**Guard:** assert the JSON type in the server code that emits the event, and check the property's inferred type in Lexicon on day one of real data flowing, not weeks later.

## 7. Trusting an institution (or any string property) breakdown at face value

Live production data on the existing `institution name` property shows missing values in at least three simultaneous disguises: empty string `""` (1,849 of 4,552, the single largest bucket), the literal string `"undefined"` (77), and a hyphen `"-"` (74). Docs add two more: absent and null, both rendering as `(not set)` but being different things underneath (`is set` catches both of these, but none of the three string sentinels). Over 40% of rows had no usable institution value.

Separately, values are case-sensitive with zero folding: `"jove"` (474) and `"JoVE"` (37) are different buckets, and this repeats across at least eight real institution names in the same breakdown (`"college of charleston"` vs `"College of Charleston"`, etc.).

**Guard:** enforce exactly one canonical "missing" representation and one canonical casing, server-side, at send time, this cannot be fixed at query time (the Insights formula language has no string functions, and a custom-property `IFS` chain would need one branch per institution, unmaintainable). Every breakdown-by-string-property tile gets a coverage companion tile ("share of events with this property set").

## 8. Assuming super properties reach server-emitted events

Docs, verbatim: super properties are "mostly applicable to our client-side libraries," persisted via `register()` into a cookie or localStorage on the end user's device. **There is no server-side equivalent and none is documented.** If `user_id` and `user_role` (JVA-30536's super properties) are declared once on the client and never explicitly passed in server-side track calls, every server-emitted event (`Lab Trainee Invited`, `Lab Module Started`, `Lab Module Completed`, and everything added since) is simply undefined for both.

Related and worth internalising: a super property is registered once per session, so it can only ever carry session-scoped context. Anything scoped to an entity rather than a person (a lab, an order, a document) cannot be a super property at all. This is why `owning_institution_id` was moved off Super on 31 Jul 2026: as a super property it would silently report the wrong lab's institution the moment one person touched two labs.

The failure mode is worse than an error: the adoption-by-institution tile shows labs created (client-side, has the property) but zero activity (server-side, missing the property), which reads as a genuine adoption problem rather than the tracking bug it actually is.

**Guard:** the tracking-plan sheet already carries this note correctly ("Server-emitted events do not inherit register, pass both super properties explicitly in the track call"). Verify it survives code review, don't wait to discover it on the dashboard. Note that `owning_institution_id` and `owning_institution_name` are event properties rather than super properties, so they never inherit from register on any surface and must be stamped explicitly on browser-emitted events too.

## 9. Reading today's number

Late-arriving data (offline clients, batched SDKs, retried imports) means a report for "today" is always provisional and always an undercount; it grows retroactively as those events flush. Mixpanel's own internal data-volume monitoring uses a 2-day lookback specifically to compensate for this. Result caching (1 hour for sub-day query spans, up to 12+ hours for wider ones) compounds it, a freshly built tile checked the same day can be wrong in both directions at once.

**Guard:** every tile's date window ends yesterday, never today. Use manual refresh (report/board/card overflow menu) before quoting any number that must be current.

## 10. Omitting or reusing `$insert_id` on server events

Docs, verbatim: "If an event is sent to the Ingestion API without an `$insert_id`, one will be generated for it. However, it will not qualify for the deduplication process." Every retry, every at-least-once queue redelivery, every partial-batch replay then double-counts the event permanently, with no error anywhere.

Reusing a semantic value as the insert id (e.g. setting it to `lab_id` or a user id) is the opposite failure: "can cause unintended deduplication and data loss," i.e. it silently *deletes* legitimate repeat events that happen to share that value.

Deduplication is also never applied to raw data exports, so a Redash mirror or warehouse copy will disagree with the Mixpanel UI unless dedup is reimplemented downstream.

**Guard:** a fresh, unique `$insert_id` per event (max 36 bytes, alphanumeric and hyphens only), generated independently, never derived from a business key.

## 11. Assuming a never-fired event renders as a zero

Verified live on project 2875597, 7 Sep 2026. A `Run-Query` naming only events that have never fired returns `"results":{}` and the card renders empty. Worse, in a **mixed** tile the missing event is dropped with no trace: a three-metric tile of `Lab Created`, `Lab Quiz Passed` and `Module Document Added` returned only A and C, with no row and no gap where B should have been.

Why it matters more than an empty card: a tile captioned "AC7 usage events" renders as a short list of the events that did fire, and a reader has no way to distinguish a missing row from a tile that was never built. The absence, which is the whole finding, becomes invisible.

**Guard:** never express a zero as a tile. Run the lexicon inventory first (`Get-Events`, or an exact-name lookup: Mixpanel omits names that have never landed), and put every never-fired event into a **text card** that names it and names the ticket that would make it fire. A tile is for a number that exists; a text card is for a number that does not.

## Honourable mentions

- Leaving `conversionTime` unset on a Funnel silently inherits the 7-day default, absurd for a flow completed in one sitting.
- Leaving `countType` at its default `unique` on the creation funnel hides every repeat attempt (a trainer who abandoned twice then succeeded reads as one clean conversion). Use `total` for per-attempt funnels.
- Assuming a saved report's configuration can be inspected later through the MCP. It cannot (`Get-Report` never returns the query), which is why a written tile spec is the only durable record.
- Putting a meaning-defining filter on the board instead of the individual report. Board-level filters don't alter the saved report, and opening the report directly (rather than via the board) shows the report's own settings, not the board's. The same report then shows two different numbers depending on how it was opened.
- Forgetting to exclude internal/test traffic (`jove`, `chris test`, `test 123`, `willo labs` all observed live in production institution data). At launch volumes this is not a rounding error, it can be the majority of the data.
- Naming any property `bucket` or `$bucket`, verbatim from docs: it hides the event from the interface entirely. No `$` prefix needed to trigger it, it reads like an ordinary business name.
