# PNAS shape and the Report D mapping

Reference paper: Zeng, Fan, Di, Wang, Havlin, "Impactful scientists have higher tendency to involve collaborators in new topics", PNAS 119(33), 8 Aug 2022, doi:10.1073/pnas.2207436119 (open, PMC9388131). About 8,900 words, 6 figures, 0 tables, 37 references. Sections in order: Significance, Abstract, (untitled introduction), Results with sub-headings, Discussion, Materials and Methods with sub-headings (Data; each measure; the surrogate control), Data Availability, Acknowledgments, References, Supplementary Material.

## Section budget (target for a Report D sized study)

| Section | Words | What goes in |
|---|---|---|
| Title | 15 | The finding, not the topic |
| Significance | 120 | Why a reader outside the field should care, plain words |
| Abstract | 250 | Question, data, method, main numbers, one implication |
| Introduction | 600 to 800 | The question, what is known (Reports A, B, C as prior work), the gap, what this study did |
| Results | 1,500 to 2,500 | Sub-heading per measure; every number with its uncertainty; one figure or table per sub-heading |
| Discussion | 800 to 1,200 | What the numbers mean, agreement and disagreement with prior work, limits, implications for design |
| Materials and Methods | 800 to 1,200 | Sample frame, data sources, reading rule, extraction and normalisation, measures, statistical bounds, versions |
| Data Availability | 100 | Where the per-PI results, dictionary, prompts and logs live |
| References | as needed | Numbered, order of first mention |

## Report D mapping

| Manuscript section | Vault sources (knowledge/jove-labs/method-experiment/) |
|---|---|
| Significance, Abstract | REPORT-D section 1 |
| Introduction | ../research-methods-2026-09-29/CRUX-reports-A-and-B.md, REPORT-C, THINK-lab-creation-why-how-next-2026-09-29.md, the 24 Sep design call (the Director's 8 to 15 / 45 / 60) |
| Results: sample | STAGE-1-sample-report.md, sample-frame-v2.csv |
| Results: extraction quality | pilot-v2/HAND-CHECK-50.md, pilot-v2/DUPLICATE-AUDIT-2-PIs.md, STAGE-2B-pilot-v2-report.md |
| Results: the rule | STAGE-3-full-run-report.md, STAGE-4-remeasure-report.md, REPORT-D sections 2 to 4 |
| Results: real labs | REPORT-D section 5 |
| Results: dictionary | dictionary-v1.md, STAGE-4-remeasure-report.md |
| Discussion | REPORT-D sections 6 to 8 |
| Materials and Methods | PLAN-method-repertoire-experiment-2026-09-30.md, tools/method-experiment/README.md (versions, prompts, seed, temperature, keys never named) |
| Data Availability | full-run/, stage4/per-pi.json, dictionary-v1.json, prompts/ |

## Reporting checklist (observational study of published records)

Sample frame and how it was drawn; inclusion and exclusion of papers; the share read as full text versus abstract; the extraction instrument and its measured accuracy; how names were normalised and the merge rate; each measure defined once; confidence bounds and how computed; every version change during the study and why; what was decided after seeing the data (flag it as post hoc); who funded and who ran it.

## Citation style

PNAS: numbered in order of first mention, in parentheses, e.g. "(1, 3 to 5)". Reference format: Authors, Title. Journal Volume, pages (Year). For Reports A, B and C (unpublished deep-research runs) cite as "Internal report, JoVE, 29 Sep 2026" with the vault filename in Data Availability.
