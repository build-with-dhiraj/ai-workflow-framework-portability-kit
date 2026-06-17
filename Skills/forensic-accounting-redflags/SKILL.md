---
name: forensic-accounting-redflags
description: >
  Use at the DOSSIER / UNDERSTANDING stage (Stage 1) on EVERY stock to run the governance-integrity
  screen before any conviction or IV work. India-specific promoter and accounting red-flag checklist
  grounded in the SEBI-Satyam, SEBI-IL&FS-CRA, and Damodaran-forensic canon. Covers: CF-vs-PAT
  divergence, fabricated cash / bank-confirmation tests, related-party loan and pledge chains,
  promoter share-pledging, auditor independence and resignation signals, provisioning games,
  asset-liability maturity mismatch (NBFC / infra), group-entity opacity / interdependency
  complexity, and insider-trading sale patterns. Outputs a GOVERNANCE-RISK verdict (CLEAN /
  CAUTION / RED) that can cap conviction or push a name to AVOID / TOO_HARD — it is a defensive
  gate, not a valuation. A RED verdict hard-fails the thesis; CAUTION caps conviction at 2.
  Triggers: "run the forensic screen", "check governance", "red flags", "is the accounting clean",
  "related-party risk", "pledge risk", "auditor concerns", dossier stage on any new name.
---

# Forensic Accounting & Governance Red-Flag Screen (the finance-desk "forensic accountant")

**Role:** defensive capital-protector gate. This screen runs BEFORE conviction, BEFORE IV. A
fraudulent or severely-mismanaged business does not earn a conviction grade — it earns AVOID or
TOO_HARD.

**The binding frame (why this gate exists):** *accounting red flags are incentive-caused bias made
visible* ([[forensic-redflags-are-incentive-bias-made-visible]]). Every dimension below is a place
where management's incentives to flatter the numbers leave a forensic fingerprint — Munger's
[[incentive-caused-bias-distorts-judgment]] and Buffett's [[avoid-accounting-gimmicks]] are the
binding anchors, and the nine quantitative tests are simply how that bias becomes measurable. The
gate's authority therefore *ladders up to the binding CIO*, not down from academic canon. This is
what makes Hard Rule 4 (CIO management-integrity supersedes a forensic CLEAN) load-bearing: the
Munger/Buffett vault is the binding CIO; this skill supplies the forensic *technique*, not the
*verdict*. The CIO's management-integrity and owner-orientation principles override any forensic
"pass" that conflicts with them.

## STEP 0 — Pull the canon (binding-safe)

The SEBI-Satyam, SEBI-IL&FS-CRA, and Damodaran-forensic method-atomics live in the `canon`
layer. Pull them before running the checklist:

```bash
set -a && source /Users/pw/invest/.env && set +a && /Users/pw/invest/.venv/bin/python \
  /Users/pw/invest/data/scripts/32_consult_brain.py \
  --corpus canon \
  --company "<company name> cash flow PAT related party pledge auditor provisioning NBFC group entity insider trading forensic" \
  --model <bank|general|...> \
  --step circle \
  --json-out extracted/grilling/<TICKER>_forensic.json
```

Cite only slugs that appear in the returned `principles[].slug`. If `principles` comes back empty
or thin, flag it and stay conservative — abstain rather than fabricate.

(Use `--corpus blended` instead of `--corpus canon` when you also want the desk-synthesis
connective atomics — `[[forensic-redflags-are-incentive-bias-made-visible]]`,
`[[acquisition-accounting-is-a-shared-forensic-and-capital-allocation-redflag]]`,
`[[a-cheap-turnaround-framing-cannot-reverse-a-governance-flag]]`,
`[[a-forensic-flag-must-become-an-immutable-kill-criterion]]` — surfaced alongside the binding
layer. `blended` keeps the Munger/Buffett CIO primary and down-weights pitch-side voices.)

## STEP 0b — Ladder the verdict up to the binding CIO

STEP 0 pulls the forensic *technique* from canon. STEP 0b pulls the binding *authority* — run the
Munger/Buffett consult and confirm the four binding anchors are returned before you trust any
verdict:

```bash
set -a && source /Users/pw/invest/.env && set +a && /Users/pw/invest/.venv/bin/python \
  /Users/pw/invest/data/scripts/32_consult_brain.py \
  --corpus binding \
  --company "<company> incentive-caused bias accounting gimmicks operating cash flow faulty accounting management integrity" \
  --model <bank|general|...> \
  --step conviction \
  --json-out extracted/grilling/<TICKER>_forensic_binding.json
```

The four binding anchors this gate ladders up to are
[[focus-on-operating-cash-flow]], [[avoid-accounting-gimmicks]],
[[incentive-caused-bias-distorts-judgment]], and [[do-not-rely-on-faulty-accounting-or-ratings]].
The CIO's read on management character supersedes the forensic checklist: a technically-CLEAN
screen still yields CAUTION if the binding consult flags integrity. The forensic dimensions are
*how* the bias shows up; these anchors are *why* the gate has authority.

**Channel-check handoff (don't stay filing-desk-bound).** The filing is what management chose to
disclose; triangulate it ([[triangulation-of-banker-and-auditor-feedback]]). Where a flag turns on
counterparty behaviour — lenders quietly cutting limits, an auditor's informal reputation, supplier
or distributor whispers — hand the channel-check to the **primary-research-sentiment** skill and
fold its read back into the dimension that raised the flag. A filing that looks CLEAN while bankers
are de-risking is a CAUTION, not a pass.

## CHECKLIST — nine red-flag dimensions

Run every dimension. Mark each **CLEAR / FLAG / HARD-FAIL** and note the evidence or absence.

---

### 1. Cash-Flow vs PAT Divergence (accrual-cash gap)
*Canon: [[earnings-quality-gap-analysis]], [[accounting-malfeasance-red-flags-checklist]]*

- Compare operating-cash-flow vs PAT over ≥5 years. Persistent OCF < PAT is the single most
  reliable signal of earnings inflation (aggressive accruals, revenue recognized before cash
  arrives, deferred cost capitalisation).
- **Flag threshold:** OCF/PAT < 0.75 in ≥3 of 5 years, or a sudden deterioration after a
  management change.
- Check for large, growing "other receivables" or "advances to suppliers/subsidiaries" — common
  hiding spots for cash diversion that inflate PAT while OCF bleeds.
- **HARD-FAIL:** OCF negative while PAT is consistently positive with no capex-cycle explanation.

---

### 2. Fabricated Cash / Bank-Confirmation Test
*Canon: [[cash-balance-fabrication-test]], [[test-for-inflated-cash-balances-and-bank-confirmations]], [[auditor-confirmation-reliability-check]]*

- Cross-check reported cash + bank balances against:
  (a) interest income earned (implied yield on reported balance — an implausibly low yield signals
      fictitious cash that earns nothing);
  (b) auditor bank-confirmation notes in the audit report (Satyam lesson: confirmations can be
      fabricated if the auditor doesn't independently verify with the bank);
  (c) schedule of cash balances vs bank certificates in the annual report.
- **Flag:** reported cash ≫ interest income implies; auditor did not independently confirm with
  multiple banks; bank balances concentration in a single related-party bank.
- **HARD-FAIL:** restatement of cash balances; auditor qualified the bank-confirmation procedures.

---

### 3. Related-Party Loan and Pledge Chains
*Canon: [[related-party-loan-and-pledge-chain-analysis]], [[related-party-entity-mapping]], [[forensic-footnote-mining-for-hidden-assets-and-liabilities]]*

- Map all related-party transactions from Schedule of Related Party Disclosures (Ind AS 24):
  loans given to / received from promoter-owned entities, purchases/sales between group companies,
  guarantees extended.
- Trace fund flows: loans from the listed entity → related party → back as equity or further
  loans (circular funding = siphoning red flag).
- Mine footnotes for off-balance-sheet guarantees, contingent liabilities with related parties,
  and any "advances" that have been outstanding ≥1 year without repayment.
- **Flag:** material unsecured loans to promoter-related entities; growing inter-company
  receivables; RPT volumes > 15% of revenue without clear arm's-length rationale.
- **HARD-FAIL:** circular RPT flow confirmed; loans written off to related parties.

---

### 4. Promoter Share Pledging
*Canon: [[promoter-share-pledge-tracing]], [[pledge-margin-trigger-risk-assessment]]*

- Check BSE/NSE pledging disclosures (quarterly) and SHP (shareholding pattern).
- Assess: % of promoter holding pledged; trend (rising pledge = rising leverage at the promoter
  level); which lenders hold the pledge; any margin-call trigger history.
- Pledged shares fund promoter-level debt — the listed entity is the collateral. A margin-call
  cascade can force a block sale that decimates the stock and the promoter's control.
- **Flag:** ≥20% of promoter holding pledged; pledge % rising YoY; promoter holding already
  below 40% (limited buffer before loss of control).
- **HARD-FAIL:** pledge ≥50% of promoter holding + evidence of promoter-level financial stress
  (defaults, court orders against promoter entities).

---

### 5. Auditor Independence and Resignation Signals
*Canon: [[auditor-confirmation-reliability-check]], [[cross-verification-of-management-disclosures]]*

- Check: auditor tenure (excessively long tenure with a single Big-4 office = comfort-capture
  risk; Satyam's PW signed off for years); auditor resignations mid-year (Indian law requires
  explanation — a resignation before completing the audit is a hard signal); qualifications or
  emphasis-of-matter paragraphs in the audit report; restatements requiring re-audit.
- **Flag:** auditor resignation in the last 3 years; qualified opinion on any material line item;
  auditor downgraded from Big-4 to a small/unknown firm without explanation.
- **HARD-FAIL:** auditor cited the company for going-concern doubts; auditor resigned and no
  replacement was appointed for ≥30 days; SEBI/NFRA enforcement action against the auditor on
  this engagement.

---

### 6. Provisioning Games and Aggressive Accounting Policies
*Canon: [[provisioning-and-accounting-policy-scrutiny]], [[accounting-malfeasance-red-flags-checklist]], [[earnings-quality-gap-analysis]]*

- Review the accounting policies note (Schedule of Significant Accounting Policies) and compare
  YoY for silent changes in depreciation life, provisioning rates, revenue recognition, or
  capitalisation of R&D / pre-operative expenses.
- For NBFCs and banks: check NPA recognition lag (RBI norms require 90-day NPD; some NBFCs
  use 120+ DPD under regulatory forbearance); compare reported Gross NPA% with SEBI stress-test
  disclosures and peer NPA ratios at similar ticket sizes.
- Sudden drop in effective tax rate, large deferred-tax asset creation, or income from "sale of
  investments" used to prop operating profit are Damodaran's flagged red-flag patterns.
- **R&D / pre-operative capitalization adjustment** ([[rd-expense-capitalization-adjustment]]):
  re-expense any capitalised R&D or pre-operative cost back through the P&L and ask — does reported
  profit survive? If margins collapse once the capitalisation is unwound, the "quality" was
  accrual-manufactured. Run this as a **binary red-flag trigger (yes/no)**, not a valuation
  re-build — IV stays downstream and is voided entirely on a RED verdict.
- **Return-on-capital decomposition** ([[decompose-return-on-capital]]): split ROC into
  margin × capital-turnover. A "high-ROC" business whose return is driven by an implausibly thin
  capital base (aggressive capitalisation, off-balance-sheet assets, related-party leverage) is
  showing manufactured quality, not a real franchise — flag the mismatch and hand the durability
  question to the **moat-analysis** skill (the ROIC-vs-WACC signature test there).
- **Flag:** accounting policy changes that mechanically inflate profits; NPA provisions below peer
  median with no credit-quality explanation; growing deferred revenue or contract liabilities
  that never convert to cash; reported margin does not survive the R&D re-expensing.
- **HARD-FAIL:** SEBI enforcement action for accounting fraud; statutory auditor flagged
  provisioning adequacy in emphasis-of-matter.

---

### 7. Asset-Liability Maturity Mismatch (NBFC / Infra / Group-Entity)
*Canon: [[asset-liability-mismatch-detection]], [[stress-testing-liquidity-under-adverse-scenarios]], [[alignment-of-fund-inflow-timing-with-obligation-dates]]*

- Applicable to any NBFC, HFC, infrastructure holding company, or large group with
  debt-funded subsidiaries.
- Map the ALM bucket disclosure (RBI mandated for NBFCs): short-term borrowings (CP, NCDs
  < 1yr) funding long-term loan assets (mortgage, infra) is the IL&FS pattern — a liquidity
  crisis can crystallise overnight even when solvency looks fine.
- Check CP/NCD refinancing schedule vs liquid assets and committed credit lines.
- **Flag:** >30% of borrowings maturing in <1 year with asset book duration >3 years; no
  disclosed committed liquidity backstop; rising CP issuance in a rising-rate environment.
- **HARD-FAIL:** an NCD default or missed CP rollover, even if cured; SEBI or RBI corrective
  action on liquidity.

---

### 7b. Hidden NPA / Evergreening / Restructuring (lenders only)
*Canon: [[asset-liability-mismatch-detection]], [[provisioning-and-accounting-policy-scrutiny]]*

- For any bank / NBFC / HFC, the asset-quality book is the single largest place to hide losses.
  Look for evergreening (fresh loans issued to a stressed borrower to keep an account "standard"),
  serial restructuring, large "standard restructured" or SMA-1/SMA-2 pools, and a divergence
  between RBI's Asset Quality Review (AQR) GNPA and the reported GNPA.
- **Flag:** restructured book growing while headline GNPA falls; provision coverage ratio below
  peer median; recurring "technical write-offs" that flatter GNPA without real recovery.
- **HARD-FAIL:** RBI AQR divergence material and undisclosed; a restated NPA book; promoter-group
  borrower kept standard through related-party refinancing.
- **HANDOFF — the thinnest forensic seam.** Lender asset-quality forensic canon is sparse, so the
  *verdict* on whether the book is honestly stated belongs to the **bank-valuation** skill plus
  SEBI/RBI canon — NOT to pitch-side perspective voices commenting on the lender. This dimension
  raises the flag; `bank-valuation` quantifies it (cost-of-funds, credit-cost normalisation,
  Ke vs ROA). Carry the flag forward; do not resolve it here.

---

### 8. Group-Entity Interdependency / Complexity Opacity
*Canon: [[group-entity-interdependency-analysis]], [[complexity-scorecard-financial-statements]], [[forensic-footnote-mining-for-hidden-assets-and-liabilities]]*

- Build a complexity scorecard: count subsidiary/associate/JV entities, cross-holdings, guarantees
  extended to group entities, off-balance-sheet vehicles, and intra-group eliminations that are
  material.
- IL&FS had 348 group entities — complexity itself was the opacity weapon. A listed entity that
  cannot be understood standalone (its cash flows depend on opaque inter-company flows) is
  TOO_HARD or AVOID regardless of headline metrics.
- **Acquisition / consolidation accounting is a shared red flag**
  ([[acquisition-accounting-is-a-shared-forensic-and-capital-allocation-redflag]]): serial
  acquisitions, large goodwill that is never impaired, earn-outs that mask organic decline, and
  consolidation that buries acquired-entity weakness are forensic flags here AND capital-allocation
  flags. Raise the forensic flag and hand the *quality of the deal-making* to the
  **capital-allocation-judge** skill — the two desks share this signal.
- **Flag:** ≥20 subsidiaries/associates with material intra-group transactions; consolidation
  eliminates ≥20% of gross revenue; auditor's report on subsidiaries includes qualifications not
  visible in the standalone.
- **HARD-FAIL:** group entity list changes materially YoY with no disclosed rationale; a
  subsidiary that is a significant borrower is unaudited or has a different (smaller) auditor.

---

### 9. Insider-Trading Sale Patterns
*Canon: [[insider-trading-sale-pattern-analysis]], [[insider-trading-pattern-detection]], [[promoter-share-pledge-tracing]]*

- Pull SAST/bulk-deal disclosures and NSE/BSE insider-trading disclosures (Form C/D) for promoter
  and key-managerial-personnel (KMP) transactions.
- Flag coordinated selling by promoters/KMPs during "positive sentiment" windows (strong quarterly
  results, bullish analyst commentary) that predated a negative event — the Satyam pattern of
  insider liquidation while concealing fraud.
- Check SEBI enforcement actions: any prior insider-trading charge against the promoter or a
  connected entity, even in a different company, is a character signal.
- **Flag:** promoter/KMP net sellers ≥3 of last 5 quarters while publicly making bullish
  statements; block deal at a significant discount to market; SEBI investigation (even
  pending, not convicted).
- **HARD-FAIL:** SEBI proven or court-confirmed insider-trading conviction against the promoter
  in any entity.

---

## SCORING AND GOVERNANCE-RISK VERDICT

After running all nine dimensions, tally the signals and issue one verdict:

| Verdict | Criteria | Effect on pipeline |
|---------|----------|--------------------|
| **CLEAN** | 0 HARD-FAILs, ≤2 FLAGs, no flags in dimensions 2, 3, or 4 | No cap; proceed to conviction normally |
| **CAUTION** | 0 HARD-FAILs but ≥3 FLAGs, OR any FLAG in dim 2/3/4 | **Cap conviction at 2**; requires explicit disclosure in dossier; WATCH/AVOID bias |
| **RED** | Any HARD-FAIL in any dimension | **Hard-fail the thesis** → AVOID or TOO_HARD; do not compute IV; note the specific trigger |

State the verdict, the dimension(s) that drove it, and the specific evidence (filing, year, source).

**Post-fraud disposition (RED pathway):** once fraud is *established* (not merely suspected), the
intrinsic value is **voided, not discounted** ([[intrinsic-value-adjustment-rejection-in-fraudulent-context]]).
Do NOT net any residual book value, "salvageable" segment, or sum-of-parts floor back into the
thesis — fraudulent financials cannot be partially trusted, so there is no reliable base to
discount from. The name is AVOID/TOO_HARD with conviction 1, full stop.

## OUTPUT (feeds Stage 1 of the v2 machinery)

Return a structured block to embed in the dossier's `## Governance / Forensic Screen` section:

```
GOVERNANCE-RISK VERDICT: <CLEAN | CAUTION | RED>
Dimensions assessed: 9/9
Flags: [list dimension numbers that FLAGged]
Hard-fails: [list dimension numbers that HARD-FAILed, or NONE]
Key evidence: [1-3 sentences on the most material finding]
Conviction cap: [NONE | 2 (CAUTION) | HARD-FAIL (RED)]
Pipeline effect: [no cap / cap at conv-2 / hard-fail → AVOID|TOO_HARD]
Canon cited: [slug list from the returned principles]
```

## INTEGRATION WITH THE V2 MACHINERY

This screen runs at **Stage 1 (dossier)**, dimension 2 of the dossier template, BEFORE the
conviction consult at Stage 3. The output is a frozen input — it does not get re-run at
re-ranking unless a new governance event occurs (restatement, SEBI action, pledge surge).

- **RED verdict** short-circuits to Stage 6 directly: verdict = AVOID or TOO_HARD, conviction = 1,
  no IV computed. The one-line reason goes into the dossier `kill_criteria` field.
- **CAUTION verdict** flows normally through Stages 2-4 but conviction is hard-capped at 2,
  which by the MoS thresholds (conv2 ≥40%) means the price must be ≥40% below IV-base to buy.
  Effectively, CAUTION names rarely clear the bar — that is intentional.
- **CLEAN verdict** means the forensic gate passes and conviction is set by business quality
  alone (the rubric in stock-onboarding-pipeline KEY REGISTRY).

## Hard rules

1. Run all nine dimensions on every new name — skip nothing because the analyst "likes" the stock.
2. Cite only canon slugs the STEP 0 consult actually returns; never fabricate a citation.
3. A HARD-FAIL in ANY dimension immediately ends valuation work — write AVOID/TOO_HARD and move on.
4. The Munger/Buffett binding CIO's management-integrity verdict supersedes a forensic CLEAN:
   if the vault flags character issues and the forensic screen is technically CLEAN, CAUTION applies.
5. This is a defensive gate, not a valuation — a CLEAN verdict is not a reason to buy; it is a
   prerequisite to proceed.
6. For NBFCs and group-holding-companies, dimension 7 (ALM) and dimension 8 (complexity) are
   mandatory; do not skip them citing "not applicable."
7. Do not re-run this screen on dossiers that already have a frozen governance verdict unless a
   new material governance event has occurred since the original dossier date.
8. **A low-valuation, turnaround, or optionality framing can NEVER reverse a CAUTION/RED verdict.**
   The 30 perspective voices are pitch-side/promotional (down-weighted 0.85) and frame
   balance-sheet stress as upside optionality; they may add context but they may not argue around a
   flag ([[a-cheap-turnaround-framing-cannot-reverse-a-governance-flag]]). For a forever-hold
   mandate, a balance-sheet-stressed special situation is structurally disqualified
   ([[special-situation-vs-compounder-distinction]]; [[do-not-rely-on-faulty-accounting-or-ratings]]).
   Only the binding Munger/Buffett CIO arbitrates the verdict.
9. **Every FLAG / HARD-FAIL is written verbatim into the decision-journal `kill_criteria` at
   discovery time and is immutable** ([[a-forensic-flag-must-become-an-immutable-kill-criterion]];
   [[decision-journal-method]]). It cannot be re-litigated or softened by a later bullish thesis —
   face the reality on the record rather than rationalising it away
   ([[avoid-denial-and-face-reality]]).
