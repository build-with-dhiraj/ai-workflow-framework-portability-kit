---
name: vault-to-manuscript
description: Turns a JoVE HQ vault report (a REPORT-, SYNTH- or stage report under knowledge/) into a PNAS-shaped research manuscript (Significance, Abstract, Introduction, Results, Discussion, Materials and Methods, Data Availability, References) written as prose, with every number traced to its vault source, and lands it as a native Google Doc via tools/jove-drive. Use when Dhiraj asks to write a report "like a paper", "as a manuscript", "in journal format", "for PNAS", or wants a Google Doc version of an experiment report such as Report D.
---

# Vault to manuscript

Project root is `~/dev/jove-hq`. The vault report is the only source of facts; the manuscript may not add a number, a claim or a citation the vault does not hold (CLAUDE.md rule 1). Generic academic-writing craft is the model's own; what this skill fixes is the shape, the provenance and the landing.

## Quick start

```bash
# 1. gather sources (the report plus every stage/audit note it cites)
# 2. write the manuscript as markdown to knowledge/<area>/<slug>/MANUSCRIPT-<slug>-<date>.md
node ~/.claude/skills/vault-to-manuscript/scripts/lint-manuscript.mjs MANUSCRIPT.md --sources REPORT.md STAGE-*.md
# 3. land it as a Google Doc (JoVE Workspace account, GCP project jove-drive-mcp)
node ~/dev/jove-hq/tools/jove-drive/jove-drive-upload-doc.mjs MANUSCRIPT.md "<Title>" [folderId]
```

## Workflow

1. **Classify.** Who reads it (the Director, the Labs team, an external reviewer) and what they do with it. Internal readers still get a real paper, not a memo; a memo is what `writing-for-dhiraj` produces and this skill does not replace it.
2. **Assemble the evidence table before any prose.** One row per number that will appear in the manuscript: value, the vault file and section it comes from, and its bin (observed, derived, assumed). Numbers only from stage reports, per-PI results, audits or hand checks; the vault report's own summary tables count as derived from those. A number with no row does not enter the manuscript.
3. **Outline in the PNAS shape** ([REFERENCE.md](REFERENCE.md) has the section budget and the Report D mapping). Present the outline with the evidence table to Dhiraj before drafting when the reader is external; draft straight away when he asked for the doc.
4. **Draft section by section, prose only.** Third person, past tense for what was done, present tense for what the data show. No bullets in Results or Discussion; tables and figures carry the lists. Figures are described as placeholders ("Fig. 1: ...") with the data file named, never drawn from memory. Cite the vault's external sources (Reports A, B, C; the PNAS reference; MeSH) as numbered references in order of first mention; internal notes go into Data Availability, not the reference list.
5. **Lint.** `scripts/lint-manuscript.mjs` fails on: a missing or misordered section, an em dash, a bulleted list inside Results or Discussion, or a number in the manuscript that appears in none of the `--sources` files. Fix the manuscript, never the sources.
6. **Land.** Upload with `jove-drive-upload-doc.mjs` (Drive converts markdown natively; headings, bold and tables survive). Put the Doc URL in the vault manuscript's frontmatter (`gdoc:`), commit with `Surface: code`, push (standing authorisation). Report the URL and the evidence-table count to Dhiraj.

## Hard rules

- No em dashes. Absolute dates. No engineering internals (file paths, prompts, model names) in the body; they live in Materials and Methods only where a reader needs them to reproduce the study, and in Data Availability.
- Limits and failed checks are written, not softened: the hand-check score, the abstract-only share, anything the plan set as a stop condition.
- A claim about what the product does is cited to a code read or a ticket in the vault, never inferred.
- The manuscript is a new note; the vault report it comes from is not edited.

## Optional depth

For a full peer-review loop or a real submission, the `academic-research-skills` plugin (github.com/imbad0202/academic-research-skills: research, paper, reviewer, pipeline agents) covers style calibration, citation conversion and multi-reviewer critique. It is CC-BY-NC, so check the licence before using it for JoVE work; this skill does not depend on it.
