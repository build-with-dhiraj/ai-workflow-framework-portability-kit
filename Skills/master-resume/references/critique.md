# Multi-Perspective Critique

Single-pass, comprehensive. Run AFTER generation, BEFORE presenting. Reuse the **domain-specialist lens** from the session file — do NOT re-research unless the JD changed. The critique's job: catch what leaked through generation, find remaining gaps, and estimate interview likelihood from real reader perspectives.

The output MUST contain all 8 sections below.

## 1. Domain-specialist lens
Pull the 7-element lens from the session file ([research.md](research.md) §4). If missing, build it now (1–2 web searches). Persist it; reuse across re-critiques.

## 2. Five-perspective read-through
Each persona is a person at THIS company seen through the lens — not a generic archetype. Each sees only what they'd read in their window; give a verdict.

1. **ATS robot (0s)** — keyword scan. Extract top 20 JD keywords; mark verbatim / semantic / absent. Match rate: ≥70% PASS, 60–69% MARGINAL, <60% FAIL. Flag any JD keyword appearing 3+× in JD but 0× in resume. → keyword table + top 3 truthfully-addable misses.
2. **Recruiter (10s)** — name, current title/employer, education, tagline, first 2 summary lines. Decides Forward / Maybe / Reject. Does the tagline use target-domain language? Prestige signal early?
3. **HR screen (30s)** — full summary + skills headers + first bullet per role + education. Decides Phone-screen / Borderline / Pass. Is the bridge sentence present? Do skill-group *names* signal target-domain relevance?
4. **Hiring manager (2m)** — everything; domain expert. Decides Interview / Maybe / No. Methodology transfer obvious (or do they have to translate)? Narrative arc? Red flags / overclaiming? Differentiator visible? + predicted first interview question.
5. **Deep technical reviewer (10m)** — every bullet, checks truth. Truthfulness audit (claim→verified?→source). Provenance flags correct? Verb discipline correct? Publication coherence? Internal consistency (summary↔bullets↔CL)? Over-saturation (any keyword >8×)?

## 3. Eight-dimension scoring (weights sum to 100)

| # | Dimension | Wt | Assess |
|---|---|---|---|
| 1 | ATS keyword match | 15 | coverage, verbatim vs semantic, high-value misses |
| 2 | Summary | 10 | bridge sentence, target-domain language, prestige, forward intent |
| 3 | Skills section | 10 | group names (domain signal), relevance, bold accuracy |
| 4 | Bullet quality | 25 | per-bullet JD alignment, reframing, quantification, action verbs |
| 5 | Publication selection* | 10 | venue prestige, tag relevance, first-author ratio, gap honesty |
| 6 | Narrative coherence | 15 | header-to-footer story, domain thread, first-impression timing |
| 7 | Page fill & visual | 5 | budget, orphans, clean compile |
| 8 | Credibility signals | 10 | venue quality, metrics, adoption, leadership evidence |

\* Industry mode with no publications: fold dimension 5's weight into Bullet quality (→35%) and note it.

**Per dimension:** 9–10 optimal · 8–8.5 strong · 7–7.5 good w/ gaps · 6–6.5 significant gaps · <6 major problems.
**Overall:** 85+ submit · 80–84 strong (1–2 fixes to ceiling) · 75–79 missing reframing/key bullets · 70–74 first-draft · <70 fundamental issues.

## 4. Interview likelihood + ceiling
Per reader: probability + the single deciding factor. Then a ceiling table: current / +top-3-fixes / theoretical max for this candidate+JD / hard ceiling (structural background gap) / what would close it (e.g., "1 domain publication → +3").

## 5. Tiered improvements
- **Tier 1 (≥1 pt each):** missed domain reframing, truthfully-addable JD keyword, weak→strong bullet swap, missing/weak bridge sentence. Format: current → proposed → why → expected Δ.
- **Tier 2 (0.3–0.9):** vocabulary swaps, tag refinements, skills-group renames, one keyword insert.
- **Tier 3 (<0.3):** saturation trim, wording polish.
- **Verdict:** "Apply Tier 1. Tier 2 optional. Tier 3 not worth the edit."

## 6. Interview bridge points
5–7 rows: `resume topic → target-domain equivalent → opening line` ("The same methodology I used for X applies to Y because…"). Converts claims into interview talking points.

## 7. Cover-letter critique
If a CL exists, run the checklists in [cover-letter.md](cover-letter.md) §critique (anti-patterns, tailoring, context-specific, ATS, structural, package cohesion). If no CL: assess whether the resume earns an interview standalone; note "CL not provided."

## 8. Post-generation verification
Run the [ai-fingerprint.md](ai-fingerprint.md) 12-item scan + the SKILL.md verification gate (compile, char budget, provenance, no FIXED edits). Any fail → fix before presenting.

## >>> MANDATORY STOP <<<
Present: score table + Tier-1 actionable fixes + interview likelihood. Save the full critique to `output/<folder>/critique_<name>.md` and update the session file (score, Status → Critique: CURRENT).
