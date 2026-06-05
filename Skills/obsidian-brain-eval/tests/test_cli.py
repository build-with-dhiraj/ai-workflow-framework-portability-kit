"""End-to-end CLI tests using the shipped demo vault."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Invoke the CLI as a subprocess so argparse error paths are exercised."""
    return subprocess.run(
        [sys.executable, "-m", "obsidian_brain_eval.cli", *args],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )


def test_cli_version() -> None:
    out = _run_cli("--version")
    assert out.returncode == 0
    assert "obsidian-brain-eval" in out.stdout


def test_cli_score_demo_vault_passes() -> None:
    """The shipped demo vault + sample gold-set should pass with naive BM25."""
    root = _project_root()
    out = _run_cli(
        "score",
        "--vault", str(root / "examples" / "demo-vault"),
        "--gold", str(root / "examples" / "sample-gold-set.jsonl"),
        "--backend", "naive",
    )
    assert out.returncode == 0, f"stderr: {out.stderr}\nstdout: {out.stdout}"
    assert "Recall@10" in out.stdout
    assert "PASS" in out.stdout


def test_cli_score_writes_json_out(tmp_path: Path) -> None:
    root = _project_root()
    json_path = tmp_path / "result.json"
    out = _run_cli(
        "score",
        "--vault", str(root / "examples" / "demo-vault"),
        "--gold", str(root / "examples" / "sample-gold-set.jsonl"),
        "--backend", "naive",
        "--json-out", str(json_path),
        "--quiet",
    )
    assert out.returncode == 0, f"stderr: {out.stderr}"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["k"] == 10
    assert data["n_questions"] == 8
    assert data["pass"] is True
    assert "per_question" in data


def test_cli_score_missing_vault_exits_2() -> None:
    out = _run_cli(
        "score",
        "--vault", "/nonexistent/path/that/should/never/exist",
        "--gold", "examples/sample-gold-set.jsonl",
        "--backend", "naive",
    )
    assert out.returncode == 2


def test_cli_score_missing_gold_exits_2(tmp_path: Path) -> None:
    """Pointing at an empty gold-set file should exit non-zero, not crash."""
    root = _project_root()
    empty_gold = tmp_path / "empty.jsonl"
    empty_gold.write_text("", encoding="utf-8")
    out = _run_cli(
        "score",
        "--vault", str(root / "examples" / "demo-vault"),
        "--gold", str(empty_gold),
        "--backend", "naive",
    )
    assert out.returncode == 2
