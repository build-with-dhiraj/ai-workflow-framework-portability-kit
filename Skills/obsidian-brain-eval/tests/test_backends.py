"""Tests for the NaiveBM25Backend on synthetic fixture vaults."""
from __future__ import annotations

from pathlib import Path

from obsidian_brain_eval.backends import NaiveBM25Backend, default_tokenise
from obsidian_brain_eval.eval import score
from tests.conftest import gold_for_demo, make_demo_vault


def test_default_tokenise_drops_stopwords_and_lowercases() -> None:
    tokens = default_tokenise("How does BM25 score the documents?")
    assert "bm25" in tokens
    assert "score" in tokens
    assert "documents" in tokens
    # Stopwords stripped:
    assert "how" not in tokens
    assert "the" not in tokens


def test_default_tokenise_handles_unicode() -> None:
    tokens = default_tokenise("Naïve façade — déjà vu")
    # Non-ASCII chars are folded to ASCII.
    assert "naive" in tokens
    assert "facade" in tokens
    assert "deja" in tokens
    assert "vu" in tokens


def test_naive_bm25_on_demo_vault_hits_all(tmp_path: Path) -> None:
    """A small unambiguous demo vault should hit every gold question with BM25."""
    vault = make_demo_vault(tmp_path)
    backend = NaiveBM25Backend(vault)
    gold = gold_for_demo(vault)
    result = score(gold, backend, k=10, target=0.85)
    assert result["pass"] is True, result
    assert result["recall_at_k"] == 1.0


def test_naive_bm25_empty_vault_returns_empty(tmp_path: Path) -> None:
    """An empty vault gives an empty top-k without exceptions."""
    vault = tmp_path / "empty"
    vault.mkdir()
    backend = NaiveBM25Backend(vault)
    assert backend.topk("anything", 10) == []


def test_naive_bm25_skips_underscore_files(tmp_path: Path) -> None:
    """Files starting with '_' (templates, drafts) are excluded from the index.

    Note: BM25Okapi gives degenerate (zero) scores on a 2-doc corpus, so we add
    a handful of unrelated filler notes to keep IDF non-trivial.
    """
    vault = tmp_path / "v"
    (vault / "concepts").mkdir(parents=True)
    (vault / "concepts" / "real.md").write_text(
        "# real\n\nUnicornCoffee UnicornCoffee is a unique term in this note.\n",
        encoding="utf-8",
    )
    (vault / "concepts" / "_draft.md").write_text(
        "# draft\n\nUnicornCoffee should appear but the indexer must skip me.\n",
        encoding="utf-8",
    )
    # Filler notes give BM25 a non-degenerate corpus.
    for i, body in enumerate([
        "Unrelated content alpha.",
        "Unrelated content beta on retrieval.",
        "Unrelated content gamma about search.",
        "Unrelated content delta about indexes.",
    ]):
        (vault / "concepts" / f"filler-{i}.md").write_text(
            f"# filler-{i}\n\n{body}\n", encoding="utf-8"
        )
    backend = NaiveBM25Backend(vault)
    paths = backend.topk("UnicornCoffee", 10)
    assert "v/concepts/real.md" in paths
    assert "v/concepts/_draft.md" not in paths


def test_naive_bm25_question_with_no_matching_terms_returns_empty(tmp_path: Path) -> None:
    """Pure-stopword queries should not crash and should return no hits."""
    vault = make_demo_vault(tmp_path)
    backend = NaiveBM25Backend(vault)
    assert backend.topk("the and is to of", 10) == []


def test_naive_bm25_ranks_specific_note_first(tmp_path: Path) -> None:
    """A unique term in exactly one note should rank that note first."""
    vault = make_demo_vault(tmp_path)
    backend = NaiveBM25Backend(vault)
    top = backend.topk("LanceDB embedded vector database", 5)
    assert top[0] == f"{vault.name}/entities/lancedb.md"
