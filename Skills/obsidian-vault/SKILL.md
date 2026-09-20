---
name: obsidian-vault
description: Superseded by vault-recall. Mechanical file-level lookup in the JoVE HQ vault at ~/dev/jove-hq/knowledge - locating a note by filename or path when you already know what you are looking for. Do NOT use for recall, decisions, ownership, history, cross-linking, or grilling; vault-recall owns all of those and is the skill to invoke.
---

# Obsidian Vault (JoVE HQ) - mechanical lookup only

**`vault-recall` is the skill for this vault.** It recalls, cross-links, and grills, and it is the
one to invoke for any question about what the vault says. This file covers only the mechanical
case: finding a file when you already know roughly what it is called.

Scope is `~/dev/jove-hq/knowledge` and nothing else. Read-only.

## Locate a note

```bash
V=~/dev/jove-hq/knowledge

# by filename, excluding the scraped corpus (8,718 of ~11,200 notes)
find "$V" -name "*.md" -not -path "*/youtube-academia-corpus/*" | grep -i "keyword"

# by content, signal directories only
grep -rl "keyword" "$V/jove-labs" "$V/meetings" "$V/memory" "$V/entities" --include="*.md"
```

Filenames are kebab-case with a `-YYYY-MM-DD` suffix on anything time-bound, and a SCREAMING
prefix marking kind in `jove-labs/`: `HANDOVER-`, `ANSWER-`, `METRICS-`, `TICKET-DRAFT-`,
`OUTBOX-`, `TODAY-PLAN-`. Grep and Glob tools work directly on these paths and are faster.

## Vault shape

Root holds one note, `HOME.md`. Everything else sits 2-3 levels down under 13 directories:
`youtube-academia-corpus/` 8718 (scraped corpus), `jove-labs/` 923, `archive-export/` 906,
`vault-dumps/` 186, `meetings/` 175, `copilot/` 170, `entities/` 90, `memory/` 31, and
`inbox/ research-metrics/ parity/ cowork/ vault-extras/` under 20 each.

## Anything else

Hand off to **`vault-recall`**: questions, decisions, ownership, history, backlinks, hub and MOC
navigation, contradictions, grilling. Writing notes is out of scope for both - see
`obsidian-markdown` for authoring and `obsidian-cli` for CLI operations.
