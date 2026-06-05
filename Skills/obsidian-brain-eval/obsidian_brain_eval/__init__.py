"""obsidian-brain-eval — measure Recall@10 of any retrieval system over an Obsidian vault.

Public API:
    from obsidian_brain_eval import generate, score, render_score
    from obsidian_brain_eval.backends import NaiveBM25Backend, LanceDBBackend, RetrievalBackend
"""
from __future__ import annotations

__version__ = "0.1.0"

from obsidian_brain_eval.eval import (
    generate,
    load_gold,
    render_score,
    score,
)

__all__ = [
    "__version__",
    "generate",
    "load_gold",
    "render_score",
    "score",
]
