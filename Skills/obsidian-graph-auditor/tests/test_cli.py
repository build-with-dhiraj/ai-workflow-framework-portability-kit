"""Smoke tests for the CLI driver."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obsidian_graph_auditor.cli import main
from tests.conftest import make_healthy_vault, make_orphan_heavy_vault


def test_cli_runs_against_healthy_vault(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    vault = make_healthy_vault(tmp_path)
    out_json = tmp_path / "audit.json"
    rc = main(["--vault", str(vault), "--json-out", str(out_json), "--quiet"])
    assert rc == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["total_notes"] == 30
    assert "overall_grade" in payload
    assert payload["score"] >= 0.0


def test_cli_missing_vault_returns_2(tmp_path: Path) -> None:
    rc = main(["--vault", str(tmp_path / "does-not-exist"), "--quiet"])
    assert rc == 2


def test_cli_baseline_regression_fails(tmp_path: Path) -> None:
    """Healthy → orphan-heavy is a clear regression on every dimension."""
    healthy = make_healthy_vault(tmp_path)
    baseline_json = tmp_path / "baseline.json"
    rc1 = main(["--vault", str(healthy), "--json-out", str(baseline_json), "--quiet"])
    assert rc1 == 0

    orphan = make_orphan_heavy_vault(tmp_path)
    rc2 = main(["--vault", str(orphan), "--baseline", str(baseline_json), "--quiet"])
    # Should be 1 (regressed), though if both happen to grade-out equally
    # that's still a valid passing audit. The orphan vault is severe enough
    # that orphan_pct definitely regresses A → F.
    assert rc2 == 1


def test_cli_baseline_same_vault_no_regression(tmp_path: Path) -> None:
    vault = make_healthy_vault(tmp_path)
    baseline_json = tmp_path / "baseline.json"
    assert main(["--vault", str(vault), "--json-out", str(baseline_json), "--quiet"]) == 0
    rc = main(["--vault", str(vault), "--baseline", str(baseline_json), "--quiet"])
    assert rc == 0
