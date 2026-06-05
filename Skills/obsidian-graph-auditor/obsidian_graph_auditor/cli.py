"""Command-line entry point.

Usage::

    obsidian-graph-audit --vault PATH [--json-out file] [--threshold-config file]
                         [--baseline file] [--top N] [--quiet] [--no-grade]

Examples::

    # Plain scorecard against current dir's `vault/` subfolder.
    obsidian-graph-audit

    # Audit a specific vault and write JSON for CI.
    obsidian-graph-audit --vault ~/notes --json-out audit.json

    # Compare against a baseline (CI gate: fail if any dimension regresses).
    obsidian-graph-audit --vault ~/notes --baseline previous-audit.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from obsidian_graph_auditor import __version__
from obsidian_graph_auditor.auditor import audit, render_table
from obsidian_graph_auditor.rubric import GRADES, grade, load_thresholds, score

log = logging.getLogger("obsidian_graph_auditor")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obsidian-graph-audit",
        description=(
            "Score an Obsidian vault on the 8-dimension Grade-A rubric. "
            "Read-only. Pure Python. No GPT, no API keys."
        ),
    )
    p.add_argument(
        "--vault", type=Path, default=None,
        help="Path to vault root (default: ./vault if it exists, else current dir).",
    )
    p.add_argument(
        "--json-out", type=Path, default=None,
        help="Write the JSON metrics dump to this path (default: stdout only).",
    )
    p.add_argument(
        "--threshold-config", type=Path, default=None,
        help="YAML file overriding any subset of the 8 default thresholds.",
    )
    p.add_argument(
        "--baseline", type=Path, default=None,
        help=(
            "Path to a prior audit JSON. Exit non-zero if any dimension regresses "
            "(useful as a CI gate)."
        ),
    )
    p.add_argument(
        "--top", type=int, default=10,
        help="N for top-hubs / top-bridges lists (default: 10).",
    )
    p.add_argument(
        "--quiet", action="store_true",
        help="Suppress the human-readable scorecard (JSON only).",
    )
    p.add_argument(
        "--no-grade", action="store_true",
        help="Suppress letter grades (raw metrics only).",
    )
    p.add_argument(
        "--version", action="version", version=f"obsidian-graph-audit {__version__}",
    )
    return p


def _default_vault() -> Path:
    here = Path.cwd()
    candidate = here / "vault"
    if candidate.is_dir():
        return candidate
    return here


def _compare_baseline(current: dict[str, Any], baseline: dict[str, Any], thresholds) -> tuple[bool, list[str]]:
    """Return ``(regressed, messages)``. ``regressed=True`` → CI should fail."""
    cur_grades = grade(current, thresholds)
    base_grades = grade(baseline, thresholds)
    order = {g: i for i, g in enumerate(GRADES)}
    messages: list[str] = []
    regressed = False
    for k, cur_g in cur_grades.items():
        if k == "overall":
            continue
        base_g = base_grades.get(k)
        if base_g is None:
            continue
        if order.get(cur_g, 99) > order.get(base_g, 99):
            messages.append(f"  REGRESSION  {k}: {base_g} → {cur_g}")
            regressed = True
        elif order.get(cur_g, 99) < order.get(base_g, 99):
            messages.append(f"  improvement {k}: {base_g} → {cur_g}")
    return regressed, messages


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    vault = args.vault or _default_vault()
    if not vault.exists():
        log.error("Vault not found: %s", vault)
        return 2
    if not vault.is_dir():
        log.error("Vault path is not a directory: %s", vault)
        return 2

    thresholds = load_thresholds(args.threshold_config)
    metrics = audit(vault, top=args.top)

    grades = None if args.no_grade else grade(metrics, thresholds)
    if grades is not None:
        metrics["overall_grade"] = grades["overall"]
        metrics["score"] = score(metrics, thresholds)
        metrics["per_dimension_grades"] = {k: v for k, v in grades.items() if k != "overall"}

    if not args.quiet:
        print(render_table(metrics, grades=grades))
        if grades is not None:
            print(f"\n  SCORE                      {metrics['score']:.2f} / 100  (Grade {grades['overall']})")

    payload = json.dumps(metrics, indent=2, ensure_ascii=False)
    if args.json_out:
        args.json_out.write_text(payload + "\n", encoding="utf-8")
        log.info("JSON metrics → %s", args.json_out)
    elif args.quiet:
        print(payload)

    if args.baseline:
        try:
            baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            log.error("Could not read baseline %s: %s", args.baseline, e)
            return 2
        regressed, messages = _compare_baseline(metrics, baseline, thresholds)
        if messages:
            print("\n  BASELINE COMPARISON")
            for line in messages:
                print(line)
        if regressed:
            log.error("Audit regression vs baseline.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
