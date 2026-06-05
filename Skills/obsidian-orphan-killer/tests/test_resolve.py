"""Tests for the resolve mode — the deterministic, $0 path."""
from __future__ import annotations

from pathlib import Path

from obsidian_orphan_killer.fm import body_only_hash, split_frontmatter
from obsidian_orphan_killer.resolve import resolve_notes


def _read(path: Path) -> tuple[dict, str]:
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    assert fm is not None
    return fm, body


def test_resolve_dry_run_writes_nothing(tiny_vault: Path):
    """Dry-run must not change any file on disk."""
    src_a = tiny_vault / "sources" / "src-a.md"
    before = src_a.read_text(encoding="utf-8")
    stats = resolve_notes(tiny_vault, dry_run=True)
    after = src_a.read_text(encoding="utf-8")
    assert before == after
    # Stats still report what WOULD have changed.
    assert stats["notes_with_resolution"] == 2  # src-a, src-b (second brain only)
    assert stats["resolved_occurrences"] == 4   # py, python3 in a; second brain in b; PKM in a


def test_resolve_rewrites_plain_strings_to_wikilinks(tiny_vault: Path):
    """The core promise — plain strings -> [[wikilinks]]."""
    stats = resolve_notes(tiny_vault, dry_run=False)
    assert stats["written"] >= 1
    fm_a, _ = _read(tiny_vault / "sources" / "src-a.md")
    assert "[[python]]" in fm_a["entities"]
    assert "[[knowledge-management]]" in fm_a["topics"]


def test_resolve_never_writes_dangling_links(tiny_vault: Path):
    """Unresolvable plain strings stay as plain strings — never minted as
    dangling wikilinks. KEY SAFETY GUARD."""
    resolve_notes(tiny_vault, dry_run=False)
    fm_b, _ = _read(tiny_vault / "sources" / "src-b.md")
    # `unknown-thing` has no hub — must remain a plain string.
    assert "unknown-thing" in fm_b["entities"]
    assert "[[unknown-thing]]" not in fm_b["entities"]


def test_resolve_preserves_existing_wikilinks(tiny_vault: Path):
    """A note that already has [[python]] in its entities must keep it verbatim."""
    resolve_notes(tiny_vault, dry_run=False)
    fm_c, _ = _read(tiny_vault / "sources" / "src-c.md")
    assert "[[python]]" in fm_c["entities"]


def test_resolve_body_hash_preserved(tiny_vault: Path):
    """THE non-negotiable safety contract: body bytes are NEVER modified.

    If this test ever fails, the resolver has broken its core promise and
    every downstream embedder will re-embed every touched note. This MUST hold.
    """
    src_a = tiny_vault / "sources" / "src-a.md"
    _, body_before = split_frontmatter(src_a.read_text(encoding="utf-8"))
    hash_before = body_only_hash(body_before)
    resolve_notes(tiny_vault, dry_run=False)
    _, body_after = split_frontmatter(src_a.read_text(encoding="utf-8"))
    hash_after = body_only_hash(body_after)
    assert hash_before == hash_after, "RESOLVER MUTATED THE BODY — safety contract broken"


def test_resolve_idempotent(tiny_vault: Path):
    """A second run on unchanged notes must skip them (idempotency stamp)."""
    stats1 = resolve_notes(tiny_vault, dry_run=False)
    stats2 = resolve_notes(tiny_vault, dry_run=False)
    assert stats1["written"] >= 1
    # Second run: every previously-resolved note is now skipped.
    assert stats2["skipped"] >= stats1["written"]
    assert stats2["written"] == 0


def test_resolve_stamps_meta(tiny_vault: Path):
    """Every written note gets raw_meta.resolved_at + resolved_hash."""
    resolve_notes(tiny_vault, dry_run=False)
    fm_a, _ = _read(tiny_vault / "sources" / "src-a.md")
    assert "raw_meta" in fm_a
    assert "resolved_at" in fm_a["raw_meta"]
    assert "resolved_hash" in fm_a["raw_meta"]
    assert fm_a["raw_meta"]["resolved_count"] >= 1


def test_resolve_residuals_reported(tiny_vault: Path):
    """The top_residuals report is what users use to decide what to mint next."""
    stats = resolve_notes(tiny_vault, dry_run=True)
    residual_keys = {k for k, _n in stats["top_residuals"]}
    # `unknown-thing` had no hub — it should appear as a residual.
    assert "unknownthing" in residual_keys


def test_resolve_honors_force_flag(tiny_vault: Path):
    """--force re-resolves even stamped notes (useful after an alias change)."""
    resolve_notes(tiny_vault, dry_run=False)
    # Without force, second run skips everything.
    stats_no_force = resolve_notes(tiny_vault, dry_run=False, force=False)
    # With force, second run re-scans them all.
    stats_force = resolve_notes(tiny_vault, dry_run=False, force=True)
    assert stats_force["scanned"] >= stats_no_force["scanned"]
    assert stats_force["skipped"] == 0
