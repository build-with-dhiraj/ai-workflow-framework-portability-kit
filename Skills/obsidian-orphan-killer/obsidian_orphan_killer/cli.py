"""obsidian-orphan-killer CLI.

Three subcommands:

  * ``obsidian-orphan-killer resolve --vault PATH``
      Deterministic alias-table resolution. $0, no network.
  * ``obsidian-orphan-killer anchor --vault PATH``
      Embedding anchor for true-orphan leaves. Local fastembed, $0.
  * ``obsidian-orphan-killer mint --vault PATH --experimental``
      Cluster + mint new concept hubs. Writes NEW notes. Requires
      ``--experimental`` to enable.

Every subcommand supports ``--dry-run`` (writes nothing, reports the plan).
ALWAYS dry-run first.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from obsidian_orphan_killer import __version__
from obsidian_orphan_killer.anchor import anchor_orphans
from obsidian_orphan_killer.mint import cluster_mint
from obsidian_orphan_killer.resolve import resolve_notes

log = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="obsidian-orphan-killer",
        description=(
            "Auto-link the orphan notes in any [[wikilink]] markdown vault. "
            "Three modes: resolve (deterministic), anchor (local embeddings), "
            "mint (experimental, clusters + new hubs)."
        ),
    )
    p.add_argument(
        "--version", action="version", version=f"obsidian-orphan-killer {__version__}",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="MODE")

    # ---- resolve --------------------------------------------------------
    r = sub.add_parser(
        "resolve",
        help="Deterministic alias-table resolution. Converts plain-string "
             "entities/topics to [[wikilinks]] when a matching hub exists on disk.",
    )
    r.add_argument("--vault", type=Path, required=True, help="Vault root.")
    r.add_argument(
        "--hub-dirs", default="entities,concepts",
        help="Comma-separated hub directory names (default: entities,concepts).",
    )
    r.add_argument(
        "--scope-dirs", default="sources,inbox,context",
        help="Comma-separated scope directory names. Notes inside these are "
             "the ones whose entities/topics get resolved. Pass an empty string "
             "to scope the whole vault except hubs. (default: sources,inbox,context)",
    )
    r.add_argument("--dry-run", action="store_true",
                   help="Report-only. Writes nothing. SAFE to run on a real vault.")
    r.add_argument("--force", action="store_true",
                   help="Re-resolve notes already stamped resolved_at.")
    r.add_argument("--limit", type=int, default=None,
                   help="Cap number of notes processed (smoke-test).")
    r.add_argument("--json-out", type=Path, default=None,
                   help="Write the stats JSON to this path.")
    r.add_argument("--log-level", default="INFO")

    # ---- anchor ---------------------------------------------------------
    a = sub.add_parser(
        "anchor",
        help="Embedding anchor mode. For true-orphan leaves still unlinked "
             "after resolve, attach the single nearest existing hub by cosine. "
             "Local fastembed, $0 after one-time download. Concepts-only by default.",
    )
    a.add_argument("--vault", type=Path, required=True)
    a.add_argument("--hub-dirs", default="entities,concepts")
    a.add_argument("--scope-dirs", default="sources,inbox,context")
    a.add_argument("--dry-run", action="store_true",
                   help="Report-only + write the full per-candidate audit TSV.")
    a.add_argument("--force", action="store_true")
    a.add_argument("--floor", type=float, default=0.74,
                   help="Cosine floor (default 0.74). Below this, leave orphan unlinked.")
    a.add_argument("--max-per-hub", type=int, default=50,
                   help="Anti-star cap: max orphans any one hub can absorb per run.")
    a.add_argument("--min-body-chars", type=int, default=200,
                   help="Skip orphans whose title+body slice is shorter.")
    a.add_argument("--include-entities", action="store_true",
                   help="Allow anchoring to entities/ hubs too (default: concepts-only "
                        "— safer; avoids the brand-leak failure mode where a generic "
                        "how-to anchors to a product hub).")
    a.add_argument("--embedder-max-length", type=int, default=256,
                   help="Token window for the fastembed model (default 256).")
    a.add_argument("--limit", type=int, default=None)
    a.add_argument("--dump-tsv", type=Path, default=None,
                   help="Write the per-candidate decision TSV here. Defaults to "
                        "<vault>/orphan_killer_audit/anchor.tsv on dry-run.")
    a.add_argument("--json-out", type=Path, default=None)
    a.add_argument("--log-level", default="INFO")

    # ---- mint (experimental) -------------------------------------------
    m = sub.add_parser(
        "mint",
        help="EXPERIMENTAL: cluster orphans + mint new concept hubs for coherent "
             "clusters with >= min-cluster members. Writes NEW notes. Always "
             "dry-run first. Requires --experimental.",
    )
    m.add_argument("--vault", type=Path, required=True)
    m.add_argument("--hub-dirs", default="entities,concepts")
    m.add_argument("--scope-dirs", default="sources,inbox,context")
    m.add_argument("--concepts-dir-name", default="concepts",
                   help="Where to write new concept hubs (default: concepts).")
    m.add_argument("--experimental", action="store_true",
                   help="REQUIRED to enable mint mode (writes new notes).")
    m.add_argument("--dry-run", action="store_true")
    m.add_argument("--force", action="store_true")
    m.add_argument("--min-cluster", type=int, default=5,
                   help="Minimum members for a cluster to qualify (default 5).")
    m.add_argument("--max-hubs", type=int, default=80,
                   help="Cap on NEW hubs minted per run (default 80).")
    m.add_argument("--cluster-sim", type=float, default=0.83,
                   help="Cosine edge threshold for the similarity-graph clustering.")
    m.add_argument("--anchor-floor", type=float, default=0.74,
                   help="Cosine floor a member must clear to the hub's surface.")
    m.add_argument("--max-per-hub", type=int, default=50)
    m.add_argument("--max-spread", type=float, default=0.18,
                   help="Reject clusters with intra-cluster cosine spread > this.")
    m.add_argument("--dup-hub-threshold", type=float, default=0.88)
    m.add_argument("--min-body-chars", type=int, default=200)
    m.add_argument("--name-sample", type=int, default=None,
                   help="Cap LLM naming calls to the N largest clusters.")
    m.add_argument("--embedder-max-length", type=int, default=256)
    m.add_argument("--limit", type=int, default=None)
    m.add_argument("--dump-tsv", type=Path, default=None)
    m.add_argument("--json-out", type=Path, default=None)
    m.add_argument("--log-level", default="INFO")

    return p


def _split_csv(s: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in s.split(",") if x.strip())


def _default_dump_path(vault: Path, mode: str) -> Path:
    return vault / "orphan_killer_audit" / f"{mode}.tsv"


def _cmd_resolve(args: argparse.Namespace) -> int:
    if not args.vault.exists():
        log.error("Vault not found: %s", args.vault)
        return 2
    stats = resolve_notes(
        args.vault,
        hub_dirs=_split_csv(args.hub_dirs),
        scope_dirs=_split_csv(args.scope_dirs),
        dry_run=args.dry_run,
        force=args.force,
        limit=args.limit,
    )
    print("\n=== obsidian-orphan-killer resolve ===")
    print(f"vault:                  {args.vault}")
    print(f"alias-table hubs:       {stats['hubs_known']}")
    print(f"alias-table entries:    {stats['alias_table_size']}  "
          f"(collisions: {stats['collisions']})")
    print(f"scanned:                {stats['scanned']}")
    print(f"skipped (unchanged):    {stats['skipped']}")
    print(f"notes with resolution:  {stats['notes_with_resolution']}")
    print(f"resolved occurrences:   {stats['resolved_occurrences']}")
    print(f"residual occurrences:   {stats['residual_occurrences']}")
    print(f"distinct residual keys: {stats.get('distinct_residual_keys', 0)}")
    if not args.dry_run:
        print(f"written:                {stats['written']}")
    print("top residual surface forms (normalized key, count):")
    for k, n in stats.get("top_residuals", [])[:15]:
        print(f"   {k:35} {n}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(stats, indent=2, default=str) + "\n",
                                 encoding="utf-8")
    return 0


def _cmd_anchor(args: argparse.Namespace) -> int:
    if not args.vault.exists():
        log.error("Vault not found: %s", args.vault)
        return 2
    dump_tsv = args.dump_tsv
    if dump_tsv is None and args.dry_run:
        dump_tsv = _default_dump_path(args.vault, "anchor")
    stats = anchor_orphans(
        args.vault,
        hub_dirs=_split_csv(args.hub_dirs),
        scope_dirs=_split_csv(args.scope_dirs),
        dry_run=args.dry_run,
        force=args.force,
        floor=args.floor,
        min_body_chars=args.min_body_chars,
        max_per_hub=args.max_per_hub,
        include_entities=args.include_entities,
        embedder_max_length=args.embedder_max_length,
        limit=args.limit,
        dump_tsv=dump_tsv,
    )
    print("\n=== obsidian-orphan-killer anchor ===")
    print(f"vault:                  {args.vault}")
    print(f"target hubs:            {stats['target_hub_kind']}")
    print(f"cosine floor:           {args.floor}")
    print(f"orphan candidates:      {stats['orphan_candidates']}")
    print(f"thin skipped:           {stats['thin_skipped']}")
    print(f"anchored (>=floor):     {stats['anchored']}")
    print(f"below floor (left):     {stats['below_floor']}")
    print(f"skipped (idempotent):   {stats['skipped_idempotent']}")
    print(f"hub-capped (anti-star): {stats['hub_capped']}")
    if not args.dry_run:
        print(f"written:                {stats['written']}")
    print(f"errors:                 {stats['errors']}")
    if stats.get("dump_tsv"):
        print(f"audit dump:             {stats['dump_tsv']} ({stats.get('dump_rows', 0)} rows)")
    for row in stats.get("sample", []):
        print(f"   {row['cosine']:.3f}  {row['path']}  -> [[{row['hub']}]]")
    if stats.get("hub_distribution"):
        print("hub absorption (anti-star check):")
        for slug, n in stats["hub_distribution"]:
            print(f"   {n:4}  [[{slug}]]")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(stats, indent=2, default=str) + "\n",
                                 encoding="utf-8")
    return 0


def _cmd_mint(args: argparse.Namespace) -> int:
    if not args.vault.exists():
        log.error("Vault not found: %s", args.vault)
        return 2
    if not args.experimental:
        log.error(
            "mint mode requires --experimental (writes NEW notes to your vault). "
            "Always dry-run first."
        )
        return 2
    dump_tsv = args.dump_tsv
    if dump_tsv is None and args.dry_run:
        dump_tsv = _default_dump_path(args.vault, "mint")
    stats = cluster_mint(
        args.vault,
        hub_dirs=_split_csv(args.hub_dirs),
        scope_dirs=_split_csv(args.scope_dirs),
        concepts_dir_name=args.concepts_dir_name,
        dry_run=args.dry_run,
        force=args.force,
        min_cluster=args.min_cluster,
        max_hubs=args.max_hubs,
        cluster_sim=args.cluster_sim,
        anchor_floor=args.anchor_floor,
        max_per_hub=args.max_per_hub,
        max_spread=args.max_spread,
        dup_hub_threshold=args.dup_hub_threshold,
        min_body_chars=args.min_body_chars,
        name_sample=args.name_sample,
        embedder_max_length=args.embedder_max_length,
        limit=args.limit,
        dump_tsv=dump_tsv,
    )
    print("\n=== obsidian-orphan-killer mint (EXPERIMENTAL) ===")
    print(f"vault:                     {args.vault}")
    print(f"orphan candidates:         {stats['orphan_candidates']}")
    print(f"thin skipped:              {stats['thin_skipped']}")
    print(f"clusters total:            {stats['clusters_total']}")
    print(f"clusters qualifying (>= {args.min_cluster}):  {stats['clusters_qualifying']}")
    print(f"LLM naming calls:          {stats.get('gpt_naming_calls', 0)}")
    print(f"clusters coherent (minted):{stats['clusters_coherent']}")
    print(f"clusters rejected (LLM no):{stats['clusters_rejected_incoherent']}")
    print(f"clusters rejected (guard): {stats['clusters_rejected_guard']}")
    print(f"clusters rejected (spread):{stats['clusters_rejected_spread']}")
    print(f"clusters redirected (dup): {stats['clusters_rejected_dup_hub']}")
    print(f"hubs minted:               {stats['hubs_minted']}")
    print(f"hubs over cap:             {stats['hubs_capped_out']}")
    print(f"orphans anchored:          {stats['orphans_anchored']}")
    print(f"orphans below floor:       {stats['orphans_below_anchor_floor']}")
    print(f"orphans haystack (left):   {stats['orphans_haystack']}")
    if stats.get("dup_hub_redirects"):
        print("\nS1 dup-hub redirects:")
        for r in stats["dup_hub_redirects"]:
            print(f"   {r['proposed']!r} -> [[{r['existing']}]] @ {r['cosine']:.3f}"
                  f" ({r['members']} members)")
    if not args.dry_run:
        print(f"written:                   {stats['written']}")
    if stats.get("minted_clusters"):
        print("\nminted clusters:")
        for mc in stats["minted_clusters"]:
            sp = mc.get("spread")
            sp_s = f" spread={sp:.3f}" if sp is not None else ""
            print(f"   [[{mc['slug']}]] ({mc['members']} members, "
                  f"{mc.get('anchored', 0)} anchored{sp_s}) {mc['topic']!r}")
    if stats.get("dump_tsv"):
        print(f"\naudit dump: {stats['dump_tsv']} ({stats.get('dump_rows', 0)} rows)")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(stats, indent=2, default=str) + "\n",
                                 encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(name)s: %(message)s",
    )
    if args.cmd == "resolve":
        return _cmd_resolve(args)
    if args.cmd == "anchor":
        return _cmd_anchor(args)
    if args.cmd == "mint":
        return _cmd_mint(args)
    parser.error(f"unknown mode: {args.cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
