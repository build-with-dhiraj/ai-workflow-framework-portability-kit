# master-resume

A single, adaptive skill for tailoring **resumes, CVs, and cover letters** to a specific job description — from a persistent, provenance-tagged experience library, with anti-fabrication discipline, AI-detector avoidance, and an 8-dimension multi-perspective critique. Output is `.tex`, compiled on **Overleaf** → PDF. Adapts per JD between **academic/research** and **industry/professional** modes, and handles **multi-job batches**.

## What it does (the pipeline)
Intake & mode detection → research + domain-specialist lens → gap discovery → confidence-scored matching & truth-preserving reframing → LaTeX generation (char/orphan discipline) → cover letter → multi-perspective critique (8-dim score) → edit loop + library self-improvement.

Start by reading [SKILL.md](SKILL.md).

## Layout
```
master-resume/
├── SKILL.md                 # orchestrator: when-to-use, workflow, verification gate
├── references/
│   ├── knowledge-base.md     # experience library + provenance extraction
│   ├── research.md           # JD parse + company research + 7-element domain lens
│   ├── discovery.md          # branching conversational gap discovery
│   ├── matching.md           # confidence scoring + reframing strategies
│   ├── anti-fabrication.md   # provenance flags, verb discipline, truth rules
│   ├── ai-fingerprint.md     # banned words/phrases/structure + 12-item scan
│   ├── critique.md           # 5 personas + 8-dim score + interview likelihood
│   ├── cover-letter.md       # industry/lab/academic CL + hook verification
│   ├── multi-job.md          # batch processing + gap dedup + state schema
│   └── latex.md              # char limits/orphan/bold + Overleaf workflow
├── templates/                # config, experience-file, session-file, .tex templates
└── scripts/char_count.py     # rendered-char + budget checker for .tex bullets
```

## Quick start
```
"Tailor my resume to this JD: <paste>"
"Build my resume experience library from these papers / my current resume"
"Score this resume against the job description"
"Apply to these 3 roles at once: <3 JDs>"     # multi-job batch
```
On first run the skill creates a `config.md` (from `templates/config.md`) and an experience library, then walks the pipeline with checkpoints at the bullet plan and the critique. Generated `.tex` goes to `output/<Company_Role>/` — upload to a new Overleaf project, set compiler to pdfLaTeX, Recompile.

## Char-budget helper
```bash
python3 scripts/char_count.py -f resume output/Company_Role/name_resume.tex
python3 scripts/char_count.py -f cv "\\textbf{DFT} study of \\ce{TiO2}"
```

## Credit
Merged and extended from two MIT-licensed projects:
- **[ARPeeketi/claude-resume-kit](https://github.com/ARPeeketi/claude-resume-kit)** — provenance/anti-fabrication, AI-fingerprint rules, the 8-dimension multi-perspective critique + domain-specialist lens, LaTeX char/orphan discipline, session/corrections files, `char_count.py`, cover-letter institution typing.
- **[varunr89/resume-tailoring-skill](https://github.com/varunr89/resume-tailoring-skill)** — persistent experience library, company/role research, branching conversational discovery, confidence-scored matching with reframing strategies, multi-job batch processing with gap dedup.

This skill recombines their strongest ideas into one adaptive, Overleaf-targeted workflow.
