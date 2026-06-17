---
name: portfolio-sizing
description: >
  Use when deciding HOW MUCH to put in a position — the "Max size" (col M) decision on the Action
  Dashboard. Encodes Kelly fraction + half-Kelly for estimation uncertainty, conviction-scaled
  position ceilings consistent with the v2 conviction rubric and MoS thresholds, concentration
  discipline (few bets, hold compounders, don't over-trim winners), and opportunity-cost-aware
  allocation. This skill informs the Max-size column ONLY — it does NOT set verdict, conviction,
  or any rank input. Triggers: "how much should I put in", "what's the right position size",
  "set Max size", "Kelly fraction", "too concentrated?", "should I trim", "position limits",
  "sizing a new buy", "portfolio construction".
---

# Portfolio Sizing (the finance-desk "position sizer")

The v2 machinery grades and ranks stocks but leaves col M (Max size, % of total portfolio) as a
judgment call. This skill encodes the sizing logic so Max size is derived, not arbitrary.
**The Munger/Buffett binding CIO remains the arbiter of conviction and moat;** this skill
supplies the sizing number given the conviction and MoS the v2 machinery already produced.

## STEP 0 — Pull the canon (binding-safe)

A dedicated **`--step sizing`** is now wired in `32_consult_brain.py` (maps to
`[opportunity-cost, margin-of-safety]`) — make it the primary pull. Run it on the **blended**
corpus so the desk-synthesis sizing atomics (`vault/desk/sizing/atomic/`, weight 0.9) surface
ALONGSIDE the binding CIO, then keep the two underlying canon steps as a fallback union:
```bash
set -a && source /Users/pw/invest/.env && set +a
# Primary: dedicated sizing step on blended corpus (surfaces desk atomics + binding)
/Users/pw/invest/.venv/bin/python /Users/pw/invest/data/scripts/32_consult_brain.py \
  --company "<ticker or name> Kelly position sizing edge opportunity cost fractional half kelly catastrophic loss risk uncertainty liquidity" \
  --model general \
  --step sizing \
  --corpus blended \
  --json-out extracted/grilling/<TICKER>_sizing.json
# Fallback / detail: the two underlying canon steps (union the returned principles)
for STEP in opportunity-cost margin-of-safety; do
  /Users/pw/invest/.venv/bin/python /Users/pw/invest/data/scripts/32_consult_brain.py \
    --company "<ticker or name> Kelly position sizing edge opportunity cost fractional half kelly" \
    --model general \
    --step "$STEP" \
    --corpus canon \
    --json-out extracted/grilling/<TICKER>_sizing_${STEP}.json
done
```
`cites_principles` must contain ONLY slugs the consult actually returns (union across the steps).
Also run the **binding consult** (`--corpus binding`, step `opportunity-cost`) and explicitly pull
the CIO's ruin-avoidance constraint: `[[never-risk-catastrophic-loss]]` and
`[[reserve-for-unknowns-5-percent-rule]]` (a 5% reserve for being wrong). Sizing is meaningless
without knowing what else competes for the same capital — and the conviction-5 **25% ceiling
(step 3) is the BINDING CIO's hard catastrophic-loss limit, not a Kelly output.** Kelly only
chooses where *below* that ceiling to sit (`[[kelly-proposes-catastrophic-loss-test-disposes]]`).

## THE CORE LOGIC (in order)

### 1. Kelly fraction — the theoretical ceiling

From `kelly-fraction-calculation` (Thorp): `f* = edge / odds`, where:
- **edge** = expected excess return above opportunity cost (IRR of this position − ~10% Nifty hurdle)
- **odds** = the "b" in the bet — upside multiple from here to IV-high

> **Caveat — `edge / b` is a single-bet approximation, not exact binary Kelly.** The exact
> binary-bet Kelly is `f* = p − q/b` (p = win prob, q = 1−p), which `edge/b` drops the explicit
> loss-probability term from. Treat `edge/b` as a serviceable heuristic whose imprecision the
> half-Kelly haircut (step 2) is designed to absorb — not as a precise optimum. The continuous
> form below IS exact for log-normal returns.

In continuous / stock-market form (from `continuous-approximation-for-portfolio-kelly`):
`f* = (m − r) / s²` where m = expected return, r = risk-free (~6.9%), s² = return variance.

**Kelly is the mathematical ceiling — never the default size.** `kelly-long-run-dominance-test`
(Thorp) shows full Kelly maximizes long-run growth, but the path is brutal: drawdowns are
stomach-churning (`kelly-drawdown-probability-formula`: Prob(ever halving) ≈ 50% at full Kelly).

### 2. Half-Kelly for estimation uncertainty — the operating default

From `fractional-kelly-for-margin-of-safety` (Thorp) and `partial-kelly-for-volatility-control`
(Mauboussin): reduce to **half-Kelly (f = 0.5 × f*)** as the default operating size. Half-Kelly:
- reduces drawdowns substantially (roughly halves them) for ~75% of the long-run growth
- provides a margin of safety against IV estimation error and parameter uncertainty
- keeps psychological stress manageable (`loss-aversion-check` — frequent checks of a volatile
  portfolio produce myopic loss aversion and bad decisions)

From `fractional-kelly-for-risk-tolerance` (Thorp): use `f = c × f*` where c < 1. For this OS,
**c = 0.5 is the default; c = 0.33 for a conviction-3 or lower position.**

### 3. Conviction-scaled ceiling — the hard cap

The v2 conviction rubric already encodes quality judgment. Map directly to a Max-size ceiling:

| Conviction | MoS required | Max size cap | Notes |
|-----------|-------------|-------------|-------|
| 5 — wide durable moat, pristine returns, long runway | ≥ 10% | **25%** | Almost-never tier; size up only when MoS is real |
| 4 — strong moat, high returns, clean owner-earnings | ≥ 15% | **20%** | Core position territory |
| 3 — real but narrower moat, good returns, decent runway | ≥ 25% | **12%** | Mid-weight; watch for moat erosion |
| 2 — partial moat OR lumpy FCF OR returns near cost of capital | ≥ 40% | **6%** | Exploratory; prove thesis before adding |
| 1 — no durable moat | ≥ 55% | **3%** | Research / optionality only; do not compound |

These ceilings are the hard cap from `position-sizing-discipline` (Mauboussin): "betting too much
leads to near-certain ruin." The conviction rubric gates them; Kelly determines where within the
range to sit.

**Starting size = half-Kelly × conviction cap, floored at 1% for any BUY signal.**

### 4. Opportunity-cost-aware allocation

From `opportunity-costs-in-position-sizing` (Thorp): the optimal fraction per position **decreases
as the number of attractive alternatives increases.** When better ideas compete for capital,
reduce the current size.

Concrete rule: compare the new position's expected IRR to the best existing idea. If this
position's IRR advantage over the benchmark is <2%, treat its Kelly weight as halved again.
If it clears the IRR hurdle by >5%, the full half-Kelly applies.

From `joint-bet-correlation-adjustment` (Thorp): when two positions have high positive correlation
(same sector, same India-growth macro driver), reduce both fractions — the joint distribution
reduces the effective edge of the pair.

### 5. Concentration discipline — hold winners, don't over-trim compounders

From `geometric-mean-maximization` (Mauboussin): maximize geometric mean, not arithmetic. This
means **letting winners run**. A FOREVER or COMPOUND name that has appreciated past its initial
weight ceiling should NOT be mechanically trimmed — sell only on thesis-break, moat erosion, or a
strictly better opportunity.

From `variance-impact-on-compounding` (Mauboussin): higher variance reduces geometric mean.
Compounders with stable, high-ROIC earnings have lower true variance than their price volatility
suggests — don't over-penalize them for mark-to-market swings.

`arithmetic-vs-geometric-return-diagnosis` (Mauboussin): for a lifelong hold, use geometric mean
analysis. A position running from 20% to 35% of the portfolio because the business compounded is
**not concentration risk — it is the intended outcome.** Trim only if conviction drops.

`compound-growth-efficient-frontier` (Thorp): the set of fractional Kelly strategies (0 ≤ c ≤ 1)
forms the efficient frontier. A FOREVER at 30% of portfolio sitting on the efficient frontier is
correct; adding a fifth conviction-3 name to "diversify" moves the portfolio off it.

### 6. Distribution and tail awareness

From `distribution-awareness` (Mauboussin): stock returns are fat-tailed, not normal. The standard
Kelly continuous formula under-estimates downside risk. Mitigants already in the machinery:
- Half-Kelly (step 2) absorbs most of this
- `scenario-analysis-black-swans` (Thorp): explicitly model the "company is impaired" scenario
  with non-trivial probability before sizing. If the loss scenario would violate the utility
  function (`utility-function-consistency-test` — Mauboussin), reduce size until it doesn't.

### 7. Risk is not uncertainty — the gate before any size-UP

Before sizing a position *above* its baseline half-Kelly, distinguish **uncertainty** (a wide range
of outcomes) from **risk** (the probability of permanent capital loss) —
`[[risk-not-uncertainty-sizing-arbiter]]`. A Pabrai-style low-risk / high-uncertainty bet
(`[[low-risk-high-uncertainty-bets]]`) may earn a *larger* fraction, but **only after** the
black-swan / impairment scenario (step 6) confirms the downside is genuinely **bounded**. If it is
not, the binding `[[be-cautious-when-uncertainty-is-high]]` prevails and size is *reduced*, not
raised. Volatility is not the risk metric (`[[risk-is-not-volatility]]` — Marks); a calm chart can
still mask permanent-loss risk. **This gate is a hard precondition, never a footnote: uncertainty
alone is never a license to size up.**

### 8. India liquidity / promoter haircut (small-mid-caps)

For Indian small/mid-caps, apply a one-directional haircut that can only push size *below* the
conviction cap, never above it (`[[india-liquidity-haircut-on-kelly-size]]`). Discount for:
- **thin float / low ADV** — you cannot exit at the marked price in size
- **circuit-filter exit risk** — lower-circuit days block selling exactly when you want out
- **promoter pledge** — pledged-share unwinds can force cascading selling

Marks' `[[risk-is-not-volatility]]` is the anchor: illiquidity *hides* risk that the half-Kelly
variance term does not see, and fat tails (`distribution-awareness`) make it worse. Keep the
multiplier conservative and reductive only.

## THE SIZING PROCEDURE (step-by-step)

1. Confirm v2 conviction (1-5) and MoS% from the machinery output. If MoS < required threshold,
   Max size = 0% (no position; WATCH, not BUY).
2. Read IV-high (the sell target) and live price (col G). Compute upside `b = iv_high / live − 1`.
3. Estimate edge = expected IRR from here − 10% Nifty hurdle (use the buy-below IRR from the
   machinery, which already bakes in the MoS).
4. Compute `f* = edge / b` (simple Kelly for a single bet). If f* > conviction cap → use cap.
5. Apply `f = 0.5 × f*` (half-Kelly default); if conviction ≤ 3, use `f = 0.33 × f*`.
6. Adjust down if correlated positions already exist (step 4 above).
7. **Run the risk≠uncertainty gate (core logic 7) before any size-up**, and apply the India
   liquidity/promoter haircut (core logic 8) for small-mid-caps. Both can only *reduce* f.
8. **Temperament check** (`[[sizing-is-where-temperament-is-priced]]`): cap f at the size you can
   hold through a 25–50% drawdown without panic-trimming. If half-Kelly would force a panic-trim,
   the temperament-bounded size is smaller — holding it intact is what `geometric-mean-maximization`
   actually requires.
9. Floor at 1% for any position that clears the MoS bar. Cap at conviction ceiling (step 3 table).
10. **Write Max size = f to col M.** This is the target ceiling — actual buys may start smaller
    and build as the thesis confirms (`edge-identification` — only positions where your analysis
    diverges from the market earn a real edge worth sizing).

## OUTPUT (feeds the dashboard)

A single number: **Max size % of total portfolio** (col M, Action Dashboard gid 1722681272).
State the conviction, half-Kelly fraction, and any cap or correlation adjustment applied.
Do NOT write this number to verdict, conviction, buy-below, or any other column — it is purely
a position-construction input.

## Hard rules

1. **Max size informs col M only.** Verdict, conviction, and MoS are set by the v2 machinery and
   the binding CIO — this skill does not touch them.
2. **Half-Kelly is the default.** Full Kelly is never the operating size; the drawdown path is
   unacceptable (`kelly-drawdown-probability-formula`).
3. **Conviction cap is a hard ceiling.** Kelly may suggest more than the conviction cap — use
   the cap, not the raw Kelly number.
3a. **Kelly proposes, the catastrophic-loss test disposes** (`[[kelly-proposes-catastrophic-loss-test-disposes]]`).
   Whenever `f*` (or even half-`f*`) exceeds what survives a permanent-loss / impairment scenario,
   cut to the *survivable* size — never round up to the cap. The half-Kelly haircut and the 25%
   ceiling exist to serve the CIO's distrust of precise math (`margin-of-safety-over-mathematical-risk`,
   `scenario-analysis-black-swans`), not merely to absorb estimation error. The cap is a CIO-set
   ceiling the formula may *approach*, never a number a high computed `f*` *justifies reaching*.
4. **Do not trim a compounder mechanically.** Price appreciation past the initial weight is the
   intended outcome for a FOREVER/COMPOUND hold. Trim only on thesis-break or a strictly better
   alternative that frees up capital advantageously (`geometric-mean-maximization`).
5. **Cite only slugs the consult returns.** If the sizing step returns thin principles, flag it
   and apply the half-Kelly / conviction-cap table conservatively. The desk-synthesis sizing
   atomics (`[[kelly-proposes-catastrophic-loss-test-disposes]]`, `[[risk-not-uncertainty-sizing-arbiter]]`,
   `[[india-liquidity-haircut-on-kelly-size]]`, `[[sizing-is-where-temperament-is-priced]]`) are
   tagged `analyst_role: sizing` and surface on `--corpus blended` (or `--step sizing`); the Thorp/
   Mauboussin math lives in `--corpus canon`. Query both — `--role sizing` alone will miss the canon math.
6. **The Munger/Buffett binding CIO remains the arbiter.** This skill supplies the number;
   the CIO supplies the judgment that earns the conviction score that caps the number.
