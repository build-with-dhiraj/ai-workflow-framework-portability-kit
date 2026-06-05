"""Tests for the alias-table builder."""
from __future__ import annotations

from pathlib import Path

from obsidian_orphan_killer.alias_table import build


def test_build_finds_hubs_in_default_dirs(tiny_vault: Path):
    table = build(tiny_vault)
    # 3 hubs total: 2 entities + 1 concept.
    assert table.hub_slugs == {"python", "obsidian", "knowledge-management"}
    assert table.hub_kinds["python"] == "entity"
    assert table.hub_kinds["knowledge-management"] == "concept"


def test_alias_table_resolves_slug_title_and_aliases(tiny_vault: Path):
    """The hard contract: slug + slug-with-spaces + title + aliases all resolve."""
    table = build(tiny_vault)
    # slug
    assert table.resolve("python") == "python"
    # slug-with-spaces (none here, but knowledge-management has it)
    assert table.resolve("knowledge management") == "knowledge-management"
    # title
    assert table.resolve("Knowledge Management") == "knowledge-management"
    # aliases on entity
    assert table.resolve("python3") == "python"
    assert table.resolve("py") == "python"
    # aliases on concept
    assert table.resolve("PKM") == "knowledge-management"
    assert table.resolve("second brain") == "knowledge-management"


def test_alias_table_unknown_returns_none(tiny_vault: Path):
    table = build(tiny_vault)
    assert table.resolve("nothing") is None
    assert table.resolve("") is None


def test_alias_table_custom_hub_dirs(tmp_path: Path):
    """Decoupling: a user with a non-default convention can override hub_dirs."""
    import yaml
    vault = tmp_path / "v"
    (vault / "pages").mkdir(parents=True)
    (vault / "pages" / "foo.md").write_text(
        "---\n" + yaml.safe_dump({"title": "Foo", "aliases": ["the-foo"]}) + "---\n\nhi\n",
        encoding="utf-8",
    )
    table = build(vault, hub_dirs=("pages",))
    assert table.hub_slugs == {"foo"}
    assert table.resolve("the-foo") == "foo"
    assert table.hub_kinds["foo"] == "page"


def test_alias_table_missing_dirs_silently_skipped(tmp_path: Path):
    vault = tmp_path / "v"
    vault.mkdir()
    # No entities/ or concepts/ at all — should still build cleanly.
    table = build(vault)
    assert table.hub_slugs == set()
    assert table.by_norm == {}


def test_alias_table_collision_recorded(tmp_path: Path):
    """Two hubs claiming the same normalized key are recorded as collisions
    instead of silently overwriting. The first hub's claim wins."""
    import yaml
    vault = tmp_path / "v"
    (vault / "concepts").mkdir(parents=True)
    # Two concepts with the same alias.
    (vault / "concepts" / "alpha.md").write_text(
        "---\n" + yaml.safe_dump({"title": "Alpha", "aliases": ["same-alias"]}) + "---\nhi\n",
        encoding="utf-8",
    )
    (vault / "concepts" / "beta.md").write_text(
        "---\n" + yaml.safe_dump({"title": "Beta", "aliases": ["same-alias"]}) + "---\nhi\n",
        encoding="utf-8",
    )
    table = build(vault)
    # The collision was recorded.
    from obsidian_orphan_killer.slug import normalize
    collision_key = normalize("same-alias")
    assert collision_key in table.collisions
    # And the FIRST owner (alpha, alphabetic order) keeps the key.
    assert table.resolve("same-alias") == "alpha"
