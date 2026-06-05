"""Tests for the core auditor on synthetic fixture vaults."""
from __future__ import annotations

from pathlib import Path

import pytest

from obsidian_graph_auditor.auditor import audit, build_graph
from tests.conftest import (
    make_force_star_vault,
    make_healthy_vault,
    make_orphan_heavy_vault,
)


def test_empty_vault_does_not_crash(tmp_path: Path) -> None:
    """An empty directory should audit to zero notes without exceptions."""
    metrics = audit(tmp_path)
    assert metrics["total_notes"] == 0
    assert metrics["resolved_internal_edges"] == 0
    assert metrics["link_density"] == 0.0
    assert metrics["modularity"] == 0.0


def test_healthy_vault_scores_well(tmp_path: Path) -> None:
    vault = make_healthy_vault(tmp_path)
    metrics = audit(vault)

    # 30 notes total, body links wire each note to 4 cluster siblings.
    assert metrics["total_notes"] == 30
    assert metrics["resolved_internal_edges"] > 0

    # Healthy vault has near-zero orphans (we wired everything).
    assert metrics["orphan_pct"] < 5.0

    # Top-hub edge-share should be reasonable (no force-star).
    assert metrics["top_hub_edge_share_pct"] < 25.0

    # Modularity should detect the 3 themed clusters.
    assert metrics["modularity"] >= 0.3, f"expected modularity ≥ 0.3, got {metrics['modularity']}"
    assert metrics["n_communities"] >= 2


def test_orphan_heavy_vault_flags_orphans(tmp_path: Path) -> None:
    vault = make_orphan_heavy_vault(tmp_path)
    metrics = audit(vault)
    # 20 notes, only 2 connected → expect >80% orphan rate.
    assert metrics["total_notes"] == 20
    assert metrics["orphan_pct"] >= 80.0


def test_force_star_vault_flags_top_hub(tmp_path: Path) -> None:
    vault = make_force_star_vault(tmp_path)
    metrics = audit(vault)
    # The hub captures ALL edges → top-hub edge-share should be very high.
    assert metrics["top_hub"] == "mega-hub"
    assert metrics["top_hub_edge_share_pct"] >= 30.0


def test_build_graph_collapses_parallel_edges(tmp_path: Path) -> None:
    """Body wikilink + frontmatter wikilink should collapse into ONE weighted edge."""
    vault = tmp_path / "v"
    vault.mkdir()
    import yaml
    (vault / "a.md").write_text(
        "---\n" + yaml.safe_dump({"tags": ["[[b]]"]}) + "---\n\nSee [[b]].\n",
        encoding="utf-8",
    )
    (vault / "b.md").write_text("# B\n", encoding="utf-8")
    G = build_graph(vault)
    assert G.number_of_edges() == 1
    # Two unit-weight wikilink contributions should sum to 2.0.
    assert G.edges()[("a", "b")]["weight"] == pytest.approx(2.0)


def test_aliases_extracted_from_pipe_syntax(tmp_path: Path) -> None:
    """``[[Note|Alias]]`` should resolve to ``note``, not ``alias``."""
    vault = tmp_path / "v"
    vault.mkdir()
    (vault / "a.md").write_text("See [[Real Target|nice alias]].\n", encoding="utf-8")
    (vault / "real-target.md").write_text("# Real\n", encoding="utf-8")
    G = build_graph(vault)
    assert ("a", "real-target") in [tuple(sorted(e)) for e in G.edges()]


def test_obsidian_internal_dirs_skipped(tmp_path: Path) -> None:
    """``.obsidian/``, ``.git/``, ``node_modules/`` should be ignored."""
    vault = tmp_path / "v"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "config.md").write_text("# config\n[[a]]\n", encoding="utf-8")
    (vault / ".git").mkdir(parents=True)
    (vault / ".git" / "HEAD.md").write_text("# head\n[[a]]\n", encoding="utf-8")
    (vault / "real.md").write_text("# real\n", encoding="utf-8")
    metrics = audit(vault)
    assert metrics["total_notes"] == 1


def test_audit_output_is_json_serializable(tmp_path: Path) -> None:
    """The audit dict must round-trip through json.dumps cleanly."""
    import json
    vault = make_healthy_vault(tmp_path)
    metrics = audit(vault)
    payload = json.dumps(metrics)
    restored = json.loads(payload)
    assert restored["total_notes"] == metrics["total_notes"]
