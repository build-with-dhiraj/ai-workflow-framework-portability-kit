"""Shared fixture helpers for the obsidian-brain-eval test suite."""
from __future__ import annotations

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


def make_demo_vault(root: Path) -> Path:
    """Build a small 6-note vault used by most tests.

    The notes deliberately use distinct vocabulary so the BM25 backend should hit
    the right note for each question without confusion.
    """
    vault = root / "vault_demo"
    vault.mkdir(exist_ok=True)
    _write(
        vault / "concepts" / "recall-at-k.md",
        {"title": "Recall@k", "type": "concept", "related": ["[[gold-set]]"]},
        "# Recall@k\n\nRecall at k counts whether a relevant document appears in the top k results.",
    )
    _write(
        vault / "concepts" / "gold-set.md",
        {"title": "Gold Set", "type": "concept", "topics": ["[[evaluation-metrics]]"]},
        "# Gold Set\n\nA gold-set is a list of question and known-relevant document pairs.",
    )
    _write(
        vault / "concepts" / "bm25.md",
        {"title": "BM25", "type": "concept"},
        "# BM25\n\nBM25 is the bag-of-words sparse retrieval baseline algorithm.",
    )
    _write(
        vault / "concepts" / "vector-search.md",
        {"title": "Vector Search", "type": "concept"},
        "# Vector Search\n\nVector search uses sentence-embedding nearest-neighbour distance.",
    )
    _write(
        vault / "entities" / "lancedb.md",
        {"title": "LanceDB", "type": "entity"},
        "# LanceDB\n\nLanceDB is an embedded vector database with full-text search.",
    )
    _write(
        vault / "entities" / "obsidian.md",
        {"title": "Obsidian", "type": "entity"},
        "# Obsidian\n\nObsidian is a markdown-based personal knowledge management tool.",
    )
    return vault


def gold_for_demo(vault: Path) -> list[dict]:
    """Hand-curated gold records targeting the make_demo_vault notes."""
    name = vault.name
    return [
        {
            "question": "What metric counts whether a relevant document is in the top k?",
            "source_note": f"{name}/concepts/recall-at-k.md",
            "relevant_paths": [f"{name}/concepts/recall-at-k.md"],
            "title": "Recall@k",
        },
        {
            "question": "What is a list of question and known-relevant document pairs called?",
            "source_note": f"{name}/concepts/gold-set.md",
            "relevant_paths": [f"{name}/concepts/gold-set.md"],
            "title": "Gold Set",
        },
        {
            "question": "What is the bag-of-words sparse retrieval baseline algorithm?",
            "source_note": f"{name}/concepts/bm25.md",
            "relevant_paths": [f"{name}/concepts/bm25.md"],
            "title": "BM25",
        },
        {
            "question": "Which database is an embedded vector database with full-text search?",
            "source_note": f"{name}/entities/lancedb.md",
            "relevant_paths": [f"{name}/entities/lancedb.md"],
            "title": "LanceDB",
        },
    ]
