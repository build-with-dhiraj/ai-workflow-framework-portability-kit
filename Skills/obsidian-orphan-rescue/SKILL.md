---
name: obsidian-orphan-rescue
description: |
  Fix Obsidian orphans at the source. Auto-link orphan notes in any [[wikilink]] markdown vault. Three modes: resolve (deterministic alias-table resolution, $0), anchor (local embedding fallback to nearest existing hub by cosine, $0), and mint (experimental, clusters orphans + mints new concept hubs). Safe-writes contract: frontmatter-only writes, atomic, idempotent, dangling-link guard, per-hub absorption cap, body-only content hash preserved, concepts-only by default. Use when the user asks any of: fix my obsidian orphans, obsidian orphan notes, auto-link my obsidian vault, obsidian unlinked notes, obsidian de-orphan, connect my obsidian notes, obsidian wikilink resolver, obsidian entity resolution, fix obsidian link rot, obsidian auto wikilink, anchor my orphans, obsidian orphan rescuer, rescue obsidian orphans, resolve obsidian entities, fix obsidian dangling links. Works on any markdown vault using [[wikilinks]] (Obsidian, Logseq, Foam, Quartz).
license: MIT
author: Dhiraj Singh Pawar (build-with-dhiraj)
homepage: https://github.com/build-with-dhiraj/obsidian-orphan-rescue
version: 0.1.0
---

# obsidian-orphan-rescue

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

Every other PKM auto-link tool stops here because writing to a vault is dangerous. The orphan-rescue's contract is what makes it safe:

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
obsidian-orphan-rescue resolve --vault ~/Documents/MyVault --dry-run

# Approve, then write.
obsidian-orphan-rescue resolve --vault ~/Documents/MyVault
```

### Anchor mode (local fastembed, $0 after one-time model download)

```bash
# Dry-run writes a per-candidate audit TSV. Review BEFORE the live write.
obsidian-orphan-rescue anchor --vault ~/Documents/MyVault --dry-run

# Live.
obsidian-orphan-rescue anchor --vault ~/Documents/MyVault
```

### Mint mode (EXPERIMENTAL, writes new notes)

```bash
# Always dry-run. The mode writes new hub notes.
obsidian-orphan-rescue mint --vault ~/Documents/MyVault --experimental --dry-run

# Read the audit TSV. Read the minted-cluster names. Then if you approve:
obsidian-orphan-rescue mint --vault ~/Documents/MyVault --experimental
```

## Recommended workflow (with a complementary tool)

1. **Audit first** with `obsidian-graph-auditor` (read-only diagnostic). Find out HOW many orphans you have and what the worst dimension is.
2. **Resolve** with `obsidian-orphan-rescue resolve` to convert plain-string entities to canonical wikilinks.
3. **Anchor** the remaining true orphans with `anchor`.
4. **(Optional, advanced)** Mint hubs for clusters that have no hub yet.
5. **Re-audit** to verify the rubric improved.

## Install

This skill ships in the [obsidian-pkm-skills](https://github.com/build-with-dhiraj/obsidian-pkm-skills) monorepo. You need two things: the `obsidian-orphan-rescue` CLI on your PATH, and the skill files where your agent looks for them.

### 1. Install the CLI

```bash
# Working today (from source). Bare install = resolve mode only ($0, no extras):
pip install "git+https://github.com/build-with-dhiraj/obsidian-pkm-skills#subdirectory=skills/obsidian-orphan-rescue"

# Add the embedding extras for anchor + mint modes ($0, local embeddings):
pip install "obsidian-orphan-rescue[embed] @ git+https://github.com/build-with-dhiraj/obsidian-pkm-skills#subdirectory=skills/obsidian-orphan-rescue"
```

```bash
# Coming shortly, once published to PyPI:
pip install obsidian-orphan-rescue            # resolve mode only
pip install "obsidian-orphan-rescue[embed]"   # + anchor + mint
```

Either way the `obsidian-orphan-rescue` command lands on your PATH.

### 2. Install the skill files

Clone the monorepo once, then copy or symlink this skill's directory into your agent's skills folder. Symlinking lets a `git pull` update the skill in place:

```bash
git clone https://github.com/build-with-dhiraj/obsidian-pkm-skills ~/src/obsidian-pkm-skills

# Claude Code (swap the target for ~/.cursor/skills, ~/.gemini/skills, or ~/.codex/skills):
mkdir -p ~/.claude/skills
ln -s ~/src/obsidian-pkm-skills/skills/obsidian-orphan-rescue ~/.claude/skills/obsidian-orphan-rescue
```

Then ask your agent: *"fix my obsidian orphans at ~/Documents/MyVault"*.

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
