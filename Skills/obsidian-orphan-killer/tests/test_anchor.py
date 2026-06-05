"""Tests for the anchor mode using a stub embedder (no fastembed dep).

A stub embedder lets us assert the anchor LOGIC (floor, max_per_hub,
dangling guard, concepts-only target set) without downloading a model.
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from obsidian_orphan_killer.anchor import anchor_orphans
from obsidian_orphan_killer.fm import body_only_hash, split_frontmatter


class StubEmbedder:
    """Deterministic stub: maps text containing keywords to known vectors.

    The vectors are crafted so:
      - text containing 'graph' / 'nodes' / 'edges' / 'modularity' is close to
        the 'Graph Theory' hub (cosine ~0.95);
      - text containing 'pasta' / 'food' / 'recipe' is far from any hub
        (cosine well below 0.74 floor).
    """

    def __init__(self):
        self._signatures = [
            (("graph", "nodes", "edges", "modularity", "communities"), [1.0, 0.0, 0.0]),
            (("pasta", "food", "recipe", "butter"), [0.0, 0.0, 1.0]),
            (("cooking", "food", "preparation"), [0.0, 1.0, 0.1]),
            (("graph", "theory"), [1.0, 0.0, 0.0]),  # the hub itself
        ]

    def embed(self, texts: Iterable[str]):
        # Stub returns objects with a .tolist() method (mirrors fastembed's
        # numpy.ndarray return, but without the numpy dep).
        class _Vec(list):
            def tolist(self):
                return list(self)

        out = []
        for t in texts:
            tl = t.lower()
            best = [0.05, 0.05, 0.05]
            best_score = 0
            for keywords, vec in self._signatures:
                hits = sum(1 for k in keywords if k in tl)
                if hits > best_score:
                    best_score = hits
                    best = vec
            out.append(_Vec(best))
        return out


def test_anchor_dry_run_writes_nothing(orphan_vault: Path):
    src = orphan_vault / "sources" / "orphan-graph.md"
    before = src.read_text(encoding="utf-8")
    embedder = StubEmbedder()
    stats = anchor_orphans(orphan_vault, dry_run=True, embedder=embedder, floor=0.5)
    after = src.read_text(encoding="utf-8")
    assert before == after
    # Stats still report what WOULD have anchored.
    assert stats["orphan_candidates"] == 2  # graph + recipe
    assert stats["anchored"] >= 1


def test_anchor_attaches_high_cosine_match(orphan_vault: Path):
    """A genuinely-relevant orphan should anchor to the right hub."""
    embedder = StubEmbedder()
    anchor_orphans(orphan_vault, dry_run=False, embedder=embedder, floor=0.5)
    fm, _ = split_frontmatter(
        (orphan_vault / "sources" / "orphan-graph.md").read_text(encoding="utf-8")
    )
    assert "[[graph-theory]]" in fm["entities"]
    assert "anchored_at" in fm["raw_meta"]
    assert fm["raw_meta"]["anchor_hub"] == "graph-theory"


def test_anchor_below_floor_leaves_unlinked(orphan_vault: Path):
    """A weak match must NOT be force-linked — safety behavior."""
    embedder = StubEmbedder()
    anchor_orphans(orphan_vault, dry_run=False, embedder=embedder, floor=0.99)
    fm, _ = split_frontmatter(
        (orphan_vault / "sources" / "orphan-recipe.md").read_text(encoding="utf-8")
    )
    # No entities attached because nothing cleared the 0.99 floor.
    assert "entities" not in fm or not fm.get("entities")


def test_anchor_body_hash_preserved(orphan_vault: Path):
    """KEY safety contract — body bytes never modified."""
    src = orphan_vault / "sources" / "orphan-graph.md"
    _, body_before = split_frontmatter(src.read_text(encoding="utf-8"))
    hash_before = body_only_hash(body_before)
    embedder = StubEmbedder()
    anchor_orphans(orphan_vault, dry_run=False, embedder=embedder, floor=0.5)
    _, body_after = split_frontmatter(src.read_text(encoding="utf-8"))
    hash_after = body_only_hash(body_after)
    assert hash_before == hash_after, "ANCHOR MUTATED THE BODY — safety contract broken"


def test_anchor_dump_tsv_emitted(orphan_vault: Path, tmp_path: Path):
    """The audit TSV must contain every candidate's decision row."""
    embedder = StubEmbedder()
    dump = tmp_path / "anchor.tsv"
    anchor_orphans(orphan_vault, dry_run=True, embedder=embedder, floor=0.5,
                   dump_tsv=dump)
    assert dump.exists()
    text = dump.read_text(encoding="utf-8")
    assert "cosine\tdecision\thub\tnote" in text
    # The graph orphan should appear with decision 'anchored'.
    assert "anchored" in text


def test_anchor_max_per_hub_caps_absorption(tmp_path: Path):
    """Anti-star: a single hub can't absorb more than max_per_hub per run."""
    import yaml
    vault = tmp_path / "v"
    # 1 concept hub + 5 graph-flavored orphans.
    (vault / "concepts").mkdir(parents=True)
    (vault / "concepts" / "graph-theory.md").write_text(
        "---\n" + yaml.safe_dump({"type": "concept", "title": "Graph Theory"}) + "---\n"
        "Nodes and edges form a graph.\n",
        encoding="utf-8",
    )
    (vault / "sources").mkdir()
    for i in range(5):
        (vault / "sources" / f"orphan-{i}.md").write_text(
            "---\n" + yaml.safe_dump({"title": f"O{i}"}) + "---\n"
            "# O\n\nGraphs nodes edges modularity communities.\n" * 5,
            encoding="utf-8",
        )

    embedder = StubEmbedder()
    stats = anchor_orphans(vault, dry_run=True, embedder=embedder,
                           floor=0.5, max_per_hub=2)
    # 5 candidates, cap=2 → 2 anchored, 3 hub-capped.
    assert stats["anchored"] == 2
    assert stats["hub_capped"] == 3


def test_anchor_idempotent(orphan_vault: Path):
    """A second anchor run must NOT re-anchor a previously-anchored orphan.

    The strongest possible idempotency: once an orphan has a [[hub]] link in
    its entities, it is no longer an orphan and is not even a candidate on
    the second pass. Either:

      - it drops out of ``orphan_candidates`` on the second pass (best case), or
      - it's still a candidate but the idempotency stamp skips it.

    Either way, ``written`` on the second pass must be 0.
    """
    embedder = StubEmbedder()
    stats1 = anchor_orphans(orphan_vault, dry_run=False, embedder=embedder, floor=0.5)
    stats2 = anchor_orphans(orphan_vault, dry_run=False, embedder=embedder, floor=0.5)
    assert stats1["written"] >= 1
    assert stats2["written"] == 0
    # Either the candidate count drops or the stamp skips them; both are valid.
    assert (stats2["orphan_candidates"] < stats1["orphan_candidates"]
            or stats2["skipped_idempotent"] >= stats1["written"])


def test_anchor_concepts_only_default(orphan_vault: Path, tmp_path: Path):
    """The default target set must EXCLUDE entities/ hubs — brand-leak guard."""
    import yaml
    # Add an entity hub.
    (orphan_vault / "entities").mkdir(exist_ok=True)
    (orphan_vault / "entities" / "neo4j.md").write_text(
        "---\n" + yaml.safe_dump({"type": "entity", "title": "Neo4j"}) + "---\n"
        "Neo4j is a graph database company.\n",
        encoding="utf-8",
    )
    embedder = StubEmbedder()
    stats = anchor_orphans(orphan_vault, dry_run=True, embedder=embedder, floor=0.5)
    # Target hub kind in stats confirms concepts-only.
    assert stats["target_hub_kind"] == "concepts-only"
    # Even with the entity hub present, anchors go to graph-theory (concept).
    if stats["sample"]:
        assert all(row["hub"] != "neo4j" for row in stats["sample"])
