---
name: stock-onboarding-pipeline
description: >
  Onboard new Indian stocks into the "Paise se Paisa" Action Dashboard end-to-end, using the v2
  vault-aligned machinery (understanding gate → quality-gated conviction with ROIC+runway →
  conservative IV range → conviction-scaled margin-of-safety vs opportunity cost → reformed verdict).
  Use when the user says "add stocks", "add the next batch", "onboard <tickers>", "grow the dashboard",
  "re-rank", or wants to extend the TO-BUY/study list. Workspace: /Users/Dhiraj/dev/invest, sheet fileId
  1N87younF990u-YGMOAiT8q6X-EtZ3jVovlWCF44orEY. Charlie Munger & Warren Buffett (the Obsidian vault)
  are the binding CIO; the vault gates conviction/verdict/MoS, it is not narrative decoration.
---

# Stock Onboarding Pipeline (v2 — vault-aligned)

The single source of truth for adding stocks to the Action Dashboard. Follow the stages in order.
**v2 machinery adopted 2026-06-12** after a CIO review (Munger/Buffett via the vault) found v1
"looked Buffett but ranked like a quant trading desk", and that the vault only fed narrative.
See [[reference-paise-se-paisa-sheet]] and [[feedback-indian-mentors-lens]] in memory. The live
process is documented in the sheet's **⚙️ Machinery v2** tab; per-stock grades in **🔍 Conviction & MoS v2**.
**Retrieval plumbing upgraded 2026-06-12 (brain-densification Phase 4):** all vault consultation now goes
through `data/scripts/32_consult_brain.py` (scoped, cited, structured) — the v2 logic itself is unchanged.

## North star
The dashboard is a **STUDY LIST in search of ONE strictly-lifelong hold (FOREVER)** — not a buy-list,
and **not a 45-name basket** (Munger: 1–3 wonderful businesses suffice; act rarely). Indian Substack
analysts (Vaibhav & Gaurav Tambade = "India's Buffett/Munger"; plus Karan Shah, The Megatrend Investor,
Dhruva) supply the bull thesis + ground-truth context; **Charlie Munger & Warren Buffett (the vault) are
the FINAL, BINDING arbiters.** Finding zero FOREVER names — and finding that nothing clears the
margin-of-safety bar at today's prices — is an acceptable, expected result. Patience is the edge.

**See also — ETFs / REITs / InvITs:** this pipeline is for individual stocks → the 🎯 Action Dashboard.
For a fund (ETF, REIT, InvIT) use **`etf-reit-onboarding`** instead — it evaluates funds like stocks but
publishes to the **🌍 Global & Passive Base** tab and NEVER touches the LOCKED Action Dashboard.

## HARD RULES (never violate)
1. **Never re-grill / re-dossier stocks already done.** Existing dossiers in `vault/research/dossiers/*.md`
   are frozen inputs. Only dossier the NEW stocks. (Exception A — DATA FIX: a stock whose dossier had a *data error* —
   e.g. wrong price — may be corrected; that is a fix, not a re-grill.) (Exception B — EVENT REFRESH: when
   `data/scripts/70_detect_material_events.py` flags a MATERIAL event on a dashboard/HELD name, the dossier HEAD WINDOW may be
   refreshed under the **`news-results-refresh`** skill. Only the head window is touched — research PROSE stays frozen.
   **L0** staleness-stamp (`last_event_checked`) + **L1** one-line catalyst/"Why" refresh AUTO-apply.
   **L2 — IV / conviction / verdict-DEMOTION / within-tier flips / MoS recompute now ALSO AUTO-apply AND AUTO-re-rank the
   LOCKED Action Dashboard** through the guarded loop (user override, 2026-06-25): an earning-power event passes
   `coln_iv_event_gate.py` → `71_refresh_orchestrator.py` runs a targeted Stage-3 re-grade (binding-vault consult +
   `80_estimate_iv.py` price-independent IV + conviction gates + MoS/buy_below recompute + verdict re-derive + board
   sanity-check) → re-freezes the dossier head → **`73_refresh_cycle.sh` stage 3c invokes `82_rerank_guard.py --tag headwindow`** (once per cycle, after the reindex) to re-rank + publish the whole set behind a 3-tab
   backup + dry-run-diff + **ticker-keyed** checksum + auto-revert + maker≠checker, gated by env **`RERANK_AUTO=1`** AND brain-healthy post-reindex AND ≥1 L1 applied this cycle (`71` never calls 82 — the re-rank is once-per-cycle in 73).
   **`RERANK_AUTO` is DEFAULT-OFF: the capability shipped (PR #33) and is now wired into the loop (73 stage 3c), but stays off pending a supervised first-enable** — until
   then 73 doesn't even invoke 82; if run manually, 82 dry-runs + asserts + prints the order-diff and STOPS (no live re-rank). `RERANK_AUTO` is NOT set in the plist — enabling it is the user's explicit supervised toggle. (A re-rank CARRIES the live col-D verdict + col-M conv byte-for-byte; reconcile a stale D/M cell to the dossier oracle first with the sanctioned writer `sync_col_dm.py` → `write_col_dm.mjs`, else 82's carried-cell assertion ABORTS.) **SOLE human gate: a FOREVER *promotion*
   (Stage-4 adversarial "strictly-lifelong" inversion a cron can't do) — and any `needs_review`/board-contradiction — routes
   to `data/state/pending_reviews/<TICKER>.json` and is NEVER auto-applied.** Price / FII / MF flows / ratings / buy-calls
   move live MoS + Upside (cols I/J/K) ONLY — they NEVER trigger IV or a re-grade.)
   **HEAD-WINDOW RULE: when correcting a dossier (data fix OR a re-grill finding), you MUST edit the HEAD WINDOW — the frontmatter snapshot + the one-line thesis in the first ~4,000 chars — NOT just an appended tail section. `26_build_lancedb_index.py` embeds only ONE ~4,000-char head vector per dossier, so tail appends are invisible to brain retrieval. (A stale Repco-CBI "open case" flag kept surfacing until the head one-line thesis was fixed, 2026-06-18; appending a "## Re-grill" section at the tail alone did nothing.)**
2. **Always re-rank the WHOLE set** (old + new) after adding — never just the new ones. (The whole-set re-rank is now
   ALSO wired into the news loop: `73_refresh_cycle.sh` stage 3c invokes `82_rerank_guard.py --tag headwindow` to re-run the
   Stage-6 publish runbook unattended behind the re-rank guard + auto-revert + maker≠checker, gated by `RERANK_AUTO=1`
   (default-OFF, NOT in the plist, pending supervised enable) AND a healthy post-reindex brain AND ≥1 applied L1 this cycle. A
   FOREVER *promotion* still requires the human Stage-4 gate.)
3. **The vault is BINDING, not decoration.** `data/scripts/32_consult_brain.py` (scoped, cited retrieval — see
   CONSULTING THE BRAIN below) gates conviction, verdict and MoS at Stages 0/3/4. `cites_principles` may contain
   ONLY slugs it actually returns (`principles[].slug`). No fabricated citations. If `principles` comes back
   empty/thin → abstain + flag. (`29_vault_chat.py` stays available for free-form cited Q&A / ad-hoc grilling.)
4. **Quality is a HARD GATE before price.** Order of analysis: understanding → moat/owner-earnings/management
   → ONLY THEN price. A business you can't understand, or with no durable moat, cannot earn high conviction
   regardless of price or optics.
5. **Conviction = JUDGMENT, not a formula** (Munger: avoid false precision / formulaic thinking). It measures
   durable business quality, price-independent — see the rubric in KEY REGISTRY. Gates: no moat → 1;
   chronically weak/near-zero FCF → cap 2; returns below ~12% cost of capital → cap 2. Banks/NBFCs judged on
   ROE vs cost of equity (ROCE/FCF N/A); InvITs cap 2; quasi-financials (heavy FCF can offset modest ROCE).
6. **Margin of safety is THE gate** (the cornerstone, widens with uncertainty), scaled to conviction
   (conv5 ≥10%, conv4 ≥15%, conv3 ≥25%, conv2 ≥40%, conv1 ≥55%), measured vs **opportunity cost** (the best
   existing idea), NOT a bond yield. **IRR HURDLE (named gate):** a BUY must clear the index — expected IRR > the ~9–10% Nifty return (the default opportunity cost); a wonderful business that can't beat the index from today's price is a WATCH, not a BUY. **Volatility ≠ risk** — the old GBM price engine is a DEMOTED clerk
   (informational only: "is an entry plausible / where's the MoS line"), never the judge or tiebreak.
7. **Intrinsic value is a conservative RANGE** (low/base/high), never a false-precise point. Buy-below =
   `iv_base × (1 − required_MoS)`. **IV = business EARNING POWER, and is PRICE-INDEPENDENT** — it re-estimates ONLY when
   news changes earning power (a structural results delta, a capacity add, a durable order win) via a real DCF / justified-P/B
   (`80_estimate_iv.py` takes NO price input). **Price, FII/MF flows, ratings and buy-calls NEVER move IV** — they move live
   MoS + Upside (cols I/J/K) only. A "dynamic IV" that drifts with the quote would make the dashboard buy high and sell low.
8. **Sell ₹ + Upside are written for every NON-FOREVER verdict — never blank them (Chairman rule 2026-06-13).**
   WATCH / AVOID / TOO_HARD each carry a numeric **Sell ₹ = fair-value target (IV-high)** AND an **Upside%**
   `=(Sell−Live)/Live` (honestly negative when the price is above fair value), alongside the WATCH buy-below
   entry trigger. ONLY FOREVER/COMPOUND show "DON'T SELL" / "∞ hold" (lifelong hold; sell only on thesis-break,
   moat erosion, a better opportunity, or a cash need). Do NOT blank a Sell/Upside cell for a WATCH/AVOID name
   (that was a publish bug — the upside column must always render a number for non-FOREVER rows).
9. **Too-hard → DISCARD from the buy-list**, don't rank it (Buffett's three buckets: in / out / too-hard).
   Loss-makers with no clear path, unpredictable/rapid-change businesses → TOO_HARD quarantine. Forced
   inactivity is a feature.
10. **Read the article AND its comment thread** (Substack API — comments are real signal). Method-appropriate
    valuation (DCF for operating cos; justified-P/B for banks; distribution-yield for InvITs; mid-cycle-EPS
    multiple for commodity cyclicals). Always check for stock splits and validate the dossier's current_price
    against the live yfinance close (a stale enriched-pipeline snapshot once put a price 17% wrong).
11. **5-tier verdict** exactly one per stock: FOREVER / COMPOUND / WATCH / AVOID / TOO_HARD.

**Autonomy-ladder ratification.** Ratified 2026-07-03 (PW-13): the daily loop auto-consults fresh (≤2d)
RED+MATERIAL events, hard-capped at CYCLE_CONSULT_BUDGET=25/cycle, RED-first-oldest-first. L1 auto-applies;
L2 IV/conviction/verdict changes including upgrades up through COMPOUND auto-apply under 82_rerank_guard.
FOREVER promotion remains the sole permanent human gate. Backlog (>2d) events consult only under DRAIN_GO=1
(founder-gated). The value-digest reports these changes (email); it never grades.

## CONSULTING THE BRAIN (`data/scripts/32_consult_brain.py` — the ONE retrieval entrypoint)
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<name>" \
  --model <bank|insurance|consumer-brand|commodity-cyclical|utility-psu|capital-goods|platform|general> \
  --step <circle|conviction|intrinsic-value|margin-of-safety|opportunity-cost|verdict|inversion|capital-allocation|sizing> \
  [--corpus <binding|blended>] [--entities <peer-slugs,comma-sep>] [--k 8] --json-out extracted/grilling/<TICKER>_<step>.json
```
- **What it does:** derives 2-3 model-aware retrieval questions from the stock context, routes internally
  (specific model or entities → ScopedLanceDBBackend with caller-supplied scope, **0 Azure calls**;
  `general` + no entities → hybrid + GPT rerank, 1 Azure call/question — the two are NEVER stacked,
  measured worse), RRF-merges + dedupes, and hygiene-filters to mentors' atomics/raws + `_synthesis`
  (hubs, MOCs, `_system`, dossiers, positions excluded; every path verified on disk).
- **How to read the output:** `principles: [{claim, path, slug, citation, mentor, note_type, source_note,
  applies_to_model, applies_to_filter, rrf_score}]`. `claim` = the principle to apply; `citation`/`slug` =
  the ONLY tokens permitted in `cites_principles`; `source_note` = traceability to the raw transcript/letter.
  Empty `principles` → vault is thin here → ABSTAIN + flag, never pad.
- **Step → lens map (binding):** circle→circle · conviction→moat+management+owner-earnings ·
  intrinsic-value→owner-earnings+MoS · margin-of-safety→MoS+opportunity-cost ·
  opportunity-cost→opportunity-cost · verdict→moat+circle+opportunity-cost ·
  inversion→moat+management+MoS (disconfirming) · capital-allocation→reinvestment-runway+ROCE+allocation-discipline ·
  sizing→kelly+conviction-cap+catastrophic-loss. Aliases: understanding=circle, iv, mos, oc.

## FINANCE-DESK SPECIALISTS (additive advisory layer — they inform; the binding CIO at 0/3/4 decides)
Dispatch these sharpened skills at the stages below to SHARPEN the analysis. They are an additive, `--corpus blended`-informed
advisory layer (blended surfaces desk-synthesis atomics + perspectives ALONGSIDE binding); the perspectives they surface are
pitch-side / down-weighted and **NEVER reverse a `--corpus binding` verdict.** The Munger/Buffett CIO at Stages 0/3/4 stays THE arbiter.

| Skill | Stage | Role |
|---|---|---|
| `primary-research-sentiment` | 1 | DD/sentiment harvest (ValuePickr/Reddit/concall), framed as disconfirmation-seeking |
| `forensic-accounting-redflags` | 1 | governance-integrity gate → CLEAN/CAUTION/RED (CAUTION caps conviction; RED hard-fails to AVOID/TOO_HARD) |
| `moat-analysis` | 3 | enriches the moat call in conviction/verdict |
| `capital-allocation-judge` | 3 | 6-axis CEO scorecard; consults `--step capital-allocation --corpus blended` |
| `valuation-dcf-longrunway` | 3 (& 1 step 4) | IV method for operating cos (conservative range); operationalized price-free by `80_estimate_iv.py` (multi-stage DCF) for the news-loop IV re-grade |
| `bank-valuation` | 3 (& 1 step 4) | IV method for banks/NBFCs (justified-P/B); operationalized price-free by `80_estimate_iv.py` (justified-P/B / excess-return) — fixes the least-grounded IVs |
| `decision-journal` | 4 | behavioral decision artifact + inversion enrichment; records sentiment-cycle locus + FOREVER re-decision cadence |
| `portfolio-sizing` | 4 | Max-size (col-M) decision; consults `--step sizing --corpus blended` |

## MODEL / EFFORT TIERING (not ultracode)
- New-stock dossier workers (the bulk): **Sonnet**, 1 rigorous pass each, in a **Workflow** (resumable).
- v2 conviction/verdict re-grade over the FULL set: **Sonnet** workflow (judgment, vault-bound, structured output).
- Inversion / strict FOREVER gate: **Opus/Fable** (few agents, high stakes, adversarial).
- Fundamentals fetch + price-engine clerk + sheet publish: **mechanical** (Bash/MCP) — no model reasoning.

## STAGE 0 — Scope, ingest & understanding gate (orchestrator)
- New stocks = universe (`extracted/_final_v2.json`) minus done (`ls vault/research/dossiers/`). Beware
  name/ticker spelling mismatches.
- Per stock map: author/article (`extracted/<author>.json`), valuation g-file (`grep <TICKER> extracted/valuation/v2/g*.json`),
  enriched financials (`grep <TICKER> extracted/enriched/batch_*.json` — VERIFY price vs live), 7-factor scores, v2 rank/theme.
- Fetch article + comments via Substack API: `curl -s "https://<pub>.substack.com/api/v1/posts/<slug>"` → id;
  `curl -s ".../api/v1/post/<id>/comments?all_comments=true&token="` → `.comments[].children`.
- **Understanding gate + triage:** for each name ask "would I own the whole business 10 years with the market shut?"
  Ground the call: `32_consult_brain.py --company "<name>" --model <model> --step circle` and apply the returned
  circle-of-competence principles (cite their slugs). Genuinely too-hard → TOO_HARD bucket, off the buy-list.
  Verify NSE symbol (live ≈ expected ±5%; .BO/BSE for InvITs).

## STAGE 1 — N parallel dossier workers (Workflow, Sonnet) — NEW stocks only
Each writes `vault/research/dossiers/<TICKER>.md` to IGI-depth (read `vault/research/dossiers/IGI.md` as the
template; frontmatter per `vault/CLAUDE.md`). Steps: (1) WebFetch article + Substack comments; (2) fresh web
research (latest quarter, price, splits, governance); (3) **brain consult** (`32_consult_brain.py --company "<name>"
--model <model> --step conviction --json-out extracted/grilling/<TICKER>_conviction.json`, then likewise
`--step margin-of-safety` — both mentors arrive in one call, mentor carried per-principle; use ONLY returned
slugs); (4) method-appropriate IV as a **conservative range** (ground with `--step intrinsic-value` if needed); (5) "Author's voice" + "Comment-thread
red flags" sections; (6) verdict + kill-criteria (inversion) + honesty flags. **Barrier:** all dossiers exist.
- **Desk specialists (advisory):** run `primary-research-sentiment` (disconfirmation-seeking DD harvest) and the
  `forensic-accounting-redflags` integrity gate (CLEAN/CAUTION/RED — CAUTION caps conviction, RED hard-fails to AVOID/TOO_HARD);
  `valuation-dcf-longrunway` / `bank-valuation` may build the conservative IV range in step 4. They inform; the binding gate decides.

## STAGE 2 — Fundamentals fetch (mechanical) — the compounding-quality data
For ALL stocks (old + new), fetch via **yfinance statements** (NOT `.info` — it rate-limits): ROCE
(`EBIT / (Stockholders Equity + Total Debt)`), ROE (`Net Income / Equity`), and 4-year **FCF** (`Free Cash Flow`,
count positive years + latest FCF/PAT). This is the owner-earnings + returns-on-capital evidence conviction needs.
Add a 0.3s sleep between tickers. Output `/tmp/fundamentals_v2.json`.

## STAGE 3 — v2 conviction & verdict re-grade (Workflow, Sonnet — judgment, vault-bound)
One agent per stock over the FULL set. Each reads its dossier + gets its fundamentals (ROCE/ROE/FCF) + the
**binding vault principles** — the per-stock `32_consult_brain.py` output for steps `conviction`,
`margin-of-safety` and (where IV is contested) `intrinsic-value`/`verdict`; embed the returned claims+citations
in the prompt, `cites_principles` ⊂ returned slugs — + the conviction rubric & MoS thresholds, then
applies JUDGMENT (not a formula) and returns structured: `{understanding (in|too_hard), conviction_v2 (1-5) +
rationale, roic_runway_note, iv_low/iv_base/iv_high, mos_pct, required_mos_pct, clears_bar, buy_below_v2,
verdict_v2, sell_logic}`. Honest + conservative — "nothing clears the bar" is the expected answer. (Existing
dossiers are frozen *inputs*; re-grading their conviction/verdict against the whole set is allowed and required.)
- **Desk specialists (advisory):** `moat-analysis` sharpens the moat call, `capital-allocation-judge` runs the 6-axis CEO
  scorecard (`--step capital-allocation --corpus blended`), and `valuation-dcf-longrunway` / `bank-valuation` supply the IV
  method. They inform the re-grade; the `--corpus binding` conviction/verdict gate remains the arbiter.

## STAGE 4 — Inversion / strict FOREVER gate (Opus/Fable, adversarial)
For every FOREVER *candidate*: a skeptic pulls **disconfirming** vault principles
(`32_consult_brain.py --company "<name>" --model <model> --step inversion` — moat erosion, management failure,
MoS as protection against being wrong) and checks for bias
(mere-association, overconfidence, market-prediction focus), and argues the strongest case it is NOT strictly
lifelong (moat that can't be lost overnight, clean owner-earnings, aligned long-horizon owner, price not heroic).
Survive all axes → FOREVER; else demote. Default = demote. **No standing Chairman FOREVER overrides** — the prior IGI & CAMS override was REVOKED 2026-06-17 (both graded to WATCH on the merits; the FOREVER tier is currently EMPTY). Grade every name honestly, IGI/CAMS included, no exceptions.
- **Desk specialists (advisory):** `decision-journal` records the behavioral decision artifact + inversion enrichment (sentiment-cycle locus,
  standing FOREVER re-decision cadence), and `portfolio-sizing` informs the Max-size (col-M) call (`--step sizing --corpus blended`).
  They inform; the `--corpus binding` FOREVER gate decides — desk perspectives never lift a name into FOREVER.

## STAGE 5 — Price engine as a CLERK (mechanical, optional, informational only)
The Family-D engine (`data/scripts/30_d_engine.py`) may be run to answer "is a buyable entry plausible / where
is the MoS line" — but it is **demoted**: volatility ≠ risk, it does NOT set verdict, conviction, or the rank.
Its sheet tab (🧮 D-Engine, gid 1487890548) is annotated DEMOTED. Skip if not needed.

## STAGE 6 — Final sort & publish (mechanical, no rework)
**⚠️ READ BEFORE TOUCHING THE SHEET — the cockpit is hand-tuned & LOCKED ([[feedback-sheet-is-locked]]). The live sheet is canonical; if a helper disagrees, FIX THE HELPER, never the sheet, and NEVER bypass a helper with raw `sheets_update_cells` for new/reordered rows (raw writes lose number-formats, banding, verdict colors, sparkline colors → broke the dashboard 2026-06-17). The Action Dashboard is **18 columns A–R**: A Rank·B Stock·C Company·D Verdict·E Buy-below·F Avg·G Live·H Sell·I Status·J To-buy·K Upside·L Sparkline·M Conv·N Why·O Dossier·**P P/E (TTM)·Q P/S·R EV/Sales**. Locked format spec: `dashboards/action-dashboard-style.json` (re-capture via `introspect-dashboard.js` when layout changes).**
- **Rank key = lexicographic (verdict_tier [FOREVER<COMPOUND<WATCH<AVOID<TOO_HARD], −conviction_v2, −mos_pct).** No other tiebreakers (not author, not legacy sheet order, not D-engine). Within WATCH, higher conviction always ranks above lower; within same verdict+conviction, higher MoS% ranks above lower (even if MoS is negative). TOO_HARD quarantined off the buy-list. **Two-rank gotcha:** the Dashboard EXCLUDES TOO_HARD; companion tabs (Conv, Deep) INCLUDE them → compute TWO orders (companion = same sort with TOO_HARD appended last; non-TOO_HARD companion rank MUST equal dashboard rank so dashboard col-O `range=A<rank+1>` resolves in the Deep tab). To re-derive mos for EXISTING rows from the dashboard alone: `iv_base = buy_below / (1 − req_mos/100)`, `mos% = (iv_base − live)/iv_base × 100` (req_mos by conv: 5→10,4→15,3→25,2→40,1→55).
- **PUBLISH RUNBOOK (every batch, in order):** (1) **BACK UP all 3 tabs** to `extracted/dengine/backup_<tag>_<ts>/` (values+grid) — a revert point is mandatory. (2) **Re-rank the WHOLE set** + insert new rows with the CANONICAL helpers in `/Users/Dhiraj/dev/invest/tools/sheets-bridge/`: **`multi_insert_dashboard.js` is the reliable multi-row insert** (reads full grid, carries col-B author hyperlinks byte-for-byte, regenerates row-relative I/J/K/L, re-stamps A rank + O dossier link, colors new col-B by author_rgb; NEW non-Substack names → PLAIN black ticker, no hyperlink). It takes `orderFile=[{rank,ticker,verdict,conv,mos,is_new}]` + `newStocksFile={TICKER:{symbol,company,verdict,buyBelow,sell,conv,why,priceFallback,exch,(source_url+author_rgb only if Substack)}}`. **`why` MUST come from dossier `## One-line thesis`** — never Obsidian `[!info]` callouts. Writes A–O only. **Always `--dry-run` first** (manual onboarding); **the news loop runs this same runbook UNATTENDED via `82_rerank_guard.py`, where "dry-run first" becomes an automated dry-run-diff gate that ABORTS on any unexpected diff** — `82` backs up all 3 tabs, dry-runs the order, asserts ONLY row-order + col-A rank changed and each row's verdict/conv/IV matches its re-graded dossier (checksum keyed by **ticker, not row**), and auto-reverts on anomaly; the live write is armed by `RERANK_AUTO=1` (**code default OFF; ENABLED in the LaunchAgent plist 2026-06-25 → live on the scheduled loop**). Do NOT use `republish.js` (drops HYPERLINK rows) and do NOT use `add-stock.js` for batches (single-row); raw `sheets_update_cells` is BANNED for new/reordered rows. (3) Companion tabs: `multi_insert_conv.js` (🔍 Conviction & MoS v2) + `multi_insert_deep.js` (Buffett-Munger Deep Ranking — needed for dossier links). **IS_NEW RULE: in the companion order, any ticker that ALREADY exists in that companion tab (e.g. a prior-batch TOO_HARD like MAHSCOOTER, which the dashboard omits but companion tabs keep) MUST be `is_new:false` — else the deep/conv insert errors ("no row for new <ticker>"). The dry-run catches it. So a carried-over TOO_HARD just gets its rank re-stamped, never re-built.** (2b) **`sync_dashboard_extras.js`** — mandatory after every `multi_insert_dashboard.js` reorder: re-key **col N (Why)** from dossier `## One-line thesis` (`data/scripts/extract_dashboard_why.py`) and **cols P/Q/R** from `extracted/research/dashboard_multiples_live.json` by ticker on col B (reorder leaves P/Q/R on stale physical rows). **Col N is now the structured news-aware quick-read** `VERDICT · ✅ best: … · ⚠️ worst: … · 📰 <YYYY-MM-DD>: <factual signal>` across **EVERY dashboard row** (PR #31/#32 + col-N-for-every-row 2026-06-26): the maker is `77_synthesize_dashboard_why.py` (drives a sweep universe via `--universe sweep`), the checker `78_verify_dashboard_why.py` (Gate 8 re-derives the 📰 segment from `event_index.sqlite` so news is never fabricated and never precedes the verdict word; **Gate 7 board-alignment is ADVISORY — it RECORDS a board (mis)alignment but never fails verification**), and the **sanctioned single-column writer `tools/sheets-bridge/write_col_n.mjs`** via `79_publish_col_n.py`. **col-N is published for EVERY row — including AVOID / board-contradiction / `needs_review` names, analysed and filled exactly like any other stock. The binding Munger/Buffett CIO (vault) verdict is PRIMARY and is what col-N shows; the 56-director board panel is ADVISORY and NEVER vetoes col-N publication.** 79 publishes whenever a VALID col-N can be synthesized and skips ONLY: `verdict==NEEDS_REVIEW`, a genuinely THIN dossier (BOTH best AND worst NEEDS_REVIEW), no rendered string, or head_overflow. A board contradiction / governance flag / within-tier `needs_review` is a CONTESTED GRADE that still publishes the current verdict's col-N and is RECORDED for human adjudication (78's `board_contradictions` + `81_audit_dashboard_consistency.py`), never withheld. The 📰 clause is verdict-NEUTRAL reportage (`coln_news_segment.py`, ~80-char budget), appended LAST so truncation never eats verdict/best/worst. On an L1 head edit, `71_refresh_orchestrator.py` chains 77 re-synth → 79 re-publish (col-N-only). **There are now TWO sanctioned single-column writers: `write_col_n.mjs` (col N) and `write_col_l.mjs` (col L, 1-yr-trend SPARKLINE, PR #30)** — each with a single-column assert + inverted checksum (excluded live-col set `{6,8,10,11,13,18}`) + per-row diff + backup + auto-revert + env flag (`COL_N_DASHBOARD_WRITE=1` / `COL_L_DASHBOARD_WRITE=1`); `lib/dashboard-format.js` now renders a diagnosable `—` sparkline fallback instead of a silent blank. (4) **Lock formatting:** if layout changed, **`introspect-dashboard.js`** → refresh `dashboards/action-dashboard-style.json` (must be **18-col A–R**); then **`lock-dashboard-style.js`** to extend banding/CF — running lock with a stale capture corrupts the sheet. (5) `link-authors.js` only if Substack names were added. (6) Reindex (next bullet) → **reload daemon** → verify.
- Values: conviction = conv_v2, buy-below = buy_below_v2 (MoS-gate), verdict = verdict_v2; FOREVER/COMPOUND → Sell "DON'T SELL" (Upside "∞ hold"); **WATCH/AVOID/TOO_HARD → numeric Sell = iv_high** (rule 8 — NEVER blank a non-FOREVER Sell/Upside; Upside formula `=IF($D="FOREVER","∞ hold",TEXT(($H-$G)/$G,"+0%;-0%"))` needs a numeric Sell). **NEVER hand-paint C/J/K — they auto-color via native conditional formatting** (K&C green when (H−G)/G>50% or FOREVER/COMPOUND, yellow 30–50%; J yellow when within 20% of buy-below; AVOID/TOO_HARD never colored). E/F/G/H must be NUMBER-typed (₹#,##0). `sheet-exec.js` runs generic ops.
- New dossiers → embed into RAG: `.venv/bin/python data/scripts/26_build_lancedb_index.py --vault vault --db vault/.lancedb` (this script auto-reloads the warm daemon; confirm `/health` after).
- **🔍 Conviction & MoS v2 (gid 1264181600):** rewrite the full per-stock table (rank, ROCE/ROE, FCF, IV range,
  MoS%, req MoS%, clears-bar, buy-below, verdict, conviction rationale, sell logic).
- **⚙️ Machinery v2 (gid 49292954):** the documented process — update only if the machinery itself changes.
- **Buffett-Munger Deep Ranking (gid 508986127):** re-stamp col A = new rank + col I = verdict for ALL, then
  `sortRange` by rank (so dashboard "view" hyperlinks → row = rank+1 resolve). Add rows for new stocks (C&W prose).
- Back up the prior engine/grade state (e.g. `extracted/dengine/backup_v1/`). Sync `avgCost` from INDmoney
  (`mcp__indmoney__networth_holdings IND_STOCK`: avg = invested_amount/total_units) for held names.
- Update memory ([[reference-paise-se-paisa-sheet]]) with the new order + FOREVER finding + whether anything cleared the MoS bar.

## KEY REGISTRY
- Sheet fileId `1N87younF990u-YGMOAiT8q6X-EtZ3jVovlWCF44orEY`; tabs: **Action Dashboard 1722681272**,
  **🔍 Conviction & MoS v2 1264181600**, **⚙️ Machinery v2 49292954**, Buffett-Munger Deep Ranking 508986127,
  🧮 D-Engine 1487890548 (demoted), Final Ranking v2 528383543, Stock Picks 747182097.
- Scripts: brain consult `data/scripts/32_consult_brain.py` (the BINDING gate — scoped+cited, see CONSULTING
  THE BRAIN); free-form vault RAG `29_vault_chat.py` (ad-hoc Q&A only); index `26_build_lancedb_index.py`;
  price-engine clerk `30_d_engine.py` (demoted); fundamentals = yfinance statements (ROCE/ROE/FCF, not `.info`).
- **Dynamic-IV + news machinery (PR #30–#34, the `news-results-refresh` loop drives these):**
  `data/scripts/80_estimate_iv.py` (price-INDEPENDENT fundamental IV by `brain_model`: multi-stage DCF for compounders /
  justified-P/B for banks-NBFC-insurance / mid-cycle DCF for cyclicals; binding-brain-grounded slugs; `compute_iv` is a
  cold-start fallback only — `--test` proves two prices → identical IV); `data/scripts/coln_iv_event_gate.py`
  (earning-power-vs-sentiment discriminator — only a structural results delta / capacity / durable order-book / restatement
  arms an IV re-grade; price/FII/MF/ratings/buy-calls → False); `data/scripts/82_rerank_guard.py` (the ONLY thing allowed to
  re-rank the LOCKED dashboard — 3-tab backup + dry-run-diff + ticker-keyed checksum vs the re-graded dossiers + auto-revert,
  behind `RERANK_AUTO=1`, **default-OFF**, `--self-test`; **invoked in the loop by `73` stage 3c** gated by RERANK_AUTO + brain-health + ≥1 L1, never from `71`); `data/scripts/sync_col_dm.py` + `tools/sheets-bridge/write_col_dm.mjs` (sanctioned col-D(verdict)/col-M(conviction) sync — reconciles the carried D/M cells to the dossier oracle so a guarded re-rank passes 82's carried-cell assertion; default dry-run, `COL_DM_DASHBOARD_WRITE=1` to write; 2-column assert + inverted checksum + per-row diff + backup + auto-revert; `--test`/`--self-test`); `data/scripts/81_audit_dashboard_consistency.py` (read-only daily
  drift auditor — re-derives every col-N cell / verdict word / 📰 / rank-position vs the source of truth, WRITES NOTHING,
  gates exit on class-1/2/5; `--strict` gates all); `data/scripts/coln_news_segment.py` (read-only 📰 segment — latest
  MATERIAL event from `event_index.sqlite` → dated factual verdict-neutral clause; never fabricates).
- Helpers in `/Users/Dhiraj/dev/invest/tools/sheets-bridge/`: `add-stock.js` (new styled row), `republish.js` (formula-preserving
  reorder + overrides), `sheet-exec.js` (generic ops runner), `verify-row.js`, `clear-row.js`, `lock-dashboard-style.js`,
  `introspect-dashboard.js` (capture live format → `dashboards/action-dashboard-style.json`), `sync_dashboard_extras.js`
  (post-reorder col N + P/Q/R by ticker), `multi_insert_dashboard.js`, `add_multiples_columns.js`. **Sanctioned single-column
  writers (single-column assert + inverted checksum + auto-revert + env flag): `write_col_n.mjs` (col N) and `write_col_l.mjs`
  (col L).** `lib/dashboard-format.js` (shared row-cell builder; diagnosable `—` sparkline fallback).
- **CONVICTION RUBRIC (1-5, judgment within gates, price-independent):** 5 = wide durable moat + pristine high
  ROCE/ROE (≥25%) + clean multi-year FCF + long reinvestment runway + aligned mgmt (almost never). 4 = strong moat +
  high returns + clean owner-earnings + good mgmt. 3 = real but narrower moat + good returns + reasonably clean FCF +
  decent runway. 2 = partial moat OR lumpy/weak FCF OR returns near cost of capital OR short/unproven. 1 = no durable
  moat (commodity/replicable/no pricing power). Gates: no-moat→1; weak-FCF→cap2; ROIC<~12%→cap2; bank-below-Ke→cap2;
  InvIT→cap2. **MoS thresholds:** conv5 ≥10%, conv4 ≥15%, conv3 ≥25%, conv2 ≥40%, conv1 ≥55%.
- Verdict colors (Dashboard col D, rows 4-60): FOREVER green, COMPOUND blue #c9daf8, WATCH amber, AVOID red.
  E/F/G/H must be NUMBERS (₹#,##0 format) for the live GOOGLEFINANCE/Status/sparkline engine to work.
