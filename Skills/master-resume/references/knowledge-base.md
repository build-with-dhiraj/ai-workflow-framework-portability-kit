# Experience Library (Knowledge Base)

The library is the single source of truth. Every bullet on every resume must trace back to an entry here. The library **grows** — after each successful resume, write strong new/reframed bullets back.

## Layout

```
library/
  config.md              # identity, links, FIXED sections, provenance flags  (from templates/config.md)
  experience/            # one file per role / project / paper
    2023_acme_ml.md
    2021_phd_protein.md
  publications.md        # academic mode only — full pub list with venues + provenance
  _INVENTORY.md          # index: id, title, org, dates, domain tags, status
```

## Two ways to populate the library

### A. From existing resumes / CVs (industry, fast path)
Read the user's current resume(s). For each role, create an `experience/<id>.md` file. Extract every achievement as an atomic, dated, sourced bullet. Ask the user to confirm any metric you're unsure about. **Do not infer numbers.**

### B. From papers / projects (academic / research path)
For each paper or project the user supplies (PDF, `.tex`, repo, or description), extract structured data with **provenance**. Ask the contribution questions below — they surface what the candidate *actually did* vs. what the team did.

**Contribution questions (ask per paper/project):**
1. What was *your* specific contribution vs. co-authors? (first author? corresponding? support?)
2. What method/tool did you personally build or run?
3. What is the headline quantitative result, and is it published / under review / internal?
4. What problem did it solve, for whom?
5. What would a domain expert at a hiring company recognize as transferable here?

## Experience file schema

Use [templates/experience-file.md](../templates/experience-file.md). Each file holds:

- **Header:** id, role/title, organization, dates, location, domain tags, archetype (academic/industry/both).
- **Bullets:** each with `text`, `metric` (+ how verified), `provenance` flag, `verbs allowed` (ownership level), and `keywords` it satisfies.
- **Raw facts:** tools, scale numbers, methods, named entities — the inventory matching draws from.

## Provenance flags (carry through to every bullet)

| Status | Rule for how it may appear |
|---|---|
| `published` | Cite venue; specific numbers OK |
| `under-review` | "under review at [Journal]" — no "published" language |
| `preprint` | Always flag as preprint |
| `internal` / `proprietary` | "infrastructure I developed" — not peer-reviewed; no external metrics |
| `unpublished` | No specific numbers or publication claims |
| `team` | Contributing-author verbs only (see [anti-fabrication.md](anti-fabrication.md)) |

## Verb-ownership level (set per bullet at capture time)

- **Full ownership** ("built, led, designed, shipped") — only where the candidate personally owned it.
- **Contributing** ("contributed to, supported, co-developed") — team work where the candidate was one of several.

Storing this at capture time prevents overclaiming during generation.

## Corrections log

Every error the user corrects (wrong metric, wrong title, wrong date, misattributed work) goes into `config.md` → Corrections, and is checked before every generation so it never reappears.

## Self-improvement

After a resume is approved: any newly discovered experience (from [discovery.md](discovery.md)) or strong reframing becomes a permanent library entry, tagged with the JD/company it was created for. Next tailoring run is faster and richer.
