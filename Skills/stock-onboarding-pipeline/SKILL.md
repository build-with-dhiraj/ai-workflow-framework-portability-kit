---
name: stock-onboarding-pipeline
description: >
  Onboard new Indian stocks into the "Paise se Paisa" Action Dashboard end-to-end — the matured
  pipeline (deep dossier → blended advisor board with a strict FOREVER gate → deterministic D-Engine
  re-rank → publish). Use when the user says "add stocks", "add the next batch", "onboard <tickers>",
  "grow the dashboard", or wants to extend the 20→N stock TO-BUY list. Workspace: /Users/pw/invest,
  sheet fileId 1N87younF990u-YGMOAiT8q6X-EtZ3jVovlWCF44orEY.
---

# Stock Onboarding Pipeline

The single source of truth for adding stocks to the Action Dashboard. Follow the stages in order.
This is the *distilled* mature workflow — every step earned through prior batches. See
[[reference-paise-se-paisa-sheet]] and [[feedback-indian-mentors-lens]] in memory for context.

## North star
The dashboard is a **search for ONE strictly-lifelong hold (FOREVER)** — not a buy-list. The Indian
Substack analysts (Vaibhav & Gaurav Tambade = "India's Buffett/Munger"; plus Karan Shah, The Megatrend
Investor, Dhruva) supply the bull thesis + ground-truth context; **Charlie Munger & Warren Buffett are
the FINAL arbiters of "is this lifelong."** Finding zero FOREVER names is an acceptable, expected result.
Patience is the edge.

## HARD RULES (never violate)
1. **Never re-grill / re-dossier stocks already done.** Existing dossiers in `vault/research/dossiers/*.md`
   are frozen inputs. Only dossier the NEW stocks.
2. **Always re-rank the WHOLE set** (old + new) after adding — never just the new ones.
3. **No fabricated citations.** Dossier `cites_principles` may contain ONLY slugs the vault RAG actually
   returns (`data/scripts/29_vault_chat.py ... --json-out`). Abstain + flag if the vault is thin.
4. **Method-appropriate valuation.** DCF for operating cos; **justified-P/B for banks & sub-book names**;
   **distribution-yield for InvITs** (strip return-of-capital); **multiple-on-mid-cycle-EPS for commodity
   cyclicals** (the DCF under-converts FCF — trust the multiple, demand bigger MoS). Check for stock splits.
5. **Read the article AND its comment thread** (Substack API — comments are real signal).
6. **4-tier verdict** exactly one per stock: FOREVER / COMPOUND / WATCH / AVOID.

## MODEL / EFFORT TIERING (not ultracode)
- Dossier workers (the bulk): **Sonnet**, 1 rigorous pass each, run in a **Workflow** (resumable).
- Board + strict FOREVER gate + adversarial verify: **Opus/Fable** (few agents, high stakes).
- D-Engine re-run + sheet publish: **mechanical** (Bash/MCP) — no model reasoning, engine already verified.

## STAGE 0 — Scope & ingest (orchestrator, mechanical)
- Derive the new stocks = universe (`extracted/_final_v2.json`) minus done (`ls vault/research/dossiers/`).
  Beware name-spelling/ticker mismatches (e.g. Gemmological vs Gemological, ticker ≠ filename).
- Per stock map: author + article via `extracted/<author>.json` (`source_url/date/title`); valuation g-file
  (`grep <TICKER> extracted/valuation/v2/g*.json`); enriched financials (`grep <TICKER> extracted/enriched/batch_*.json`);
  7-factor scores (`extracted/_principles_scores_v2.json`, `_holdings_principles_scores.json`); v2 rank/theme.
- Fetch article + comments via Substack API:
  `curl -s "https://<pub>.substack.com/api/v1/posts/<slug>"` → get id;
  `curl -s "https://<pub>.substack.com/api/v1/post/<id>/comments?all_comments=true&token="` → JSON (`.comments[].children`).
- Flag **sector pieces** (one URL → many stocks, e.g. Megatrend "Transformer/Recycling/EV&BESS", Karan
  "AI Data Center"): the worker extracts ONLY its stock's section.
- Verify NSE symbol (live price ≈ expected to ±5%) — recently-listed names may need .BO or symbol fixes.

## STAGE 1 — N parallel dossier workers (Workflow, Sonnet)
Each writes `vault/research/dossiers/<TICKER>.md` to **IGI-depth** (read `vault/research/dossiers/IGI.md`
as the exact template; ~150 lines; frontmatter schema per `vault/CLAUDE.md`: note_type, ticker, company,
sector, status, conviction_level, filter_1_circle..filter_6_opportunity_cost (pass|partial|fail),
intrinsic_value_estimate, current_price, margin_of_safety_pct, cites_principles, kill_criteria, created).
Worker steps: (1) WebFetch the article + Substack comments (honest paywall handling); (2) fresh web research
(latest quarter, price, splits, governance); (3) dual-lens RAG (`29_vault_chat.py "<q>" --k 10 --mentor
charlie-munger|warren-buffett --json-out extracted/grilling/<TICKER>_{munger,buffett}.json` — use ONLY
returned slugs); (4) method-appropriate IV/MoS + buy-below/sell informed by the author's target; (5) a
named **"Author's voice"** section + a **"Comment-thread red flags"** section; (6) 4-tier verdict, kill-
criteria (inversion), honesty flags. Self-validate before returning. **Barrier:** all dossiers exist.

## STAGE 2 — Blended board over the FULL set (Opus/Fable)
Four advisor agents (Gaurav, Vaibhav, Charlie, Warren personas) tier ALL stocks (old digests + new
dossiers); India theses + comment threads feed context; reconcile into one TO-BUY list. Record each
advisor's vote + split notes. Output `extracted/grilling/<batch>_ranking.json`.

## STAGE 3 — Strict FOREVER gate (Opus/Fable, adversarial)
For every FOREVER *candidate* only: a skeptic makes the strongest case it is NOT a strictly-lifelong hold
(moat that can't be lost overnight, owner-earnings, management/alignment, price not demanding heroics).
Survive all axes → FOREVER; else demote. Default to demote. Honor any Chairman (user) override explicitly.

## STAGE 4 — D-Engine deterministic re-rank (mechanical)
- Append the new stocks to `extracted/dengine/stock_params.json` (ticker, yahoo, E=buy-below, H=sell or
  null for FOREVER, verdict, conv, flags). Fetch their daily histories (`extracted/dengine/fetch_price_histories.py`
  pattern, yfinance, 1y; validate last_close ≈ live ±5%; split-check). Re-run
  `.venv/bin/python data/scripts/30_d_engine.py --data ... --stocks ... --params ... --out extracted/dengine/d_engine_results.json`.
- Engine = GBM first-passage (reflection principle), Bayesian-shrunk drift, EV(buy-now) vs EV(wait), half-Kelly.
  **Rank key = lexicographic (verdict_tier [FOREVER<COMPOUND<WATCH<AVOID], −conv, −D_score); FOREVER ranked by
  P(entry).** Do NOT re-verify the math (one-time done); just feed new data. Determinism: two runs byte-identical.

## STAGE 5 — Publish (mechanical, no rework)
- New dossiers → embed into RAG: `.venv/bin/python data/scripts/26_build_lancedb_index.py --vault ... --db vault/.lancedb`.
- Append new rows to "Buffett-Munger Deep Ranking" (gid 508986127), update its A=rank + I=tier columns for ALL,
  then `sortRange` by rank.
- Extend "🎯 Action Dashboard" (gid 1722681272) via `/Users/pw/.cursor/mcp-servers/google-drive/add-stock.js`
  (`--rank --ticker --symbol --company --verdict --buyBelow --avgCost --sell --maxSize --conv --why --priceFallback`;
  row = 3+rank; FOREVER → `--sell "DON'T SELL"`; InvIT → BSE symbol patch on G/L; styling auto via locked
  buffer to row 60). Re-sort all 20+N rows to the new D-Engine order; verify with `verify-row.js`.
- Update the "🧮 D-Engine" tab (gid 1487890548) with the full new results table.
- Sync `avgCost` from INDmoney (`mcp__indmoney__networth_holdings IND_STOCK`) for any held names.
- Update memory ([[reference-paise-se-paisa-sheet]]) with the new order + any FOREVER finding.

## KEY REGISTRY
- Sheet fileId `1N87younF990u-YGMOAiT8q6X-EtZ3jVovlWCF44orEY`; tabs: Action Dashboard 1722681272,
  Buffett-Munger Deep Ranking 508986127, D-Engine 1487890548, Final Ranking v2 528383543, Stock Picks 747182097.
- Engine `data/scripts/30_d_engine.py` (+ spec `dashboards/d-engine-spec.md`); RAG `data/scripts/29_vault_chat.py`,
  index `data/scripts/26_build_lancedb_index.py`; dashboard helper `~/.cursor/mcp-servers/google-drive/add-stock.js`.
- Verdict colors (conditional fmt on Dashboard col D, rows 4-60): FOREVER green, COMPOUND blue #c9daf8,
  WATCH amber, AVOID red. Upside col K = numeric + blue gradient (lightest→darkest = low→high).
