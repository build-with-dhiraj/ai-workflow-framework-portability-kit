# How obsidian-graph-auditor Compares

> Feature matrix and qualitative comparison against the established Obsidian-vault tooling. Updated 2026-06.

The Obsidian-vault tooling space has matured rapidly in the last 18 months. The auditor is not a replacement for those tools, it is the missing **opinionated CLI** that grades a vault against expert-cited thresholds and runs in any agentic CLI. This page is where to read about the trade-offs.

---

## Feature matrix

| Feature | obsidian-graph-auditor | [Vault Inspector](https://www.obsidianstats.com/plugins/vault-inspector) | [Vault Physician](https://obsidian.md/plugins?id=vault-physician) | [Vault Intelligence](https://www.obsidianstats.com/plugins/vault-intelligence) | [obsidian-graph-query](https://forum.obsidian.md/t/obsidian-graph-query-let-your-ai-agent-query-your-vaults-knowledge-graph-bfs-shortest-path-bridges-hubs-orphans/111828) | [obsidiantools](https://github.com/mfarragher/obsidiantools) | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) |
|---|---|---|---|---|---|---|---|
| Opinionated 8-dim rubric | yes | no | partial | partial | no | no | partial |
| Expert-cited thresholds | yes | no | no | no | no | no | no |
| CLI / scriptable | **yes** | npm CLI | no (plugin) | no (plugin) | partial | yes (lib) | no (skills) |
| Cross-CLI skill compat | **yes** | no | no | no | partial | no | yes (Claude) |
| Before / after CI gate | **yes** | no | no | no | no | manual | no |
| No GPT / API key | yes | yes | yes | **no** | yes | yes | varies |
| Read-only | yes | yes | partial (one-click fix) | partial (writes notes) | yes | yes | varies |
| Open source MIT | yes | varies | varies | varies | varies | yes | yes |
| Logseq / Foam / Quartz | yes | no | no | no | partial | partial | no |
| Custom thresholds | **yes** | no | no | no | no | n/a | no |
| Markdown + wikilink only (no Obsidian required) | yes | no | no | no | no | yes | partial |
| Modularity + community detection | yes | no | no | no | yes | partial | no |

---

## When to use each

### Use **obsidian-graph-auditor** when you want:
- A **single number** for vault health and a graded report with citations.
- A **CI gate** that fails when a vault regresses.
- A **scriptable command-line** workflow that runs in any agentic CLI (Claude Code, Cursor, Gemini, Codex).
- **Custom thresholds** for your style (zettelkasten, digital garden, lab notebook).
- A **tool-agnostic** check that works on Logseq, Foam, Quartz, and any markdown-with-wikilinks directory.

### Use **Vault Inspector** when you want:
- A **fast, in-app dashboard** that surfaces broken links, orphan attachments, duplicate files, and unused tags.
- A maintenance UI that lives where you live (the Obsidian sidebar).
- Vault Inspector and the auditor are **complementary**: Inspector finds the broken-link surface issues; the auditor grades the underlying graph.

### Use **Vault Physician** when you want:
- A **continuous dashboard** with decay scanners and frontmatter linters.
- **One-click fixes** without leaving Obsidian.
- Tradeoff: Vault Physician is plugin-only, has no opinionated rubric, and isn't scriptable in CI.

### Use **Vault Intelligence** when you want:
- An **LLM-augmented** vault that cross-references your writing with live web search.
- A "Gardener agent" that suggests new notes and links via GPT.
- Tradeoff: requires an LLM key, mutates your vault, isn't free, and doesn't grade against fixed thresholds.

### Use **obsidian-graph-query** when you want:
- An **AI-agent skill** for querying graph topology via natural language.
- BFS, shortest path, bridges, hubs, orphans, but as on-demand answers, not a graded report.
- Tradeoff: forum-distributed skill, not a polished installable, no rubric.

### Use **obsidiantools** when you want:
- A **Python library** for programmatic vault analysis with pandas DataFrames.
- Full control over the analysis pipeline; you bring your own metrics.
- Tradeoff: no CLI, no rubric, no agentic-CLI integration.

### Use **kepano/obsidian-skills** when you want:
- A collection of **stylistic and convention skills** for Claude Code (note structure, frontmatter conventions).
- **The "Properties as links" convention** which the auditor's dimension 8 directly measures.
- Tradeoff: kepano's skills don't audit; they advise. Run obsidian-graph-auditor after applying kepano's conventions to measure adoption.

---

## What the auditor does NOT replace

- **Vault Inspector / Vault Physician** for surface maintenance (broken links, orphan attachments, large files, duplicate filenames). The auditor measures graph topology, not housekeeping.
- **obsidiantools** for custom analyses outside the 8 dimensions. If you need a notebook to slice your vault by tag, by created-date, or by custom heuristics, obsidiantools is the right primitive.
- **kepano/obsidian-skills** for *how* to structure a healthy vault. The auditor measures whether your vault is healthy after you've structured it.

A reasonable workflow:

1. Apply kepano conventions to your vault.
2. Run obsidian-graph-auditor for a baseline scorecard.
3. Identify the worst dimension and use Vault Inspector / Vault Physician for surface remediation, or a custom obsidiantools notebook for deeper diagnostics.
4. Re-run the auditor as the gate that says "you fixed it".

---

## Why this tool exists

The Obsidian-tooling ecosystem has *measurement* (Vault Inspector, obsidiantools), *automation* (Vault Physician, Vault Intelligence), and *advice* (kepano/obsidian-skills), but nothing in between. There was no **rubric-based grade** with **cited thresholds** that ran from the command line and worked across Claude Code, Cursor, Gemini CLI, and Codex. The auditor fills that gap.

The auditor is also the **only tool in this list that you can run on a non-Obsidian vault** (Logseq, Foam, Quartz, or any markdown-with-wikilinks directory), because the underlying graph model and the rubric are tool-agnostic.
