---
name: master-resume
description: Research-grade resume, CV, and cover-letter tailoring from a persistent experience library to specific job descriptions, with provenance-checked anti-fabrication, confidence-scored matching, AI-detector avoidance, an 8-dimension multi-perspective critique, and LaTeX output ready for Overleaf/PDF. Adapts between academic/research and industry modes per JD and supports multi-job batches. Use when the user wants to write, tailor, improve, critique, or batch-generate a resume, CV, or cover letter; build a resume experience library; score a resume against a job description; bridge a career/domain transition; or prepare application materials for Overleaf/PDF.
---

# Master Resume

Tailors a resume / CV / cover letter to a specific job description from a persistent, provenance-tagged **experience library**, then critiques it from five reader perspectives. Adapts per JD between **Academic/Research** mode (CV, publications, under-review/preprint provenance, faculty/lab cover letters) and **Industry/Professional** mode (one-page resume, ATS keywords, company research). Final deliverable is `.tex`, compiled on **Overleaf** → PDF.

## Core principle (non-negotiable)

**Truth-preserving optimization.** Never fabricate experience, metrics, titles, or claims. Reframe and re-emphasize what is real. Every quantitative claim must trace to the library. When a requirement isn't met, flag it as a gap — do not invent. See [anti-fabrication.md](references/anti-fabrication.md).

## When to use which file

| You are… | Load |
|---|---|
| Building / updating the experience library | [knowledge-base.md](references/knowledge-base.md) |
| Researching a JD + company, building the domain lens | [references/research.md](references/research.md) |
| Surfacing undocumented experience to fill gaps | [references/discovery.md](references/discovery.md) |
| Selecting & reframing bullets for a JD | [references/matching.md](references/matching.md) |
| Enforcing truthfulness, provenance, verb discipline | [references/anti-fabrication.md](references/anti-fabrication.md) |
| Generating the `.tex` (limits, orphans, Overleaf) | [references/latex.md](references/latex.md) |
| Removing AI-writing fingerprints before presenting | [references/ai-fingerprint.md](references/ai-fingerprint.md) |
| Writing the cover letter | [references/cover-letter.md](references/cover-letter.md) |
| Scoring / critiquing a generated resume | [references/critique.md](references/critique.md) |
| Tailoring 3–5 similar jobs at once | [references/multi-job.md](references/multi-job.md) |

## Workflow (single job)

1. **Intake & mode detection.** Read the JD. Classify role archetype (Academic/Research vs Industry; IC vs leadership). Pick deliverable: resume (industry) or CV (academic). If 3–5 JDs are given, switch to [multi-job.md](references/multi-job.md). Ensure `config.md` + experience library exist; if first run, build them via [knowledge-base.md](references/knowledge-base.md). Create `output/<Company_Role>/` and a session file from [templates/session-file.md](templates/session-file.md).
2. **Research & lens.** Parse the JD, research the company, benchmark the role, and build the 7-element **domain-specialist lens**. Persist it to the session file. → [references/research.md](references/research.md).
3. **Gap discovery (gated).** From the gap assessment, run branching conversational discovery for uncovered requirements. Write any new experiences back to the library, provenance-tagged. → [references/discovery.md](references/discovery.md).
4. **Match & frame.** Confidence-score each library experience against each slot; select and truth-preservingly reframe. Apply provenance flags + verb discipline. Write the **bullet plan** to the session file. **CHECKPOINT — present the plan; wait for approval.** → [references/matching.md](references/matching.md) + [references/anti-fabrication.md](references/anti-fabrication.md).
5. **Generate.** Fill the template, respecting char limits / orphan / bold-penalty / FIXED-section rules. Run the **12-item AI-fingerprint scan** and fix every hit. → [references/latex.md](references/latex.md) + [references/ai-fingerprint.md](references/ai-fingerprint.md).
6. **Cover letter (optional).** Detect institution type, generate, **verify every external hook by web search**, fingerprint-scan. → [references/cover-letter.md](references/cover-letter.md).
7. **Critique.** Reuse the lens. Five-perspective read-through + 8-dimension score + interview likelihood + tiered fixes + interview bridge points. **CHECKPOINT — present score table + Tier-1 fixes.** → [references/critique.md](references/critique.md).
8. **Edit loop & library update.** Apply approved fixes, re-run verification gates, log corrections in the session file, and write strong reframed bullets back to the library so it self-improves.

## Verification gate (before presenting any document)

- [ ] Compiles (or is Overleaf-ready and you've told the user how to compile — see [latex.md](references/latex.md))
- [ ] Char/line budget respected (`python3 scripts/char_count.py -f [resume|cv] file.tex`)
- [ ] Every metric/claim traces to the library; provenance flags correct
- [ ] 12-item AI-fingerprint scan passes
- [ ] No FIXED section was modified

## Setup helper

`scripts/char_count.py` strips LaTeX markup and reports rendered chars + variant + budget status per bullet. Templates and a `config.md` schema live in [templates/](templates/). On first use, copy `templates/config.md` into the working project and fill it in.

> Merged and extended from two MIT-licensed projects: ARPeeketi/claude-resume-kit (provenance, AI-fingerprint rules, 8-dim critique, LaTeX discipline) and varunr89/resume-tailoring-skill (experience library, research, branching discovery, confidence matching, multi-job). See [README.md](README.md).
