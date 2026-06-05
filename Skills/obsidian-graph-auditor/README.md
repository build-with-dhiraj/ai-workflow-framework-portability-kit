# obsidian-graph-auditor

![Obsidian Graph Auditor: score your second brain on an 8-dimension Grade-A rubric](social-card.png)

> Score your Obsidian vault on an 8-dimension Grade-A rubric. Read-only. Pure Python. No GPT, no API keys. Works in Claude Code, Cursor, Gemini CLI, and Codex.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-21%20passing-brightgreen)](tests/)
[![Cross-CLI](https://img.shields.io/badge/works%20in-Claude%20Code%20%E2%80%A2%20Cursor%20%E2%80%A2%20Gemini%20%E2%80%A2%20Codex-purple)](SKILL.md)

![Before/after 8-dimension scorecard on the bundled demo vault: orphan rate, top-hub edge-share, frontmatter-wikilink adoption, and Louvain modularity climb from failing grades to passing, taking the overall grade from F to D with per-dimension deltas](docs/02-scorecard-before-after.png)

---

## 30-second quickstart

Not on PyPI yet, so install from git and run it against the bundled demo vault:

```bash
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor
cd obsidian-graph-auditor
pip install -e .

obsidian-graph-audit --vault examples/demo-vault
```

That prints a full letter-graded scorecard for the shipped demo vault in well under a second. Point `--vault` at your own vault when you are ready. The tool is read-only and never writes to your notes.

---

## What is the Obsidian Graph Auditor?

`obsidian-graph-auditor` is a command-line tool that **audits your Obsidian vault** and **scores your second brain** on eight dimensions of PKM graph health. It is read-only, pure Python, and does not need GPT, an API key, or an Obsidian plugin. Point it at any markdown directory that uses `[[wikilinks]]` (Obsidian, Logseq, Foam, Quartz) and it returns a letter-graded scorecard backed by expert-cited thresholds.

**What it measures:**
- link density (edges per note)
- orphan rate and near-orphan rate
- connected-2plus share
- top-hub edge-share and top-hub:next ratio
- Louvain modularity
- frontmatter-wikilink adoption

Each dimension grades A-F against a threshold from the network-science and PKM canon (kepano, Matuschak, Ahrens, Konik, Paranyushkin, Milo, Newman). A vault is **Grade A** only if every dimension is A. The worst dimension is the overall grade, by design, so you always see the highest-leverage fix.

---

## Why your Obsidian vault needs an audit

Most Obsidian vaults rot silently. Notes accumulate, links don't, and the graph view becomes a hairball of orphans around one mega-hub. The graph view is great for staring at, but it isn't a measurement. You can't tell from a hairball whether your vault is healthy or whether the entire structure is collapsing around one dominant tag.

Established PKM and network-science work gives us specific thresholds. kepano's "Properties as links" convention puts typed metadata in the graph and expects high frontmatter-wikilink adoption. Andy Matuschak's evergreen-notes practice keeps every note "well-connected on multiple sides": empirically, a link density of 4-10 edges per note. Konik's PKM-as-graph framing treats orphan rate as a capture-to-connection ratio: above 10% means you're collecting faster than you're integrating. Dmitry Paranyushkin's InfraNodus and Newman's modularity work pin the healthy community-structure band at 0.4-0.65. Below 0.4 your vault has no coherent topics; above 0.65 your topics are siloed islands.

An auditor turns those thresholds into a single number: a score, a grade, a CI gate to pass before declaring your second brain Grade A. It answers, with citations: **Is my Obsidian healthy? What's a good orphan rate? How many hubs should a vault have?**

---

## The 8-dimension Grade-A rubric

| # | Dimension | Healthy range | Source |
|---|---|---|---|
| 1 | Link density (edges/note) | 4-10 | network-science consensus; kepano |
| 2 | Orphan rate (degree 0) | < 10% | Konik PKM-as-graph |
| 3 | Near-orphan rate (degree 1) | < 15% | derived complement |
| 4 | Connected ≥2 share | > 75% | derived |
| 5 | Top-hub edge-share | < 5% | power-law avoidance; Milo motifs |
| 6 | Top-hub : next-hub ratio | < 2.0 | concentration check |
| 7 | Louvain modularity | 0.40-0.65 | Newman; Paranyushkin (InfraNodus) |
| 8 | Frontmatter-wikilink adoption | > 80% | kepano "Properties as links" |

Full rationale with citations in [`docs/RUBRIC.md`](docs/RUBRIC.md).

---

## Example output

```
================================================================
  OBSIDIAN VAULT AUDIT - Grade-A Rubric
================================================================
  vault                       /Users/you/Documents/MyVault

  STRUCTURE
    total notes                    3,127
    resolved internal edges       12,548
    link density (edges/note)     4.0128   A

  CONNECTIVITY
    orphans (deg 0)                  375  (12.00%)   B
    near-orphans (deg 1)             437  (13.97%)   A
    connected (deg >=2)            2,315  (74.04%)   B
    frontmatter-wikilink           84.00%  adoption    A

  CONCENTRATION
    top hub                   research
    top-hub edge-share              1.14%   A
    top-hub : next ratio           1.230   A

  COMMUNITY
    Louvain modularity            0.5142   A
    # communities                     27

  OVERALL GRADE              B

  SCORE                      93.75 / 100  (Grade B)
================================================================
```

![Sample scorecard rendered from examples/sample-scorecard.txt](examples/sample-scorecard.png)

A run against a small synthetic fixture vault ships in [`examples/sample-scorecard.txt`](examples/sample-scorecard.txt). The audit finishes in well under a second on a 3,000-note vault.

---

## Real before/after

The tool was developed against a 3,000-note vault used during its own design. Concrete data points from the same vault, before and after one audit-driven cleanup cycle:

| Dimension | Day 1 | After cleanup | Grade Day 1 -> After |
|---|---|---|---|
| Orphan rate | 32.2% | 12.0% | D -> B |
| Top-hub edge-share | 31.4% (force-star) | 1.14% | F -> A |
| Frontmatter-wikilink adoption | 6% | 84% | F -> A |
| Louvain modularity | 0.22 | 0.51 | F -> A |
| Overall grade | F | B | F -> B |

The single largest move came from breaking up one mega-hub: a "research" anchor that captured 31% of all edge-weight in the vault. After de-starring and minting topic-specific hubs, top-hub edge-share dropped to 1.14% and modularity climbed from 0.22 to 0.51. The rubric surfaces this kind of structural fix automatically; you don't have to know to look for it.

---

## How to install

Not published to PyPI yet. Install directly from GitHub.

### From git (any environment)

```bash
pipx install "git+https://github.com/build-with-dhiraj/obsidian-graph-auditor.git"
obsidian-graph-audit --vault ~/Documents/MyVault
```

Prefer a clone you can hack on? `git clone` the repo and `pip install -e .` instead. Either way the `obsidian-graph-audit` command lands on your PATH.

### Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.claude/skills/obsidian-graph-auditor
pip install -e ~/.claude/skills/obsidian-graph-auditor
```

Then ask: *"audit my obsidian vault at ~/Documents/MyVault"*. Claude Code reads `SKILL.md` and invokes the CLI.

### Cursor

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.cursor/skills/obsidian-graph-auditor
pip install -e ~/.cursor/skills/obsidian-graph-auditor
```

### Gemini CLI

```bash
mkdir -p ~/.gemini/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.gemini/skills/obsidian-graph-auditor
pip install -e ~/.gemini/skills/obsidian-graph-auditor
```

### Codex CLI

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/build-with-dhiraj/obsidian-graph-auditor ~/.codex/skills/obsidian-graph-auditor
pip install -e ~/.codex/skills/obsidian-graph-auditor
```

---

## CI gate (block regressions)

Save a baseline. On every PR that touches the vault, fail the build if any rubric dimension regresses:

```bash
# In CI, after checking out the vault repo:
obsidian-graph-audit --vault ./vault --json-out audit.json --baseline last-good.json
# Exit code 1 if any dimension dropped a grade vs last-good.json.
```

A GitHub Actions workflow scaffold is in [`.github/workflows/test.yml`](.github/workflows/test.yml).

---

## How it compares

| | obsidian-graph-auditor | Vault Inspector | Vault Physician | Vault Intelligence | obsidian-graph-query | obsidiantools |
|---|---|---|---|---|---|---|
| Opinionated rubric | yes | no | partial | partial | no | no |
| Expert-cited thresholds | yes | no | no | no | no | no |
| CLI / scriptable | **yes** | npm CLI | no (plugin) | no (plugin) | partial | yes |
| Cross-CLI skill compat | **yes** | no | no | no | partial | no |
| Before/after gate | **yes** | no | no | no | no | manual |
| No GPT / API key | yes | yes | yes | **no** | yes | yes |
| Read-only | yes | yes | partial | partial | yes | yes |
| MIT licensed | yes | varies | varies | varies | varies | yes |
| Logseq/Foam compatible | yes | no | no | no | no | partial |
| Custom thresholds | **yes** | no | no | no | no | n/a |

Full matrix and analysis in [`docs/COMPARISON.md`](docs/COMPARISON.md).

---

## FAQ

### Will this modify my vault?
No. Read-only by design. The auditor only opens files for reading.

### Does it require GPT or any API key?
No. Pure local Python. No network calls.

### What if I use Logseq, Roam, Foam, or Quartz?
Works on any vault that uses `[[wikilinks]]`. The tool reads markdown files plus optional YAML frontmatter and builds the graph from explicit links only.

### How long does it take?
Sub-second for a 3,000-note vault on a modern laptop. The bottleneck is YAML parsing, not graph algorithms.

### What's a "Grade-A" vault?
A vault where every one of the eight rubric dimensions independently grades A. Because the overall grade is the worst dimension, you always see the single most-actionable fix. See [`docs/RUBRIC.md`](docs/RUBRIC.md) for the threshold rationale.

### Can I customize the thresholds?
Yes. Pass `--threshold-config thresholds.yaml` with any subset of dimensions overridden. Example:

```yaml
orphan_pct:
  a: 15.0
  b: 25.0
  c: 35.0
  d: 45.0
```

### Why don't I just look at the Obsidian Graph view?
The Graph view shows you a hairball. It doesn't measure orphan rate, modularity, or hub concentration. You can't tell whether your vault is rotting by squinting at it. The auditor gives you a number.

### Can I run this in CI?
Yes. The `--baseline previous.json` flag exits non-zero on regression. See [CI gate](#ci-gate-block-regressions) above.

---

## Documentation

- [`SKILL.md`](SKILL.md): Cross-CLI skill manifest (Claude Code, Cursor, Gemini CLI, Codex)
- [`docs/RUBRIC.md`](docs/RUBRIC.md): The 8-dimension Grade-A rubric, with citations
- [`docs/COMPARISON.md`](docs/COMPARISON.md): Feature matrix vs other vault tools
- [`docs/GRAPH-ANALYSIS.md`](docs/GRAPH-ANALYSIS.md): Deep-dive on graph analysis and orphan remediation
- [`CHANGELOG.md`](CHANGELOG.md): Release history
- [`CONTRIBUTING.md`](CONTRIBUTING.md): How to file issues, run tests, propose new dimensions

---

## License

MIT, Copyright (c) 2026 Dhiraj Singh Pawar.

---

## Credits

Built by [Dhiraj Singh Pawar](https://github.com/build-with-dhiraj). Engine derived from real audit work on a 3,000-note vault and adapted to be tool-agnostic. Threshold rationale draws on published work by kepano (`obsidian-skills`), Andy Matuschak (`evergreen notes`), Sönke Ahrens (`How to Take Smart Notes`), Dmitry Paranyushkin (`InfraNodus`), Mark Newman (modularity / community detection), and Ron Milo (network motifs).
