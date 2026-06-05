"""Tests for the safety guards — lexical, URL fragment, DO_NOT_MERGE."""
from __future__ import annotations

from obsidian_orphan_killer.guards import (
    CLUSTER_GENERIC_DENY,
    TOPIC_DENYLIST,
    is_forbidden_pair,
    is_url_fragment,
    lexical_guard_passes,
    proposed_name_is_clean,
)
from obsidian_orphan_killer.slug import normalize


def test_lexical_guard_substring():
    assert lexical_guard_passes("Python", "Python 3")
    assert lexical_guard_passes("OpenAI", "Open AI")


def test_lexical_guard_blocks_unrelated():
    """KEY: cosine alone is not enough — lexical guard must catch this."""
    assert not lexical_guard_passes("OpenAI", "Anthropic")
    assert not lexical_guard_passes("apple", "banana")


def test_lexical_guard_shared_token():
    assert lexical_guard_passes("graph theory", "discrete graph")


def test_url_fragment_detects_domains():
    assert is_url_fragment("app.jove.com")
    assert is_url_fragment("https://example.com/foo")
    assert is_url_fragment("www.foo.com")
    assert is_url_fragment("foo.io")


def test_url_fragment_allows_normal_names():
    assert not is_url_fragment("Knowledge Management")
    assert not is_url_fragment("artificial intelligence ai")
    assert not is_url_fragment("Python")


def test_do_not_merge_user_pairs():
    """Users supply DO_NOT_MERGE pairs that look similar but are distinct."""
    do_not_merge = [
        frozenset({normalize("claude-ai"), normalize("claude-code")}),
    ]
    assert is_forbidden_pair(normalize("claude-ai"), normalize("claude-code"),
                             do_not_merge)
    # Other pairs are fine.
    assert not is_forbidden_pair(normalize("foo"), normalize("bar"), do_not_merge)


def test_proposed_name_clean_passes_real_topics():
    """The mint guard should ACCEPT a real specific subject."""
    ok, reason = proposed_name_is_clean("Protein Crystallization")
    assert ok, reason
    ok, _ = proposed_name_is_clean("Knowledge Management")
    assert ok


def test_proposed_name_rejects_denylist():
    """The mint guard must REJECT generic catch-alls."""
    ok, reason = proposed_name_is_clean("Technology")
    assert not ok and "denylist" in reason.lower()


def test_proposed_name_rejects_generic_cluster_words():
    """The mint guard's CLUSTER_GENERIC_DENY backstop must fire."""
    for bad in ("Science", "Videos", "Knowledge", "Podcasts"):
        ok, reason = proposed_name_is_clean(bad)
        assert not ok, f"{bad!r} should not pass: got {reason}"


def test_proposed_name_rejects_url_fragments():
    ok, _ = proposed_name_is_clean("app.jove.com")
    assert not ok


def test_proposed_name_rejects_empty():
    ok, _ = proposed_name_is_clean("")
    assert not ok
    ok, _ = proposed_name_is_clean("   ")
    assert not ok


def test_denylists_are_well_formed():
    """Sanity: every denylist key is a non-empty lowercase string."""
    for s in TOPIC_DENYLIST:
        assert isinstance(s, str) and s and s.lower() == s
    for s in CLUSTER_GENERIC_DENY:
        assert isinstance(s, str) and s
