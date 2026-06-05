"""Shared fixture helpers for the test suite."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def _write(path: Path, frontmatter: dict | None, body: str) -> None:
    """Write a markdown file with optional YAML frontmatter + body."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if frontmatter is not None:
        import yaml
        lines.append("---")
        lines.append(yaml.safe_dump(frontmatter, sort_keys=True, default_flow_style=False).rstrip())
        lines.append("---")
    lines.append(body.rstrip() + "\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def make_healthy_vault(root: Path, n_notes: int = 30) -> Path:
    """A vault with healthy link density, low orphan rate, and proper community structure.

    Structure: 3 themed clusters of 10 notes each. Each note links to 4 siblings.
    """
    vault = root / "vault_healthy"
    vault.mkdir(exist_ok=True)
    clusters = ["alpha", "beta", "gamma"]
    per_cluster = n_notes // len(clusters)
    for _ci, name in enumerate(clusters):
        for j in range(per_cluster):
            slug = f"{name}-{j:02d}"
            fm = {"type": "concept", "tags": [name], "related": [f"[[{name}-{(j + 1) % per_cluster:02d}]]"]}
            siblings = [f"[[{name}-{(j + k) % per_cluster:02d}]]" for k in (1, 2, 3, 4) if (j + k) % per_cluster != j]
            body = f"# {slug}\n\nThis is a note in cluster {name}. See {' '.join(siblings)}."
            _write(vault / f"{name}-{j:02d}.md", fm, body)
    return vault


def make_orphan_heavy_vault(root: Path, n_notes: int = 20) -> Path:
    """A vault where most notes are orphans (no internal links)."""
    vault = root / "vault_orphans"
    vault.mkdir(exist_ok=True)
    for i in range(n_notes):
        slug = f"note-{i:02d}"
        body = f"# {slug}\n\nThis is a captured save with no connections to anything else.\n"
        # First two notes link to each other; the rest are orphans.
        if i == 0:
            body += "\nSee [[note-01]] for the connection.\n"
        if i == 1:
            body += "\nSee [[note-00]] for the connection.\n"
        _write(vault / f"{slug}.md", None, body)
    return vault


def make_force_star_vault(root: Path, n_spokes: int = 15) -> Path:
    """A vault with one mega-hub everyone links to (force-star anti-pattern)."""
    vault = root / "vault_starhub"
    vault.mkdir(exist_ok=True)
    fm_hub = {"type": "entity", "aliases": ["The Hub"]}
    _write(vault / "mega-hub.md", fm_hub, "# Mega Hub\n\nThe center.\n")
    for i in range(n_spokes):
        slug = f"spoke-{i:02d}"
        body = f"# {slug}\n\nEverything connects to [[mega-hub]] and only [[mega-hub]].\n"
        _write(vault / f"{slug}.md", None, body)
    return vault


def all_notes(vault: Path) -> Iterable[Path]:
    return sorted(vault.rglob("*.md"))
