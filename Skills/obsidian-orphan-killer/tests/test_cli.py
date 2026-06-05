"""Smoke tests for the CLI entry point."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obsidian_orphan_killer.cli import main


def test_cli_version(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "obsidian-orphan-killer" in captured.out


def test_cli_resolve_dry_run(tiny_vault: Path, capsys: pytest.CaptureFixture[str]):
    rc = main(["resolve", "--vault", str(tiny_vault), "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "obsidian-orphan-killer resolve" in out
    assert "scanned:" in out


def test_cli_resolve_emits_json(tiny_vault: Path, tmp_path: Path):
    json_out = tmp_path / "stats.json"
    rc = main([
        "resolve", "--vault", str(tiny_vault), "--dry-run",
        "--json-out", str(json_out),
    ])
    assert rc == 0
    assert json_out.exists()
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["scanned"] == 3
    assert "top_residuals" in data


def test_cli_mint_requires_experimental_flag(tiny_vault: Path,
                                              caplog: pytest.LogCaptureFixture):
    """Safety: mint mode must refuse without --experimental."""
    import logging
    with caplog.at_level(logging.ERROR):
        rc = main(["mint", "--vault", str(tiny_vault), "--dry-run"])
    assert rc == 2
    # Error message mentions --experimental.
    assert any("experimental" in m.lower() for m in caplog.messages)


def test_cli_vault_missing(tmp_path: Path):
    rc = main(["resolve", "--vault", str(tmp_path / "does-not-exist")])
    assert rc == 2
