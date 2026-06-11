# Content Matching & Reframing

Match library experiences to template slots with **transparent confidence scoring**, then truth-preservingly reframe. The single biggest score lever is **domain reframing** — most improvement comes from speaking the JD's language about real experience.

## Weighted scoring

| Criterion | Weight | Bands (90–100 / 70–89 / 50–69 / <50) |
|---|---|---|
| **Direct match** | 40% | exact (same skill+domain+context) / strong (same skill, diff domain) / good (overlapping kw) / weak |
| **Transferable** | 30% | directly transferable / minor domain translation / analogy required / a stretch |
| **Adjacent** | 20% | just different framing / clearly adjacent / needs explanation / loose |
| **Impact alignment** | 10% | perfect / strong / moderate / weak (vs what the JD values: metrics, collaboration, scale, innovation) |

```
Overall = Direct×0.4 + Transferable×0.3 + Adjacent×0.2 + Impact×0.1
```

**Confidence bands → action**
- **90–100 DIRECT** — use with confidence
- **75–89 TRANSFERABLE** — strong candidate
- **60–74 ADJACENT** — acceptable with reframing
- **45–59 WEAK** — only if no better option
- **<45 GAP** — flag as unaddressed → [discovery.md](discovery.md)

## Reframing strategies (preserve meaning, change emphasis)

1. **Keyword alignment** — same facts, the JD's terminology.
   `"Led experimental design and data analysis"` → `"Led data science programs combining experimental design and statistical analysis"` (JD says "data science").
2. **Emphasis shift** — same facts, the focus the role values.
   `"Designed experiments… saving millions in recall costs"` → `"Prevented millions in recall costs through predictive risk detection"` (role values business outcomes).
3. **Abstraction level** — adjust technical specificity to the audience. Drop the tool if the role is language-agnostic; name it if the role values the stack.
4. **Scale emphasis** — surface the relevant scale. `"Managed project with 3 stakeholders"` → `"Led cross-functional initiative across 3 organizational units."`

**The line you may never cross:** reframing changes *how* a true fact is described. It never changes the fact, the number, the title, or who did the work. If you can't write the methodology-transfer sentence honestly (see [research.md](research.md) §4.6), it's a gap, not a reframe.

## Gap handling (match < 60%)
Present the choice; don't silently stretch:
```
TEMPLATE SLOT: {requirement}
BEST MATCH: {experience} (confidence {score}%)
OPTION 1 — Reframe adjacent:
  Original:  "{bullet}"
  Reframed:  "{adjusted}"
  Justification: {why this is truthful}
OPTION 2 — Flag as gap (no match >60%) → cover-letter angle or discovery
RECOMMENDATION: {your call}
```

## Output → bullet plan
Write the selection to the session file as a per-position table: `# | id | achievement | confidence | variant (1L/2L/3L) | rationale`. Then **CHECKPOINT** — present the plan and wait for approval before generating. Each chosen bullet carries its provenance flag and verb-ownership from the library into generation ([anti-fabrication.md](anti-fabrication.md)).
