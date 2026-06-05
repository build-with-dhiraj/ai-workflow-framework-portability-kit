"""Tests for the scorer and gold-set loading."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obsidian_brain_eval.eval import load_gold, render_score, score, vault_path_str


class _FixedBackend:
    """Deterministic backend used to verify scoring math without retrieval noise."""

    def __init__(self, mapping: dict[str, list[str]]) -> None:
        self._mapping = mapping

    def topk(self, question: str, k: int) -> list[str]:
        return self._mapping.get(question, [])[:k]


def test_score_all_hits_passes() -> None:
    gold = [
        {"question": "q1", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]},
        {"question": "q2", "source_note": "v/b.md", "relevant_paths": ["v/b.md"]},
    ]
    backend = _FixedBackend({"q1": ["v/a.md", "v/x.md"], "q2": ["v/b.md"]})
    result = score(gold, backend, k=10, target=0.85)
    assert result["recall_at_k"] == 1.0
    assert result["hits"] == 2
    assert result["pass"] is True


def test_score_partial_hit_fails_target() -> None:
    gold = [
        {"question": "q1", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]},
        {"question": "q2", "source_note": "v/b.md", "relevant_paths": ["v/b.md"]},
        {"question": "q3", "source_note": "v/c.md", "relevant_paths": ["v/c.md"]},
    ]
    # Two hits, one miss => recall = 0.667 < 0.85 target.
    backend = _FixedBackend({"q1": ["v/a.md"], "q2": ["v/b.md"], "q3": ["v/x.md"]})
    result = score(gold, backend, k=10, target=0.85)
    assert result["hits"] == 2
    assert result["recall_at_k"] == pytest.approx(0.6667, abs=1e-3)
    assert result["pass"] is False


def test_score_per_question_breakdown_has_rank() -> None:
    gold = [
        {"question": "q1", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]},
        {"question": "q2", "source_note": "v/b.md", "relevant_paths": ["v/b.md"]},
    ]
    backend = _FixedBackend({"q1": ["v/x.md", "v/y.md", "v/a.md"], "q2": ["v/b.md"]})
    result = score(gold, backend, k=10)
    per_q = {q["question"]: q for q in result["per_question"]}
    assert per_q["q1"]["hit"] is True
    assert per_q["q1"]["first_hit_rank"] == 3
    assert per_q["q2"]["first_hit_rank"] == 1


def test_score_truncates_topk_to_k() -> None:
    """k=2 means only the first two paths count even if backend returns more."""
    gold = [{"question": "q", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]}]
    backend = _FixedBackend({"q": ["v/x.md", "v/y.md", "v/a.md"]})  # relevant at rank 3
    result = score(gold, backend, k=2)
    assert result["hits"] == 0
    assert result["recall_at_k"] == 0.0


def test_score_raises_on_empty_gold() -> None:
    backend = _FixedBackend({})
    with pytest.raises(ValueError):
        score([], backend, k=10)


def test_load_gold_roundtrip(tmp_path: Path) -> None:
    """A JSONL file with two records loads back into the same shape."""
    p = tmp_path / "gold.jsonl"
    records = [
        {"question": "q1", "source_note": "v/a.md", "relevant_paths": ["v/a.md"], "title": "A"},
        {"question": "q2", "source_note": "v/b.md", "relevant_paths": ["v/b.md", "v/c.md"], "title": "B"},
    ]
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    loaded = load_gold(p)
    assert loaded == records


def test_load_gold_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_gold(tmp_path / "does-not-exist.jsonl") == []


def test_render_score_includes_pass_or_fail() -> None:
    gold = [{"question": "q", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]}]
    backend = _FixedBackend({"q": ["v/a.md"]})
    out = render_score(score(gold, backend, k=10))
    assert "PASS" in out
    assert "Recall@10" in out


def test_render_score_lists_misses() -> None:
    gold = [{"question": "lost question", "source_note": "v/a.md", "relevant_paths": ["v/a.md"]}]
    backend = _FixedBackend({"lost question": ["v/x.md"]})
    out = render_score(score(gold, backend, k=10))
    assert "BELOW TARGET" in out
    assert "lost question" in out


def test_vault_path_str_uses_vault_name(tmp_path: Path) -> None:
    """vault_path_str must return 'vaultname/relative/path.md' shape."""
    vault = tmp_path / "myvault"
    (vault / "concepts").mkdir(parents=True)
    note = vault / "concepts" / "foo.md"
    note.write_text("# foo\n", encoding="utf-8")
    assert vault_path_str(vault, note) == "myvault/concepts/foo.md"
