"""obsidian-graph-auditor.

Read-only auditor that scores an Obsidian vault on the 8-dimension Grade-A
rubric (link density, orphan rate, near-orphan rate, connected-2plus share,
top-hub edge-share, top-hub:next ratio, Louvain modularity, frontmatter-wikilink
adoption).

Pure Python. No GPT, no API keys, no plugins. Works on any vault that uses
``[[wikilinks]]`` (Obsidian, Logseq, Foam, Quartz, anything markdown-based).
"""
from __future__ import annotations

from obsidian_graph_auditor.auditor import audit, build_graph, render_table
from obsidian_graph_auditor.rubric import (
    DEFAULT_THRESHOLDS,
    GRADES,
    Thresholds,
    grade,
    load_thresholds,
    score,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "audit",
    "build_graph",
    "render_table",
    "DEFAULT_THRESHOLDS",
    "GRADES",
    "Thresholds",
    "grade",
    "load_thresholds",
    "score",
]
