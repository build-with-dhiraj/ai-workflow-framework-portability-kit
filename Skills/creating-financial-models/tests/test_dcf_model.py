"""
Unit tests for dcf_model.DCFModel.

Run standalone (no pytest required):  /usr/bin/python3 tests/test_dcf_model.py
Or with pytest:                       pytest tests/test_dcf_model.py

These cover two fixed economic defects in the free-cash-flow / terminal-value path:

  1. Depreciation was hardcoded to equal capex. It is now a separate assumption
     (`depreciation_percent`) that DEFAULTS to capex_percent for backward
     compatibility, so a firm whose capex >> true D&A (expansion phase) is modelled
     correctly (lower depreciation -> higher taxable EBIT/NOPAT).

  2. NWC change was modelled as a fixed % of revenue, so the LAST projection year
     carried the largest dNWC, and the Gordon terminal value capitalised that
     depressed final-year FCF. Net effect: equity value was a hump-shaped (often
     monotonically DECREASING) function of revenue growth for profitable, high-NWC
     firms -- a pure artifact that also breaks reverse-DCF binary search. The terminal
     value now normalises dNWC to its steady-state level (NWC_level * terminal_growth).
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dcf_model import DCFModel  # noqa: E402


def _equity_value(growth: float, depreciation_percent: float | None = None, base: float = 5000.0):
    """Equity value for the high-NWC profitable parameter set from the bug report,
    at a constant revenue growth rate. Used to assert monotonicity in growth."""
    m = DCFModel("Test")
    m.set_historical_financials(
        revenue=[base], ebitda=[base * 0.18], capex=[base * 0.10],
        nwc=[base * 0.35], years=[2025],
    )
    kwargs = dict(
        projection_years=5,
        revenue_growth=[growth] * 5,
        ebitda_margin=[0.18] * 5,
        tax_rate=0.25,
        capex_percent=[0.10] * 5,
        nwc_percent=[0.35] * 5,
        terminal_growth=0.045,
    )
    if depreciation_percent is not None:  # don't pass the new kwarg unless exercising it
        kwargs["depreciation_percent"] = [depreciation_percent] * 5
    m.set_assumptions(**kwargs)
    m.calculate_wacc(
        risk_free_rate=0.069, beta=1.0, market_premium=0.055,
        cost_of_debt=0.09, debt_to_equity=0.0,
    )
    m.project_cash_flows()
    m.calculate_enterprise_value()
    return m.calculate_equity_value(net_debt=0.0, shares_outstanding=100.0)["equity_value"]


def test_equity_value_nondecreasing_in_growth():
    """Defect 2: for a profitable firm, higher revenue growth must not LOWER value."""
    growths = [-0.05, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25]
    vals = [_equity_value(g) for g in growths]
    for lo, hi in zip(vals, vals[1:]):
        assert hi >= lo - 1e-6, (
            "equity value must be non-decreasing in revenue growth for a profitable "
            f"firm; got {list(zip(growths, vals))}"
        )


def test_depreciation_can_differ_from_capex():
    """Defect 1: depreciation_percent is honoured independently of capex_percent."""
    m = DCFModel("Test")
    m.set_historical_financials(revenue=[1000], ebitda=[200], capex=[100], nwc=[100], years=[2025])
    m.set_assumptions(
        projection_years=3, revenue_growth=[0.10] * 3, ebitda_margin=[0.20] * 3,
        tax_rate=0.25, capex_percent=[0.10] * 3, nwc_percent=[0.10] * 3,
        terminal_growth=0.03, depreciation_percent=[0.04] * 3,
    )
    p = m.project_cash_flows()
    rev0 = p["revenue"][0]
    assert math.isclose(p["depreciation"][0], rev0 * 0.04, rel_tol=1e-9)
    assert math.isclose(p["capex"][0], rev0 * 0.10, rel_tol=1e-9)
    assert math.isclose(p["ebit"][0], p["ebitda"][0] - rev0 * 0.04, rel_tol=1e-9)
    assert p["depreciation"][0] != p["capex"][0]


def test_depreciation_defaults_to_capex():
    """Backward compatibility: omitting depreciation_percent keeps depreciation == capex."""
    m = DCFModel("Test")
    m.set_assumptions(
        projection_years=3, revenue_growth=[0.10] * 3, ebitda_margin=[0.20] * 3,
        capex_percent=[0.08] * 3, nwc_percent=[0.10] * 3, terminal_growth=0.03,
    )
    p = m.project_cash_flows()
    for i in range(3):
        assert math.isclose(p["depreciation"][i], p["capex"][i], rel_tol=1e-9)


def test_terminal_fcf_override():
    """The exposed terminal_fcf override is capitalised directly by the Gordon model."""
    m = DCFModel("Test")
    m.set_assumptions(projection_years=5, terminal_growth=0.04)
    m.calculate_wacc(
        risk_free_rate=0.05, beta=1.0, market_premium=0.05,
        cost_of_debt=0.06, debt_to_equity=0.0,
    )
    m.project_cash_flows()
    wacc = m.wacc_components["wacc"]
    tv = m.calculate_terminal_value(method="growth", terminal_fcf=100.0)
    assert math.isclose(tv, 100.0 / (wacc - 0.04), rel_tol=1e-9)


def test_default_example_is_sane():
    """Sanity: a standard profitable projection yields a positive, finite equity value."""
    eq = _equity_value(0.10)
    assert math.isfinite(eq) and eq > 0


def _run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run() else 0)
