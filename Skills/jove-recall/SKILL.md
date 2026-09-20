---
name: jove-recall
description: SUPERSEDED 20 Aug 2026 — do not invoke for recall. Pinecone jove-memory is frozen (15 Aug 2026 decision, CLAUDE.md rule 16) and receives no writes; querying it returns stale answers by design. All recall questions route to the vault-recall skill (ledger-ask.mjs full-ledger read + lexical over the vault). This stub exists only so /jove-recall out of habit lands on the redirect instead of a dead index.
---

# Superseded

This skill queried Pinecone `jove-memory`. That index was frozen on 15 Aug 2026 (readable by id/vector, no new writes, mirror stale by design — CLAUDE.md rule 16; the 15 Aug "reinstated" addendum that used to live here was itself superseded by the freeze decision later that day).

**Use the `vault-recall` skill instead** (`~/.claude/skills/vault-recall/SKILL.md`). It wraps `~/dev/jove-hq/tools/sweep/ledger-ask.mjs`: whole-ledger read for Labs questions, `--corpus` exhaustive shard-read for primary sources, lexical search over the git-committed vault for everything else. Cite-or-abstain unchanged.

The routing rules that were mechanism-independent (metrics → stakeholder-artifacts registry; work-state → Linear continuation tracker) moved into vault-recall. Nothing else here is current.
