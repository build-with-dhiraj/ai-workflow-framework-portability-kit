#!/usr/bin/env python3
"""Recommend loop-engineering repos from scorecard for a task."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_SCORECARD = SKILL_ROOT / "data" / "repo-scorecard.json"
KIT_SCORECARD = Path(__file__).resolve().parents[4] / "research/loop-engineering-agent-hub-2026/synthesis/repo-scorecard.json"

TASK_RULES: list[tuple[str, list[str]]] = [
    ("loop init", ["loop-engineering", "loop-init", "cc-loop"]),
    ("audit", ["loop-audit", "loop-engineering"]),
    ("registry", ["pi-factory", "agent-hub", "pgmnemo", "blackboard"]),
    ("ralph", ["ralph", "ouroboros", "briefloop"]),
    ("self-improving", ["skill-opt", "self-improv", "agenticmind", "nabu"]),
    ("harness", ["caveman", "codegraph", "agent-starter"]),
    ("skills", ["ai-agent-skills", "agent-starter", "skill-opt"]),
]


def load_scorecard() -> list[dict]:
    path = BUNDLED_SCORECARD if BUNDLED_SCORECARD.exists() else KIT_SCORECARD
    if not path.exists():
        print(f"Scorecard not found: {path}", file=sys.stderr)
        print("Run: python3 research/loop-engineering-agent-hub-2026/scripts/synthesize_doctrine_v2.py", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text(encoding="utf-8"))
    repos = data.get("repos", [])
    for r in repos:
        if "total_score" not in r:
            r["total_score"] = r.get("scores", {}).get("total", 0)
        if "tier" not in r:
            r["tier"] = "installable" if r.get("scores", {}).get("direct_install", 0) >= 4 else "reference_only"
    return repos


def match_repos(repos: list[dict], task: str, limit: int = 5) -> list[dict]:
    task_l = task.lower()
    keywords: list[str] = []
    for key, kws in TASK_RULES:
        if key in task_l:
            keywords.extend(kws)
    if not keywords:
        keywords = task_l.split()

    scored: list[tuple[float, dict]] = []
    for r in repos:
        blob = f"{r['slug']} {(r.get('description') or '')}".lower()
        hits = sum(1 for kw in keywords if kw in blob)
        if hits:
            scored.append((hits * 10 + r.get("total_score", 0), r))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return repos[:limit]
    return [r for _, r in scored[:limit]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pick loop-engineering repos for a task")
    parser.add_argument("--task", default="loop init", help="Task description")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    repos = load_scorecard()
    picks = match_repos(repos, args.task, args.limit)

    print(f"# Repo picks for: {args.task}\n")
    for i, r in enumerate(picks, 1):
        print(f"{i}. {r['slug']} (code score {r['total_score']}, tier {r.get('tier', '?')})")
        if r.get("files_read"):
            print(f"   files_read: {r['files_read']}, lines: {r.get('total_lines', '?')}")
        if r.get("audit_path"):
            print(f"   audit: {r['audit_path']}")
        print()


if __name__ == "__main__":
    main()
