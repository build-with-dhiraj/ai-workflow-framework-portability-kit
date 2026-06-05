"""Standing resolver — convert plain-string entities/topics → ``[[wikilinks]]``.

This is the deterministic, $0, no-network path. For each note in the resolution
scope (default: every ``.md`` in the source/inbox/context layers of a vault),
walk its frontmatter ``entities:`` and ``topics:`` lists. For each plain string,
look it up in the alias table and rewrite to ``[[slug]]`` IFF the resolved slug
has a hub note on disk. Never invents a slug. Never writes a dangling link.

Hard safety guards (non-negotiable):

  - Frontmatter-only writes; body bytes are NEVER modified.
  - Atomic write via tempfile + os.rename.
  - Idempotency stamp (``raw_meta.resolved_at`` + ``resolved_hash``) — re-runs
    on unchanged notes are no-ops.
  - Dangling-link guard — only rewrites if the target slug exists on disk.
  - Existing wikilinks are passed through verbatim.
"""
from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from obsidian_orphan_killer.alias_table import AliasTable
from obsidian_orphan_killer.alias_table import build as build_alias_table
from obsidian_orphan_killer.fm import (
    RESOLVE_FIELDS,
    resolve_hash,
    serialize,
    should_skip,
    split_frontmatter,
    stamp_meta,
    write_atomic,
)
from obsidian_orphan_killer.slug import normalize

log = logging.getLogger(__name__)

# Default resolution scope — leaf layers of a typical PKM vault.
DEFAULT_SCOPE_DIRS: tuple[str, ...] = ("sources", "inbox", "context")


@dataclass
class NoteResolution:
    changed: bool
    resolved: list[tuple[str, str, str]]   # (field, before_surface, after_slug)
    residual: list[tuple[str, str]]        # (field, surface_left_as_plain)


def discover_notes(
    vault_root: Path,
    paths: list[Path] | None = None,
    scope_dirs: tuple[str, ...] = DEFAULT_SCOPE_DIRS,
) -> list[Path]:
    """Source notes to resolve. If ``paths`` is given, use those exactly."""
    if paths:
        return [p for p in paths if p.suffix == ".md" and p.exists()]
    if not scope_dirs:
        # Scope: whole vault except hub dirs.
        return [
            p for p in sorted(vault_root.rglob("*.md"))
            if "_quarantine" not in p.relative_to(vault_root).parts
        ]
    out: list[Path] = []
    for sub in scope_dirs:
        root = vault_root / sub
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.md")):
            if "_quarantine" in p.relative_to(vault_root).parts:
                continue
            out.append(p)
    return out


def _resolve_fm_fields(
    fm: dict, table: AliasTable
) -> tuple[dict, NoteResolution]:
    """Walk ``entities`` / ``topics``; rewrite plain strings to ``[[slug]]``.

    Two surface forms in the same list that resolve to the same hub collapse
    onto a single ``[[slug]]`` entry (preserving first-seen order) — otherwise
    ``[python3, py]`` would become ``[[[python]], [[python]]]``.
    """
    fm = dict(fm)
    resolved: list[tuple[str, str, str]] = []
    residual: list[tuple[str, str]] = []
    changed = False
    for fld in RESOLVE_FIELDS:
        items = fm.get(fld)
        if not isinstance(items, list):
            continue
        new_items: list = []
        seen_in_field: set[str] = set()
        for it in items:
            if not isinstance(it, str):
                new_items.append(it)
                continue
            s = it.strip()
            if s.startswith("[[") and s.endswith("]]"):
                if s not in seen_in_field:
                    new_items.append(it)
                    seen_in_field.add(s)
                else:
                    # Pre-existing duplicate (e.g. two `[[python]]` lines) —
                    # dedupe silently. Counts as a change so the file gets
                    # rewritten with the cleaner form.
                    changed = True
                continue
            if not s:
                continue
            key = normalize(s)
            slug = table.by_norm.get(key)
            if slug and slug in table.hub_slugs:
                link = f"[[{slug}]]"
                if link not in seen_in_field:
                    new_items.append(link)
                    seen_in_field.add(link)
                resolved.append((fld, s, slug))
                changed = True
            else:
                if s in seen_in_field:
                    changed = True
                    continue
                new_items.append(it)  # leave plain — never dangle
                seen_in_field.add(s)
                residual.append((fld, s))
        fm[fld] = new_items
    return fm, NoteResolution(changed=changed, resolved=resolved, residual=residual)


def resolve_notes(
    vault_root: Path,
    note_paths: list[Path] | None = None,
    *,
    table: AliasTable | None = None,
    hub_dirs: tuple[str, ...] | None = None,
    scope_dirs: tuple[str, ...] = DEFAULT_SCOPE_DIRS,
    dry_run: bool = False,
    force: bool = False,
    limit: int | None = None,
) -> dict:
    """Resolve every plain-string entity/topic across the scope.

    Args:
        vault_root: Vault root.
        note_paths: Optional explicit list of notes to resolve (overrides scope).
        table: Pre-built alias table; built from ``hub_dirs`` if absent.
        hub_dirs: Hub directories for the alias-table builder. Defaults to
            ``("entities", "concepts")``.
        scope_dirs: Leaf-layer directories to resolve. Defaults to
            ``("sources", "inbox", "context")``. Pass ``()`` for whole-vault.
        dry_run: Report-only; writes nothing.
        force: Re-resolve notes whose ``resolved_hash`` matches the current
            state (the normal path skips them — idempotency).
        limit: Cap the number of notes processed (for smoke-testing).

    Returns:
        Stats dict with ``scanned``, ``written``, ``resolved_occurrences``,
        ``residual_occurrences``, ``top_residuals`` (top 20 unresolved
        surface forms by frequency), etc.
    """
    if table is None:
        if hub_dirs is None:
            table = build_alias_table(vault_root)
        else:
            table = build_alias_table(vault_root, hub_dirs=hub_dirs)

    notes = discover_notes(vault_root, note_paths, scope_dirs)
    if limit is not None:
        notes = notes[:limit]

    stats: dict = {
        "scanned": 0, "skipped": 0, "written": 0, "errors": 0,
        "resolved_occurrences": 0, "residual_occurrences": 0,
        "notes_with_resolution": 0,
        "hubs_known": len(table.hub_slugs),
        "alias_table_size": len(table.by_norm),
        "collisions": len(table.collisions),
    }
    residual_counter: Counter[str] = Counter()

    for p in notes:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("cannot read %s: %s", p, exc)
            stats["errors"] += 1
            continue
        fm, body = split_frontmatter(text)
        if fm is None:
            continue
        stats["scanned"] += 1
        ch = resolve_hash(fm, body)
        if not force and should_skip(fm, "resolved_at", "resolved_hash", ch):
            stats["skipped"] += 1
            continue
        new_fm, res = _resolve_fm_fields(fm, table)
        stats["resolved_occurrences"] += len(res.resolved)
        stats["residual_occurrences"] += len(res.residual)
        for _fld, surface in res.residual:
            k = normalize(surface)
            if k:
                residual_counter[k] += 1
        if res.changed:
            stats["notes_with_resolution"] += 1
        if dry_run:
            continue
        if not res.changed:
            continue
        new_hash = resolve_hash(new_fm, body)
        new_fm = stamp_meta(
            new_fm, "resolved_at", "resolved_hash", new_hash,
            extras={"resolved_count": len(res.resolved)},
        )
        try:
            write_atomic(p, serialize(new_fm, body))
            stats["written"] += 1
        except OSError as exc:
            log.warning("cannot write %s: %s", p, exc)
            stats["errors"] += 1

    stats["distinct_residual_keys"] = len(residual_counter)
    stats["top_residuals"] = residual_counter.most_common(20)
    return stats
