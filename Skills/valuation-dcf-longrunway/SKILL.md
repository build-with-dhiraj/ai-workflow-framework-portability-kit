---
name: valuation-dcf-longrunway
description: >
  Use when valuing a durable, high-ROIC LONG-RUNWAY COMPOUNDER — a proven franchise with a
  10–20 year reinvestment runway (IGI, CAMS, the HUL/NESTLE/TITAN "forever-in-waiting" trio,
  consumer/franchise/platform compounders) — where a standard 5-year DCF would TRUNCATE the
  value and wrongly flag a wonderful business as overvalued. Provides multi-stage DCF, the
  growth = reinvestment × ROIC identity, growth/ROIC fade, terminal-value discipline, and the
  reverse-DCF "is this heroic?" check. This is the fix for the v2 machinery over-demoting genuine
  compounders on a too-short, guidance-anchored window. Triggers: "value this compounder",
  "long-runway DCF", "is the 5-yr DCF truncating this", grading a proven high-ROIC franchise.
---

# Long-Runway DCF (the finance-desk "valuation analyst")

**The diagnosed hole:** the v2 IV step anchored to a ~5-year, management-guidance window with a
4.5% terminal — which *undervalues* genuine 10–20yr compounders (it demoted IGI iv-high 511→370,
CAMS to negative MoS). This skill corrects that **without becoming a license to overpay** — the
margin-of-safety + IRR-beats-Nifty gates still bind. The goal is to stop *falsely demoting* a
wonderful compounder, not to justify a heroic price.

## STEP -1 — The false-precision gate (binding; run BEFORE any staging)
The binding CIO can **veto the extended-window model itself**. Before modelling, ask: *is the value obvious
without a 15-year projection?* If the buy case only survives at the far end of a 10–15yr forecast, the margin
of safety is a **modelling artifact**, not a fact (`avoid-false-precision`, `invest-only-when-value-is-obvious`,
`beware-of-believing-your-own-projections`; desk: `[[extended-window-must-pass-the-false-precision-test]]`).
A long runway is a reason not to *truncate* a value that is *already* compelling on conservative numbers — it is
**not** a tool to manufacture upside that isn't there on a 5–7yr view. If the case fails this gate, STOP: this
is a WATCH, and no amount of multi-stage machinery rescues it. Calibrate this as a veto on *heroic far-window*
cases only — not a rejection of disciplined multi-stage DCF for a genuinely obvious compounder.

## STEP 0 — Pull the canon (binding-safe)
Damodaran's DCF/terminal-value method-atomics are in the `canon` layer:
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<name>" --model general --step intrinsic-value --corpus canon \
  --json-out extracted/grilling/<TICKER>_dcf.json
```
**If that returns 0 / thin `principles`** (the valuation method-atomics aren't model-scoped, so a bare
company name can miss them), re-run with method terms appended to `--company`, e.g.
`--company "<name> DCF terminal value reinvestment fade growth ROIC"` — that reliably surfaces the
two/three-stage DCF, `g=b×ROIC`, terminal-value, and reverse-DCF atomics. Cite only returned slugs.

Also run the binding consult (Munger/Buffett CIO) for the moat-durability judgment that *justifies*
the runway. The canon is the method; the CIO is the judge of whether the runway is real.

**Pull the moat-erosion atoms to CAP the explicit window** — runway length is an *output of the moat verdict*,
not a free parameter (`[[runway-length-equals-moat-durability]]`). Add a moat consult on the `conviction` step
(which maps to the moat/management/owner-earnings filters), `--corpus blended` to surface the desk + canon moat
atomics alongside the binding CIO:
```bash
... 32_consult_brain.py --company "<name> moat durability erosion contestable pricing power" --model general --step conviction --corpus blended ...
```
`moats-are-hard-to-maintain` and `fast-moats-can-be-lost-fast` are the binding governors: a Wide+Widening moat
earns a long explicit window; a contestable/eroding one caps it short. The fade (METHOD §3) then competes the
excess returns away regardless.

## WHEN this skill applies (the gate)
ONLY for a **proven** compounder: durable moat (binding CIO-confirmed), high & sustained ROIC
(≫ cost of capital), a real reinvestment runway, aligned long-horizon ownership. A 5-yr window is
*correct* for an ordinary business — do NOT extend the window for a contestable or commodity name.
Extending the runway is earned by moat durability, not assumed.

**Bank / financial hand-off (STOP-gate).** If the subject is a bank, NBFC, SFB, or insurer, this skill does
**not** apply — `g = b × ROIC` with FCFF is invalid when *debt is raw material, not financing*
(`debt-as-raw-material-diagnostic`). Route to **`bank-valuation`**, which values equity directly via the
excess-return / justified-P/B model (`excess-return-model-for-equity-valuation`). Do not free-hand a firm-DCF
on a financial.

## METHOD — multi-stage DCF
0. **Fix the cash-flow object FIRST: it is OWNER EARNINGS** — FCF to equity *net of true maintenance capex*,
   not reported EPS or unadjusted FCF (`intrinsic-value-is-discounted-future-cash`, `focus-on-owners-earnings`).
   If you instead model **FCFF**, you MUST discount at **WACC** and never at Ke; equity cash flows discount at
   Ke (`match-cash-flows-and-discount-rates`). A mismatched numerator/denominator silently corrupts the IV.
1. **Stage the model to the RUNWAY, not to guidance.** Explicit high-growth period = the *justified*
   runway (often 10–15yr for a proven compounder), then a **fade/transition** stage, then stable.
   Anchoring iv to 5yr of guided growth is the error that demoted IGI/CAMS.
2. **Growth = reinvestment rate × ROIC** (`g = b × ROIC`; canon: `fundamental-growth-rate-formula`). This is
   the load-bearing identity: the value of a compounder comes from **reinvesting a high fraction at a high
   ROIC**, not from a high headline g. A franchise reinvesting 50% at 30% ROIC compounds intrinsic value
   ~15%/yr — and *that* is what a 5-yr window throws away. Model the reinvestment explicitly, and treat the
   assumed reinvestment rate as a **capital-allocation judgment**, not a free dial
   (`[[reinvestment-rate-is-a-capital-allocation-judgment]]`): b is only credible if management actually has
   the runway and discipline to deploy it above the cost of capital.
3. **FADE both growth AND ROIC toward the economy / cost of capital.** Never extrapolate peak growth or
   peak ROIC to perpetuity — excess returns get competed away. The fade is what keeps the extended
   window honest.
4. **Terminal-value discipline.** `TV = CF_{n+1} / (r − g)` (canon: `stable-growth-terminal-value-formula`);
   **stable g ≤ risk-free rate ≤ economy growth** (`terminal-growth-rate-riskfree-rate-cap`); terminal ROIC
   fades toward cost of capital. **The real TV guardrail is NOT a percentage cap.** A high TV share is
   *expected* for a true compounder and is **not** a reliability test
   (`terminal-value-percent-dcf-value-not-a-reliability-test`; desk:
   `[[high-terminal-value-share-is-not-a-red-flag-for-a-compounder]]`). What actually disciplines the terminal
   value is (a) the **reverse-implied-growth check** (`reverse-implied-growth-check`, see SANITY CHECK below)
   and (b) **stable-period reinvestment = g / ROC consistency** (`reinvestment-rate-terminal-value-consistency`):
   the terminal g you assume must be funded by a terminal reinvestment rate the ROC can support. Get those two
   right and the TV share takes care of itself.
5. **Discount rate:** WACC for the firm (or Ke for equity-DCF). India: rf ~6.9% + ERP ~5.5% × β.
   **India cuts both ways — model it, don't assume it helps.** Extending the explicit window for an India
   compounder is *currently UNGROUNDED in the brain* (a known gap — do not pretend canon backs it), AND
   India's **country-risk premium RAISES the discount rate** (`country-risk-premium-adjustment`,
   `implied-equity-risk-premium-extraction`). So "longer window + higher discount rate" has an **ambiguous**
   net effect on IV — model it **both ways** and let the more conservative outcome bind. The honest posture is
   "model both directions and demand a larger margin of safety," never a blanket India bonus *or* a blanket ban.

## THE SANITY CHECK (already in the machinery — keep it)
**Reverse-DCF** (canon: `reverse-implied-growth-check`): back out the growth the *current price* implies;
compare to demonstrated + plausibly-sustainable growth. If the price implies ≫ demonstrated (e.g. CAMS
implied 36.8% vs demonstrated 16%), it's **heroic** → no margin of safety, regardless of how good the
business is. The g-files (`extracted/valuation/v2/g*.json`) already do this; treat it as the
overpaying-guardrail. This — together with the g/ROC reinvestment-consistency check — is the guardrail that
*replaces* the old "TV >80% = trap" rule (which canon rejects as a reliability test).

## THE BALANCE (the Munger caveat — do NOT skip)
Extending the explicit window raises IV — so it MUST be paired with:
- the **conviction-scaled margin of safety** (buy_below = iv_base × (1 − required_MoS)), and
- the **IRR-beats-~10%-Nifty** opportunity-cost gate.
A longer runway widens the IV *range*; it does not lower the MoS you demand. A wonderful compounder
at a heroic price is still a WATCH, not a BUY. The fix is **don't falsely demote** — not "pay anything."

## OUTPUT (feeds the v2 machinery)
A conservative **IV range** (iv_low / iv_base / iv_high) from the multi-stage DCF, with the explicit-window
length, g-vs-ROIC reinvestment assumptions, fade path, and terminal g stated. `sell = iv_high`;
`buy_below = iv_base × (1 − required_MoS)`. If the reverse-DCF says heroic, say so honestly.

## Hard rules
1. Pass the **STEP -1 false-precision gate first**: if the buy case only survives at the far end of a 10–15yr
   projection, it's an artifact — WATCH, not BUY. Extend the window ONLY for a CIO-confirmed durable compounder
   whose moat verdict earns it (`[[runway-length-equals-moat-durability]]`); default to 5yr otherwise.
2. Always fade growth AND ROIC; never perpetuity-extrapolate peak metrics.
3. Stable terminal g ≤ risk-free (`terminal-growth-rate-riskfree-rate-cap`). **Do NOT use a fixed "TV >80% =
   trap" rule** — canon rejects TV-share as a reliability test (`terminal-value-percent-dcf-value-not-a-reliability-test`).
   Discipline the terminal value with the **reverse-implied-growth check** + **g/ROC reinvestment consistency**
   (`reinvestment-rate-terminal-value-consistency`) instead; a high TV share is normal for a real compounder.
4. Always run the reverse-DCF heroic-check; the MoS + IRR gates still bind. For India, model the longer window
   AND the higher country-risk discount rate **both ways** and demand a larger MoS — the net effect is not
   assumed positive (the extended-India-window itself is an acknowledged ungrounded gap).
5. Cite only canon slugs the consult returns; the binding CIO judges the moat that earns the runway. If the
   subject is a bank/financial, STOP and use `bank-valuation`. Desk atomics (`vault/desk/valuation/atomic/…`)
   are referenced via `[[slug]]` as connective tissue — they are not authored or edited here, and perspectives
   may inform window length but never override the binding CIO's veto.
