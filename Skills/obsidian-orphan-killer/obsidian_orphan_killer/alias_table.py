"""Alias-table builder — the deterministic, $0, no-network resolution layer.

The table maps ``normalize(surface)`` → canonical hub slug, where the slug is
guaranteed to exist on disk. Entries are mined from each hub note's:

  1. filename stem (e.g. ``open-ai.md`` → ``open-ai``)
  2. slug with hyphens replaced by spaces (``open ai``)
  3. frontmatter ``title:`` value
  4. each frontmatter ``aliases:`` value

Within a hub, identity wins over alias: the slug and title are added in pass 1
and aliases in pass 2, so an alias from hub B can never overwrite the hard
identity of hub A.

Decoupled from any particular vault convention: the caller supplies the list
of hub directories (e.g. ``["entities", "concepts"]`` for an Obsidian-style
PKM, or ``["pages"]`` for a flat Logseq vault, or whatever the user wants).
Defaults to ``["entities", "concepts"]`` because that's the most common pattern
in zettelkasten / second-brain vaults.
"""
from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from obsidian_orphan_killer.fm import split_frontmatter
from obsidian_orphan_killer.slug import normalize

log = logging.getLogger(__name__)

# Default hub-dir convention: ``entities/`` (brand / proper-noun hubs) +
# ``concepts/`` (topical hubs). Override via the ``hub_dirs`` parameter.
DEFAULT_HUB_DIRS: tuple[str, ...] = ("entities", "concepts")

# Default kind classification — the anchor leg uses this to do concepts-only
# linking by default (so a generic how-to note doesn't anchor to a brand hub).
DEFAULT_KINDS: dict[str, str] = {
    "entities": "entity",
    "concepts": "concept",
}


@dataclass
class AliasTable:
    """``normalize(surface)`` → canonical hub slug (on-disk-existing)."""
    by_norm: dict[str, str] = field(default_factory=dict)
    hub_slugs: set[str] = field(default_factory=set)
    hub_names: dict[str, str] = field(default_factory=dict)
    hub_kinds: dict[str, str] = field(default_factory=dict)
    # ``norm_key`` -> {slug, ...} for keys two different hubs both claim.
    collisions: dict[str, set[str]] = field(default_factory=dict)

    def add(self, norm_key: str, slug: str) -> None:
        if not norm_key or not slug:
            return
        existing = self.by_norm.get(norm_key)
        if existing is not None and existing != slug:
            self.collisions.setdefault(norm_key, {existing}).add(slug)
            return
        self.by_norm[norm_key] = slug

    def resolve(self, surface: str) -> str | None:
        """Loose-key lookup: return the canonical slug for a surface form."""
        return self.by_norm.get(normalize(surface))

    def has_hub(self, slug: str) -> bool:
        return slug in self.hub_slugs


def build(
    vault_root: Path,
    hub_dirs: Iterable[str] = DEFAULT_HUB_DIRS,
    kinds: dict[str, str] | None = None,
) -> AliasTable:
    """Build the alias table from a vault's hub directories.

    Args:
        vault_root: Vault root (parent of the hub dirs).
        hub_dirs: List of subdirectory names that contain hub notes. Defaults
            to ``("entities", "concepts")``. A directory that doesn't exist is
            silently skipped — partial vaults are fine.
        kinds: Optional mapping from ``dir_name`` to ``kind`` label (used by
            the anchor leg to do concepts-only targeting). Defaults to
            ``{"entities": "entity", "concepts": "concept"}``; other dirs map
            to their stem if not supplied.

    Returns:
        Populated ``AliasTable``.
    """
    if kinds is None:
        kinds = dict(DEFAULT_KINDS)

    table = AliasTable()
    # Pass 1: hard identity (slug + title); pass 2: soft aliases.
    pending_aliases: list[tuple[str, str]] = []
    for dirname in hub_dirs:
        d = vault_root / dirname
        if not d.exists() or not d.is_dir():
            continue
        hub_kind = kinds.get(dirname, dirname.rstrip("s"))
        for p in sorted(d.glob("*.md")):
            if p.name.startswith("_"):
                continue
            slug = p.stem
            table.hub_slugs.add(slug)
            table.hub_kinds[slug] = hub_kind
            table.add(normalize(slug), slug)
            table.add(normalize(slug.replace("-", " ")), slug)
            display = slug.replace("-", " ")
            try:
                fm, _ = split_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
            except OSError as exc:
                log.warning("cannot read hub %s: %s", p, exc)
                fm = None
            if fm:
                title = fm.get("title")
                if isinstance(title, str) and title.strip():
                    table.add(normalize(title), slug)
                    display = title.strip()
                aliases = fm.get("aliases") or []
                if isinstance(aliases, list):
                    for a in aliases:
                        if isinstance(a, str) and a.strip():
                            pending_aliases.append((a.strip(), slug))
            table.hub_names[slug] = display
    # Pass 2: soft aliases never overwrite a hard key.
    for alias_str, slug in pending_aliases:
        table.add(normalize(alias_str), slug)
    return table
