"""obsidian-orphan-killer.

Auto-link the orphan notes in any markdown vault that uses ``[[wikilinks]]``.
Three modes:

  * ``resolve`` — deterministic alias-table resolution of plain-string
    entities/topics to canonical hubs. $0, no network, no LLM.
  * ``anchor``  — embedding fallback: attach each true-orphan leaf to the
    single nearest existing hub by cosine similarity, with a quality floor.
    Local fastembed model, $0 after one-time download.
  * ``mint`` (EXPERIMENTAL) — cluster orphans + mint new concept hubs for
    coherent clusters with ≥ min_cluster members, then anchor those members.
    Uses an LLM to name + judge coherence (cost: bounded, configurable).

Hard safety guards (advertised loudly because trust matters in a write-tool):

  - frontmatter-only writes (body bytes never modified)
  - atomic writes (tempfile + os.rename, crash-safe)
  - body-only content hash preserved (downstream embedders never re-embed)
  - idempotency stamps (re-runs on unchanged notes are no-ops)
  - dangling-link guard (only links to hubs that exist on disk)
  - per-hub absorption cap (anti-star, prevents one hub absorbing everything)
  - concepts-only target set by default (prevents brand-leak class)
  - DO_NOT_MERGE honored (user-supplied list of pairs that must never collapse)
"""
from __future__ import annotations

from obsidian_orphan_killer.alias_table import AliasTable
from obsidian_orphan_killer.alias_table import build as build_alias_table
from obsidian_orphan_killer.anchor import anchor_orphans
from obsidian_orphan_killer.fm import (
    body_only_hash,
    resolve_hash,
    split_frontmatter,
)
from obsidian_orphan_killer.mint import cluster_mint
from obsidian_orphan_killer.resolve import resolve_notes
from obsidian_orphan_killer.slug import normalize, slugify

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "AliasTable",
    "build_alias_table",
    "anchor_orphans",
    "cluster_mint",
    "resolve_notes",
    "body_only_hash",
    "resolve_hash",
    "split_frontmatter",
    "slugify",
    "normalize",
]
