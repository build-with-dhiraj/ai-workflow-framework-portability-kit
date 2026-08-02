---
name: capital-allocation-judge
description: >
  Use when assessing how well a CEO/management team allocates capital — to score the
  CONVICTION dimension "management quality" with a structured, cross-CEO scorecard drawn
  from William Thorndike's Outsiders framework. Applies during Stage 1 dossier writing,
  Stage 3 conviction re-grade, and any ad-hoc "is this management great at capital
  allocation?" question. The Munger/Buffett binding CIO already carries Buffett's own
  allocation wisdom — this skill ADDS the cross-CEO Outsiders methodology: per-share-value
  as the CEO scoreboard, opportunistic (not programmatic) buybacks, FCF/owner-earnings over
  GAAP, centralized capital + decentralized ops, leverage matched to cash-flow predictability,
  and contrarian analytical discipline. Triggers: "capital allocation", "how does management
  deploy FCF", "are buybacks value-accretive", "Outsiders framework", "management scorecard",
  "owner-operator quality", grading mgmt in any v2 conviction step.
---

# Capital-Allocation Judge (the finance-desk "Outsiders analyst")

The v2 conviction rubric scores management quality as part of the conviction grade, but gives
no structured method for *how* to read a management team's capital-allocation discipline.
This skill encodes the Thorndike Outsiders cross-CEO scorecard as a reusable procedure.
Ground every judgment in the canon (below) — never free-hand a management grade.

**The binding Munger/Buffett vault remains the FINAL CIO.** This skill supplies the *scorecard
and method*; the vault supplies the *judgment* (moat, owner-alignment, integrity) and the
*verdict*. Both must clear before conviction rises above 3.

## STEP 0 — Pull the canon (binding-safe)

The method now lives in **two** layers: the Thorndike Outsiders canon atomics (tagged
`role=capital-allocation`) AND the 30 external perspective voices that richly cover the India
reinvestment-runway question (Raamdeo QGLP, Saurabh Mukherjea capital-discipline, Terry Smith,
Manish Gupta, the Tambade asset-light lens). **Do a dual-pull and union the slugs:**

```bash
# (a) BINDING — the CIO ranking and arbiter (run ALWAYS; these atoms are the verdict)
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --corpus binding --step capital-allocation \
  --company "<company> capital allocation owner earnings reinvest above cost of capital buybacks dividends" \
  --model general --json-out extracted/grilling/<TICKER>_capalloc_binding.json

# (b) PERSPECTIVES — the India runway voices (context/divergence only, NEVER the verdict)
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --corpus perspectives --step capital-allocation --k 15 \
  --company "<company> reinvestment runway incremental ROCE QGLP asset light capital discipline long runway" \
  --model general --json-out extracted/grilling/<TICKER>_capalloc_persp.json
```

`cites_principles` ⊂ the union of returned slugs.

**Retrieval wiring (canonical pattern).** A dedicated `--step capital-allocation` exists; the canonical
pull is the dual-corpus pattern above — `--corpus binding` for the CIO ranking, and `--corpus perspectives`
(with runway seed terms on `--company`) to surface the 30 external India-runway voices. Use `--corpus blended`
when you want the desk-synthesis atomics below alongside the binding layer in one call.

- Score the perspectives layer **evidence-gated** — credit a long runway only on *actual incremental
  ROCE history*, never on a projected TAM narrative. The perspectives are promotional (managers and
  newsletter writers talking their book), so they are context and divergence-detection, never the
  verdict.
- **ABSTAIN on any axis whose atom the consult does not return** — do not assign a non-zero score on
  an axis you could not ground. Thin retrieval ⇒ lower the grade, never fabricate the slug.

## THE BINDING PRIOR (what the CIO already holds)

Before the scorecard, anchor to the CIO's own allocation ranking — the scorecard measures
**HOW WELL** management executes against this prior, not **WHETHER** the prior is right. The
binding order of preference, from [[owner-earnings-and-capital-allocation-as-intrinsic-value-engine]]:

> **reinvest above cost of capital  >  buy back stock when cheap  >  tax-efficient buyback  >  dividend**

([[prefer-buybacks-over-dividends-for-tax-efficiency]], [[seek-companies-with-strong-capital-return]].)
This ranking is the binding prior; the six-axis scorecard below grades execution quality against
it. The Munger/Buffett CIO remains the arbiter — a high scorecard cannot override the binding
veto on a business that must constantly reinvest just to stand still
([[avoid-businesses-requiring-constant-reinvestment]]).

## WHY this scorecard (the core insight)

The Outsiders CEOs outperformed the S&P 500 by ~20× over their tenures — not by being the
best operators, but by being the best *capital allocators*. Thorndike's lens: the CEO is
first and foremost a capital allocator; operational excellence matters, but FCF + what
management *does* with it is what compounds per-share value. GAAP earnings are a distraction.
The eight Outsider CEOs shared five structural traits (the scorecard below).

## THE SCORECARD — six axes, rate each 0 / 1 / 2

(Axes 1–5 are the Thorndike Outsiders style traits; Axis 6 adds the literal compounding driver —
incremental ROCE × runway — so the scorecard grades the economics, not just the style.)

Run through each axis for the company under review. Use only evidence from the dossier,
annual reports, and canon-returned principles. Never infer a high score without evidence.

### Axis 1 — Per-share value as the CEO scoreboard
*Canon slug: `per-share-value-optimization`*

Score 2: Management explicitly tracks per-share owner-earnings growth (not total PAT / revenues /
market cap) as the primary internal metric; discusses reinvestment decisions in terms of their
per-share IV impact; resists accretive-to-EPS dilutive raises.
Score 1: Some awareness of per-share metrics but mixes with revenue/headcount growth language.
Score 0: Management scorecard is total profit, EBITDA, revenue, or market cap — not per-share value.

### Axis 2 — FCF / owner-earnings over GAAP
*Canon slugs: `cash-flow-over-earnings`, `cash-flow-over-earnings-metric`*

Score 2: Management consistently discusses FCF or owner-earnings (not GAAP net income or EBITDA)
in communications; capex and reinvestment are laid out explicitly; the income statement is
secondary to the cash flow statement in how they talk to investors.
Score 1: FCF mentioned alongside GAAP; some explicit capex vs maintenance distinction.
Score 0: Communication anchored to PAT/EBITDA; FCF treated as incidental.

### Axis 3 — Value-accretive deployment OR disciplined non-deployment
*Canon slugs: `buybacks-when-cheap`, `opportunistic-buybacks-vs-programmatic`*
*Desk/binding: [[capital-light-vs-capital-heavy-allocation-is-not-a-style-score]],
[[holding-cash-is-a-deliberate-allocation-choice]], [[capital-light-moats-perform-best-in-inflation]],
[[avoid-businesses-requiring-constant-reinvestment]]*

This axis credits *value-accretive action* OR *disciplined inaction* — do NOT penalise an
asset-light compounder for low capex. Three Score-2 paths:
- **(i) Opportunistic deployment:** buybacks / acquisitions / aggressive organic reinvestment in
  large, irregular blocks when price is demonstrably below IV — then nothing for long periods;
  management can articulate *why* the price was cheap.
- **(ii) Capital-light high-ROC:** the business reinvests little yet earns high ROC and returns the
  rest — low capex is the *feature*, not a deployment failure
  ([[capital-light-vs-capital-heavy-allocation-is-not-a-style-score]];
  [[capital-light-moats-perform-best-in-inflation]]).
- **(iii) Deliberate cash-holding:** management holds cash on purpose to await sub-IV prices
  ([[holding-cash-is-a-deliberate-allocation-choice]]) — credited ONLY when paired with documented
  sub-IV opportunity-awareness AND an above-cost-of-capital core business.

Score 1: Some evidence of price-sensitivity in buybacks/M&A, OR capital-light economics without a
clear return-of-cash record.
Score 0: Programmatic steady-state buybacks regardless of price; acquisitions driven by growth
narrative / peer pressure; consistent over-payment for M&A; **or idle cash hoarded in a mediocre
(below-cost-of-capital) business** — that is empire-protection, not discipline, and scores 0.

### Axis 4 — Centralized capital + decentralized operations
*Canon slug: `centralized-capital-decentralized-ops`*

Score 2: Capital allocation authority sits with the CEO / board (not diffused to divisional
heads); operating decisions are pushed to the business unit or branch level; HQ is lean.
Score 1: Partial centralization — some capital decisions decentralized or locked in budgets.
Score 0: Capital decisions fragmented across divisions; headquarters is bureaucratic;
operating autonomy low.

### Axis 5 — Leverage matched to cash-flow predictability + contrarian discipline
*Canon slugs: `leverage-matched-to-predictability`, `leverage-predictability-test`,
`contrarian-analytical-discipline`, `contrarian-analytical-temperament`*

Score 2: Debt (if any) is sized to the *predictability* of recurring cash flows and stress-
tested through economic cycles; management can quantify the FCF cushion. Capital decisions
are rooted in independent quantitative analysis, not peer benchmarking or analyst consensus.
Score 1: Leverage moderate with some stress-test evidence; or contrarian actions documented
but not quantitatively grounded.
Score 0: Leverage sized to optimism/guidance, not to cycle-adjusted FCF; or management
consistently follows the herd on capital deployment.

### Axis 6 — Reinvestment runway × incremental ROCE (the compounding driver)
*Desk: [[reinvestment-runway-as-the-sixth-allocation-axis]]*

The five style axes measure *how* management allocates; this axis measures the literal compounding
economics — **incremental ROCE × length of runway** — which is what actually drives per-share value.
Score it on *realised* incremental ROCE history, never a projected TAM narrative (the perspectives
layer is promotional; this axis is evidence-gated).

Score 2: High incremental ROCE (>~18–20%; Raamdeo's >15% ROE floor as a minimum, Terry Smith's ~30%
as the aspiration) AND a demonstrably long runway — large under-penetrated TAM, QGLP "Longevity",
reinvestment opportunity not yet exhausted.
Score 1: Solid incremental ROCE but a maturing / partly-penetrated runway; OR a long runway at only
moderate incremental returns.
Score 0: Incremental ROCE near the cost of capital (reinvestment is not compounding value), OR the
runway is nearly exhausted (high ROC with nowhere left to deploy → the engine is stalling).

## SCORING + CONVICTION FEED

Sum the six axes (max = 12):

| Total  | Capital-allocation grade | Conviction feed |
|--------|--------------------------|-----------------|
| 11–12  | Outsider-class (rare)    | +1 to conviction (subject to moat gate) |
| 8–10   | Strong allocator         | Supports conv 4–5 if moat present |
| 6–7    | Adequate / mixed         | Neutral; does not lift or cap |
| 4–5    | Weak allocator           | −1 to conviction ceiling |
| 0–3    | Capital destroyer        | Cap conviction at 2 regardless of moat |

**Gates still bind:**
- No moat → conviction cap 1, regardless of allocation score.
- Chronically weak/near-zero FCF → conviction cap 2, regardless of allocation score.
- ROIC below ~12% cost of capital → conviction cap 2.
- An Outsider-class score in a commoditized or moat-free business is *not* a pass — great
  allocation of bad economics still compounds mediocre results.

## OUTPUT (feeds Stage 3 / conviction re-grade)

Return a structured block:

```
capital_allocation_scorecard:
  per_share_value:        [0|1|2] — <evidence sentence>
  fcf_over_gaap:          [0|1|2] — <evidence sentence>
  value_accretive_deploy: [0|1|2] — <evidence sentence (deployment OR disciplined non-deployment)>
  centralized_capital:    [0|1|2] — <evidence sentence>
  leverage_contrarian:    [0|1|2] — <evidence sentence>
  reinvestment_runway:    [0|1|2] — <incremental-ROCE × runway, realised history not TAM>
  total:                  [0–12]
  grade:                  [Outsider-class | Strong | Adequate | Weak | Destroyer]
  conviction_feed:        [+1 | supports 4-5 | neutral | -1 | cap 2]
  cites_principles:       [slugs returned by the consult ONLY]
  cites_moat:             [moat-gate link — seek-enduring-moats / moat-reinvestment-opportunity-valuation-integration]
  cites_valuation_link:   [reinvestment-rate-terminal-value-consistency — the g = reinvest-rate × ROC identity feeds DCF terminal value]
  portfolio_mirror:       [opportunity-cost-and-capital-allocation — this name's allocation vs the portfolio's best alternative use of capital]
  allocation_kill_criteria: <one sentence — what would prove the grade wrong>
```

Embed this block in the dossier's "Capital Allocation" section and carry `conviction_feed` forward
into the Stage 3 structured output. The three horizontal edges make the dossier explicitly carry
allocation into (a) the **moat gate** ([[seek-enduring-moats]],
[[moat-reinvestment-opportunity-valuation-integration]]), (b) the **DCF terminal value** — runway ×
incremental ROCE *is* the g = reinvestment-rate × ROC identity
([[reinvestment-rate-terminal-value-consistency]]), and (c) **portfolio sizing**
([[opportunity-cost-and-capital-allocation]]).

## Hard rules

1. Never assign Outsider-class (11–12) without documentary evidence on all six axes.
   Narrative framing from management IR is not evidence — look for actions (actual buyback
   timing, deal multiples, capex decisions vs guidance, realised incremental ROCE) not words.
   Axis 6 in particular must rest on realised incremental-ROCE history, never a projected TAM.
2. Always cite only canon slugs the consult actually returns. If `principles` comes back
   empty / thin on Thorndike atomics, flag it and score conservatively.
3. The allocation grade feeds conviction but does NOT override the moat gate. A conv 1
   (no moat) stays at 1 regardless of allocation score.
4. The Munger/Buffett binding CIO remains the arbiter of moat / verdict / margin-of-safety.
   This skill supplies the capital-allocation *number* inside conviction; it does not issue
   verdicts.
5. Indian listed companies rarely have Axis 3 (buyback) evidence — but Axis 3 now also credits
   capital-light high-ROC economics and deliberate sub-IV cash-holding, so do not auto-score it 0
   for a low-capex compounder. Still score 0 for a *routine* buyback programme (not opportunism)
   and for idle cash hoarded in a below-cost-of-capital business.
6. **The perspectives layer is context, never the verdict.** The dual-pull surfaces 30 external
   voices (Raamdeo, Mukherjea, Terry Smith, Tambade) who talk their book and frequently agree with
   each other — they can inform Axis 6 and flag divergence, but they may NEVER override the binding
   Munger/Buffett CIO on temperament, moat, verdict, or MoS. Always run the separate `--corpus
   binding` call; its atoms are the arbiter. A glossy "long runway" narrative does not lift
   conviction without realised incremental-ROCE evidence, and the binding veto
   ([[avoid-businesses-requiring-constant-reinvestment]]) sits above the whole scorecard.
