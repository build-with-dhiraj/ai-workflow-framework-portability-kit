# Valuation — forward DCF, reverse-DCF, and the reliability-weighted blend

Valuation is an **overlay** on the quality rank, not the driver (it moves ~15% of the score via the
Margin-of-Safety factor). Its job is to flag which high-ranked names are *cheap for their quality* vs
*priced for perfection*. Use the **right method per stock type** and be honest about model limits.

## The engine
Import the bug-fixed model — do NOT reimplement:
```python
import sys; sys.path.insert(0, "/Users/pw/.claude/skills/creating-financial-models")
from dcf_model import DCFModel
```
Run with `/usr/bin/python3`. The model now: decouples `depreciation_percent` from capex; normalises
terminal working-capital (ΔNWC = NWC × terminal_growth) so **equity value is monotonic in revenue
growth** (a plain binary search for the reverse solve is therefore valid); and exposes a `terminal_fcf`
override. `scripts/valuation_runner.py` wraps all of this.

## Discount-rate assumptions (India; tunable)
- Cost of equity Ke = `risk_free + beta × ERP`, with **risk_free ≈ 6.9%** (India 10Y G-sec) and
  **ERP ≈ 5.5%** (a defensible mid; an earlier run used 7.5% which was too punitive and made every
  quality name look "Heroic"). Beta per stock (≈1.0–1.2 if unmeasured, note it).
- WACC via `model.calculate_wacc(...)`; **terminal_growth ≈ 4.5%** (≤ risk-free); 5-year projection;
  tax 25%.
- Update risk_free/ERP if the user asks or rates have clearly moved.

## Method by stock type
- **Non-financial, profitable → reverse-DCF + forward DCF.** Set `depreciation_percent` ≈ true D&A
  (P&L depreciation / revenue), **not** expansion capex; set `capex_percent` ≈ recent capex (note if
  expansion-elevated). Forward → fair value/share + upside. Reverse → binary-search a flat revenue
  growth `g` in [-0.10, 0.80] so equity/share == current price (monotone, so it converges). That `g`
  is the **market-implied growth**.
- **Bank / NBFC / power-trading → justified-P/B (NO DCF).** Implied book growth `g = (P/B·Ke − ROE)/(P/B − 1)`;
  compare to sustainable (≈ ROE × retention, capped at loan/AUM growth). If ROE < Ke, a P/B > 1 is
  pricing a future ROE recovery — flag it.
- **Loss-maker → EV/Sales (NO DCF).** Judge EV/Sales vs growth/path-to-profit; usually a low score; Low confidence.
- **InvIT → distribution-yield.** Compare yield to a ~9–10% required yield; note net-debt/AUM, rating,
  return-of-capital component.
- **Cyclical / commodity → reverse-DCF on a THROUGH-CYCLE margin** (not peak/trough), flagged **Low confidence**.

## Verdict + score
Compare implied growth (or implied book growth) to demonstrated 3Y CAGR (or sustainable):
≤0.8× → **Undemanding**; 0.8–1.1× → **Reasonable**; 1.1–1.5× → **Demanding**; >1.5× OR implied >30%
sustained → **Heroic**. When demonstrated growth ≈0 or negative, classify on the *absolute* implied
growth instead (a flat/declining business with low implied growth can still be Undemanding).
Map to `valuation_score_1to5`: Undemanding 4.5–5 · Reasonable 3.5–4 · Demanding 2–2.5 · Heroic 1–1.5.

## Known model limitation → why we reliability-weight
Even fixed, this is a *simplified* 5-year FCFF DCF. It still **under-converts FCF for thin-margin,
high-NWC, and high-capex names** — for them the reverse solve can clamp at the 0.80 ceiling or report
"price unreachable," tagging genuinely-cheap names (e.g. a P/E-12 compounder) as "Heroic." That is a
**model artifact**, not reality. So:
- Mark a read **artifact / Low confidence** when: it clamps/can't reach price; the firm is thin-margin
  /high-NWC/cyclical; or the verdict is Heroic but the P/E is actually low (<~18).
- In those cases, **trust the multiples-based Margin-of-Safety (factor F2)** over the reverse-DCF.

## The blend (done by `scripts/rank.py`)
The reverse-DCF `valuation_score` is blended into F2 weighted by reliability, so artifacts can't corrupt
the rank:
`F2' = w·valuation_score + (1−w)·F2_old`, where
`w = 0.55` (reverseDCF, High conf, not artifact) · `0.40` (Med) · `0.20` (artifact or Low) ·
`0.45` (justifiedPB or yield) · `0.25` (EV/Sales). Then the principles score is recomputed with F2'
and re-ranked. Net effect on a curated growth universe: the ranking is *confirmed* with modest
movement — value-for-quality names tick up, names pricing unproven re-ratings tick down.

## Output schema (`valuation/v2/*.json`)
```json
{"v2":[{"company":"","method":"reverseDCF|justifiedPB|EV/Sales|yield","current_price":0,
  "discount_rate_ke":0,"implied_growth_pct":0,"demonstrated_growth_pct":0,"verdict":"",
  "valuation_score_1to5":0,"fair_value_base":0,"upside_pct":0,"confidence":"High|Med|Low",
  "artifact":false,"notes":"","sources":[""]}]}
```
Everything here is **illustrative / assumption-driven — not investment advice**, and the workbook says so.
