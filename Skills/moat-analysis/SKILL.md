---
name: moat-analysis
description: >
  Use when the conviction step needs a rigorous moat judgment — taxonomy, durability test, and
  pricing-power check — for any Indian stock being onboarded or re-graded. Enriches the existing
  v2 conviction step (STAGE 3) and the inversion/FOREVER gate (STAGE 4); it is NOT a new pipeline
  step. Outputs a moat-tier (Wide / Narrow / Contestable / None) and a durability verdict
  (Widening / Stable / Eroding) that feed directly into the conviction rubric (Wide+Stable → higher
  conviction, Contestable → COMPOUND-not-FOREVER, None → conviction cap 1). Triggers: "what is
  the moat here", "is this moat durable", "why COMPOUND not FOREVER", "contestable vs durable",
  grading INDIAMART-style marketplace or IGI-style trust franchise moat, any stock where the
  conviction band is uncertain because the moat characterisation is unclear.
---

# Moat / Industry-Structure Analyst

**The diagnosed hole:** the v2 conviction rubric uses moat as a *necessary* gate (a
conviction-ceiling input, not the final verdict — see "MOAT DOES NOT SET ITS OWN PRICE" below) but
the dossier step does not force a structured taxonomy + durability verdict. Analysts were writing "has a moat"
without distinguishing Tren Griffin's five sources, Dorsey's structural durability, or Mauboussin's
contestability test. This produced INDIAMART overstated as FOREVER-quality when its network effect
is contestable (Justdial proved the moat does not exclude), and IGI being soft-called narrow when
its trust franchise is the actual moat. This skill makes the moat call explicit, taxonomised, and
durability-tested so conviction is grounded, not inferred.

## STEP 0 — Pull the canon (binding-safe)

The moat-method atomics are in three canon folders. Pull them at the conviction step:

```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && \
/Users/Dhiraj/dev/invest/.venv/bin/python /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<name + moat terms, e.g. 'INDIAMART network effect switching costs contestable'>" \
  --model <model> --step conviction \
  --json-out extracted/grilling/<TICKER>_moat.json
```

Use `--corpus blended` so the consult routes to BOTH the academic canon
(`vault/canon/tren-griffin-moats/`, `vault/canon/pat-dorsey-moats/`, `vault/canon/mauboussin-moat/`)
AND the binding Munger/Buffett moat cluster, surfacing the desk-synthesis atomics
([[scale-economics-shared-as-self-reinforcing-moat]], [[narrative-moat-fails-the-financial-signature-test]],
[[deposit-franchise-is-a-banks-cost-of-funds-moat]], [[moat-width-does-not-set-its-own-price]])
alongside them. The blend keeps the CIO primary and down-weights the pitch-side perspective voices
(0.85). Cite only slugs actually returned in `principles[].slug`. If `principles` is thin → flag it
and treat the moat as unconfirmed (cap conviction at 2, no FOREVER).

**Erosion is a binding-CIO judgment, not a canon footnote.** The durability section below MUST cite
at least one of the six binding erosion atoms — [[moats-are-hard-to-maintain]],
[[recognize-the-limits-of-moats]], [[fast-moats-can-be-lost-fast]],
[[moats-are-constantly-under-threat]], [[avoid-commoditized-businesses]] — and, where erosion is
found, the CIO's own sell-discipline action atom [[sell-when-competitive-advantage-erodes]]. This
wires the erosion finding directly to what the binding arbiter would *do* about it.

Also run the binding consult at `--step inversion` for any FOREVER candidate — pull
disconfirming moat-erosion principles before endorsing the moat as lifelong.

**India retrieval blindness (known gap — seed around it).** The India perspective moat atoms are
currently NOT tagged `analyst_role: moat`, so a `--role moat` filter never surfaces them — Terry
Smith's scale-matters-in-durability / dominant-position-pricing-power / valuation-discipline-relative-to-quality,
SOIC's premiumization-financialization-as-moat, and Saurabh Mukherjea's consistent-compounder lens
stay invisible. Two mitigations: (1) a one-time, *narrowly scoped* frontmatter retag pass to add
`analyst_role: moat` to those specific atoms (review each — do NOT bulk-sed, or non-moat atoms get
mis-tagged and pollute the role filter for the capital-allocation / behavioral desks); and (2) until
that lands, add those terms as explicit `--company` seeds so the cold consult still pulls them. These
voices enter strictly as CONTEXT/lenses (down-weighted 0.85) — they never upgrade a moat tier on
their own; the binding arbiter ([[do-not-be-charmed-by-moats-alone]], [[moats-are-hard-to-maintain]],
[[avoid-commoditized-businesses]]) sets the verdict.

## TAXONOMY — seven sources (apply all that fire)

Source the taxonomy from the canon. Map each claimed moat to exactly one (or two) of:

| Source | What makes it real | Indian archetype |
|---|---|---|
| **Scale economies** | Unit costs fall as volume rises; replicating scale is capital-intensive | CAMS (asset-light but fixed-cost processing at scale beats any new entrant) |
| **Scale-economics SHARED** _([[scale-economics-shared-as-self-reinforcing-moat]]; binding atom [[scale-creates-self-reinforcing-moats]])_ | The flywheel of *returning* scale gains to customers as lower prices → more volume → more scale → still-lower prices; rivals cannot match the price without the volume | DMart (the Costco / low-cost-airline pattern); guard with pricing-power + ROIC-persistence so a thin-margin commodity retailer is NOT mislabelled Wide |
| **Network effects** | Each new node raises value for all existing nodes | INDIAMART (buyers attract sellers, but value is searchable, not locked) |
| **Switching costs** | Customers bear real economic pain to leave | CAMS (registrar switching = AMC back-office disruption; very high) |
| **Intangibles / brand** | Pricing power above cost without losing share; or regulatory licence | IGI (gemological trust, 50-yr brand, lab accreditation) |
| **Cornered resource** | Proprietary access to an input competitors cannot replicate | Rare in Indian listed cos; check for regulatory exclusivity |
| **Counter-positioning** _(unanchored — Helmer concept, no atom in the tren-griffin/dorsey/mauboussin canon; use as a lens only, never cite a slug for it)_ | Business model the incumbent cannot copy without destroying itself | Watch for fintech disruptors challenging PSU banks |
| **Process power** | Embedded operational know-how; 15+ years to replicate | Specialty chemicals, some pharma API makers |

**Dorsey fourth-source check** (`four-moat-sources-categorization`): for each source confirmed
above, test whether it is *structural* (embedded in the business model) or merely *transient*
(market position, first-mover, or size). Only structural sources earn moat credit.

**Mauboussin sources-of-added-value** (`sources-of-added-value-categorization`): confirm the moat
maps to a genuine source of added value in the industry structure — innovation lead, supply-side
advantage, demand-side advantage, or regulatory barrier. A moat with no industry-structure anchor
is brand storytelling, not an economic moat.

**Bank / lender sub-clause** ([[deposit-franchise-is-a-banks-cost-of-funds-moat]]; binding atom
[[underappreciated-moats-in-commodity-businesses]]): for a bank or NBFC, the moat is NOT captured by
the generic pricing-power test — it is the **low-cost sticky deposit franchise (CASA / cost of
funds).** A lender that funds itself cheaper than rivals and retains those deposits through cycles
has the durable advantage; one chasing bulk/term deposits at market rates does not. Identify the
franchise here, then **route the actual metric (CASA %, cost of funds vs peers, deposit stickiness,
Ke) to the bank-valuation sibling** rather than running the four-question pricing-power test.

## PRICING-POWER TEST (the single sharpest moat signal)

*A business with a real moat can raise prices without losing material volume.*

Run the four-question test (from `pricing-power-test`, `pricing-power-assessment`):

1. Has the company raised prices above input-cost inflation over a 5-year window?
2. Did volumes hold or grow through the price rise?
3. Would customers bear meaningful pain (time, money, risk) to switch to a cheaper alternative?
4. Do gross margins trend stable or expanding over 5+ years (not just 1-yr blip)?

All four YES → strong pricing power, moat confirmed.
Three YES → moderate pricing power, narrow moat.
Two or fewer YES → pricing power is weak or unproven, moat is contestable or none.

**The Tren Griffin pricing-power cross-check** (`pricing-power-test-8`): "Would I rather own
the pricing power or the product?" If the answer is the pricing power, the moat is real. If the
answer is the product (commodity/feature), the moat is missing regardless of market share.

## DURABILITY TEST — widening vs eroding

*Moat age + trend + contestability determines whether a stock earns FOREVER or COMPOUND.*

**Step 1 — Empirical backtest** (`moat-durability-empirical-backtest`, `moat-durability-analysis`):
- ROIC vs WACC spread: Is ROIC persistently above cost of capital over 5–10 years? Persistence =
  the moat is real. Mean-reversion to cost of capital = the moat is being competed away
  (`regression-to-the-mean-test`, `quantitative-moat-test-roic-wacc-spread`).
- **The financial-signature test for a NARRATIVE moat**
  ([[narrative-moat-fails-the-financial-signature-test]];
  [[owner-earnings-vs-accounting-earnings]]): a real moat leaves a signature in *owner-earnings-based*
  returns on capital, not just in the story. A moat asserted in the narrative (brand, "ecosystem",
  network) but with **no persistent ROIC-above-WACC signature** is treated as UNPROVEN — cap
  conviction, do not award it "Narrow" as a consolation tier. Use owner-earnings (not GAAP) in the
  numerator so accrual-manufactured "quality" (see forensic Dimension 6) cannot fake the signature.
- Market share stability: Has the company's share been stable or rising over 5 years?
  (`market-share-stability-metric`). Falling share under a claimed moat = moat is eroding.

**Step 2 — Five-forces structural check** (`five-forces-industry-attractiveness`):
- Supplier power / buyer power / threat of substitutes / new entrant barriers / rivalry intensity.
  A durable moat requires at least two forces working *for* the firm. Pure market-share leadership
  without structural protection is a moat on paper, not in cash flows.

**Step 3 — Barriers-to-entry check** (`barriers-to-entry-analysis`):
- List the *specific* barriers: capital requirements, regulatory licences, brand incumbency,
  switching-cost lock-in, network density. For each, ask: "Could a well-funded new entrant
  replicate this in 5 years?" If YES → the barrier is low, moat is contestable.

**Step 4 — Disruption-risk flag** (`disruption-risk-evaluation`):
- Is a lower-cost, lower-feature disruptor attacking the bottom of the market?
- Is technology compressing the cost of replication? (E.g., AI compressing human-expertise moats.)
- A moat that cannot survive a technology shift is durable in the short term only.

**Step 5 — Inversion** (`moat-durability-inversion-check`, `management-vs-moat-inversion-test`):
- State the strongest case that the moat is *not* durable: the one failure mode that invalidates
  the thesis. If that failure mode is plausible within 10 years, the moat earns NARROW not WIDE,
  and COMPOUND not FOREVER.

## DURABILITY VERDICT (output of the test)

| Verdict | Criteria | Conviction impact |
|---|---|---|
| **Widening** | ROIC spread expanding, share rising, barriers hardening, no plausible disruptor | FOREVER-eligible if all other gates clear |
| **Stable** | ROIC spread flat, share stable, barriers holding | COMPOUND if price is right; FOREVER only if inversion fails |
| **Eroding** | ROIC mean-reverting, share slipping, new entrant viable | Cap conviction at 3; WATCH or AVOID, never FOREVER |
| **Contestable** | Network/scale moat that a well-funded rival has partially replicated OR can replicate | COMPOUND-not-FOREVER; cap conviction at 3 |
| **None** | No structural source, no pricing power, commodity economics | Conviction cap 1; AVOID unless extreme MoS |

## THE INDIAMART PROBLEM (the contestable-moat archetype)

INDIAMART's B2B marketplace has a two-sided network effect that is *real but weak*: buyers and
sellers both show up, but the value (supplier discovery) is searchable — Justdial, TradeIndia, and
Google Maps erode it without needing to match scale. The switching cost on the buyer side is near
zero (a buyer can search two platforms in 30 seconds). The seller-side lock-in is moderate (paid
subscription), not high. Classification: **Network effect + weak switching cost, Contestable,
Stable-to-Eroding**. Correct verdict: COMPOUND-not-FOREVER, conviction capped at 3.

## THE IGI PROBLEM (the trust-fragile archetype)

IGI's gemological certification carries a 50-year brand and lab accreditation that is genuinely hard
to replicate — the moat source is Intangibles (trust + regulatory recognition). But trust moats are
*fragile*: one high-profile false certification scandal destroys decades of brand equity in months.
The moat is Wide today, but the fragility risk makes it Stable-not-Widening. Classification:
**Intangibles (trust/brand), Wide, Stable**. Correct verdict: COMPOUND or FOREVER eligible, but
the inversion (fraud/scandal) must be explicitly stress-tested before FOREVER is granted; conviction
4 unless inversion is dismissed.

## MAPPING TO THE CONVICTION RUBRIC

This skill enriches the existing STAGE 3 conviction grading. The moat verdict feeds conviction as:

| Moat tier | Durability | Conviction contribution | Verdict ceiling |
|---|---|---|---|
| Wide | Widening | Supports conv 4–5 (all other gates must also clear) | FOREVER eligible |
| Wide | Stable | Supports conv 4 | COMPOUND; FOREVER only if inversion dismissed |
| Narrow | Stable | Supports conv 3 | COMPOUND |
| Contestable | Any | Cap conv 3 | COMPOUND-not-FOREVER |
| Narrow / Contestable | Eroding | Cap conv 2 | WATCH |
| None | — | Cap conv 1 | AVOID |

The conviction rubric's hard gates still apply on top: weak FCF → cap 2; ROIC < ~12% → cap 2;
bank below Ke → cap 2. The moat tier is necessary but not sufficient for high conviction.

## MOAT DOES NOT SET ITS OWN PRICE (ceiling input, not the verdict)

The moat tier is a **conviction-ceiling input, not the final gate.** It remains NECESSARY (None →
cap 1) but is never SUFFICIENT — the valuation + temperament arbiter binds on top. Hold the binding
contradiction in view: [[pay-up-for-extraordinary-businesses]] (a wide+widening moat justifies a
*higher* multiple) sits against [[do-not-be-charmed-by-moats-alone]] (the price still binds). A
Wide+Widening moat **raises the conviction ceiling; it does not set the verdict** — the
**valuation-dcf-longrunway** model plus the binding temperament arbiter retain the final call. A
great moat at a bad price is still capped: "pay up" means accept a fuller multiple for genuine
quality, never "pay any price." Smith-style quality-at-a-price reasoning is paired with the CIO's
price-still-binds discipline, not used to justify paying up indefinitely.

## OUTPUT (feeds STAGE 3 conviction and STAGE 4 inversion gate)

Return a structured moat block embedded in the conviction/dossier output:

```
moat_source: [list of active sources from the seven-source taxonomy]
moat_tier: Wide | Narrow | Contestable | None
durability: Widening | Stable | Eroding
pricing_power: Strong | Moderate | Weak
contestability_note: <one sentence on what a well-funded rival would need to replicate>
inversion_risk: <the single most plausible moat-destruction scenario>
conviction_ceiling: <max conviction this moat justifies, before FCF/ROIC gates>
forever_eligible: yes | no  (no if Contestable or Eroding or inversion_risk is plausible <10yr)
cites_principles: [only slugs returned by 32_consult_brain.py — never fabricated]
```

## Hard rules

1. Never call a moat "wide" without passing the pricing-power test (all four questions). Narrative
   descriptions of market leadership are not moat evidence.
2. Contestable moats (replicated by a well-funded rival in 5 years) cap conviction at 3 and
   permanently block FOREVER — do not override this with qualitative enthusiasm.
3. The ROIC-vs-WACC spread is the *quantitative moat test* (`quantitative-moat-test-roic-wacc-spread`).
   A business with ROIC persistently at or below WACC has no moat, regardless of what management says.
4. Always run the inversion step for any Wide moat claim: state the one scenario that destroys the
   moat. If that scenario is plausible within 10 years, downgrade to Narrow or Stable.
5. Cite only slugs the canon consult actually returns. If the moat canon is thin for this stock →
   flag it, treat as unconfirmed, and cap conviction at 2.
6. The Munger/Buffett binding CIO remains the final arbiter of moat/verdict. This skill supplies
   the *taxonomy and durability test*; the CIO judges whether the moat is real enough to act on.
