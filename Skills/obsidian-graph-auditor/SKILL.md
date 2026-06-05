---
name: obsidian-graph-auditor
description: |
  Audit Obsidian vault, score second brain, and grade PKM graph health on an 8-dimension Grade-A rubric. Pure Python CLI, read-only, no GPT or API keys. Measures link density, orphan rate, near-orphan rate, connected-2plus share, top-hub edge-share, top-hub:next ratio, Louvain modularity, and frontmatter-wikilink adoption against expert-cited thresholds (kepano, Matuschak, Ahrens, Konik, Paranyushkin, Milo). Use when the user asks any of: audit my obsidian vault, score my obsidian, is my obsidian healthy, is my second brain healthy, score my pkm graph, obsidian vault review, obsidian graph analysis, measure my obsidian, find orphans in my obsidian vault, obsidian orphans, cross-linking review, obsidian graph health check, grade my pkm, obsidian vault quality, obsidian scorecard, zettelkasten audit, second brain audit, why is my vault rotting, pkm metrics, atomic notes review. Works on any markdown vault using wikilinks (Obsidian, Logseq, Foam, Quartz).
license: MIT
author: Dhiraj Singh Pawar (build-with-dhiraj)
homepage: https://github.com/build-with-dhiraj/obsidian-graph-auditor
version: 0.1.0
---

# Obsidian Graph Auditor

Score an Obsidian vault on the 8-dimension Grade-A rubric. Read-only. Pure Python. No GPT, no API keys.

## When to use this skill

Trigger this skill whenever the user wants to:

1. **Audit a vault.** "audit my obsidian vault", "is my obsidian healthy", "is my second brain healthy"
2. **Find orphans.** "find orphans in my vault", "obsidian orphans", "show me unconnected notes"
3. **Diagnose a mega-hub.** "is my vault a force-star?", "top-hub edge-share", "vault concentration"
4. **Grade community structure.** "Louvain modularity", "community detection", "are my clusters siloed?"
5. **Establish a CI gate.** Use `--baseline` to fail CI when a vault regresses.
6. **Compare before/after.** Run twice across a refactor to prove improvement.
7. **Decide what to fix first.** The rubric's worst dimension is the highest-leverage fix.

## What it measures (the 8 dimensions)

| # | Dimension | Healthy range | Why |
|---|---|---|---|
| 1 | Link density (edges/note) | 4-10 | network-science consensus, kepano "Properties as links" |
| 2 | Orphan rate (deg 0) | < 10% | Konik PKM-as-graph |
| 3 | Near-orphan rate (deg 1) | < 15% | derived complement of orphan threshold |
| 4 | Connected ≥2 share | > 75% | derived, most notes should be actually integrated |
| 5 | Top-hub edge-share | < 5% | power-law avoidance, Milo motifs |
| 6 | Top-hub : next-hub ratio | < 2.0 | healthy power-law tail |
| 7 | Louvain modularity | 0.4-0.65 | Newman / Paranyushkin (InfraNodus) |
| 8 | Frontmatter-wikilink adoption | > 80% | kepano typed-metadata convention |

A vault is **Grade A** only if every dimension grades A. The worst dimension is the overall grade, by design, so you always see the highest-leverage fix.

## How to run

After installation (see `## Install` below):

```bash
# Default: audits ./vault if present, else the current directory.
obsidian-graph-audit

# Explicit vault path with JSON dump (useful for CI).
obsidian-graph-audit --vault ~/Documents/MyVault --json-out audit.json

# CI gate: fail (exit 1) if any dimension regresses vs the baseline.
obsidian-graph-audit --vault ~/Documents/MyVault --baseline last-audit.json

# Custom thresholds for non-default styles (e.g. heavier orphan tolerance).
obsidian-graph-audit --vault ~/Documents/MyVault --threshold-config my-rubric.yaml
```

Default exit codes:

- `0`: audit ran cleanly (and matched/exceeded baseline, if supplied)
- `1`: at least one dimension regressed vs baseline
- `2`: vault path missing or unreadable

## How to read the output

The scorecard has 5 sections:

- **STRUCTURE**: total notes, edges, link density. If density < 1.5 you have a capture-heavy vault that isn't connecting.
- **CONNECTIVITY**: orphan + near-orphan + connected-2plus percentages. The headline metric.
- **CONCENTRATION**: top-hub edge-share + top:next ratio. High values = force-star.
- **COMMUNITY**: Louvain modularity. < 0.3 = no coherent clusters; > 0.75 = siloed islands.
- **TOP HUBS / TOP BRIDGES**: the high-influence notes. Useful for "what should I de-star?" or "what's a connector worth protecting?"

## Install

### Claude Code

```bash
pip install obsidian-graph-auditor
mkdir -p ~/.claude/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.claude/skills/obsidian-graph-auditor
```

Then ask Claude Code: "audit my obsidian vault at ~/Documents/MyVault".

### Cursor

```bash
pip install obsidian-graph-auditor
mkdir -p ~/.cursor/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.cursor/skills/obsidian-graph-auditor
```

### Gemini CLI

```bash
pip install obsidian-graph-auditor
mkdir -p ~/.gemini/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.gemini/skills/obsidian-graph-auditor
```

### Codex CLI

```bash
pip install obsidian-graph-auditor
mkdir -p ~/.codex/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.codex/skills/obsidian-graph-auditor
```

## What it does NOT do

- It does **not** modify your vault. Read-only by design.
- It does **not** call GPT, Claude, or any other LLM. Pure local Python.
- It does **not** rewrite your notes, change frontmatter, or move files.
- It does **not** require an Obsidian plugin install. Pure CLI.
- It does **not** require Obsidian to be installed at all. Works on any markdown directory with wikilinks.

## Related

- Full rubric with citations: `docs/RUBRIC.md`
- Comparison vs Vault Inspector / Vault Physician / Vault Intelligence / obsidiantools / obsidian-graph-query: `docs/COMPARISON.md`
- Deep-dive on graph analysis and orphan remediation: `docs/GRAPH-ANALYSIS.md`
