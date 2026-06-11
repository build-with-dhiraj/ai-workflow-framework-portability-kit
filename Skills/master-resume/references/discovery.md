# Branching Experience Discovery

Conversational, NOT a static questionnaire. Each answer informs the next question. Only run for requirements the library doesn't already cover (from the Gap Assessment in [research.md](research.md)). Goal: surface real, undocumented experience to fill gaps — never to invent it.

## When to run
A requirement scores **< 60% confidence** in [matching.md](matching.md) and is **Fatal or Serious** in the gap ranking. Skip cosmetic gaps.

## Multi-job context line (if batching)
Lead each gap with leverage so the user knows the payoff:
```
"{SKILL} appears in {N} of your target jobs ({Company1}, {Company2}).
This is a {HIGH/MEDIUM/LOW}-LEVERAGE gap — addressing it helps {N} application(s).
Current best match: {X}% ('{best_match_text}').
{branching question}"
```
HIGH = 3+ jobs · MEDIUM = 2 jobs · LOW = 1 job.

## Technical-skill gap pattern
```
PROBE: "The job requires {SKILL}. Have you worked with {SKILL} or {RELATED_AREA}?"
 A — Direct:   what for? → scale/metric? → prod or dev? → challenges solved? → CAPTURE detailed bullet
 B — Indirect: your role relative to it? → did you {a/b/c}? → what did you learn? → CAPTURE as support role if substantial
 C — Adjacent: tell me about {ADJACENT_TECH} → relevant activity? → CAPTURE as related expertise
 D — Personal: side projects/courses? → what did you build/deploy? → how recent? → CAPTURE if recent & substantive
 E — None:     any broader {category} work? → if no, move on
```

## Soft-skill / experience gap pattern
```
PROBE: "The role emphasizes {SOFT_SKILL}. Tell me about a time you {demonstrated it}."
 A — Strong:   who was involved? → the challenge? → how did you drive it? → result/metrics? → CAPTURE with impact
 B — Vague:    reframe the question → the situation? → how many stakeholders? → CAPTURE, help articulate
 C — Project:  your role vs others? → who did you coordinate? → how ensure alignment? → CAPTURE as leadership if substantial
 D — Volunteer/side: scope & timeline? → which skills transfer? → measurable outcomes? → CAPTURE if relevant
```

## Recent-work probe
```
PROBE: "What have you worked on in the last 6 months that isn't in your resume yet?"
 A — Describes project: role? tech? problem? impact? → does it address {gap}? → CAPTURE
 B — Multiple: go through each, prioritize by gap relevance
 C — "Nothing new": small improvements? new tools? mentoring/teaching? → even small items fill gaps
```

## Principles
1. **Start broad, go narrow.** Open-ended first; follow-ups drill into what they actually share. Don't re-ask covered ground.
2. **Branch dynamically.** Promising → deeper. "No" → adjacent probe or move on. Unclear → rephrase or offer concrete examples ("Was it like X or Y?").
3. **Adapt to style.** Verbose → "what's the key takeaway?" Terse → offer options. Uncertain → validate and prompt.
4. **Know when to stop.** After 2–3 dry attempts on a gap, move on gracefully. Don't manufacture content. Flag the gap for the cover letter or accept it.
5. **Cross-reference.** "Earlier you mentioned X — does that relate here too?" Build connections the user may not see.

## Capture
Every captured item is written to the library ([knowledge-base.md](knowledge-base.md)) as a real experience entry with a provenance flag and verb-ownership level — so it's reusable and stays truthful. If the user is unsure of a number, mark the metric `unverified` and do not put it on the resume until confirmed.
