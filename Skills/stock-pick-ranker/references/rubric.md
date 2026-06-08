# Principles Rubric — 7 factors, weights, and mapping

Score each stock **1–5 (0.5 steps)** on the seven factors. Use **live financials** for the
quantitative factors (F2/F3/F4) and the **author thesis** for the qualitative ones (F1/F5/F7). F6 uses
promoter/governance data. The factors synthesise eight investing-principle sources ("MindSnacks":
Buffett, Munger, Dhandho/Pabrai, Howard Marks, Taleb, Naval, Cialdini-inverted) cross-checked with two
quant frameworks (Greenblatt Magic Formula = ROIC + earnings yield; Piotroski F-Score = fundamental
health). Use ONLY provided evidence — never outside knowledge or invented numbers. If a factor can't be
judged, score 3 (neutral) and say so.

## Factor anchors

**F1 Moat & Position** — *Dhandho moats, Munger circle of competence, Buffett quality.*
5 = explicit monopoly / near-monopoly / regulatory barrier / winner-take-most / certification / high
switching costs central to the thesis. 3 = moderate/emerging. 1 = commodity, price-taker, no moat.

**F2 Margin of Safety (valuation)** — *Dhandho "tails I don't lose much", Marks price-vs-value; Greenblatt earnings-yield.*
5 = clearly cheap vs quality (e.g. P/E <~15 with high ROCE, low P/B with recovery, deep mispricing/trough
earnings). 3 = fair. 1 = priced-for-perfection (P/E >~70, all-time-high). If a high P/E is OPTICAL
(depressed/one-off earnings), judge on a normalised basis; a low P/E on a structurally declining business
is not true safety.

**F3 Capital Efficiency & Compounding** — *Buffett quality, Munger compounding, Naval leverage; Greenblatt ROIC + Piotroski profitability.*
5 = ROCE/ROE ≥~25-30% + healthy margins + asset-light. 4 = ~18-25%. 3 = ~12-18%. 2 = ~8-12%. 1 = <8%
or negative. **Banks/NBFCs:** use ROA/ROE + franchise, not ROCE (ROA >2% & healthy ROE = strong).

**F4 Antifragility & Balance Sheet** — *Taleb antifragile, Buffett/Guerin avoid leverage; Piotroski leverage/liquidity.*
5 = net cash / debt-free and/or survived shocks (e.g. COVID). 3 = D/E ~0.3-0.6. 1 = D/E >1 or losses
straining solvency. **Lenders:** use CAR + GNPA (CAR >18% & GNPA <2% = strong); **InvIT:** net-debt/AUM + rating.

**F5 Asymmetry & Optionality** — *Taleb convexity, Dhandho "heads I win".*
5 = large explicit upside (5x/10x) + limited downside / unpriced optionality. 3 = moderate. 1 = capped/negative skew.

**F6 Management & Skin-in-game** — *Buffett integrity, Taleb skin-in-game, Naval accountability.*
5 = strong aligned owner-operator, high promoter holding, ZERO pledge, clean governance. 3 = neutral /
widely-held-but-clean (DEFAULT when silent). 1 = governance red flags (high pledge >20%, SEBI action,
related-party concerns, MPS-dilution overhang).

**F7 Convergence & 2nd-level Edge** — *Munger Lollapalooza, Marks 2nd-level/anti-euphoria, Cialdini (inverted → discount hype).*
5 = multiple stacking tailwinds + clear, fundamentally-grounded variant perception. 3 = some edge.
1 = single thin driver OR consensus euphoria / a thesis that's mostly narrative/hype.

**Inversion (Munger)** is applied as low scores, not a separate factor: governance flags → low F6;
all-time-high + extreme multiple → low F2; high leverage → low F4.

## Weights (sum = 1.0)

| Factor | Weight |
|---|---|
| F1 Moat | 0.20 |
| F3 Capital Efficiency | 0.20 |
| F2 Margin of Safety | 0.15 |
| F4 Antifragility | 0.15 |
| F6 Management | 0.10 |
| F5 Asymmetry | 0.10 |
| F7 Convergence | 0.10 |

`principles_score (0–100) = 20 × Σ(weight × factor)`. (`rank.py` applies this; don't compute by hand.)

## Confidence

Set **High** for every stock once the live hard data is complete (the user's standing rule: no
low-confidence stocks). Earnings-quality caveats (one-off tax, deferred-tax gain, trough/exceptional
base, calendar-year reporting, very recent listing) go in `red_flags` + rationale — NOT as a confidence
downgrade.

## Output schema (`_principles_scores_v2.json`)
```json
{"scores":[{"company":"","f1":0,"f2":0,"f3":0,"f4":0,"f5":0,"f6":0,"f7":0,
  "confidence":"High","key_live_metrics":"the decisive live numbers used",
  "rationale":"1-2 sentences citing live data + thesis","top_principle":"","red_flags":[]}]}
```
