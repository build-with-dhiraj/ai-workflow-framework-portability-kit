---
name: etf-reit-onboarding
description: >
  Systematically FIND, GRADE and BUY great ETFs / REITs / InvITs that ride durable global trends —
  evaluating funds LIKE stocks (verdict → conviction → margin-of-safety) and holding the good ones
  for life. The fund mirror of the stock onboarding pipeline. Use when the user says "add an
  ETF/REIT/InvIT", "grade this fund", "build a global-trend buy-list", "passive sleeve", "evaluate
  a fund like a stock", "should I buy <ETF>", "is this trend worth owning", or wants to extend /
  re-rank the global-trend exposure list. Workspace: /Users/pw/invest. Publish target is the
  🌍 Global & Passive Base tab (re-architected per the plan) — the LOCKED Action Dashboard is
  NEVER touched. Charlie Munger & Warren Buffett (the Obsidian vault) are the binding CIO; the
  vault gates trend-durability/conviction/verdict/MoS — it is not narrative decoration.
---

# ETF / REIT / InvIT Onboarding Pipeline (global-trend machinery)

The single source of truth for finding and grading global-trend funds, REITs and InvITs, and publishing
them to the **🌍 Global & Passive Base** tab. Follow the stages in order. This is the **fund mirror** of
[[stock-onboarding-pipeline]]: the SAME board (binding Munger/Buffett CIO · 31 perspectives · 14 canon ·
8 desks · WC) evaluates ETFs/REITs the **same way it evaluates stocks** — verdict → conviction → margin of
safety. The design source of truth is `/Users/pw/.claude/plans/build-a-plan-to-iterative-creek.md`.

The retrieval plumbing is identical to the stock pipeline — all vault consultation goes through
`data/scripts/32_consult_brain.py` (scoped, cited, structured), now carrying the four NEW fund models
`passive-etf | commodity-etf | reit | invit`. ETF/REIT mechanical fund-quality reuses the MF methodology
(`extracted/mf/_mf_methodology.md` + `_mf_rubric.md`); REIT/InvIT dossiers reuse the ALTIUS template
(`vault/research/dossiers/ALTIUS.md`).

## North star
The 🌍 tab is a **forward BUY-LIST of durable global-trend exposures** in search of a small set of
**CORE holds you keep for life** — NOT a one-off cleanup of what's already held, and **not a sprawling
basket of every thematic ETF**. The point is to **buy good ETFs, keep good ETFs, and compound wealth via
durable global megatrends** — the fund-side parallel of the stock FOREVER/COMPOUND hunt. Bogle/Buffett's
default (broad, lowest-cost index held for life) is the anchor; thematic trends are capped satellites you
buy only when the underlying index is at a sane valuation. Finding that a trend is real but **expensive
right now → WATCH, don't buy** is an acceptable, expected result. Patience on the entry is the edge.

## The framework — evaluate ETFs / REITs LIKE stocks
Map the stock machinery's three sort keys onto funds so the board reasons identically:

| Stock key | ETF analog | REIT / InvIT analog |
|---|---|---|
| **Moat** (durable advantage) | **Trend durability** (is the exposure a 10-yr structural tailwind, not a fad?) × **wrapper quality** (lowest TER · tightest tracking error · deepest AUM/liquidity · right structure · best tax bucket) | Asset/lease durability · tenant diversification · sponsor quality · contracted-revenue runway (WALE) |
| **Conviction 1–5** | trend-strength × wrapper-quality (a broad low-cost index defaults HIGH; a narrow thematic ETF needs higher proof to earn the same band) | adapted ALTIUS-style filters — **InvIT/REIT conviction CAP 2** (yield instrument, not a compounder) |
| **Margin of safety** | **index valuation vs its OWN history** (CAPE / PE percentile) — don't pile into an expensive index; wait for the trend at a sane price | **sustainable (return-ON-capital) distribution yield vs the ~9–10% required yield** (ALTIUS method) |

**Verdict tiers (re-cut to mirror the stock 5-tier — so they read the same):**
- **CORE (≈ FOREVER):** the broad, lowest-cost index you hold for life regardless of price (Bogle/Buffett default — broad-world, Nifty-500-style India core). The anchor. This is the only tier where price is not a gate.
- **COMPOUND-TREND (≈ COMPOUND):** a high-conviction *durable* global megatrend (AI/compute · US innovation · India structural growth · energy transition · EM …) via the best India-accessible wrapper, **at a fair index valuation** — buy and hold for years.
- **WATCH:** great trend + great wrapper, but the underlying index is **expensive now** → wait for the entry (the MoS gate is unmet).
- **AVOID:** a **bad wrapper** (high TER / poor structure / bad tax bucket / wide tracking error) **OR** a fad / fading trend.
- **TOO_HARD:** trend durability is genuinely unknowable, **or** there is no clean India-accessible wrapper for it.

**Rank key = verdict → conviction → MoS** (exactly the stock key). Here MoS = how far the index trades below
its own fair/historical value (ETF) or how far the sustainable yield clears required (REIT/InvIT). This is
what lets the board "look at ETFs the same way as stocks." TOO_HARD is quarantined OFF the buy-list.

## HARD RULES (never violate)
1. **The binding CIO is the arbiter.** `data/scripts/32_consult_brain.py --corpus binding` (Munger/Buffett vault)
   gates trend-durability, conviction, verdict and MoS at Stages A/B/C. The new perspectives & canon (Bogle,
   Malkiel/Ellis, Damodaran-REITs, Dalio, Marks) are **down-weighted advisory context** surfaced via
   `--corpus blended` — they SHARPEN the call but **NEVER reverse a `--corpus binding` verdict.**
2. **The vault is BINDING, not decoration.** `cites_principles` may contain ONLY slugs the brain actually
   returns (`principles[].slug` / `citation`). No fabricated citations. If `principles` comes back empty/thin →
   ABSTAIN + flag, never pad. (`29_vault_chat.py` stays available for free-form cited Q&A / ad-hoc grilling.)
3. **Never fabricate** a trend, a TER, a tracking error, an index valuation, a DPU, or a yield. Every number
   is fetched (INDmoney / WebFetch / BSE filing) or it is flagged as unknown. A guessed number is worse than a
   missing one. (See [[feedback-paywall-enumeration-honesty]] / the never-fabricate rule in memory.)
4. **Evaluate funds LIKE stocks** — three sort keys, five verdict tiers, rank = verdict → conviction → MoS.
   A fund is not exempt from the discipline because it is "passive." A narrow thematic ETF must EARN its
   conviction band against trend-durability × wrapper-quality, exactly as a stock earns its moat grade.
5. **Trend durability is the moat, and it is a HARD GATE before price.** Order of analysis:
   is-the-trend-durable → is-the-wrapper-best-in-class → ONLY THEN index valuation. A fad trend, or a great
   trend wrapped in a costly/badly-structured/badly-taxed vehicle, cannot earn high conviction regardless of
   how cheap the index looks.
6. **Conviction = JUDGMENT, not a formula** (Munger: avoid false precision). Gates: fad/fading trend → AVOID;
   no clean wrapper → TOO_HARD; **InvIT/REIT → conviction CAP 2** (a yield instrument cannot be a compounder,
   so its ceiling is WATCH — never COMPOUND-TREND or CORE). A broad lowest-cost index defaults to high
   conviction (low cost IS the durable edge); a narrow thematic needs higher proof for the same band.
7. **Margin of safety is THE gate.** ETF → index valuation vs its own history (CAPE/PE percentile); a durable
   trend at a stretched index → WATCH, not buy. REIT/InvIT → the **sustainable (return-ON-capital) yield vs the
   ~9–10% required yield** (ALTIUS method — strip return-OF-capital out of the headline DPU before judging).
   The ONLY tier exempt from the MoS gate is CORE (Bogle's "buy the haystack, hold for life regardless of price").
8. **For passive ETFs, low cost IS the moat — `moat-analysis` does NOT apply.** Do not run the business-moat
   taxonomy on a passive index fund; its edge is structural (cost + breadth + tracking), graded by the wrapper-quality
   read and the MF cost/overlap gates. `moat-analysis` applies ONLY to the **trend-durability** judgment (Stage A)
   and to REIT asset/tenancy durability — never to "the index fund's moat."
9. **InvIT/REIT = yield instrument, dossier on the ALTIUS template.** Full dossier at
   `vault/research/dossiers/<CODE>.md` (`brain_model: reit` or `invit`): 6-filter walk (Filter 2 = asset +
   contracted tenancy, Filter 3 = distribution coverage + return-OF vs return-ON split, Filter 5 =
   distribution-yield vs required, NOT a growth DCF), FFO/AFFO · LTV · occupancy · WALE, distribution-yield MoS,
   numeric buy-below + trim/sell triggers, kill criteria, 5-tier verdict. Live price via BSE code for InvITs
   (GOOGLEFINANCE NSE will not resolve — see ALTIUS).
10. **NEVER edit the LOCKED Action Dashboard.** The stock dashboard ([[feedback-sheet-is-locked]]) is canonical
    and untouched by this pipeline. ETFs/REITs publish ONLY to the **🌍 Global & Passive Base** tab. Back up the
    🌍 tab before any write; if a helper disagrees with the live tab, FIX THE HELPER, never the sheet.
11. **Sell ₹ + Upside are written for every NON-CORE verdict — never blank them** (mirrors the stock rule).
    WATCH / AVOID / TOO_HARD each carry a numeric Sell/trim target AND an Upside% (honestly negative when the
    price is above fair value). ONLY CORE / COMPOUND-TREND show "∞ hold". For REIT/InvIT the trim target is the
    price at which the yield compresses materially below required (ALTIUS: trim above ~₹185, sell above ~₹200).
12. **5-tier verdict** exactly one per vehicle: CORE / COMPOUND-TREND / WATCH / AVOID / TOO_HARD.

## CONSULTING THE BRAIN (`data/scripts/32_consult_brain.py` — the ONE retrieval entrypoint)
```bash
set -a && source /Users/pw/invest/.env && set +a && /Users/pw/invest/.venv/bin/python \
  /Users/pw/invest/data/scripts/32_consult_brain.py \
  --company "<trend or fund name>" \
  --model <passive-etf|commodity-etf|reit|invit> \
  --step <circle|conviction|intrinsic-value|margin-of-safety|opportunity-cost|verdict|inversion|capital-allocation|sizing> \
  [--corpus <binding|blended>] [--entities <peer-slugs,comma-sep>] [--k 8] \
  --json-out extracted/grilling/<CODE>_<step>.json
```
- **NEW models (Phase 2, the only change to `32_consult_brain.py` — 4 dicts: `MODELS`, `MODEL_PHRASE`, `MOAT_HINT`, `MGMT_HINT`):**
  - `passive-etf` — broad/thematic index funds. MOAT_HINT = trend durability × wrapper quality (cost/tracking/liquidity/structure/tax); MGMT_HINT = tracking discipline + AMC/issuer reliability.
  - `commodity-etf` — gold/silver/commodity wrappers. MOAT_HINT = hedge/diversification role + storage/structure quality; valuation lens = real-asset / cycle, not earnings.
  - `reit` — real-estate trusts (e.g. Embassy). MOAT_HINT = asset + lease durability, tenant diversification, sponsor; MGMT_HINT = sponsor quality + capital allocation (dividend/M&A).
  - `invit` — infra trusts (e.g. ALTIUS/Embassy-style annuities). Same as `reit` but **conviction CAP 2**; MOAT_HINT = contracted-tenancy annuity + WALE; MGMT_HINT = sponsor + leverage discipline.
- **What it does (unchanged):** derives 2-3 model-aware retrieval questions, routes internally (specific model
  or entities → ScopedLanceDBBackend, **0 Azure calls**; `general` + no entities → hybrid + GPT rerank — never
  stacked), RRF-merges + dedupes, hygiene-filters to mentors' atomics/raws + canon/perspectives + `_synthesis`
  (hubs/MOCs/`_system`/dossiers/positions excluded; every path verified on disk). Assets carry `brain_model: <slug>`.
- **How to read the output:** `principles: [{claim, path, slug, citation, mentor, note_type, source_note, …}]`.
  `claim` = the principle to apply; `citation`/`slug` = the ONLY tokens permitted in `cites_principles`;
  `source_note` = traceability to the raw transcript/letter/lecture. Empty `principles` → vault is thin here →
  ABSTAIN + flag, never pad.
- **Corpus discipline:** `--corpus binding` (Munger/Buffett ONLY) for every conviction/verdict/MoS/inversion
  gate — this is the arbiter. `--corpus blended` to ALSO surface the new world-canon (Bogle, Malkiel/Ellis,
  Damodaran-REITs, Dalio, Marks) + desk-synthesis atomics for trend-durability and wrapper context — advisory,
  down-weighted, **never reverses a binding verdict.**
- **Step → lens map (binding):** circle→circle (is this a trend/structure you understand?) · conviction→
  moat(=trend-durability)+management(=wrapper/sponsor)+owner-earnings(=coverage for REITs) · intrinsic-value→
  index-fair-value / REIT distributable-DCF · margin-of-safety→index-valuation-vs-history / yield-vs-required ·
  opportunity-cost→opportunity-cost (vs the CORE index and the equity book) · verdict→trend+wrapper+opp-cost ·
  inversion→fad-trend? + flawed-wrapper? + bubble-index? (disconfirming) · capital-allocation→REIT dividend/M&A
  discipline · sizing→kelly + conviction-cap + concentration (passive core disciplined, thematic capped).

## FINANCE-DESK SPECIALISTS (additive advisory layer — they inform; the binding CIO at A/B/C decides)
Dispatch these sharpened desk skills to SHARPEN the analysis. They are an additive, `--corpus blended`-informed
advisory layer (blended surfaces desk-synthesis atomics + the new world-canon ALONGSIDE binding); the
perspectives they surface are down-weighted and **NEVER reverse a `--corpus binding` verdict.** The
Munger/Buffett CIO stays THE arbiter. **No new desk seats — the existing 8 desks gain ETF/REIT competence.**

| Skill | Attaches at | ETF role | REIT / InvIT role |
|---|---|---|---|
| `moat-analysis` | A (& B) | **trend-durability** judgment ONLY (NOT a passive ETF's "moat" — low cost is the moat, rule 8) | REIT asset / lease / tenancy durability |
| `valuation-dcf-longrunway` | B | n/a (index uses CAPE/PE-vs-history, not a DCF) | **REIT distributable-DCF** (FFO/AFFO over a long runway; the ALTIUS 12%-hurdle DCF) |
| `bank-valuation` | B | n/a | **REIT leverage / justified-P-BV** (LTV discipline, the levered-trust read) |
| `forensic-accounting-redflags` | B | **ETF structure** integrity (synthetic vs physical replication, securities-lending, issuer/counterparty risk) → CLEAN/CAUTION/RED | **REIT sponsor** + related-party + distribution-quality integrity (return-OF vs return-ON honesty) |
| `capital-allocation-judge` | B | n/a (passive — no capital allocation) | **REIT dividend / M&A** discipline (Outsiders scorecard on the sponsor; e.g. debt-reduction IPO) |
| `portfolio-sizing` | D | Max-size (passive core = disciplined anchor; thematic = capped satellite) | Max-size as an income sleeve, not a concentrated bet |
| `decision-journal` | D | thesis + kill-criteria + trend re-decision cadence | thesis + kill-criteria (yield-break, rate-shock, tenant impairment) |
| `primary-research-sentiment` | A & B | live trend sentiment (Reddit/X/news) — disconfirmation-seeking | tenant/sponsor/sector DD harvest |

Also available: `creating-financial-models` (the DCF engine for REIT distributable-DCF and index fair-value),
`idea-researcher` + `deep-research` (global-trend discovery & temporal "what's happening now" layering),
`grill-with-docs` / `grill-me` (stress-test a trend conviction before it earns COMPOUND-TREND).

## MODEL / EFFORT TIERING (max-effort, not ultracode)
- **Stage A trend-durability scoring** (the wealth engine): **Sonnet** workflow, vault-bound, one rigorous pass
  per trend; escalate a contested CORE/COMPOUND-TREND trend to **Opus** for the durability call.
- **Stage B grading** over the full set: **Sonnet** workflow (judgment, vault-bound, structured output) — the
  analyst-desk fan-out + MF-methodology's 8 fund subagents run in parallel.
- **Stage C inversion** (adversarial — fad? flawed wrapper? bubble index?): **Opus/Fable** (few agents, high stakes).
- **Data fetch (TER/tracking/NAV/AUM/DPU/index-valuation) + 🌍 tab publish: mechanical** (Bash / MCP) — no model reasoning.

## STAGE A — Global-trend map (the discovery front-end / wealth engine)
*Before grading any single fund, decide which durable trends are worth owning at all.* This is the front-end
that has no equivalent in a "cleanup" — it parallels the stock FOREVER/COMPOUND hunt.
1. **Enumerate durable megatrends** worth owning: broad-world · India structural growth · US innovation ·
   AI / compute · energy transition · EM · gold/silver hedge sleeve. Write them to
   `extracted/research/global_trend_map.md` (the trend-map artifact).
2. **Score each trend's DURABILITY** with the binding CIO + the new perspectives:
   `32_consult_brain.py --company "<trend>" --model passive-etf --step circle` (do I understand the structural
   driver?) then `--step conviction` (is this a 10-yr tailwind or a fad?). Pull Dalio/Marks/Bogle/megatrend
   voices via `--corpus blended`; cite ONLY returned slugs. A trend whose durability is unknowable → TOO_HARD,
   off the map. Optionally enrich with `idea-researcher` / `deep-research` for live, dated sentiment.
3. **Map each KEPT trend to its best India-accessible wrapper:** the lowest TER, tightest tracking error,
   deepest AUM/liquidity, best tax bucket vehicle (use `mcp__indmoney__get_indian_stocks_details` for the
   listed ETF + WebFetch mfdata.in/valueresearch for TER & tracking error; `lookup_ind_keys` first to resolve).
   If there is no clean India-accessible wrapper, the trend is still graded but flagged TOO_HARD-to-execute
   (the route may open later — US/LRS execution is kernel-deferred, out of scope to BUY, in scope to GRADE).
**Barrier:** a ranked, cited trend map exists; every kept trend has a named best-wrapper candidate (or a
TOO_HARD-to-execute flag).

## STAGE B — Grade (like stocks), branching by asset type at Stage 0
For each candidate wrapper, **branch by asset type:**

### B-ETF — passive / thematic / commodity ETF
The mechanical fund-quality layer reuses the **MF methodology** (`extracted/mf/_mf_methodology.md`) and the
**6-factor rubric** (`extracted/mf/_mf_rubric.md`):
1. **Fund facts (mechanical):** TER, tracking error, AUM/liquidity, structure (physical vs synthetic),
   tax bucket, issuer. Source: INDmoney `get_indian_stocks_details` (nav/aum/ltp) + `get_mf_funds_details`
   where applicable + WebFetch (mfdata.in / valueresearch for TER & tracking error).
2. **MF-methodology subagents (parallel):** Book Recon · Fund Facts · Holdings Quality · **Overlap Mapper** ·
   Category Benchmarker · **Cost & SIP Auditor** · Debt Sleeve · **Global Sleeve** — the same 8 fund subagents,
   producing the wrapper-quality evidence.
3. **Apply the MF portfolio gates** (the known structural checks): **Overlap** (effective overlap >40% →
   downgrade weaker one band — this reproduces the held-book overlaps: 4 commodity ETFs → consolidate to
   UTI Gold + ABSL Silver; Mirae FANG+ vs S&P-500-Top-50 overlap → retire the duplicate lot) ·
   **Concentration** (single fund >25% of the passive sleeve) · **Cap-bucket** / sector-tilt (e.g.
   PSU-Bank-BeES) · **Global** (intl FOF + US ETFs >15% NW → consolidate to the lower-cost ETF).
4. **Conviction (trend × wrapper):** the binding `32_consult_brain.py --model passive-etf --step conviction`
   read, applied as JUDGMENT. Broad lowest-cost index → high; narrow thematic → must prove durability for the
   same band. Bad wrapper (high TER / poor structure / bad tax / wide tracking) → caps conviction or → AVOID.
5. **MoS (index valuation vs its OWN history):** CAPE / PE percentile of the underlying index (WebFetch the
   index CAPE/PE; `--step margin-of-safety`). A durable trend at a stretched index → WATCH. Cheap-vs-history
   + durable + best wrapper → COMPOUND-TREND (or CORE if it is the broad anchor).
6. **Verdict + Sell/Upside:** one 5-tier verdict; numeric Sell/Upside for every non-CORE row (rule 11).
   `forensic-accounting-redflags` checks ETF structure integrity (synthetic/securities-lending/counterparty).

### B-REIT / B-InvIT — full ALTIUS-template dossier
Write `vault/research/dossiers/<CODE>.md` to ALTIUS depth (read `vault/research/dossiers/ALTIUS.md` as the
template; frontmatter `note_type: dossier`, `brain_model: reit` or `invit`):
1. **6-filter walk-through, yield-instrument-adapted:** Filter 1 Circle · Filter 2 Moat = **asset quality +
   contracted tenancy/escalators** (WALE) · Filter 3 Owner-earnings = **distribution coverage + return-OF vs
   return-ON-capital split** (the heart — strip return-OF-capital out of the headline DPU) · Filter 4
   Management = **sponsor quality** + capital allocation (`capital-allocation-judge`) · Filter 5 MoS =
   **distribution-yield vs required (~9–10%), NOT a growth DCF** · Filter 6 Opportunity cost.
2. **The metrics:** FFO / AFFO · LTV (vs SEBI ceiling) · occupancy · WALE · NAV premium/discount · DPU split
   (return-ON ₹ + return-OF ₹) · headline yield vs sustainable (income-only) yield vs required.
3. **Valuation = distribution-yield MoS** (+ a `valuation-dcf-longrunway` distributable-DCF cross-check at a
   strict hurdle, the ALTIUS 12% read; `bank-valuation` for leverage / justified-P-BV). Buy-below = the price
   where the SUSTAINABLE income-only yield clears required; trim/sell = where the yield compresses below required.
4. **Conviction CAP 2** (rule 6 — yield instrument, ceiling = WATCH). Kill criteria (tenant/MSA impairment,
   rate shock, distribution-coverage break, leverage creep). `forensic-accounting-redflags` on sponsor +
   distribution-quality. 5-tier verdict (in practice WATCH or AVOID for a REIT/InvIT — never COMPOUND-TREND/CORE).
5. Data: BSE filings for DPU (live price via BSE code — GOOGLEFINANCE NSE will not resolve for InvITs).
**Barrier:** every candidate has a verdict + conviction + MoS; REIT/InvIT dossiers mirror ALTIUS depth.

## STAGE C — Inversion (Opus, adversarial)
For every **CORE / COMPOUND-TREND candidate**, a skeptic pulls **disconfirming** vault principles
(`32_consult_brain.py --company "<trend/fund>" --model <model> --step inversion`) and argues the strongest
case AGAINST: **is the trend a fad / already fading?** (the megatrend that everyone already owns) ·
**is the wrapper structurally flawed?** (synthetic replication, securities-lending counterparty, a tax trap,
chronic tracking drift, thin AUM that could close) · **is the index in a bubble?** (CAPE in its top decile —
a durable trend bought at a euphoric index is still a bad buy). Survive all three axes → keep the tier; else
demote (default = demote). `decision-journal` records the pre-mortem + kill-criteria. Desk perspectives inform
but never lift a fund into CORE/COMPOUND-TREND — the `--corpus binding` gate decides.

## STAGE D — Buy-list + sizing (mechanical-ish)
1. **`portfolio-sizing` sets Max-size** (`--step sizing --corpus blended`): the **passive base stays a
   disciplined CORE** (the anchor, sized for life); **thematic = capped satellites** (Kelly-fraction /
   half-Kelly, conviction-scaled ceilings, concentration discipline — few bets, hold the good ones, don't
   over-trim winners). REIT/InvIT sized as an income sleeve, not a concentrated bet.
2. **`decision-journal` records the thesis + kill-criteria** per kept fund (what we believe, the bet size,
   what would change our mind, the trend re-decision cadence).
3. **Rank the WHOLE set** (verdict → conviction → MoS); TOO_HARD quarantined off the buy-list. Produce the
   ranked, cited buy-list (is there a CORE/COMPOUND-TREND worth buying NOW at a sane valuation, vs WATCH the
   expensive ones).

## STAGE E — Publish to the 🌍 Global & Passive Base tab (mechanical, no rework)
**⚠️ READ BEFORE TOUCHING THE SHEET — the LOCKED Action Dashboard is NEVER touched ([[feedback-sheet-is-locked]]).
ETFs/REITs publish ONLY to the 🌍 tab. The 🌍 tab is RE-ARCHITECTED from scratch per the plan (the old
CORE-PASSIVE/ACCUMULATE 11-col sketch is a data point, NOT a template). BACK UP the 🌍 tab first; same
auto-coloring / locked-format discipline as the stock dashboard; if a helper disagrees with the live tab,
FIX THE HELPER, never the sheet, and never bypass a helper with raw writes for new/reordered rows.**

**Re-architected 🌍 tab schema (reads like the stock dashboard — a decision cockpit):**
`Rank · Vehicle · Trend/Exposure · Verdict · Conviction · Buy-zone (index-value) · Live NAV/price · Upside ·
TER · Tracking-error · Tax-bucket · Liquidity/AUM · Held? · Max-size · Why (1-line) · Sources`
with a **REIT / InvIT block** carrying: `Yield · Sustainable-yield (income-only) · NAV premium/discount ·
LTV · Occupancy`.
- **Rank key = lexicographic (verdict_tier [CORE < COMPOUND-TREND < WATCH < AVOID < TOO_HARD], −conviction, −MoS).**
  No other tiebreakers. TOO_HARD quarantined off the buy-list rows.
- **Values:** conviction (capped 2 for REIT/InvIT), buy-zone = index-fair-value entry (ETF) or the
  sustainable-yield-clears-required price (REIT), verdict = the 5-tier. CORE / COMPOUND-TREND → "∞ hold";
  WATCH / AVOID / TOO_HARD → numeric Sell/trim + Upside% (rule 11 — never blank a non-CORE Upside).
  `Why` = the one-line thesis from the dossier / fund brief (never an Obsidian `[!info]` callout).
- **Publish runbook:** (1) BACK UP the 🌍 tab (values + grid) to a revert point. (2) Build/extend the
  fund/REIT publish helper (parallels the stock `multi_insert_*` / `sync_dashboard_extras.js` helpers — reads
  the full grid, re-stamps Rank, carries any hyperlinks byte-for-byte, regenerates row-relative formulas,
  colors by verdict). **Always `--dry-run` first.** (3) Lock formatting if the layout changed.
- **Reindex:** new REIT/InvIT dossiers → `.venv/bin/python data/scripts/26_build_lancedb_index.py --vault vault
  --db vault/.lancedb` (auto-reloads the warm daemon; confirm `/health`). Remember the HEAD-WINDOW rule — a
  dossier correction must edit the head snapshot + one-line thesis, not just a tail append (only the ~4,000-char
  head vector is embedded).
- Update memory ([[reference-paise-se-paisa-sheet]] / the global-trend note) with the new 🌍 order + which
  trends are CORE/COMPOUND-TREND-worth-buying-now vs WATCH-the-expensive, and the held-book consolidations.

## KEY REGISTRY
- **Publish target:** the **🌍 Global & Passive Base** tab (re-architected) on the Paise se Paisa sheet
  (fileId `1N87younF990u-YGMOAiT8q6X-EtZ3jVovlWCF44orEY`). The **Action Dashboard is LOCKED and untouched.**
- **Brain models (Phase 2, `data/scripts/32_consult_brain.py`):** `passive-etf` · `commodity-etf` · `reit` ·
  `invit` — added to the 4 dicts (`MODELS`, `MODEL_PHRASE`, `MOAT_HINT`, `MGMT_HINT`); assets carry
  `brain_model: <slug>`. Retrieval auto-applies (no STEP/corpus/weight changes).
- **Templates:** REIT/InvIT dossier = `vault/research/dossiers/ALTIUS.md` (6-filter, DPU return-ON/return-OF
  split, distribution-yield MoS, buy-below/sell triggers, kill criteria, conviction cap 2). ETF fund-quality =
  `extracted/mf/_mf_methodology.md` (8 subagents + 4 gates + Buffett 5-filter) + `extracted/mf/_mf_rubric.md`
  (6-factor M1–M6 rubric + verdict bands + overlap rules).
- **Scripts:** brain consult `data/scripts/32_consult_brain.py` (the BINDING gate — scoped+cited);
  free-form vault RAG `29_vault_chat.py` (ad-hoc only); index `26_build_lancedb_index.py`; DCF engine via
  `creating-financial-models` / `valuation-dcf-longrunway`.
- **Data sources:** **INDmoney** (`networth_holdings`, `get_indian_stocks_details` nav/aum/ltp/sector,
  `get_mf_funds_details`, `networth_allocation_breakdown`, `lookup_ind_keys`) · **WebSearch/WebFetch** (TER &
  tracking error from mfdata.in / valueresearch; index CAPE/PE) · **BSE filings** (REIT/InvIT DPU; live price by
  BSE code) · optionally **reddit / youtube MCP** for live trend sentiment via `idea-researcher`.
- **Artifacts:** trend map `extracted/research/global_trend_map.md`; brain consults
  `extracted/grilling/<CODE>_<step>.json`; REIT/InvIT dossiers `vault/research/dossiers/<CODE>.md`.
- **VERDICT TIERS:** CORE (≈FOREVER, the broad lowest-cost anchor, price-exempt) · COMPOUND-TREND (≈COMPOUND,
  durable trend at a fair index valuation) · WATCH (great trend+wrapper, expensive index → wait) · AVOID (bad
  wrapper OR fad/fading trend) · TOO_HARD (durability unknowable OR no clean wrapper). Rank = verdict →
  conviction → MoS.
- **CONVICTION (1–5, judgment within gates):** broad lowest-cost index → high (low cost is the moat); narrow
  thematic → must prove trend-durability × wrapper-quality for the same band. Gates: fad/fading trend → AVOID;
  no clean wrapper → TOO_HARD; **REIT/InvIT → CAP 2.** MoS gate exempt only for CORE.
- **OUT OF SCOPE:** US-via-dollar/LRS execution (kernel-deferred — a trend may still be GRADED for when the
  route opens, just not BUYABLE); new desk SEATS (the 8 desks gain ETF/REIT competence, no new seats); active
  mutual-fund onboarding (a separate book); any trade; any edit to the LOCKED Action Dashboard.
