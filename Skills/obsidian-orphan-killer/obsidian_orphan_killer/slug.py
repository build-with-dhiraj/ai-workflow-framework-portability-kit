"""Slug + normalize helpers.

These define the SAME loose-grouping key the alias table uses. Two surface
forms are considered the same key iff ``_normalize(a) == _normalize(b)``, so
``Open AI`` / ``open-ai`` / ``openai`` all collapse onto ``openai``.

Decoupled from any vault-specific assumption: a slug is just a lowercase
hyphenated identifier, and ``_normalize`` strips the hyphens to make the loose
key. Mirrors the convention used by most ``[[wikilink]]`` PKM tools.
"""
from __future__ import annotations

import re

_UNSAFE_RE = re.compile(r"[^a-z0-9\-]+")
_COLLAPSE_RE = re.compile(r"-{2,}")


def slugify(name: str) -> str:
    """Lowercase-hyphen slug. Stable across the project; used for hub filenames."""
    s = name.strip().lower().replace("_", "-").replace(" ", "-").replace(".", "-")
    s = _UNSAFE_RE.sub("-", s)
    s = _COLLAPSE_RE.sub("-", s)
    return s.strip("-")


def normalize(name: str) -> str:
    """Loose canonical key for grouping variants.

    Strips hyphens so ``open-ai`` and ``openai`` share the same key. This is the
    alias-table lookup key.
    """
    return slugify(name).replace("-", "")
