# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-03

### Added
- Initial public release.
- Core auditor (`obsidian_graph_auditor.auditor`) computing 8-dimension Grade-A rubric:
  link density, orphan rate, near-orphan rate, connected-2plus share, top-hub edge-share,
  top-hub:next-hub ratio, Louvain modularity, frontmatter-wikilink adoption.
- 8-dimension rubric (`obsidian_graph_auditor.rubric`) with A-F letter grades and a
  0-100 GPA score. Defaults from network-science + PKM canon (kepano, Matuschak,
  Konik, Paranyushkin, Milo, Newman).
- CLI (`obsidian-graph-audit`) with `--vault`, `--json-out`, `--threshold-config`,
  `--baseline`, `--top`, `--quiet`, `--no-grade`.
- Cross-CLI `SKILL.md` for Claude Code, Cursor, Gemini CLI, and Codex.
- Three docs pages: `docs/RUBRIC.md`, `docs/COMPARISON.md`, `docs/GRAPH-ANALYSIS.md`.
- `llms.txt` for AI crawlers.
- GitHub Actions test workflow.
- Issue templates (bug + feature).
- 21 tests across auditor, rubric, and CLI.

### Bug fixes (carried over from upstream prototype)
- Wikilink `[[Target|Display Alias]]` was incorrectly parsing the *display* segment
  as the target. Now correctly extracts the first segment as target; strips
  section anchors (`#`) and block references (`^`).
- Empty-metrics `grade({})` now returns overall `F` instead of accidentally
  returning `A` via the `top_hub_next_ratio is None` shortcut.
