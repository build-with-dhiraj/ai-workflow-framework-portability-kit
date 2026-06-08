# Enrichment — live financials & Substack extraction

## Golden rule
**Never fabricate a number.** Record a figure only if a real source shows it; cite the source URL;
mark any reasoned estimate as an estimate. A ranking built on invented financials is worthless. The
user's standing rule is also: **drive every stock to High confidence** by going to the web and filling
the hard data — "Low confidence because the article didn't say" is not acceptable; the data is public
for listed companies. (Confidence reflects *data completeness*; earnings-quality nuances go in
`red_flags`, not confidence.)

## Sources
Screener.in (primary — has the ratios + multi-year tables), then Moneycontrol / Tickertape /
Trendlyne / company investor presentations / BSE-NSE. Cross-check two sources where a figure looks off.
Verify the ticker yourself (don't trust a guessed symbol).

## Currency
India FY ends March. Target the **latest full FY + the latest reported quarter**, and stamp an
`as_of` month. Beware calendar-year reporters (e.g. some commodity names) — note it.

## Fields to gather (₹ crore unless noted)
Standard (non-financial):
`price_inr, market_cap_cr, pe_ttm, pb, roce_pct, roe_pct, op_margin_pct, net_margin_pct,
rev_fyN_cr, rev_fyN-1_cr (3–4y history), rev_growth_pct, rev_cagr_3y_pct, pat_fyN_cr, pat_fyN-1_cr,
pat_growth_pct, pat_cagr_3y_pct, depreciation_cr (D&A — needed for DCF, separate from capex),
capex_cr, total_debt_cr, debt_to_equity, net_cash_or_debt, nwc (or working-capital days),
shares_outstanding (CRORE), promoter_holding_pct, promoter_pledge_pct, latest_quarter, q_pat_yoy_pct,
div_yield_pct, beta`.

Per-type extras:
- **Bank / NBFC:** `roa_pct, nim_pct, gnpa_pct, car_pct, pb` (use these instead of ROCE/EV).
- **InvIT:** distribution/unit, distribution yield, NDCF/payout, net-debt/AUM, rating, sponsor, WALE.
- **Loss-maker:** revenue + EV components (for EV/Sales); P/E is N/A.
- **Cyclical/commodity:** capture the multi-year margin band so a *through-cycle* margin can be set.

Always capture **governance** signals: promoter holding %, **pledge %**, and any audit/regulatory/
related-party/demerger/MPS-overhang flags → these drive factor F6 and Low-confidence/cyclical tags.

## Units discipline (avoids per-share nonsense)
Keep money in **₹ crore** and share counts in **crore** so `value_per_share = equity_value_cr /
shares_cr` comes out in ₹. Sanity-check any computed fair value against the live price's order of magnitude.

## Output (`extracted/enriched/*.json`)
```json
{"stocks":[{"company":"","ticker":"","as_of":"YYYY-MM","price_inr":"","market_cap_cr":"","pe_ttm":"",
  "pb":"","roce_pct":"","roe_pct":"","op_margin_pct":"","net_margin_pct":"","rev_fy_cr":"","rev_growth_pct":"",
  "rev_cagr_3y_pct":"","pat_fy_cr":"","pat_growth_pct":"","pat_cagr_3y_pct":"","depreciation_cr":"","capex_cr":"",
  "total_debt_cr":"","debt_to_equity":"","net_cash_or_debt":"","nwc_cr":"","shares_cr":"","roa_pct":"","nim_pct":"",
  "gnpa_pct":"","car_pct":"","promoter_holding_pct":"","promoter_pledge_pct":"","div_yield_pct":"",
  "governance_notes":"","data_quality":"High|Medium|Low","sources":[""]}]}
```
Use **exact** company names so downstream joins work (normalise by dropping trailing Ltd/Limited and
parenthetical aliases when matching).

---

## Substack extraction (only when given profiles)
Use `scripts/substack_fetch.py` (Substack public JSON API, no key):
1. **Resolve** handle → publication: `…/api/v1/user/<handle>/public_profile` → `primaryPublication.subdomain`.
2. **List** posts: `https://<sub>.substack.com/api/v1/archive?sort=new&offset=N&limit=50` (paginate);
   each post has `title, slug, post_date, audience` (`everyone`=free, `only_paid`=paywalled),
   `canonical_url`.
3. **Body** (free only): `https://<sub>.substack.com/api/v1/posts/<slug>` → `body_html` (strip tags).
   **Paid bodies are truncated/empty — the user must paste them manually.** Podcast/video posts also
   have empty bodies.
Then per article, extract the **main recommended stock(s)** + `thesis_crux`, `key_risk`,
`upside_target`, `sector`, ticker if stated. Skip thematic/educational posts (no specific pick) → list
them separately as "no_pick". One row per main pick. Record only what the author states.
