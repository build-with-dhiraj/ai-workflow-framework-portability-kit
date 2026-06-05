"""Tests for slug + normalize helpers."""
from __future__ import annotations

from obsidian_orphan_killer.slug import normalize, slugify


def test_slugify_basic():
    assert slugify("Open AI") == "open-ai"
    assert slugify("python_3") == "python-3"
    assert slugify("Microsoft.Excel") == "microsoft-excel"


def test_slugify_strips_unsafe():
    assert slugify("foo / bar !! baz") == "foo-bar-baz"
    assert slugify("--leading--and--trailing--") == "leading-and-trailing"


def test_normalize_collapses_variants():
    """The KEY property: variants of the same name collapse to the same key."""
    assert normalize("Open AI") == normalize("open-ai") == normalize("openai")
    assert normalize("Python 3") == normalize("python3") == normalize("python-3")
    assert normalize("Knowledge Management") == normalize("knowledge-management")


def test_normalize_distinguishes_real_distinctions():
    """Strings that are genuinely different MUST get different keys."""
    assert normalize("Claude AI") != normalize("Claude Code")
    assert normalize("JoVE") != normalize("JoVE Labs")


def test_slugify_empty():
    assert slugify("") == ""
    assert slugify("   ") == ""
    assert normalize("") == ""
