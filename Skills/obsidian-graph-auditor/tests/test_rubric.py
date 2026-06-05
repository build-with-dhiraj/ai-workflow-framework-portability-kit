"""Tests for the 8-dimension rubric + grader."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from obsidian_graph_auditor.auditor import audit
from obsidian_graph_auditor.rubric import (
    DEFAULT_THRESHOLDS,
    GRADES,
    grade,
    load_thresholds,
    score,
)
from tests.conftest import (
    make_force_star_vault,
    make_healthy_vault,
    make_orphan_heavy_vault,
)


def test_grade_letters_are_well_formed() -> None:
    assert GRADES == ("A", "B", "C", "D", "F")


def test_empty_metrics_grade_overall_f() -> None:
    # No metrics at all → no per-dim grades → overall F by definition.
    out = grade({})
    assert out["overall"] == "F"


def test_orphan_heavy_vault_grades_orphans_low(tmp_path: Path) -> None:
    vault = make_orphan_heavy_vault(tmp_path)
    metrics = audit(vault)
    g = grade(metrics)
    # 90% orphan rate → MaxThreshold a=10, b=20, c=30, d=40 → above all → F.
    assert g["orphan_pct"] == "F"
    assert g["overall"] == "F"


def test_force_star_vault_grades_concentration_low(tmp_path: Path) -> None:
    vault = make_force_star_vault(tmp_path)
    metrics = audit(vault)
    g = grade(metrics)
    # mega-hub captures 100% of edges → F on top_hub_edge_share_pct.
    assert g["top_hub_edge_share_pct"] == "F"


def test_healthy_vault_passes_link_density(tmp_path: Path) -> None:
    vault = make_healthy_vault(tmp_path)
    metrics = audit(vault)
    g = grade(metrics)
    # 30 notes wired to ≥4 siblings → density ≥ 2 → at least C, often A.
    assert g["link_density"] in ("A", "B", "C")


def test_score_is_0_to_100() -> None:
    metrics = {
        "link_density": 5.0,
        "orphan_pct": 5.0,
        "near_orphan_pct": 10.0,
        "connected_2plus_pct": 85.0,
        "top_hub_edge_share_pct": 3.0,
        "top_hub_next_ratio": 1.5,
        "modularity": 0.5,
        "fm_wikilink_adoption_pct": 85.0,
    }
    s = score(metrics)
    assert 0.0 <= s <= 100.0
    # All A's → 100.
    assert s == pytest.approx(100.0)


def test_threshold_yaml_override_loads(tmp_path: Path) -> None:
    cfg = tmp_path / "thresholds.yaml"
    cfg.write_text(yaml.safe_dump({"orphan_pct": {"a": 50.0, "b": 60.0, "c": 70.0, "d": 80.0}}))
    t = load_thresholds(cfg)
    # Original strict default would grade 40% as D. With our override (a=50), 40% should be A.
    g = grade({"orphan_pct": 40.0}, t)
    assert g["orphan_pct"] == "A"
    # Other dimensions should still use defaults.
    assert t.link_density.a == DEFAULT_THRESHOLDS.link_density.a


def test_top_hub_next_ratio_none_treated_as_a() -> None:
    g = grade({"top_hub_next_ratio": None, "link_density": 5.0})
    assert g["top_hub_next_ratio"] == "A"


def test_modularity_range_grade() -> None:
    # 0.5 is inside the A range [0.40, 0.65].
    assert grade({"modularity": 0.5})["modularity"] == "A"
    # 0.35 is in B range [0.30, 0.75] but outside A.
    assert grade({"modularity": 0.35})["modularity"] == "B"
    # 0.05 is below all ranges.
    assert grade({"modularity": 0.05})["modularity"] == "F"
