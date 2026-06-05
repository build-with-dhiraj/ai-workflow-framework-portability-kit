"""Command-line entry point.

Usage::

    obsidian-brain-eval generate --vault PATH --out gold.jsonl [--n 40]
    obsidian-brain-eval score    --gold gold.jsonl --vault PATH [--backend naive|lancedb]

Examples::

    # Generate a gold-set with GPT-4.1 (requires OPENAI_API_KEY).
    obsidian-brain-eval generate --vault ~/notes --out gold.jsonl --n 40

    # Score with the zero-infra BM25 backend.
    obsidian-brain-eval score --vault ~/notes --gold gold.jsonl --backend naive

    # Score against a LanceDB index already populated by your retrieval stack.
    obsidian-brain-eval score --vault ~/notes --gold gold.jsonl \\
        --backend lancedb --db ~/notes/.lancedb
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from obsidian_brain_eval import __version__
from obsidian_brain_eval.eval import (
    DEFAULT_K,
    DEFAULT_N,
    DEFAULT_TARGET,
    generate,
    load_gold,
    render_score,
    score,
)

log = logging.getLogger("obsidian_brain_eval")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obsidian-brain-eval",
        description=(
            "Measure Recall@k of any retrieval system over an Obsidian vault. "
            "Read-only. Pluggable retrieval backends. Default target Recall@10 >= 0.85."
        ),
    )
    p.add_argument("--version", action="version", version=f"obsidian-brain-eval {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="Generate a gold-set via GPT-4.1 (needs OPENAI_API_KEY).")
    g.add_argument("--vault", type=Path, required=True, help="Path to the vault root.")
    g.add_argument("--out", type=Path, required=True, help="JSONL gold-set output path.")
    g.add_argument("--n", type=int, default=DEFAULT_N, help=f"# questions to generate (default: {DEFAULT_N}).")
    g.add_argument("--seed", type=int, default=42)
    g.add_argument(
        "--folders", type=str, default="entities,concepts,themes,notes",
        help="Comma-separated subfolders to sample from. Pass an empty string for whole-vault.",
    )
    g.add_argument("--model", type=str, default="gpt-4.1", help="Chat-completions model name.")
    g.add_argument("--force", action="store_true", help="Overwrite the gold-set instead of appending.")

    s = sub.add_parser("score", help="Run Recall@k against a gold-set.")
    s.add_argument("--vault", type=Path, required=True, help="Path to the vault root.")
    s.add_argument("--gold", type=Path, required=True, help="JSONL gold-set path.")
    s.add_argument(
        "--backend", type=str, default="naive", choices=("naive", "lancedb"),
        help="Retrieval backend. 'naive' = BM25 (zero infra). 'lancedb' = hybrid FTS+vector.",
    )
    s.add_argument("--db", type=Path, default=None, help="LanceDB directory (lancedb backend only).")
    s.add_argument(
        "--table", type=str, default="items",
        help="LanceDB table name (lancedb backend only). Default: items.",
    )
    s.add_argument("--k", type=int, default=DEFAULT_K, help=f"Recall@k cutoff (default: {DEFAULT_K}).")
    s.add_argument("--target", type=float, default=DEFAULT_TARGET,
                   help=f"Pass/fail threshold (default: {DEFAULT_TARGET}).")
    s.add_argument("--json-out", type=Path, default=None, help="Write the result dict as JSON.")
    s.add_argument("--quiet", action="store_true", help="Suppress the human scorecard.")

    return p


def _build_backend(args: argparse.Namespace) -> Any:
    if args.backend == "naive":
        from obsidian_brain_eval.backends import NaiveBM25Backend
        return NaiveBM25Backend(args.vault)
    if args.backend == "lancedb":
        from obsidian_brain_eval.backends import LanceDBBackend
        db_path = args.db or (args.vault / ".lancedb")
        return LanceDBBackend(db_path=db_path, table_name=args.table)
    raise SystemExit(f"Unknown backend: {args.backend}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not args.vault.exists():
        print(f"Vault not found: {args.vault}", file=sys.stderr)
        return 2

    if args.command == "generate":
        folders_raw = (args.folders or "").strip()
        folders = tuple(f.strip() for f in folders_raw.split(",") if f.strip()) if folders_raw else ()
        new = generate(
            vault=args.vault,
            gold_path=args.out,
            n=args.n,
            seed=args.seed,
            force=args.force,
            folders=folders,
            model=args.model,
        )
        print(f"Wrote {len(new)} new gold records -> {args.out}")
        return 0

    if args.command == "score":
        gold = load_gold(args.gold)
        if not gold:
            print(f"Gold-set is empty: {args.gold}. Run `generate` first.", file=sys.stderr)
            return 2
        backend = _build_backend(args)
        result = score(gold, backend, k=args.k, target=args.target)
        if not args.quiet:
            print(render_score(result))
        if args.json_out:
            args.json_out.write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            log.info("JSON -> %s", args.json_out)
        return 0 if result["pass"] else 1

    parser.error("unknown command")
    return 2  # unreachable, parser.error exits


if __name__ == "__main__":
    raise SystemExit(main())
