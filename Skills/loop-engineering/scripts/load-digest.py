#!/usr/bin/env python3
"""Load full source digest or repo code audit by ID or slug."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
KIT_ROOT = SKILL_ROOT.parents[2]
RESEARCH = KIT_ROOT / "research" / "loop-engineering-agent-hub-2026"
INGEST_SRC = RESEARCH / "ingest" / "sources"
INGEST_GH = RESEARCH / "ingest" / "github-code"
BUNDLED_AUDITS = SKILL_ROOT / "data" / "repo-audits"


def load_source(source_id: str, lines: bool = False) -> None:
    dest = INGEST_SRC / source_id
    digest = dest / "digest.md"
    if not digest.exists():
        print(f"Source digest not found: {source_id}", file=sys.stderr)
        sys.exit(1)
    print(digest.read_text(encoding="utf-8"))
    if lines:
        lp = dest / "lines.jsonl"
        if lp.exists():
            print("\n--- lines.jsonl (first 50) ---")
            for i, line in enumerate(lp.read_text(encoding="utf-8").splitlines()):
                if i >= 50:
                    print("... (truncated)")
                    break
                print(line)


def load_repo(slug: str, lines: bool = False) -> None:
    dir_name = slug.replace("/", "__")
    audit = INGEST_GH / dir_name / "code-audit.md"
    if not audit.exists():
        bundled = BUNDLED_AUDITS / f"{dir_name}.md"
        if bundled.exists():
            audit = bundled
        else:
            print(f"Repo audit not found: {slug}", file=sys.stderr)
            sys.exit(1)
    print(audit.read_text(encoding="utf-8"))
    if lines:
        idx = INGEST_GH / dir_name / "file-index.json"
        if idx.exists():
            data = json.loads(idx.read_text(encoding="utf-8"))
            print("\n--- file-index (top 20) ---")
            for f in data[:20]:
                print(f"  {f['path']} ({f['lines']} lines)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load corpus digest or repo code audit")
    parser.add_argument("--source", help="Source ID e.g. S02")
    parser.add_argument("--repo", help="Repo slug e.g. cobusgreyling/loop-engineering")
    parser.add_argument("--lines", action="store_true", help="Include line index preview")
    args = parser.parse_args()
    if args.source:
        load_source(args.source, args.lines)
    elif args.repo:
        load_repo(args.repo, args.lines)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
