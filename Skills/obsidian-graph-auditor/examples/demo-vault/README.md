# demo-vault (messy by design)

A small, deliberately messy public Obsidian vault used as the "before" state
in the obsidian-graph-auditor walkthrough. It contains:

- a handful of `concepts/` and `entities/` hub notes
- `sources/` and `inbox/` notes whose `entities:` / `topics:` frontmatter are
  still plain strings (not yet `[[wikilinks]]`)
- several true orphan notes (no links in or out)
- one deliberately over-connected hub (PARA method) that many notes reference

All content is generic public PKM material. Run:

    obsidian-graph-audit --vault examples/demo-vault

to score it, then use obsidian-orphan-killer `resolve` to convert the
plain-string entities/topics into wikilinks and re-audit the "after" state.
