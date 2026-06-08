"""Test fixtures — tiny in-memory vault builders for the test suite."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _write(path: Path, fm: dict | None, body: str) -> None:
    """Write a markdown file with optional YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if fm is not None:
        lines.append("---")
        lines.append(yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip())
        lines.append("---")
    lines.append(body.rstrip() + "\n")
    path.write_text("\n".join(lines), encoding="utf-8")


@pytest.fixture
def tiny_vault(tmp_path: Path) -> Path:
    """Build a minimal vault with two entity hubs, one concept hub, and three sources."""
    vault = tmp_path / "vault"
    # Hubs.
    _write(vault / "entities" / "python.md",
           {"type": "entity", "title": "Python", "aliases": ["python3", "py"]},
           "Python is a language.\n")
    _write(vault / "entities" / "obsidian.md",
           {"type": "entity", "title": "Obsidian", "aliases": ["obsidian.md"]},
           "Obsidian is a PKM tool.\n")
    _write(vault / "concepts" / "knowledge-management.md",
           {"type": "concept", "title": "Knowledge Management",
            "aliases": ["PKM", "second brain"]},
           "PKM is organizing notes.\n")
    # Sources.
    _write(vault / "sources" / "src-a.md",
           {"title": "A", "entities": ["python3", "py"], "topics": ["PKM"]},
           "# A\n\nA note about python and PKM.\n")
    _write(vault / "sources" / "src-b.md",
           {"title": "B", "entities": ["unknown-thing"], "topics": ["second brain"]},
           "# B\n\nResidual demo.\n")
    _write(vault / "sources" / "src-c.md",
           {"title": "C", "entities": ["[[python]]"]},
           "# C\n\nAlready linked.\n")
    return vault


@pytest.fixture
def orphan_vault(tmp_path: Path) -> Path:
    """Build a vault with one concept hub and two orphan source notes.

    No fastembed call here — fixtures stay deterministic. The orphan-anchor
    tests stub out the embedder.
    """
    vault = tmp_path / "vault"
    _write(vault / "concepts" / "graph-theory.md",
           {"type": "concept", "title": "Graph Theory", "aliases": ["graphs"]},
           "Graph theory studies nodes and edges.\n")
    _write(vault / "concepts" / "cooking.md",
           {"type": "concept", "title": "Cooking", "aliases": []},
           "Cooking is food preparation.\n")
    _write(vault / "sources" / "orphan-graph.md",
           {"title": "Thinking about graphs"},
           "# Thinking about graphs\n\nNodes, edges, communities, modularity.\n" * 5)
    _write(vault / "sources" / "orphan-recipe.md",
           {"title": "Random recipe"},
           "# Random recipe\n\nBoil pasta, drain, butter, salt.\n" * 5)
    return vault
