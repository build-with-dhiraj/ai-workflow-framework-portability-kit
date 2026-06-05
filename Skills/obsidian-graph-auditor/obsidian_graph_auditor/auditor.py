"""Core auditor, read-only signal-layer health metrics for an Obsidian vault.

Deterministic. Read-only. Pure NetworkX. No LLM calls, no API keys, no plugins.

The audit builds a weighted undirected graph from three edge layers:

  1. ``[[wikilinks]]`` in note bodies and frontmatter values  (weight 1.0)
  2. Typed ``relationships:`` list in frontmatter, e.g. ``- uses [[X]]``  (weight 2.0)
  3. Vector-similarity ``related:`` list in frontmatter  (weight 0.7, decay with rank)

Then computes the structural metrics that feed the 8-dimension Grade-A rubric:

  - link density (edges / note)
  - orphan rate, near-orphan rate, connected-2plus share
  - top-hub edge-share, top-hub:next ratio
  - Louvain modularity
  - frontmatter-wikilink adoption
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import networkx as nx
import yaml
from networkx.algorithms.community import louvain_communities, modularity

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Edge weights
# ---------------------------------------------------------------------------
WEIGHT_WIKILINK = 1.0    # organic body / frontmatter [[links]]
WEIGHT_TYPED_REL = 2.0   # curated "relationships:" predicates
WEIGHT_VECTOR_REL = 0.7  # synthetic "related:" vector-similarity links

# Frontmatter keys to skip when extracting generic wikilinks (handled separately).
_FM_SKIP_KEYS = frozenset({"relationships"})

# Heuristic "signal" classes, notes that are *meant* to be hubs (entities,
# concepts, themes, MOCs / Maps of Content). Folder fallbacks when frontmatter
# `type` is absent. Configurable via Thresholds.signal_types / signal_folders.
DEFAULT_SIGNAL_TYPES = frozenset({"entity", "concept", "theme", "moc"})
DEFAULT_SIGNAL_FOLDERS = frozenset({"entities", "concepts", "themes", "mocs"})


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (fm_dict, body) or (None, text) if no valid frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    raw_fm = text[4:end]
    body = text[end + 5:]
    try:
        fm = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(fm, dict):
        return None, text
    return fm, body


# ---------------------------------------------------------------------------
# Wikilink extraction
# ---------------------------------------------------------------------------
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _slugify(name: str) -> str:
    s = name.strip().lower().replace("_", "-").replace(" ", "-").replace(".", "-")
    s = re.sub(r"[^a-z0-9\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")


def _slug_from_wikilink_inner(inner: str) -> str | None:
    """Parse the inside of ``[[...]]`` into the target slug.

    Obsidian convention: ``[[Target|Display Alias]]``, first segment before the
    pipe is the *target* note, second is the display text. Section anchors
    (``[[Note#Heading]]``) and block-refs (``[[Note^block]]``) are stripped.
    """
    inner = inner.strip()
    if "|" in inner:
        inner = inner.split("|", 1)[0]  # Obsidian: [[Target|Alias]], first is target.
    # Strip section anchors and block references.
    for sep in ("#", "^"):
        if sep in inner:
            inner = inner.split(sep, 1)[0]
    return _slugify(inner) if inner else None


def _extract_wikilinks_from_text(text: str) -> list[str]:
    """Return all ``[[...]]`` slugs found in arbitrary text."""
    slugs: list[str] = []
    for m in _WIKILINK_RE.finditer(text):
        s = _slug_from_wikilink_inner(m.group(1))
        if s:
            slugs.append(s)
    return slugs


def _extract_wikilinks_from_fm_value(val: Any) -> list[str]:
    """Recursively extract slugs from a frontmatter value (str, list, dict)."""
    slugs: list[str] = []
    if isinstance(val, str):
        slugs.extend(_extract_wikilinks_from_text(val))
    elif isinstance(val, list):
        for item in val:
            slugs.extend(_extract_wikilinks_from_fm_value(item))
    elif isinstance(val, dict):
        for v in val.values():
            slugs.extend(_extract_wikilinks_from_fm_value(v))
    return slugs


def _parse_typed_rel_target(rel_str: str) -> str | None:
    """``'uses [[target]]'`` → ``'target-slug'``; handles no-wikilink gracefully."""
    m = _WIKILINK_RE.search(rel_str)
    if m:
        return _slug_from_wikilink_inner(m.group(1))
    return None


def _has_frontmatter_wikilink(fm: dict | None) -> bool:
    """True if any frontmatter value contains a ``[[wikilink]]`` (adoption signal)."""
    if not fm:
        return False

    def _scan(v: Any) -> bool:
        if isinstance(v, str):
            return bool(_WIKILINK_RE.search(v))
        if isinstance(v, list):
            return any(_scan(x) for x in v)
        if isinstance(v, dict):
            return any(_scan(x) for x in v.values())
        return False

    return any(_scan(v) for v in fm.values())


# ---------------------------------------------------------------------------
# Vault traversal
# ---------------------------------------------------------------------------

def _iter_md_files(vault: Path):
    """Yield all ``.md`` files under ``vault/``, skipping ``.obsidian/``."""
    for p in vault.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        if ".git" in p.parts:
            continue
        if "node_modules" in p.parts:
            continue
        yield p


def _note_class(
    fm: dict | None,
    path: Path,
    vault: Path,
    signal_types: frozenset[str],
    signal_folders: frozenset[str],
) -> str:
    """Classify a note as ``'signal'`` (curated hub) or ``'source'`` (raw leaf).

    Priority: explicit ``type`` field → top-level folder fallback.
    """
    fm = fm or {}
    t = str(fm.get("type") or "").strip().lower()
    if t in signal_types:
        return "signal"
    try:
        rel_parts = path.relative_to(vault).parts
    except ValueError:
        rel_parts = path.parts
    if rel_parts and rel_parts[0].lower() in signal_folders:
        return "signal"
    return "source"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph(vault: Path) -> nx.Graph:
    """Build a weighted undirected graph from all three edge layers.

    Node IDs are note stem slugs (filename without ``.md``, lower-cased). Parallel
    edges from multiple layers are collapsed to a single edge with summed weights
    so standard graph algorithms can run directly.
    """
    edge_weights: dict[tuple[str, str], float] = defaultdict(float)

    for md_path in _iter_md_files(vault):
        src = md_path.stem.lower()
        if not src:
            continue

        try:
            text = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        fm, body = _split_frontmatter(text)
        if fm is None:
            fm = {}

        # Layer (a): frontmatter wikilinks (all keys except relationships).
        for key, val in fm.items():
            if key in _FM_SKIP_KEYS:
                continue
            for tgt in _extract_wikilinks_from_fm_value(val):
                if tgt and tgt != src:
                    pair = (min(src, tgt), max(src, tgt))
                    edge_weights[pair] += WEIGHT_WIKILINK

        # Layer (a) continued: body wikilinks.
        for tgt in _extract_wikilinks_from_text(body):
            if tgt and tgt != src:
                pair = (min(src, tgt), max(src, tgt))
                edge_weights[pair] += WEIGHT_WIKILINK

        # Layer (b): typed relationships (higher weight, curated edges).
        relationships = fm.get("relationships") or []
        if isinstance(relationships, str):
            relationships = [relationships]
        for rel in relationships:
            tgt = _parse_typed_rel_target(str(rel))
            if tgt and tgt != src:
                pair = (min(src, tgt), max(src, tgt))
                edge_weights[pair] += WEIGHT_TYPED_REL

        # Layer (c): vector related links (weight decays slightly with rank).
        related = fm.get("related") or []
        if isinstance(related, str):
            related = [related]
        for i, item in enumerate(related):
            for tgt in _extract_wikilinks_from_fm_value(item):
                if tgt and tgt != src:
                    w = WEIGHT_VECTOR_REL * max(0.1, 1.0 - 0.05 * i)
                    pair = (min(src, tgt), max(src, tgt))
                    edge_weights[pair] += w

    G = nx.Graph()
    for (u, v), w in edge_weights.items():
        G.add_edge(u, v, weight=w)

    log.info("Graph built: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return G


# ---------------------------------------------------------------------------
# Per-note scan
# ---------------------------------------------------------------------------

def _scan_vault(
    vault: Path,
    signal_types: frozenset[str],
    signal_folders: frozenset[str],
) -> dict[str, Any]:
    """Single read-only pass collecting per-note class + frontmatter signals."""
    total = 0
    class_counts: Counter = Counter()
    type_counts: Counter = Counter()
    fm_wikilink_notes = 0
    hub_alias_total = 0
    hub_alias_with = 0
    node_class: dict[str, str] = {}

    for md_path in _iter_md_files(vault):
        slug = md_path.stem.lower()
        if not slug:
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        total += 1
        fm, _body = _split_frontmatter(text)
        cls = _note_class(fm, md_path, vault, signal_types, signal_folders)
        class_counts[cls] += 1
        node_class[slug] = cls

        type_label = str((fm or {}).get("type") or (fm or {}).get("source") or "_none")
        type_counts[type_label] += 1

        if _has_frontmatter_wikilink(fm):
            fm_wikilink_notes += 1

        if (fm or {}).get("type") == "entity":
            hub_alias_total += 1
            if (fm or {}).get("aliases"):
                hub_alias_with += 1

    return {
        "total": total,
        "class_counts": dict(class_counts),
        "type_counts": dict(type_counts),
        "fm_wikilink_notes": fm_wikilink_notes,
        "hub_alias_total": hub_alias_total,
        "hub_alias_with": hub_alias_with,
        "node_class": node_class,
    }


# ---------------------------------------------------------------------------
# Graph-derived metrics
# ---------------------------------------------------------------------------

def _graph_metrics(G: nx.Graph, top: int = 10) -> dict[str, Any]:
    """Compute the structural signal-layer metrics from the built graph."""
    n = G.number_of_nodes()
    m = G.number_of_edges()

    degrees = dict(G.degree())
    deg_vals = list(degrees.values())
    orphans = sum(1 for d in deg_vals if d == 0)
    near_orphans = sum(1 for d in deg_vals if d == 1)
    connected_2plus = sum(1 for d in deg_vals if d >= 2)

    weighted_deg = dict(G.degree(weight="weight"))
    ranked = sorted(weighted_deg.items(), key=lambda kv: kv[1], reverse=True)
    total_w_deg = sum(weighted_deg.values()) or 1.0
    top_hub = ranked[0] if ranked else (None, 0.0)
    next_hub = ranked[1] if len(ranked) > 1 else (None, 0.0)
    top_hub_edge_share = top_hub[1] / total_w_deg
    top_next_ratio = (top_hub[1] / next_hub[1]) if next_hub[1] else float("inf")

    if m > 0:
        communities = louvain_communities(G, weight="weight", seed=42)
        mod = modularity(G, communities, weight="weight")
        n_communities = len(communities)
    else:
        mod = 0.0
        n_communities = 0

    if n > 0 and m > 0:
        k = min(n, 500) if n > 100 else None
        bc = nx.betweenness_centrality(G, weight=None, normalized=True, k=k, seed=42)
        top_bridges = sorted(bc.items(), key=lambda kv: kv[1], reverse=True)[:top]
    else:
        top_bridges = []

    return {
        "graph_nodes": n,
        "graph_edges": m,
        "in_graph_degree1": near_orphans,
        "in_graph_orphans": orphans,
        "in_graph_connected_2plus": connected_2plus,
        "top_hubs_weighted": [(s, round(w, 4)) for s, w in ranked[:top]],
        "top_hub": top_hub[0],
        "top_hub_edge_share_pct": round(100 * top_hub_edge_share, 2),
        "top_hub_next_ratio": round(top_next_ratio, 3) if top_next_ratio != float("inf") else None,
        "modularity": round(mod, 4),
        "n_communities": n_communities,
        "top_bridges": [(s, round(b, 4)) for s, b in top_bridges],
    }


# ---------------------------------------------------------------------------
# Audit driver (public API)
# ---------------------------------------------------------------------------

def audit(
    vault: Path,
    top: int = 10,
    *,
    signal_types: frozenset[str] | None = None,
    signal_folders: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Compute the full read-only audit. Returns a JSON-able dict.

    Args:
        vault: Path to the vault root (any markdown folder using ``[[wikilinks]]``).
        top: How many top hubs / bridges to surface.
        signal_types: Frontmatter ``type:`` values that count as curated hubs.
                      Defaults to ``{"entity", "concept", "theme", "moc"}``.
        signal_folders: Top-level folder names that count as curated hubs.
                        Defaults to ``{"entities", "concepts", "themes", "mocs"}``.

    Returns:
        A dict with all 8 rubric metrics plus diagnostic context (top hubs,
        top bridges, per-class breakdown). Safe to ``json.dumps()``.
    """
    sig_types = signal_types or DEFAULT_SIGNAL_TYPES
    sig_folders = signal_folders or DEFAULT_SIGNAL_FOLDERS

    log.info("Scanning vault %s …", vault)
    scan = _scan_vault(vault, sig_types, sig_folders)

    log.info("Building signal graph …")
    G = build_graph(vault)
    gm = _graph_metrics(G, top=top)

    total = scan["total"]
    edges = gm["graph_edges"]

    in_graph_slugs = {s for s in G.nodes() if G.degree(s) >= 1}
    in_graph_deg = dict(G.degree())
    note_slugs = set(scan["node_class"].keys())
    connected_notes = note_slugs & in_graph_slugs
    deg1_notes = {s for s in connected_notes if in_graph_deg.get(s, 0) == 1}
    deg2_notes = {s for s in connected_notes if in_graph_deg.get(s, 0) >= 2}
    orphan_notes = note_slugs - connected_notes

    def pct(a: int, b: int) -> float:
        return round(100 * a / b, 2) if b else 0.0

    node_class = scan["node_class"]
    class_breakdown: dict[str, dict[str, Any]] = {}
    for cls in ("signal", "source"):
        members = {s for s, c in node_class.items() if c == cls}
        if not members:
            continue
        conn = members & connected_notes
        orph = members - conn
        class_breakdown[cls] = {
            "count": len(members),
            "connected": len(conn),
            "orphans": len(orph),
            "orphan_pct": pct(len(orph), len(members)),
        }

    link_density = round(edges / total, 4) if total else 0.0

    return {
        "vault": str(vault),
        "total_notes": total,
        "resolved_internal_edges": edges,
        "link_density": link_density,
        "orphan_count": len(orphan_notes),
        "orphan_pct": pct(len(orphan_notes), total),
        "near_orphan_count": len(deg1_notes),
        "near_orphan_pct": pct(len(deg1_notes), total),
        "connected_2plus_count": len(deg2_notes),
        "connected_2plus_pct": pct(len(deg2_notes), total),
        "fm_wikilink_adoption_pct": pct(scan["fm_wikilink_notes"], total),
        "top_hub": gm["top_hub"],
        "top_hub_edge_share_pct": gm["top_hub_edge_share_pct"],
        "top_hub_next_ratio": gm["top_hub_next_ratio"],
        "modularity": gm["modularity"],
        "n_communities": gm["n_communities"],
        "top_bridges": gm["top_bridges"],
        "top_hubs_weighted": gm["top_hubs_weighted"],
        "hub_alias_total": scan["hub_alias_total"],
        "hub_alias_covered": scan["hub_alias_with"],
        "hub_alias_coverage_pct": pct(scan["hub_alias_with"], scan["hub_alias_total"]),
        "note_class_counts": scan["class_counts"],
        "note_class_breakdown": class_breakdown,
        "type_counts": dict(sorted(scan["type_counts"].items(), key=lambda kv: -kv[1])),
    }


# ---------------------------------------------------------------------------
# Rendering, human-readable table
# ---------------------------------------------------------------------------

def render_table(m: dict[str, Any], grades: dict[str, str] | None = None) -> str:
    """Render a clean human-readable scorecard.

    If ``grades`` is supplied (output of ``rubric.grade()``), per-dimension
    letter grades are interleaved into the table.
    """
    g = grades or {}
    lines: list[str] = []
    A = lines.append
    A("=" * 64)
    A("  OBSIDIAN VAULT AUDIT, Grade-A Rubric")
    A("=" * 64)
    A(f"  vault                       {m['vault']}")
    A("")
    A("  STRUCTURE")
    A(f"    total notes               {m['total_notes']:>10,}")
    A(f"    resolved internal edges   {m['resolved_internal_edges']:>10,}")
    A(f"    link density (edges/note) {m['link_density']:>10.4f}   {g.get('link_density', '')}")
    A("")
    A("  CONNECTIVITY")
    A(f"    orphans (deg 0)           {m['orphan_count']:>10,}  ({m['orphan_pct']:.2f}%)   {g.get('orphan_pct', '')}")
    A(f"    near-orphans (deg 1)      {m['near_orphan_count']:>10,}  ({m['near_orphan_pct']:.2f}%)   {g.get('near_orphan_pct', '')}")
    A(f"    connected (deg >=2)       {m['connected_2plus_count']:>10,}  ({m['connected_2plus_pct']:.2f}%)   {g.get('connected_2plus_pct', '')}")
    A(f"    frontmatter-wikilink      {m['fm_wikilink_adoption_pct']:>10.2f}%  adoption    {g.get('fm_wikilink_adoption_pct', '')}")
    A("")
    A("  CONCENTRATION")
    ratio = m["top_hub_next_ratio"]
    ratio_s = f"{ratio:.3f}" if ratio is not None else "inf"
    A(f"    top hub                   {str(m['top_hub'])}")
    A(f"    top-hub edge-share        {m['top_hub_edge_share_pct']:>10.2f}%   {g.get('top_hub_edge_share_pct', '')}")
    A(f"    top-hub : next ratio      {ratio_s:>10}   {g.get('top_hub_next_ratio', '')}")
    A("")
    A("  COMMUNITY")
    A(f"    Louvain modularity        {m['modularity']:>10.4f}   {g.get('modularity', '')}")
    A(f"    # communities             {m['n_communities']:>10,}")
    A("")
    if m.get("hub_alias_total", 0):
        A("  ALIAS COVERAGE (entity hubs)")
        A(f"    hubs                      {m['hub_alias_total']:>10,}")
        A(f"    with aliases              {m['hub_alias_covered']:>10,}  ({m['hub_alias_coverage_pct']:.2f}%)")
        A("")
    if m.get("note_class_breakdown"):
        A("  NOTE CLASSES")
        for cls, b in m["note_class_breakdown"].items():
            A(f"    {cls:<10}  n={b['count']:>7,}  orphans={b['orphans']:>6,}  ({b['orphan_pct']:.2f}%)")
        A("")
    A("  TOP HUBS (weighted degree)")
    for slug, w in m["top_hubs_weighted"][:10]:
        A(f"    {w:>10.2f}  {slug}")
    A("")
    A("  TOP BRIDGES (betweenness)")
    for slug, b in m["top_bridges"][:10]:
        A(f"    {b:>10.4f}  {slug}")
    if g.get("overall"):
        A("")
        A(f"  OVERALL GRADE              {g['overall']}")
    A("=" * 64)
    return "\n".join(lines)
