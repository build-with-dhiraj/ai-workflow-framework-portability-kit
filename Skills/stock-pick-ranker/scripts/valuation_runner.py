#!/usr/bin/env python3
"""
Valuation helpers wrapping the FIXED creating-financial-models DCFModel, plus
method-appropriate alternatives. Run with /usr/bin/python3 (needs numpy via that model).

Provides:
  forward_value(inp)            -> equity value per share (forward DCF at given Ke)
  reverse_implied_growth(inp,p) -> flat revenue growth the price implies (binary search; monotone)
  justified_pb_growth(pb,roe,ke)-> implied book-value growth for a bank/NBFC (Gordon)
  ev_sales(mcap,net_debt,sales) -> EV/Sales multiple for loss-makers
  verdict(implied, demonstrated)-> (verdict, valuation_score_1to5)

`inp` dict (₹cr for money, crore for shares):
  base_revenue, ebitda_margin, depreciation_pct, capex_pct, nwc_pct, tax(0.25),
  terminal_growth(0.045), beta, cost_of_debt(0.09), debt_to_equity, net_debt, shares,
  risk_free(0.069), erp(0.055), proj_years(5)

Example: /usr/bin/python3 valuation_runner.py '<json inp>' <current_price>
"""
import json
import sys

sys.path.insert(0, "/Users/pw/.claude/skills/creating-financial-models")
from dcf_model import DCFModel  # noqa: E402


def _build(inp):
    m = DCFModel(inp.get("company", "Co"))
    base = float(inp["base_revenue"])
    nwc_pct = float(inp.get("nwc_pct", 0.10))
    # seed one year of history so the model anchors NWC to a real level
    m.set_historical_financials(
        revenue=[base], ebitda=[base * float(inp["ebitda_margin"])],
        capex=[base * float(inp.get("capex_pct", 0.05))],
        nwc=[base * nwc_pct], years=[0],
    )
    return m, base, nwc_pct


def _assume(m, inp, growth):
    yrs = int(inp.get("proj_years", 5))
    m.set_assumptions(
        projection_years=yrs,
        revenue_growth=[growth] * yrs,
        ebitda_margin=[float(inp["ebitda_margin"])] * yrs,
        tax_rate=float(inp.get("tax", 0.25)),
        capex_percent=[float(inp.get("capex_pct", 0.05))] * yrs,
        nwc_percent=[float(inp.get("nwc_pct", 0.10))] * yrs,
        terminal_growth=float(inp.get("terminal_growth", 0.045)),
        depreciation_percent=[float(inp.get("depreciation_pct", inp.get("capex_pct", 0.05)))] * yrs,
    )
    m.calculate_wacc(
        risk_free_rate=float(inp.get("risk_free", 0.069)),
        beta=float(inp.get("beta", 1.0)),
        market_premium=float(inp.get("erp", 0.055)),
        cost_of_debt=float(inp.get("cost_of_debt", 0.09)),
        debt_to_equity=float(inp.get("debt_to_equity", 0.0)),
    )


def forward_value(inp, growth=None):
    m, base, _ = _build(inp)
    g = inp.get("base_growth", 0.10) if growth is None else growth
    _assume(m, inp, g)
    m.project_cash_flows()
    m.calculate_enterprise_value()
    eq = m.calculate_equity_value(net_debt=float(inp.get("net_debt", 0)),
                                  shares_outstanding=float(inp.get("shares", 100)))
    return eq["value_per_share"]


def reverse_implied_growth(inp, price, lo=-0.10, hi=0.80, tol=0.005):
    """Flat revenue growth that makes equity value/share == price (model is monotone in g)."""
    f = lambda g: forward_value(inp, g) - price
    flo, fhi = f(lo), f(hi)
    if flo > 0:          # even at -10% growth the model over-values vs price
        return lo, "below"
    if fhi < 0:          # unreachable even at +80% growth (often a thin-margin model artifact)
        return hi, "clamped"
    for _ in range(60):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < tol * max(price, 1):
            return mid, "ok"
        if fm < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2, "ok"


def justified_pb_growth(pb, roe, ke):
    """Gordon bank model: g_implied = (PB*Ke - ROE)/(PB - 1)."""
    pb, roe, ke = float(pb), float(roe), float(ke)
    if abs(pb - 1) < 1e-6:
        return None
    return (pb * ke - roe) / (pb - 1)


def ev_sales(mcap, net_debt, sales):
    return (float(mcap) + float(net_debt)) / float(sales) if float(sales) else None


def verdict(implied, demonstrated):
    """Return (verdict, valuation_score_1to5)."""
    if demonstrated is None or abs(demonstrated) < 0.02:
        # flat/declining base -> classify on absolute implied growth
        if implied <= 0.05:
            return "Undemanding", 4.5
        if implied <= 0.12:
            return "Reasonable", 3.5
        if implied <= 0.30:
            return "Demanding", 2.25
        return "Heroic", 1.25
    ratio = implied / demonstrated
    if ratio <= 0.8:
        return "Undemanding", 4.75
    if ratio <= 1.1:
        return "Reasonable", 3.75
    if ratio <= 1.5 and implied <= 0.30:
        return "Demanding", 2.25
    return "Heroic", 1.0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = json.loads(sys.argv[1])
    price = float(sys.argv[2]) if len(sys.argv) > 2 else None
    fv = forward_value(inp)
    out = {"forward_value_per_share": round(fv, 2)}
    if price:
        g, status = reverse_implied_growth(inp, price)
        out.update({"current_price": price, "implied_growth": round(g, 4),
                    "reverse_status": status, "upside_pct": round(fv / price - 1, 4)})
    print(json.dumps(out, indent=2))
