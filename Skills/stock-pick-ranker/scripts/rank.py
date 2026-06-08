#!/usr/bin/env python3
"""
Deterministic ranking math: principles score (weighted 7 factors) + hotness +
reliability-weighted reverse-DCF blend into Margin-of-Safety + Master score + re-rank.

Run over the WHOLE universe (existing + new) every time — the ranking is relative.

Input  : a JSON file {"stocks":[ {stock record} ]} where each record has
         f1..f7, f2 (== the original multiples MoS, same as the factor f2),
         valuation_score_1to5, valuation_confidence (High|Med|Low), valuation_method
         (reverseDCF|justifiedPB|EV/Sales|yield), artifact (bool),
         theme, authors_recommending (int), corpus_mentions (int),
         plus passthrough fields (company, by, sector, verdict, pe, ...).
Output : same list with principles_score, hotness, f2_blended, master, rank added,
         sorted by master desc. Writes <input>.ranked.json (or --out).

Usage: /usr/bin/python3 rank.py universe.json [--out final_v2.json]
"""
import json
import sys

# Factor weights (sum = 1.0). Tilted to quality + downside protection for long-term focus.
W = {"f1": 0.20, "f3": 0.20, "f2": 0.15, "f4": 0.15, "f6": 0.10, "f5": 0.10, "f7": 0.10}
MASTER_PRINCIPLES_W = 0.85          # Master = 85% principles + 15% hotness
MASTER_HOTNESS_W = 0.15


def blend_weight(method, confidence, artifact):
    """How much to trust the reverse-DCF valuation_score vs the multiples F2."""
    conf = (confidence or "").lower()
    if method in ("justifiedPB", "yield"):
        return 0.45
    if method == "EV/Sales":
        return 0.25
    if artifact or conf.startswith("low"):
        return 0.20
    if conf.startswith("high"):
        return 0.55
    return 0.40  # Med / unspecified reverseDCF


def hotness(theme_picks, authors_recommending, corpus_mentions, max_theme_picks):
    theme_heat = (theme_picks / max_theme_picks * 100) if max_theme_picks else 0
    cross_author = 100 if (authors_recommending or 1) >= 2 else 35
    mentions = min(corpus_mentions or 0, 5) / 5 * 100
    return 0.5 * theme_heat + 0.3 * cross_author + 0.2 * mentions


def rank(stocks):
    # theme concentration (picks per theme) across the universe
    theme_picks = {}
    for s in stocks:
        t = s.get("theme") or "Other"
        theme_picks[t] = theme_picks.get(t, 0) + 1
    max_tp = max(theme_picks.values()) if theme_picks else 1

    for s in stocks:
        f2_old = float(s.get("f2", 3))
        v2 = float(s.get("valuation_score_1to5", f2_old) or f2_old)
        w = blend_weight(s.get("valuation_method"), s.get("valuation_confidence"),
                         bool(s.get("artifact")))
        f2_blended = w * v2 + (1 - w) * f2_old
        s["f2_blended"] = round(f2_blended, 2)
        s["blend_weight"] = w

        factors = {k: float(s.get(k, 3)) for k in W}
        factors["f2"] = f2_blended  # replace MoS with the blended value
        s["principles_score"] = round(20 * sum(W[k] * factors[k] for k in W), 1)

        s["hotness"] = round(hotness(theme_picks[s.get("theme") or "Other"],
                                     s.get("authors_recommending", 1),
                                     s.get("corpus_mentions", 0), max_tp), 1)
        s["master"] = round(MASTER_PRINCIPLES_W * s["principles_score"]
                            + MASTER_HOTNESS_W * s["hotness"], 1)

    stocks.sort(key=lambda x: -x["master"])
    for i, s in enumerate(stocks, 1):
        s["rank"] = i
    return stocks, theme_picks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else path + ".ranked.json"
    data = json.load(open(path))
    stocks = data["stocks"] if isinstance(data, dict) else data
    ranked, theme_picks = rank(stocks)
    json.dump({"stocks": ranked, "theme_picks": theme_picks},
              open(out, "w"), indent=2, ensure_ascii=False)
    print(f"ranked {len(ranked)} stocks -> {out}")
    print(f"{'rank':>4}  {'master':>6}  company")
    for s in ranked[:15]:
        print(f"{s['rank']:>4}  {s['master']:>6}  {s.get('company','')}")
