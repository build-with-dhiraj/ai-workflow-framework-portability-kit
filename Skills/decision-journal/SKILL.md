---
name: decision-journal
description: >
  Use when sharpening Stage 4 (inversion / strict FOREVER gate) of the v2 onboarding machinery,
  or when attaching a decision-journal artifact to any conviction call. Provides process-vs-outcome
  (resulting) discipline, base-rate and skill/luck awareness, calibrated probabilistic framing,
  pre-mortem/inversion protocol, and a per-stock DECISION-JOURNAL template (what we believed, bet
  size, kill-criteria, what would change our mind). Enriches — but does NOT replace — the binding
  Munger/Buffett CIO (vault) and Munger's Psychology of Misjudgment layer already embedded in the
  pipeline. Triggers: "decision journal", "pre-mortem", "kill criteria", "what would change my mind",
  "am I falling in love with this stock", "bias check on FOREVER", "was I right for the right reasons",
  "resulting", "process vs outcome", Stage 4 inversion on any FOREVER candidate.
---

# Decision Journal (the behavioral / decision-quality keeper)

**What this skill adds:** the binding Munger/Buffett CIO already owns the *substance* here —
process-over-outcome, crowd psychology, and the hold-forever-vs-cardinal-sin-of-delay tension are
all dense in the binding layer. The gap is not doctrine; it is **instrumentation**: the CIO has no
persistent artifact, no scheduled re-decision cadence, and no structured way to memorialize a call so
it can be re-read post-outcome. This skill supplies exactly that — a contemporaneous, re-readable
artifact per conviction call (to distinguish *good process that went wrong* from *bad process that
got lucky*), the missing mechanism inputs the canon method requires, and a re-decision loop so the
journal cannot quietly become a rationalization engine. Every addition below is *instrumentation of a
CIO-native principle*, not a new first-principle.

## STEP 0 — Pull the canon (binding-safe)
```bash
set -a && source /Users/pw/invest/.env && set +a && /Users/pw/invest/.venv/bin/python \
  /Users/pw/invest/data/scripts/32_consult_brain.py \
  --corpus blended \
  --company "<stock name> decision journal process outcome resulting bias premortem inversion calibrated probability base rate fear and greed market cycle sentiment crowd psychology hold-forever inconsistency-avoidance status-quo re-decision second-order and-then-what psychological distance" \
  --model general \
  --step inversion \
  --k 12 \
  --json-out extracted/grilling/<TICKER>_journal.json
```
`--corpus blended` surfaces the desk-synthesis behavioral atomics (`vault/desk/behavioral/atomic/`,
weight 0.9) alongside the binding CIO. The extended query terms (fear/greed cycle, inconsistency-
avoidance, status-quo re-decision, and-then-what, psychological distance) are deliberate — the
grilling proved those crowd-psychology / temperament atomics are in the corpus but the old query
string under-retrieved them. `cites_principles` MUST be a strict subset of returned slugs. If
`principles` is empty, ABSTAIN — do not fabricate behavioral claims. Also run the binding consult
(`--corpus binding`, Munger/Buffett CIO) for the moat/verdict judgment; the canon supplies the
*behavioral method*, the CIO is still the *arbiter*.

**Reliably-surfaced behavioral slugs** — this is a *reference list of what the consult tends to
return, NOT a citation allowlist.* Re-read the rule above: cite a slug ONLY when THIS run's
`principles[]` actually returns it; if the consult comes back thin or empty, ABSTAIN. Never cite
from this list because it appears here.
- `[[decision-journal-method]]` — maintain a contemporaneous journal documenting context, alternatives,
  reasoning, expected outcomes, probabilities, and emotional/physical state to counteract hindsight bias
- `[[decision-journaling-pre-outcome]]` — deconstruct and memorialize decisions *before* results occur
  to enable unbiased post-mortem analysis
- `[[resulting-outcome-bias-test]]` — evaluate decision quality independently of outcome; never let
  a good result validate a flawed process or a bad result indict a sound one
- `[[motivated-reasoning-diagnosis]]` — identify and control for motivated reasoning (processing
  information to confirm existing beliefs); the FOREVER confirmation trap is motivated reasoning in disguise
- `[[pre-mortem-group-analysis]]` — solicit independent disconfirming analysis *before* the outcome
- `[[probabilistic-decision-discipline]]` — frame the buy as a probability-weighted bet; state the odds,
  not a binary call; accept that well-calibrated bets can lose
- `[[calibrated-probabilistic-thinking]]` — force probabilistic quantification of beliefs; refine with
  new information; resist collapsing to "it will work" certainty
- `[[bayesian-updating-priors]]` — continuously update probability estimates by integrating new
  information with relevant base rates; resist anchoring to the original thesis
- `[[accuracy-vs-rightness-reasoning]]` — reason for accuracy (objective truth), not to be right
  (affirming priors), especially in post-hoc review
- `[[review-for-pattern-recognition]]` — periodically review past journal entries to identify recurring
  errors, cognitive biases, and judgment patterns
- `[[skill-luck-continuum-placement]]` — place the investment activity on the skill-luck continuum;
  stock-picking is HIGH-luck, requiring larger samples to evaluate analyst performance
- `[[mean-reversion-analysis]]` — analyze mean reversion rates to infer skill vs luck; a hot streak
  in a high-luck domain is not a signal of repeatable skill
- `[[can-you-lose-on-purpose-test]]` — if you can trivially construct the losing case, luck dominates;
  use this to calibrate how much weight to place on recent track-record evidence
- `[[single-outcome-deep-dive]]` — focus analysis on ONE specific failure scenario in full concrete
  detail rather than generic contingency planning
- `[[sample-size-tailoring]]` — require large samples before inferring skill from outcomes; resist
  concluding "our process works" from one or two good outcomes

## WHERE THIS SKILL PLUGS IN

**Primary hook: Stage 4 — Inversion / strict FOREVER gate** (runs alongside the adversarial
disconfirmation agent). Before the Opus/Fable verdict, run through the DECISION-JOURNAL TEMPLATE
below and flag any bias-pattern findings to the inversion agent. A FOREVER candidate that cannot
pass the resulting-test and pre-mortem is demoted by default.

**Secondary hook: any conviction call (Stage 3)**. Attach the filled template to the
`vault/research/dossiers/<TICKER>.md` as a "Decision Journal" section at the bottom. It becomes
the re-readable artifact for post-outcome calibration review.

## METHOD — process-vs-outcome discipline

### 1. Resulting test (run FIRST)
Before writing the journal entry, ask: "Would I grade this process identically if the stock had
declined 30% in the past year?" (`[[resulting-outcome-bias-test]]`). If recent performance is
influencing the conviction grade, correct for it — process quality and outcome are independent.
A FOREVER belief built on a strong recent chart is motivated reasoning, not analysis.

### 2. Base-rate / skill-luck calibration
Stock-picking sits on the HIGH-LUCK end of the continuum (`[[skill-luck-continuum-placement]]`).
Implications:
- A two-year track record of good picks means almost nothing statistically (`[[sample-size-tailoring]]`).
- Any analyst's "consistent outperformance" claim needs the `[[can-you-lose-on-purpose-test]]` and
  `[[year-to-year-correlation-test]]` checks before the Substack analyst's thesis is up-weighted.
- ROIC persistence (e.g., IGI/CAMS high ROIC sustained 5+ years) is a harder signal than analyst
  conviction, because ROIC mean-reverts in competitively weak businesses (`[[mean-reversion-analysis]]`).

### 3. Pre-mortem (mandatory for FOREVER candidates)
Run the pre-mortem as an independent step (`[[pre-mortem-group-analysis]]`): *assume the thesis
failed 3 years from now* and write the most plausible autopsy. Solicit the inversion agent's
version independently before comparing. Red flags: if the failure scenario is easy to write,
the moat is not as durable as claimed. Hard rule: a pre-mortem that produces the same 3-4 failure
modes as the bull thesis re-stated in reverse is not a real pre-mortem — push harder.

### 4. Motivated-reasoning check (the FOREVER confirmation trap)
The FOREVER tier is the highest-stakes judgment — and therefore the highest-risk locus of
motivated reasoning (`[[motivated-reasoning-diagnosis]]`). Before confirming, explicitly list
*three pieces of evidence that would have caused you not to reach this conclusion*. If you
cannot list three, you have a confirmation problem, not a conviction.

Run the same lens *outward* on management, not just on yourself: score the company's
capital-allocation narrative for self-serving bias (`[[self-serving-bias-detection]]`) and
incentive distortion (`[[institutional-incentive-analysis]]`) — a buyback/empire-building story
told by the people whose comp depends on it is a flagged input, the bridge to the
capital-allocation and forensic desks. The FOREVER label *itself* is also a behavioral hazard
(`[[forever-label-as-commitment-trap]]`): it manufactures commitment-and-consistency and endowment
bias, turning Munger's cardinal sin of inconsistency-avoidance into the gate's default — which is
why the holding must be periodically *re-decided* (see Hard rule 8).

### 5. Probabilistic framing (not binary)
Translate the verdict into a probability statement (`[[probabilistic-decision-discipline]]`,
`[[calibrated-probabilistic-thinking]]`): *"I believe there is X% probability this business
sustains its moat and compounds owner-earnings at ≥Y% for ≥10 years."* Then state what the
probability would need to be to justify buy-below at the MoS threshold. If the required
probability seems heroic, widen the MoS or demote. Express uncertainty honestly — "70% confident"
is more useful than "high conviction."

### 6. Bayesian update discipline (ongoing)
Each quarter-result, management change, or analyst revision is a Bayesian update opportunity
(`[[bayesian-updating-priors]]`). The kill-criteria in the journal (see template) define the
evidence that should *update the probability down materially*. If a trigger fires but the thesis
is unchanged, that is a motivated-reasoning warning sign.

## DECISION-JOURNAL TEMPLATE

Attach as a `## Decision Journal` section at the bottom of `vault/research/dossiers/<TICKER>.md`.
Fill BEFORE outcome is known (pre-outcome memorization per `[[decision-journaling-pre-outcome]]`).

```markdown
## Decision Journal

**Date:** YYYY-MM-DD  
**Verdict:** FOREVER / COMPOUND / WATCH / AVOID / TOO_HARD  
**Conviction:** N/5  
**Buy-below (MoS gate):** ₹X  
**Probability statement:** "I believe there is ___% probability this business sustains its moat
and grows owner-earnings at ≥___% for ≥10 years."  
**Decision-time state:** [one line — emotional / physical / time-pressure state right now, per
[[decision-journal-method]]; "rushed and excited after a great quarter" is a real input, not noise.]

### Sentiment-cycle locus
Where in the fear–greed cycle is this buy being made — **panic / normal / euphoria**? Run the
`[[be-fearful-when-others-are-greedy]]` contra-check: am I buying because the business is cheap
relative to IV, or because everyone is? (`[[sentiment-cycle-locus-of-a-decision]]`,
`[[fear-and-greed-drive-markets]]`, `[[market-cycles-are-driven-by-human-nature]]`.) A FOREVER
formed at self-identified **euphoria** is demoted by default unless the MoS is widened. This is a
*qualitative temperament check*, never a market-timing call — it adjusts MoS demand, it does not
gate entry on a macro forecast.

### What we believed (the thesis, in one paragraph)
[Write the bull case *without* using the stock's recent price action as evidence.]

**And-then-what chain:** [for the core bull driver, write 2–3 second/third-order steps —
"prices rise → and then what? (competitor adds supply / regulator caps fees / customer substitutes)"
per [[and-then-what-as-second-level-thinking]] / [[and-then-what-sequence]]. A thesis whose
first-order story is bullish but whose second-order chain turns bearish has not been thought through.]

### Alternatives considered and rejected
[Name ≥2 other verdicts you considered and why you rejected them.
Per [[explicit-alternatives-evaluation]] / [[probabilistic-decision-discipline]].]

### Key variables and assumed odds
| Variable | Assumed value | Why | If wrong → |
|---|---|---|---|
| Moat durability | [e.g., "stable 10yr"] | [reason] | [verdict change] |
| ROIC 5yr avg | [e.g., "≥28%"] | [reason] | [conviction drops to N-1] |
| Mgmt alignment | [e.g., "owner-operator"] | [reason] | [re-evaluate] |

### Kill-criteria (what would change our mind)
List the 3–5 concrete, observable triggers that would cause a verdict downgrade or sell decision:
1. [e.g., "ROIC drops below 18% for 2 consecutive years"]
2. [e.g., "Regulatory cap on registry fees imposed with no pass-through"]
3. [e.g., "Promoter stake falls below 40% without strategic rationale"]
4. [e.g., "New entrant clears SEBI approval for competing registry"]
5. [e.g., "Price breaches IV-high by >30% with no earnings upgrade"]

### Pre-mortem (failure autopsy)
*Assume this bet failed 3 years from now. What is the most plausible explanation?*
[Write 2–3 sentences. This should NOT be the bull thesis inverted — find the non-obvious failure.]

### Bias check
- [ ] Resulting-test passed: conviction grade is identical regardless of recent price performance
- [ ] Three disconfirming evidence items listed:  
  1. ___  
  2. ___  
  3. ___
- [ ] Motivated-reasoning diagnostic: no evidence of processing data to confirm a pre-existing FOREVER belief
- [ ] Psychological-distance pass: re-read the thesis as if a *stranger* wrote it — does it still
  hold? (`[[psychological-distance-on-own-thesis]]` / `[[objective-evaluation-guards-against-bias]]`)
- [ ] Management self-serving-bias check: capital-allocation narrative scored for incentive distortion
  (`[[self-serving-bias-detection]]`), not taken at face value
- [ ] Analyst source check: Substack bull thesis not driving conviction; moat evidence is independent

### Post-outcome review (fill on next annual review or after a kill-trigger)
**Date of review:** YYYY-MM-DD  
**What actually happened:** [facts]  
**Was the process sound?** Y / N — [reason, citing [[resulting-outcome-bias-test]]]  
**Bayesian update:** probability revised to ___%  
**Calibration note:** [what this outcome teaches about our priors / process]

### Standing FOREVER re-decision (re-grade at each annual review or kill-trigger)
Re-grade the holding as a **fresh buy at today's price** (`[[status-quo-decision-equivalence]]`):
would I open this position now, this size, at this price? **Not selling is logged here as an active
decision with its own probability statement** — silence is not a decision. The bar to SELL stays the
binding *compelling reason* (`[[hold-with-forever-mindset-unless-reason-to-sell]]`); this is a
re-decision *cadence*, not a license to churn on a noisy chart (`[[resulting-outcome-bias-test]]`
still guards against selling on a bad recent quarter).  
**Re-decision date:** YYYY-MM-DD — **Re-buy at today's price?** Y / N — **why:** ___
```

## INTEGRATION WITH THE INVERSION AGENT (Stage 4)

The inversion agent (Opus/Fable) receives the filled journal in its prompt. The adversarial
skeptic must:
1. Evaluate whether the kill-criteria are *real* (specific + observable) or vague (e.g.,
   "moat deteriorates" without a measurable trigger — reject vague criteria).
2. Check whether the pre-mortem failure modes overlap with the kill-criteria (they should).
3. Flag any bias-check box left unchecked — an unchecked box is a FOREVER demotion signal.
4. The inversion agent's verdict carries more weight than the journal author's —
   default is DEMOTE unless the skeptic is convinced by the journal + canon evidence together.

## Hard rules
1. Fill the journal BEFORE the outcome is known; a post-hoc journal is rationalization, not a record.
2. Kill-criteria must be specific and observable — "moat weakens" is not a kill-criterion.
3. The pre-mortem must name a non-obvious failure; restating the inversion checklist is not enough.
4. The resulting-test and motivated-reasoning check are mandatory for every FOREVER candidate; no bypass.
5. Cite only canon slugs returned by the Step 0 consult; if the vault is thin, ABSTAIN on behavioral claims.
6. The Munger/Buffett binding CIO (vault) remains the final arbiter of moat/verdict; this skill
   supplies the *process discipline and artifact*, not the *conviction judgment*.
7. Substack analyst conviction is an INPUT, not the verdict — always run the resulting-test and
   skill-luck calibration (`[[skill-luck-continuum-placement]]`) on analyst track-record claims.
8. **A FOREVER holding is re-decided, not protected.** At every annual review (or kill-trigger),
   re-grade the holding as a fresh buy at today's price (`[[status-quo-decision-equivalence]]`) and
   log *not selling* as an active decision — the FOREVER label is a commitment/endowment trap
   (`[[forever-label-as-commitment-trap]]`). This is a CADENCE, not a churn license: the SELL bar
   stays the binding *compelling reason* (`[[hold-with-forever-mindset-unless-reason-to-sell]]`), and
   the perspective voices that preach "quality compounds forever, never sell" illustrate but never
   arbitrate — Hard rule 6 (the Munger/Buffett CIO is the final arbiter) sits above them.
