# Workbook schema — Substack_Stock_Picks.xlsx

Default path: `/Users/pw/invest/Substack_Stock_Picks.xlsx`. **Always read the live workbook first**
(`openpyxl.load_workbook`) and match existing headers — the layout below is the as-built reference, but
trust the file over this doc if they diverge. **Preserve every existing sheet.** Use `/usr/bin/python3`.

When adding stocks: **append** to the data sheets, **fully recompute** the ranking/derived sheets over
the *combined* universe (existing + new), because the ranking is relative.

| # | Sheet | On new stocks | Key columns |
|---|---|---|---|
| 1 | **Stock Picks** | **append rows** | Company · Ticker · Recommended By · Source Article(s) · Date(s) · Sector · Market Cap · Valuation · Profitability · Growth · Balance Sheet · Other Key Metric · Upside/Target · Stance/Note · Thesis Crux · Key Risk · Link(s). *(author-reported snapshot)* |
| 2 | **Principles (MindSnacks)** | leave as-is | Title · People · Key Idea · Takeaways · Date · Link. *(philosophy reference; only changes if new principle pieces are added)* |
| 3 | **Appendix** | append if relevant | excluded/paywalled/thematic posts (Author · Title · Date · Reason). |
| 4 | **Master Ranking** | **recompute** | Master Rank · Stock · Recommended By · Theme · F1 Moat · F2 MoS · F3 CapEff · F4 Antifragile · F5 Asymmetry · F6 Mgmt · F7 Converge · Principles /100 · Hotness /100 · Master /100 · Confidence · Key Live Metrics · Top Principle · Red Flags · Why. *(pure principles, pre-valuation-blend)* |
| 5 | **What's Hot** | **recompute** | Theme · #Picks · #Distinct Authors · Avg Master Score · Stocks  +  per-stock frequency (Stock · #Authors Recommending · #Corpus Mentions). |
| 6 | **Live Financials (\<month\>)** | **append rows** | Master Rank · Stock · Ticker · As of · Price ₹ · Mkt Cap ₹cr · P/E · P/B · ROCE % · ROE % · Op Margin % · Net Margin % · Rev Growth % · PAT Growth % · Debt/Equity · Net Cash/Debt · ROA % · GNPA % · CAR % · Promoter % · Pledge % · Div Yield % · Governance Notes · Data Source(s). *(sheet name is date-stamped — if refreshing financials wholesale, add a new dated sheet rather than overwriting history)* |
| 7 | **Valuation (DCF)** | **append + recompute order** | Stock · Current ₹ · DCF Base ₹ · Bear ₹ · Bull ₹ · Base Upside % · WACC % · Terminal % of EV · Rev Growth Y1→Y5 · EBITDA Margin % · Terminal g % · Net Debt ₹cr · Caveats · Sources. *(forward-DCF detail)* |
| 8 | **Final Ranking** | leave as-is (superseded) | the older top-15-only valuation ranking; **Final Ranking v2 supersedes it**. Optionally delete once the user is comfortable. |
| 9 | **Final Ranking v2** ← **definitive** | **recompute** | Rank (v2) · Δ vs prior · Stock · By · Theme · Master v2 /100 · Valuation Verdict · Method · Val Score (1-5) · Confidence · MoS factor old→new · P/E · Notes. |

## Formatting conventions (match existing)
Dark header fill `1F4E78`, bold white text; freeze header (+ first 2–3 cols on wide sheets); autofilter
on header; bold the headline score column; 3-color scale on Master/Final scores; conditional fills on
the Valuation Verdict (green Undemanding/Fairly · amber Demanding · red Heroic · grey N/A); wrap
long-text columns; widths capped ~50; thin borders; valign top. Top of ranking/valuation sheets carries
a merged **methodology + "NOT investment advice"** block.

## Recompute = render from the JSON source of truth
The ranking sheets are a *rendering* of `extracted/_final_v2.json` (produced by `scripts/rank.py` over
the full universe). To refresh them: re-run rank.py over all stocks → rewrite sheets 4, 5, 7, 9 in full;
append new rows to sheets 1 and 6. `scripts/append_workbook.py` does sheets 6 + 9 and appends 1; for
full 9-sheet consistency either extend it or dispatch a builder subagent with this schema. After
writing, re-open and verify sheet count (9) and row counts.
