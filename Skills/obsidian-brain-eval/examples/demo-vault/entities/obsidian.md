---
title: Obsidian
type: entity
related:
  - "[[information-retrieval]]"
  - "[[rag]]"
---

# Obsidian

Obsidian is a personal knowledge management tool built around plain markdown
files, `[[wikilinks]]`, YAML frontmatter, and a community of plugin authors who
turn the vault into an extensible second brain. The graph view that ships in
the app is one of the most-shared screenshots in PKM, but the graph itself is
underused as a measurement surface.

This skill treats an Obsidian vault as the corpus of an information-retrieval
system and asks: "if you built a chat-with-my-vault feature, would the
retrieval layer actually return the right note?" The answer is measured in
Recall@10 against a gold-set generated from the vault itself.

The skill works on any markdown vault that uses `[[wikilinks]]` - Obsidian,
Logseq, Foam, Quartz. Obsidian is the most common reference point but the
machinery is tool-agnostic.
