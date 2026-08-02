---
name: bank-valuation
description: >
  Use when valuing a BANK, NBFC, small-finance bank, or insurer — any financial-services
  stock where ROCE and free-cash-flow break down and the stock-onboarding v2 machinery's
  `bank` model applies (CSBBANK, UJJIVANSFB, NORTHARC, KOTAKBANK, HDFCLIFE, etc.). Provides
  the equity-side method a financial-firm analyst uses — justified-P/B / excess-return /
  equity-DCF, through-cycle provisioning, the regulatory-capital growth constraint, and the
  deposit-franchise moat read. This is the fix for the vault being thin on bank principles
  (the least-grounded IVs on the dashboard). Triggers: "value this bank", "bank IV",
  "justified P/B", "how do I value an NBFC/insurer", grading any `--model bank` name.
---

# Bank / Financial-Firm Valuation (the finance-desk "bank analyst")

The binding Munger/Buffett vault is thin on bank-specific valuation, so bank IVs were the
weakest numbers on the Action Dashboard. This skill encodes Damodaran's free financial-firm
method as a reusable procedure. Ground every step in the canon (below) — never free-hand a bank IV.

## STEP 0 — Pull the canon (binding-safe) — ALWAYS on `--corpus blended` with financial-firm seeds
The Damodaran "Valuing Financial Service Firms" method-atomics are in the `canon` layer, tagged
`analyst_role: banks`. Surface them the way every other finance-desk skill does — **`--corpus blended`
(which admits the canon AND desk layers alongside the binding CIO) plus explicit financial-firm seed terms
appended to `--company`** so the cold consult pulls the Damodaran atomics by relevance. Without those seeds a
bare bank name can miss the financial-firm canon:
```bash
set -a && source /Users/Dhiraj/dev/invest/.env && set +a && /Users/Dhiraj/dev/invest/.venv/bin/python \
  /Users/Dhiraj/dev/invest/data/scripts/32_consult_brain.py \
  --company "<bank name> justified price to book excess return equity valuation regulatory capital deposit franchise cost of funds provisioning through cycle" \
  --model bank --step intrinsic-value --corpus blended \
  --json-out extracted/grilling/<TICKER>_bankval.json
```
`cites_principles` ⊂ the returned slugs. ALSO run the normal binding consult (`--corpus binding`,
the Munger/Buffett CIO) for conviction/moat — the canon is the *method*, the CIO is the *judge*.
**Hard rule (load-bearing):** a bank brain query that **omits the financial-firm `--company` seed terms is invalid**
— a bare `--company "<bank name>"` can return 0 Damodaran financial-firm atomics and the agent will silently
*free-hand* the IV, which is the exact failure this skill exists to fix. `--model bank` + `--corpus blended` +
the seed terms is the working pattern.

## STEP 0.5 — Pull the CIO bank-temperament gate (binding, qualitative)
Before computing any number, retrieve the binding bank-character atoms and treat them as a **gate the IV must
survive**, not flavour text: `discipline-in-lending-creates-extraordinary-returns`,
`avoid-fads-and-bad-loans-in-banking`, `complexity-increases-risk-of-error-and-fraud`,
`prioritize-corporate-culture-and-morality`. This operationalises "the CIO is the judge": a numerically high IV
on a **fad-chasing, low-culture, or opaque** lender is **capped or rejected** regardless of the math. Banking
is a business where a few years of undisciplined lending quietly destroys a decade of book value — the
temperament read precedes the valuation.

## WHY firm-DCF fails for banks (the core insight)
For a bank, **debt is raw material, not financing** — you can't separate operating from financing
flows, capex/working-capital are ill-defined, and FCFF is meaningless. So **value EQUITY directly**,
in this order of preference:

## METHOD (preferred → fallback)
1. **Excess-return (justified-value) model — PREFERRED.**
   `Value of equity = Book Equity + PV[ (ROE − Ke) × Book Equity ]`, the excess return growing at g.
   In steady state this collapses to the **justified price-to-book**:
   `Justified P/B = (ROE − g) / (Ke − g)`.
   A bank only deserves P/B > 1 when **ROE > Ke**; if ROE ≤ Ke it is worth ≤ book (and conviction caps at 2).
   *Worked sketch:* ROE 15%, Ke 13%, g 8% → P/B = (0.15−0.08)/(0.13−0.08) = **1.4× book**.
2. **Equity-DCF / Dividend-Discount.** Discount **FCFE** (≈ net income − reinvestment needed to hold
   regulatory capital) — or dividends if payout is stable — at the cost of EQUITY (Ke), never WACC.
3. **Relative (sanity-check).** P/B vs ROE across comparable Indian banks/NBFCs; a high-ROE franchise
   should trade at a justified premium, not the sector median.

## THE THREE ADJUSTMENTS THAT MATTER
- **Normalize provisioning THROUGH THE CYCLE — but forensic-screen the book FIRST**
  (`[[normalize-bank-provisioning-through-cycle]]`). Current ROE is distorted by where the credit cycle is —
  under-provisioning inflates ROE (and IV), over-provisioning deflates it. Use a **mid-cycle credit cost**, not
  the latest quarter. This is the single biggest bank-IV error. **Gate it:** before normalizing, screen the
  book for **evergreening / hidden-NPA / under-provisioning** — a normalized credit cost computed on a *managed*
  book is fiction (`complexity-increases-risk-of-error-and-fraud`, `greater-due-diligence-required-for-financials`).
  Hand off the asset-quality red-flag check to **`forensic-accounting-redflags`** and only normalize on a book
  that survives it.
- **Regulatory capital is FORCED reinvestment** (`[[regulatory-capital-is-forced-reinvestment]]`). Growth needs
  retained equity to keep CAR above the RBI minimum, so **sustainable g ≤ ROE × retention ratio**. A bank can't
  grow faster than its capital allows without dilution — model the dilution if it raises equity. Unlike a
  capital-light compounder, a bank cannot *choose* to return this capital; it is conscripted to fund the balance
  sheet, which is why a high headline ROE with thin capital is not the same quality as a self-funding franchise.
- **Cost of equity (Ke) via CAPM**, India: `Ke = rf (~6.9%) + β × ERP (~5.5%)`. Use a bank-appropriate β
  (leverage + regulatory risk push it up). Be conservative — a too-low Ke is how banks get over-valued.

## THE MOAT READ (for conviction, not just IV)
**The deposit franchise IS the bank's float** (`[[deposit-franchise-is-bank-float]]`; Munger
`use-float-for-compounding`): a sticky, low-cost CASA base is **cheap, semi-permanent capital** the bank
compounds on — that float, not the loan book, is the durable moat, and it is what lets a disciplined lender earn
ROE > Ke through-cycle (`underappreciated-moats-in-commodity-businesses` — even in "commodity" banking a real
funding edge produces unexpectedly high returns). Assess deposit stickiness, CASA ratio trend, and cost-of-funds
vs peers; cross-link `moat-analysis` for the switching-cost/scale lens behind a sticky deposit base. A lender
with no funding advantage is a commodity. Per the v2 rubric: **ROE below cost-of-equity → cap conviction at 2**;
no funding moat → narrow moat.

## INDIA / SFB CAVEAT (an acknowledged vault hole — stay honest)
The canon is Damodaran's 2009-vintage, US-framed financial-firm method. There is **NO India-specific atomic** in
the brain for NIM, CASA dynamics, the NPA cycle, ECL provisioning, or RBI / SFB capital-adequacy (CAR) minimums.
So you must **hand-supply** current Indian regulatory inputs (RBI CAR floor, SFB priority-sector + CRR/SLR drag,
ECL norms) and **mark them explicitly as un-grounded assumptions** in the output — never present a hand-supplied
India regulatory number with canon-like authority. Apply the regulatory-capital constraint with *current* RBI
minimums and flag them as agent-supplied. Default conservative when the India input is uncertain.

## OUTPUT (feeds the v2 machinery)
Return a conservative **IV range** (iv_low / iv_base / iv_high) as a justified equity value (or P/B × book).
`buy_below = iv_base × (1 − required_MoS)` (conviction-scaled); `sell = iv_high`. Honor the IRR-beats-~10%-Nifty
gate. State the ROE, Ke, mid-cycle credit cost, and g assumptions explicitly — a bank IV with hidden assumptions
is not a real number.

## Hard rules
1. Never use FCFF/WACC/ROCE for a bank — equity-side only (Ke, FCFE, justified-P/B).
2. Always normalize provisioning to mid-cycle before computing ROE — and only on a book that has **survived the
   forensic evergreening/hidden-NPA screen** (`forensic-accounting-redflags`); a normalized credit cost on a
   managed book is fiction.
3. **Always query with `--corpus blended` + financial-firm `--company` seed terms** (justified P/B, excess
   return, regulatory capital, deposit franchise, provisioning-through-cycle) — a bare bank name returns 0
   financial-firm canon and the IV gets free-handed. Cite only canon slugs the consult actually returns; if
   `principles` is thin, flag it and stay conservative. Hand-supplied India regulatory inputs (NIM/CASA/NPA/CAR)
   are labelled un-grounded.
4. **Discount every pitch-side re-rating thesis.** A high-ROE bank framed as "mispriced on mix-shift / fortress
   balance sheet" enters `iv_base` ONLY if the excess return is structurally sustainable through-cycle — route
   it through `leverage-magnifies-errors` first (on a levered financial a wrong re-rating call is amplified into
   a large equity error) (`[[discount-the-bank-re-rating-pitch]]`). Perspective voices are inputs to be
   discounted, never the verdict.
5. The IV must survive the **STEP 0.5 CIO temperament gate** (culture / lending-discipline / opacity). The
   Munger/Buffett binding CIO remains the arbiter of moat/verdict; this skill supplies the *number*, not the
   *verdict*. Desk atomics (`vault/desk/banks/atomic/…`) are referenced via `[[slug]]` as connective tissue —
   not authored or edited here.
