---
name: obsidian-orphan-killer
description: |
  Fix Obsidian orphans at the source. Auto-link orphan notes in any [[wikilink]] markdown vault. Three modes: resolve (deterministic alias-table resolution, $0), anchor (local embedding fallback to nearest existing hub by cosine, $0), and mint (experimental, clusters orphans + mints new concept hubs). Safe-writes contract: frontmatter-only writes, atomic, idempotent, dangling-link guard, per-hub absorption cap, body-only content hash preserved, concepts-only by default. Use when the user asks any of: fix my obsidian orphans, obsidian orphan notes, auto-link my obsidian vault, obsidian unlinked notes, obsidian de-orphan, connect my obsidian notes, obsidian wikilink resolver, obsidian entity resolution, fix obsidian link rot, obsidian auto wikilink, anchor my orphans, obsidian orphan rescuer, rescue obsidian orphans, resolve obsidian entities, fix obsidian dangling links. Works on any markdown vault using [[wikilinks]] (Obsidian, Logseq, Foam, Quartz).
license: MIT
author: Dhiraj Singh Pawar (build-with-dhiraj)
homepage: https://github.com/build-with-dhiraj/obsidian-orphan-killer
version: 0.1.0
---

# obsidian-orphan-killer

Fix Obsidian orphans at the source. Auto-link orphan notes in any markdown vault that uses `[[wikilinks]]`. Frontmatter-only writes. Atomic. Idempotent.

## When to use this skill

Trigger this skill whenever the user wants to:

1. **Fix orphans, not just list them.** Every other tool lists orphans; this one auto-fixes them with safety guards.
2. **Resolve plain-string entities to wikilinks.** A note tagged `entities: [Microscopy]` should become `entities: [[[microscopy]]]` if a `microscopy` hub exists.
3. **De-orphan a leaf.** Attach a true orphan to its single best matching existing hub by embedding cosine.
4. **Mint hubs for coherent orphan clusters** (experimental). For clusters of >= 5 orphans about the same topic, create a new concept hub and anchor them to it.

## The three modes

| Mode | What it does | Network? | Writes new notes? |
|---|---|---|---|
| `resolve` | Plain-string entities/topics → canonical `[[wikilinks]]` via alias table | No | No |
| `anchor`  | True-orphan leaves → nearest existing hub by cosine similarity | No (local fastembed) | No |
| `mint`    | Cluster orphans → mint new concept hubs (EXPERIMENTAL) | LLM naming call | YES (new hubs) |

## Safety guards (read this first)

Every other PKM auto-link tool stops here because writing to a vault is dangerous. The orphan-killer's contract is what makes it safe:

- **Frontmatter-only writes.** Body bytes are never modified.
- **Atomic writes.** tempfile + os.rename, crash-safe; no partial writes.
- **Body-only content hash preserved.** Downstream embedders never re-embed.
- **Idempotency stamps.** A second run on unchanged notes is a no-op.
- **Dangling-link guard.** Only links to hubs that exist on disk.
- **Per-hub absorption cap.** No single hub can absorb more than N orphans per run (anti-star).
- **Concepts-only target set by default.** Generic how-tos never anchor to brand entity hubs (the brand-leak guard).
- **DO_NOT_MERGE pairs.** User can supply pairs that look similar but must never collapse (e.g. `claude-ai` vs `claude-code`).
- **Mint mode requires `--experimental`.** It writes NEW notes; never enabled by accident.

Every guard has a test in `tests/` that locks it in.

## How to run

### Resolve mode (deterministic, $0)

```bash
# Dry-run first. ALWAYS dry-run first.
obsidian-orphan-killer resolve --vault ~/Documents/MyVault --dry-run

# Approve, then write.
obsidian-orphan-killer resolve --vault ~/Documents/MyVault
```

### Anchor mode (local fastembed, $0 after one-time model download)

```bash
# Dry-run writes a per-candidate audit TSV. Review BEFORE the live write.
obsidian-orphan-killer anchor --vault ~/Documents/MyVault --dry-run

# Live.
obsidian-orphan-killer anchor --vault ~/Documents/MyVault
```

### Mint mode (EXPERIMENTAL, writes new notes)

```bash
# Always dry-run. The mode writes new hub notes.
obsidian-orphan-killer mint --vault ~/Documents/MyVault --experimental --dry-run

# Read the audit TSV. Read the minted-cluster names. Then if you approve:
obsidian-orphan-killer mint --vault ~/Documents/MyVault --experimental
```

## Recommended workflow (with a complementary tool)

1. **Audit first** with `obsidian-graph-auditor` (read-only diagnostic). Find out HOW many orphans you have and what the worst dimension is.
2. **Resolve** with `obsidian-orphan-killer resolve` to convert plain-string entities to canonical wikilinks.
3. **Anchor** the remaining true orphans with `anchor`.
4. **(Optional, advanced)** Mint hubs for clusters that have no hub yet.
5. **Re-audit** to verify the rubric improved.

## Install

### Claude Code

```bash
pip install obsidian-orphan-killer
# Optional embedding extras for anchor + mint modes:
pip install 'obsidian-orphan-killer[embed]'
mkdir -p ~/.claude/skills
git clone https://github.com/build-with-dhiraj/obsidian-orphan-killer ~/.claude/skills/obsidian-orphan-killer
```

Then ask Claude Code: *"fix my obsidian orphans at ~/Documents/MyVault"*.

### Cursor

```bash
pip install obsidian-orphan-killer
mkdir -p ~/.cursor/skills
git clone https://github.com/build-with-dhiraj/obsidian-orphan-killer ~/.cursor/skills/obsidian-orphan-killer
```

### Gemini CLI

```bash
pip install obsidian-orphan-killer
mkdir -p ~/.gemini/skills
git clone https://github.com/build-with-dhiraj/obsidian-orphan-killer ~/.gemini/skills/obsidian-orphan-killer
```

### Codex CLI

```bash
pip install obsidian-orphan-killer
mkdir -p ~/.codex/skills
git clone https://github.com/build-with-dhiraj/obsidian-orphan-killer ~/.codex/skills/obsidian-orphan-killer
```

## What it does NOT do

- It does **not** modify your note bodies. Frontmatter-only writes.
- It does **not** write dangling links. Targets must exist on disk.
- It does **not** force a noisy match. Below the cosine floor, orphans stay unlinked.
- It does **not** require GPT for resolve or anchor (`$0`). Only mint mode uses an LLM call.
- It does **not** require an Obsidian plugin install. Pure CLI.
- It does **not** require Obsidian to be installed at all. Works on any markdown directory with wikilinks.

## Related

- Safety contract with recovery instructions: [`docs/SAFETY.md`](docs/SAFETY.md)
- The formal guard spec: [`docs/RUBRIC.md`](docs/RUBRIC.md)
- Feature comparison vs Find Unlinked Files / Various Complements / Janitor / Dangling Links / Smart Connections: [`docs/COMPARISON.md`](docs/COMPARISON.md)
- Companion diagnostic tool: [obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor). Audit first, fix second.
