---
name: stock-pick-ranker
description: >-
  SUPERSEDED (2026-06-13) — OFFLINE xlsx-research variant ONLY; for adding/ranking stocks into the LIVE
  Action Dashboard use the stock-onboarding-pipeline skill instead (vault-binding v2). This v1 runs the
  full matured equity quality+valuation ranking pipeline on new stocks and append
  them into the Substack_Stock_Picks.xlsx workbook. Use this skill WHENEVER the user gives new
  companies/tickers to evaluate, new Substack (or other newsletter) investor profile URLs to scrape
  for stock picks, or asks to "add these stocks", "rank these companies", "score this stock", "run
  the workflow on X", "append to the stock workbook", "update the ranking", or extend/refresh the
  investment ranking. It scrapes investor newsletters, enriches live (Indian-listed) financials from
  Screener/Moneycontrol, scores each stock on a 7-factor principles rubric, runs forward + reverse
  DCF valuation (method-appropriate by stock type), reliability-weights the valuation into the rank,
  re-ranks the combined universe, and appends/refreshes the workbook. Trigger it even if the user
  only names a company and a goal ("is XYZ a good long-term buy? add it to the sheet") without saying
  "rank" or "workflow" explicitly. Do NOT trigger it for standalone financial models for private/unlisted
  companies (that's the creating-financial-models skill), one-off metric lookups (a single P/E or price),
  plain Substack text extraction with no stock to rank, generic spreadsheet edits, purely conceptual
  finance questions, or ranking non-stocks (vendors, job candidates) — those are not this
  stock-ranking-into-the-workbook pipeline.
---

# Stock Pick Ranker

An end-to-end pipeline that turns **new companies** (or **new Substack investor profiles**) into
scored, valued, ranked rows appended to `Substack_Stock_Picks.xlsx`. It encodes a workflow that was
built and hardened over a long session — follow the stages and the hard-won rules below rather than
improvising, because most of the rules exist to prevent specific failures we already hit.

## What it produces

New stocks are scored, valued, **merged into the existing universe, re-ranked**, and written into the
workbook. The ranking is *relative*, so adding stocks means recomputing the ranking over the whole
set — never just bolting rows onto a stale order.

## Inputs (either or both)

- **Companies** — a list of tickers/names (e.g. "score INFY, KPITTECH and add them"). Skip straight
  to enrichment (Stage 2).
- **Substack (or other newsletter) profile URLs / handles** — scrape them first (Stage 1) to extract
  which stocks each author recommends and the thesis, then continue.

**Default workbook:** `/Users/Dhiraj/dev/invest/Substack_Stock_Picks.xlsx`. If the user names a different
file, use that. Always **preserve existing sheets/data** — this skill appends and refreshes, never
overwrites unrelated content.

## Environment & dependencies (read once — these bite if ignored)

- **Python:** use **`/usr/bin/python3`** for anything importing `numpy`/`pandas`/`openpyxl`. On this
  machine it is the *only* interpreter with those installed (Homebrew 3.14 and 3.11 lack them and
  `pip` is broken there). `uv` exists as a fallback (`uv run --with numpy --with pandas ...`).
- **DCF engine:** valuation uses the installed **`creating-financial-models`** skill at
  `~/.claude/skills/creating-financial-models/dcf_model.py` (class `DCFModel`). That model has been
  bug-fixed (depreciation decoupled from capex; terminal working-capital normalised so equity value
  is monotonic in growth). Do NOT reimplement DCF math — import that model. See `references/valuation.md`.
- **Web data:** Screener.in (primary), Moneycontrol / Tickertape / Trendlyne (fallback). For Substack,
  the public JSON API (no key) — see `scripts/substack_fetch.py`.

## The workbook

`Substack_Stock_Picks.xlsx` currently has 9 sheets. Read `references/workbook-schema.md` for the exact
column layout of each before writing, so appended rows line up and the right sheets get refreshed.
Data sheets (Stock Picks, Live Financials) get **new rows appended**; ranking/derived sheets (Master
Ranking, What's Hot, Final Ranking v2, Valuation (DCF)) get **fully recomputed** over the combined
universe.

## Source of truth

Keep the per-stock structured data in `/Users/Dhiraj/dev/invest/extracted/` as the durable store:
`_consolidated.json` (thesis), `enriched/*.json` (live financials), `_principles_scores_v2.json`
(factor scores), `valuation/v2/*.json` (valuations), `_final_v2.json` (the ranked dataset). New stocks
are merged into these, then the workbook is rendered from them. The workbook is a *rendering*; the
JSON is the truth. This is what makes a clean re-rank possible.

---

## Pipeline

Use **parallel subagents** for the heavy fan-out stages (scraping, enrichment, scoring, valuation) —
one per batch of ~6-8 stocks (or one per publication). Each stage has a reference and/or script.

### Stage 1 — Scrape Substack (only if given profiles)
Resolve handle → publication, list the post archive, fetch **free** post bodies, and extract the
**recommended** stock(s) + thesis per article (one row per main pick; skip thematic/educational posts).
Paid post bodies are paywalled — the user must paste those manually. Use `scripts/substack_fetch.py`.
Output per author into `_consolidated.json` (company, ticker, thesis_crux, key_risk, upside, sector,
source). **Never invent figures** — record only what the author states. See `references/enrichment.md`
(§Substack extraction).

### Stage 2 — Enrich live financials  → High confidence for every stock
For each new company gather the current hard data (FY-end March: latest FY + latest quarter, "as of"
today). The user's standing rule: **no stock may stay low-confidence** — go to the web and fill every
field. **Never fabricate** — only sourced figures, cite sources, flag any estimate. Use bank/NBFC/InvIT
-appropriate metrics. Full field list, sources, and per-type handling: `references/enrichment.md`.
Write to `extracted/enriched/`.

### Stage 3 — Consolidate / dedup
Merge to **one row per stock** across authors (a stock recommended by two authors = one merged row
crediting both). Run `scripts/consolidate.py` (or fold into the enrichment step). Cross-author overlap
is the basis of the "hotness" signal.

### Stage 4 — Score the 7-factor principles rubric (judgment; use a subagent)
Score each stock 1-5 on Moat (F1), Margin-of-Safety (F2), Capital-Efficiency (F3), Antifragility (F4),
Asymmetry (F5), Management/skin-in-game (F6), Convergence/2nd-level (F7), using **live financials for
the quantitative factors and the author thesis for the qualitative ones**. Anchors, weights, and the
principle→factor mapping (MindSnacks + Greenblatt + Piotroski): `references/rubric.md`. Confidence =
High for all once hard data is complete; put earnings-quality caveats in `red_flags`, not confidence.
Write `extracted/_principles_scores_v2.json`.

### Stage 5 — Valuation: forward + reverse DCF (method-appropriate; use a subagent)
For each stock, value it with the **right method for its type** and produce a verdict
(Undemanding/Reasonable/Demanding/Heroic) + a `valuation_score_1to5`:
- **Non-financial, profitable** → forward DCF + **reverse-DCF** (back out market-implied growth) on the
  fixed model. Set `depreciation_percent` ≈ true D&A (NOT expansion capex).
- **Bank/NBFC/power-trading** → justified-P/B vs ROE (no DCF).
- **Loss-maker** → EV/Sales (no DCF).
- **InvIT** → distribution-yield vs required.
- **Cyclical/commodity** → reverse-DCF on a *through-cycle* margin, flagged Low confidence.
Use `scripts/valuation_runner.py`. Full method + the model's residual limitations + reliability flags:
`references/valuation.md`. Write `extracted/valuation/v2/`.

### Stage 6 — Rank (deterministic)
Run `scripts/rank.py` over the **combined universe** (existing + new). It computes the principles
score (weighted 7 factors), hotness, **blends the reverse-DCF valuation into Margin-of-Safety
weighted by reliability** (so DCF artifacts on thin-margin/cyclical names can't corrupt the rank),
forms Master = 85% principles + 15% hotness, and re-ranks. Writes `extracted/_final_v2.json`.

### Stage 7 — Append & refresh the workbook
Append the new stocks' rows to the **data** sheets and **fully recompute** the **ranking** sheets over
the combined set. Use `scripts/append_workbook.py` (then spot-verify, or dispatch a builder subagent
for full 9-sheet consistency). Read `references/workbook-schema.md` first. Re-open and verify sheet
counts/row counts after writing.

---

## Hard rules (these prevent the specific failures we hit)

1. **No fabricated numbers, ever.** Every financial figure is sourced or left blank/flagged. The whole
   exercise is worthless if numbers are invented. Cite sources; mark estimates.
2. **`/usr/bin/python3` for numpy/pandas/openpyxl.** Other interpreters here lack them.
3. **Import the fixed `creating-financial-models` model** for DCF — don't rewrite it; set
   `depreciation_percent` separately from capex.
4. **Method-appropriate valuation** — DCF is wrong for banks (P/B), loss-makers (EV/Sales), InvITs
   (yield), and unreliable for cyclicals (through-cycle margin + Low confidence). Don't force DCF on them.
5. **Reliability-weight the valuation blend** — a simplified DCF still under-converts FCF for
   thin-margin / high-NWC / cyclical names, so down-weight flagged/Low-confidence reverse-DCF reads
   (~0.20) vs clean High-confidence ones (~0.55). Trust multiples (F2) where the DCF is a known artifact.
6. **Re-rank the whole universe** when adding stocks — the ranking is relative. Never append to a stale order.
7. **Quality is the backbone; valuation is an overlay.** Don't let a noisy DCF dominate a sound
   quality rank — it's ~15% of the move, by design.
8. **Parallel subagents** for scraping/enrichment/scoring/valuation (batch ~6-8). Consolidate centrally.
9. **Preserve the workbook** — append/refresh only; never clobber unrelated sheets.

## Files in this skill
- `references/enrichment.md` — fields to gather, sources, per-type handling, Substack extraction, no-fabrication rules.
- `references/rubric.md` — the 7 factors (1-5 anchors), weights, principle mapping, confidence.
- `references/valuation.md` — DCF/reverse-DCF method, discount-rate assumptions, method-by-type, reliability-weighted blend, model caveats.
- `references/workbook-schema.md` — the 9 sheets and their columns; what to append vs recompute.
- `scripts/substack_fetch.py` — resolve profile / list archive / fetch free post bodies (Substack public API).
- `scripts/valuation_runner.py` — forward DCF + reverse-DCF (binary search) wrapping the fixed model; justified-P/B / EV-Sales / yield helpers.
- `scripts/rank.py` — principles score + hotness + reliability-weighted valuation blend + master + re-rank.
- `scripts/append_workbook.py` — append new rows to data sheets and recompute ranking sheets.
