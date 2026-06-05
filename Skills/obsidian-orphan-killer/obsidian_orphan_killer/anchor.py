"""Anchor mode — attach true-orphan leaves to their single best matching hub.

After the deterministic resolver runs, a residual of leaves still carries NO
outbound wikilink and no inbound link from anywhere in the vault. For each
true orphan with enough body to embed, we:

  1. embed (title + body slice) using a local fastembed model
     (default: ``BAAI/bge-small-en-v1.5`` at ``max_length=256``);
  2. find the single nearest existing hub by cosine;
  3. attach that ONE ``[[hub]]`` to ``entities:`` IFF cosine ≥ floor.

Hard safety guards:

  - **Concepts-only by default.** A generic how-to ("spreadsheet formulas")
    must NOT anchor to a brand entity hub ("microsoft-excel"). Pass
    ``--include-entities`` to opt in.
  - **Per-hub absorption cap.** No single hub can absorb more than
    ``max_per_hub`` orphans per run (anti-star).
  - **Cosine floor.** Below ``floor`` (default 0.74) we leave the orphan
    unlinked rather than force a noisy link.
  - **Dangling-link guard.** Only links to hubs that exist on disk.
  - **Frontmatter-only writes.** Body is untouched.
  - **Idempotency stamp** (``raw_meta.anchored_at`` + ``anchor_hash``).
  - **Optional dry-run audit dump** — every candidate's decision row to TSV.
"""
from __future__ import annotations

import logging
import math
import re
from collections import Counter
from pathlib import Path

from obsidian_orphan_killer.alias_table import AliasTable
from obsidian_orphan_killer.alias_table import build as build_alias_table
from obsidian_orphan_killer.fm import (
    resolve_hash,
    serialize,
    should_skip,
    split_frontmatter,
    stamp_meta,
    write_atomic,
)
from obsidian_orphan_killer.resolve import DEFAULT_SCOPE_DIRS, discover_notes

log = logging.getLogger(__name__)

# Mirrors the orphan definition used by most Obsidian linters: any wikilink
# in any of these frontmatter fields OR in the body counts as outbound.
_FM_WIKILINK_FIELDS = ("entities", "topics", "relationships", "related")
_WIKILINK_RE = re.compile(r"\[\[([^\[\]|#]+?)(?:\|[^\]]+)?\]\]")


def _wikilinks_in_value(val) -> set[str]:
    out: set[str] = set()
    if isinstance(val, str):
        for m in _WIKILINK_RE.finditer(val):
            out.add(m.group(1).strip())
    elif isinstance(val, list):
        for item in val:
            out |= _wikilinks_in_value(item)
    return out


def all_wikilinks(fm: dict, body: str) -> set[str]:
    """Every wikilink target in the frontmatter fields + body."""
    targets: set[str] = set()
    if fm:
        for fld in _FM_WIKILINK_FIELDS:
            if fm.get(fld) is not None:
                targets |= _wikilinks_in_value(fm[fld])
    for m in _WIKILINK_RE.finditer(body):
        targets.add(m.group(1).strip())
    return targets


def _body_slice(body: str, max_chars: int = 600) -> str:
    """Title-free body slice for embedding (drop a leading H1, cap length)."""
    b = body.lstrip()
    if b.startswith("# "):
        parts = b.split("\n", 2)
        b = parts[2] if len(parts) >= 3 else ""
    return b.strip()[:max_chars]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _load_embedder(max_length: int = 256):
    """Lazy import to keep ``fastembed`` an optional dep at import time."""
    try:
        from fastembed import TextEmbedding  # type: ignore
    except ImportError as exc:  # pragma: no cover - tested separately
        raise RuntimeError(
            "anchor mode requires fastembed: pip install fastembed lancedb"
        ) from exc
    return TextEmbedding(model_name="BAAI/bge-small-en-v1.5", max_length=max_length)


def _iter_all_vault_notes(vault_root: Path):
    """Every ``.md`` in the vault except quarantine + internal cache dirs."""
    for p in sorted(vault_root.rglob("*.md")):
        parts = p.relative_to(vault_root).parts
        if "_quarantine" in parts or ".lancedb" in parts:
            continue
        yield p


def _note_link_keys(path: Path, fm: dict) -> set[str]:
    """The lowercased keys other notes would use to ``[[link]]`` to this note."""
    keys: set[str] = {path.stem.lower()}
    title = fm.get("title")
    if isinstance(title, str) and title.strip():
        keys.add(title.strip().lower())
    aliases = fm.get("aliases") or []
    if isinstance(aliases, list):
        for a in aliases:
            if isinstance(a, str) and a.strip():
                keys.add(a.strip().lower())
    elif isinstance(aliases, str) and aliases.strip():
        keys.add(aliases.strip().lower())
    return keys


def anchor_orphans(
    vault_root: Path,
    note_paths: list[Path] | None = None,
    *,
    table: AliasTable | None = None,
    hub_dirs: tuple[str, ...] | None = None,
    scope_dirs: tuple[str, ...] = DEFAULT_SCOPE_DIRS,
    dry_run: bool = False,
    force: bool = False,
    floor: float = 0.74,
    min_body_chars: int = 200,
    max_per_hub: int = 50,
    include_entities: bool = False,
    embedder=None,
    embedder_max_length: int = 256,
    limit: int | None = None,
    sample: int = 15,
    dump_tsv: Path | None = None,
) -> dict:
    """Attach one best-matching existing hub to each true-orphan leaf.

    Orphan definition: a leaf with NO outbound wikilink in
    entities/topics/relationships/related/body AND no inbound link from any
    other note anywhere in the vault. Inbound matches by stem OR title OR alias
    (the way Obsidian resolves ``[[X]]``).

    Args:
        floor: Cosine threshold. Defaults to 0.74 — strong topical matches
            anchor, generic how-tos stay unlinked.
        min_body_chars: Skip leaves whose title + body slice is shorter than
            this — too thin to embed reliably.
        max_per_hub: Anti-star cap. A single hub can absorb at most this many
            orphans per run.
        include_entities: Default False = concepts-only target set. True opens
            the target set to entities/ hubs too (use with care — that's the
            class that causes the brand-leak failure mode).
        dump_tsv: If set, write the full per-candidate decision row table to
            this path (every orphan, every nearest-hub, every cosine, every
            decision). Recommended on dry-run so the full list can be reviewed
            before any live write.

    Returns:
        Stats dict including ``anchored``, ``below_floor``, ``hub_capped``,
        ``hub_distribution`` (top 15 hubs by absorption), and the optional
        ``dump_tsv`` path.
    """
    if table is None:
        if hub_dirs is None:
            table = build_alias_table(vault_root)
        else:
            table = build_alias_table(vault_root, hub_dirs=hub_dirs)

    if include_entities:
        hub_slugs = list(table.hub_names.keys())
    else:
        hub_slugs = [s for s in table.hub_names if table.hub_kinds.get(s) == "concept"]
    hub_names = [table.hub_names[s] for s in hub_slugs]
    hub_slug_set = set(hub_slugs)

    notes = discover_notes(vault_root, note_paths, scope_dirs)

    # ---- Pass 1a: whole-vault inbound target set ----
    inbound_targets: set[str] = set()
    for p in _iter_all_vault_notes(vault_root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, body = split_frontmatter(text)
        for t in all_wikilinks(fm or {}, body):
            inbound_targets.add(t.lower())

    # ---- Pass 1b: parse candidate leaves; record link keys ----
    parsed: dict[Path, tuple[dict, str, set[str]]] = {}
    leaf_keys: dict[Path, set[str]] = {}
    for p in notes:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("cannot read %s: %s", p, exc)
            continue
        fm, body = split_frontmatter(text)
        if fm is None:
            continue
        wl = all_wikilinks(fm, body)
        parsed[p] = (fm, body, wl)
        leaf_keys[p] = _note_link_keys(p, fm)

    def _is_orphan(p: Path, wl: set[str]) -> bool:
        if wl:
            return False
        if leaf_keys.get(p, set()) & inbound_targets:
            return False
        return True

    # ---- Pass 2: select embeddable orphans ----
    candidates: list[tuple[Path, dict, str]] = []
    n_thin = 0
    for p, (fm, body, wl) in parsed.items():
        if not _is_orphan(p, wl):
            continue
        bslice = _body_slice(body)
        title = str(fm.get("title") or "")
        if len((title + bslice).strip()) < min_body_chars:
            n_thin += 1
            continue
        candidates.append((p, fm, body))

    if limit is not None:
        candidates = candidates[:limit]

    stats: dict = {
        "orphan_candidates": len(candidates),
        "thin_skipped": n_thin,
        "anchored": 0,
        "below_floor": 0,
        "skipped_idempotent": 0,
        "hub_capped": 0,
        "written": 0,
        "errors": 0,
        "floor": floor,
        "max_per_hub": max_per_hub,
        "target_hub_kind": "concepts+entities" if include_entities else "concepts-only",
    }
    sample_rows: list[dict] = []
    floor_misses: list[tuple[str, str, float]] = []

    if not candidates or not hub_slugs:
        stats["sample"] = sample_rows
        stats["floor_miss_sample"] = floor_misses
        return stats

    # ---- Pass 3: embed hubs + orphan candidates ----
    if embedder is None:
        embedder = _load_embedder(max_length=embedder_max_length)
    hub_vecs = [v.tolist() for v in embedder.embed([f"topic: {n}" for n in hub_names])]
    surfaces = []
    for _p, fm, body in candidates:
        title = str(fm.get("title") or "")
        surfaces.append(f"topic: {title}. {_body_slice(body)}")
    cand_vecs = [v.tolist() for v in embedder.embed(surfaces)]

    dump_rows: list[tuple[str, str, float, str]] = []
    per_hub_count: Counter[str] = Counter()

    for (p, fm, body), cvec in zip(candidates, cand_vecs, strict=True):
        rel = p.relative_to(vault_root).as_posix()
        best_slug, best_name, best_cos = None, None, 0.0
        for i, hvec in enumerate(hub_vecs):
            c = _cosine(cvec, hvec)
            if c > best_cos:
                best_cos, best_slug, best_name = c, hub_slugs[i], hub_names[i]

        if best_slug is None or best_cos < floor:
            stats["below_floor"] += 1
            dump_rows.append((rel, best_slug or "-", round(best_cos, 4), "below_floor"))
            if len(floor_misses) < sample:
                floor_misses.append((rel, best_name or "-", round(best_cos, 3)))
            continue
        if best_slug not in hub_slug_set:
            dump_rows.append((rel, best_slug, round(best_cos, 4), "not_a_hub"))
            continue
        if max_per_hub and per_hub_count[best_slug] >= max_per_hub:
            stats["hub_capped"] += 1
            dump_rows.append((rel, best_slug, round(best_cos, 4), "hub_capped"))
            continue

        ch = resolve_hash(fm, body)
        if not force and should_skip(fm, "anchored_at", "anchor_hash", ch):
            stats["skipped_idempotent"] += 1
            dump_rows.append((rel, best_slug, round(best_cos, 4), "skipped_idempotent"))
            continue

        per_hub_count[best_slug] += 1
        stats["anchored"] += 1
        dump_rows.append((rel, best_slug, round(best_cos, 4), "anchored"))
        if len(sample_rows) < sample:
            sample_rows.append({
                "path": rel, "hub": best_slug, "cosine": round(best_cos, 3),
                "title": str(fm.get("title") or "")[:60],
            })
        if dry_run:
            continue

        new_fm = dict(fm)
        ents = list(new_fm.get("entities") or []) if isinstance(new_fm.get("entities"), list) else []
        link = f"[[{best_slug}]]"
        if link not in ents:
            ents.append(link)
        new_fm["entities"] = ents
        new_hash = resolve_hash(new_fm, body)
        new_fm = stamp_meta(
            new_fm, "anchored_at", "anchor_hash", new_hash,
            extras={"anchor_hub": best_slug, "anchor_cosine": round(best_cos, 4)},
        )
        try:
            write_atomic(p, serialize(new_fm, body))
            stats["written"] += 1
        except OSError as exc:
            log.warning("cannot write %s: %s", p, exc)
            stats["errors"] += 1

    stats["sample"] = sample_rows
    stats["floor_miss_sample"] = floor_misses
    stats["hub_distribution"] = per_hub_count.most_common(15)

    if dump_tsv is not None:
        try:
            dump_tsv.parent.mkdir(parents=True, exist_ok=True)
            lines = ["cosine\tdecision\thub\tnote"]
            for rel, hub, cos, decision in sorted(dump_rows, key=lambda r: -r[2]):
                lines.append(f"{cos:.4f}\t{decision}\t{hub}\t{rel}")
            dump_tsv.write_text("\n".join(lines) + "\n", encoding="utf-8")
            stats["dump_tsv"] = str(dump_tsv)
            stats["dump_rows"] = len(dump_rows)
        except OSError as exc:
            log.warning("could not write anchor dump TSV %s: %s", dump_tsv, exc)
    return stats
