"""Retrieval backends for obsidian-brain-eval.

Two backends ship by default:

    NaiveBM25Backend  - pure BM25 over title + body. Zero infra. Works anywhere
                        with `pip install obsidian-brain-eval[naive]` (adds
                        rank-bm25). Use this as the baseline every other backend
                        has to beat.

    LanceDBBackend    - the canonical hybrid full-text + vector search the
                        upstream engine measures. Requires `pip install
                        obsidian-brain-eval[lancedb]` (adds lancedb +
                        fastembed). Optional unless you're benchmarking the
                        production stack.

Custom backends just need to implement the ``RetrievalBackend`` protocol from
``obsidian_brain_eval.eval`` - a single ``topk(question, k) -> list[str]``
method that returns vault-relative paths (see ``vault_path_str``). That's it.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from obsidian_brain_eval.eval import vault_path_str

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tokenisation - shared by the naive backend and any user-defined tokeniser
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z0-9]+")

_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "but", "by",
    "for", "from", "has", "have", "in", "is", "it", "its",
    "of", "on", "or", "that", "the", "this", "to", "was",
    "were", "will", "with", "i", "you", "we", "they", "he",
    "she", "do", "does", "did", "what", "which", "who", "how",
    "when", "where", "why", "my", "your", "our", "their", "if",
    "can", "could", "should", "would", "may", "might", "about",
})


def default_tokenise(text: str) -> list[str]:
    """Lowercase ASCII word tokens, stopwords removed. Used by NaiveBM25Backend."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return [t.lower() for t in _WORD_RE.findall(norm) if t.lower() not in _STOPWORDS]


# ---------------------------------------------------------------------------
# Frontmatter parser (kept in sync with eval._split_frontmatter)
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    try:
        fm = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(fm, dict):
        return None, text
    return fm, text[end + 5:]


def _iter_markdown(vault: Path) -> Iterable[Path]:
    for p in sorted(vault.rglob("*.md")):
        if p.name.startswith("_"):
            continue
        yield p


# ---------------------------------------------------------------------------
# Naive BM25 backend (no embeddings)
# ---------------------------------------------------------------------------

class NaiveBM25Backend:
    """BM25 over (title + body) for every markdown file in the vault.

    This is the floor every fancier backend has to beat. It needs no embeddings,
    no vector DB, no API keys. The only dependency is ``rank-bm25``.

    Args:
        vault: path to the vault root.
        tokenise: callable that turns a string into a token list. Defaults to
            ``default_tokenise`` (ASCII-fold, lowercase, stopword-strip).
    """

    def __init__(self, vault: Path, tokenise=default_tokenise) -> None:
        try:
            from rank_bm25 import BM25Okapi  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "NaiveBM25Backend needs `pip install obsidian-brain-eval[naive]` "
                "(installs rank-bm25)."
            ) from exc

        self.vault = vault
        self.tokenise = tokenise
        self._paths: list[str] = []
        self._tokens: list[list[str]] = []

        for note in _iter_markdown(vault):
            try:
                text = note.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm, body = _split_frontmatter(text)
            title = (fm or {}).get("title") or note.stem
            self._paths.append(vault_path_str(vault, note))
            self._tokens.append(tokenise(f"{title}\n{body}"))

        if not self._paths:
            log.warning("Vault %s has zero markdown files; topk() will return []", vault)
            self._bm25 = None
        else:
            self._bm25 = BM25Okapi(self._tokens)

    def topk(self, question: str, k: int) -> list[str]:
        if self._bm25 is None:
            return []
        q_tokens = self.tokenise(question)
        if not q_tokens:
            return []
        scores = self._bm25.get_scores(q_tokens)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self._paths[i] for i in order if scores[i] > 0.0]


# ---------------------------------------------------------------------------
# LanceDB backend (hybrid FTS + vector, BAAI/bge-small-en-v1.5 embedding)
# ---------------------------------------------------------------------------

class LanceDBBackend:
    """Hybrid FTS + vector search against a LanceDB ``items`` table.

    This is the backend the upstream engine measures. It assumes a LanceDB
    table named ``items`` with at minimum columns ``vault_path`` (string),
    ``text`` (string), and a ``vector`` column populated with BAAI/bge-small
    embeddings. You bring the index; this backend only QUERIES it.

    Args:
        db_path: directory passed to ``lancedb.connect``.
        table_name: defaults to ``"items"``.
        embedding_model: fastembed model name. Defaults to the same model the
            upstream stack uses.
        fts_limit: how many FTS rows to merge per query.
    """

    def __init__(
        self,
        db_path: Path,
        table_name: str = "items",
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        fts_limit: int = 15,
    ) -> None:
        try:
            import lancedb  # type: ignore[import-not-found]
            from fastembed import TextEmbedding  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "LanceDBBackend needs `pip install obsidian-brain-eval[lancedb]`."
            ) from exc

        self._db = lancedb.connect(str(db_path))
        self._table = self._db.open_table(table_name)
        self._embedder = TextEmbedding(embedding_model)
        self._fts_limit = fts_limit

    def topk(self, question: str, k: int) -> list[str]:
        rows_fts = self._fts(question, limit=max(k, self._fts_limit))
        rows_vec = self._vector(question, limit=max(k, self._fts_limit))
        merged = _merge_dedup([rows_fts, rows_vec], top_n=k)
        return [r.get("vault_path", "") for r in merged[:k]]

    def _fts(self, question: str, limit: int) -> list[dict[str, Any]]:
        try:
            results = self._table.search(question, query_type="fts").limit(limit).to_list()
        except Exception as exc:  # noqa: BLE001 - lancedb raises a variety of errors
            log.warning("FTS query failed: %s", exc)
            return []
        return list(results)

    def _vector(self, question: str, limit: int) -> list[dict[str, Any]]:
        vec = next(iter(self._embedder.embed([question])))
        try:
            results = self._table.search(vec).limit(limit).to_list()
        except Exception as exc:  # noqa: BLE001
            log.warning("vector query failed: %s", exc)
            return []
        return list(results)


def _merge_dedup(result_lists: list[list[dict[str, Any]]], top_n: int) -> list[dict[str, Any]]:
    """Round-robin merge keyed on vault_path. Stable order, no duplicates."""
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    max_len = max((len(r) for r in result_lists), default=0)
    for i in range(max_len):
        for rl in result_lists:
            if i >= len(rl):
                continue
            row = rl[i]
            vp = row.get("vault_path") or ""
            if not vp or vp in seen:
                continue
            seen.add(vp)
            merged.append(row)
            if len(merged) >= top_n:
                return merged
    return merged


__all__ = [
    "NaiveBM25Backend",
    "LanceDBBackend",
    "default_tokenise",
]
