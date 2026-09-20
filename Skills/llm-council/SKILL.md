---
name: llm-council
description: "Runs a question, idea, or decision through 5 AI advisors who answer independently, peer-review each other anonymously, and get synthesized into one verdict by a chairman. Adapted from Karpathy's LLM Council. MANDATORY TRIGGERS: 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. STRONG TRIGGERS (only alongside a real tradeoff): 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do NOT trigger on yes/no questions, factual lookups, creation tasks ('write me a tweet'), processing tasks ('summarize this'), or a casual 'should I' with no stakes. DO trigger when there are multiple live options, genuine uncertainty, and a costly wrong answer."
---

# LLM Council

Five advisors answer independently, then review each other blind, then a chairman
synthesizes. One model, five thinking lenses, plus a peer-review round that catches what
any single pass misses.

Run it when being wrong is expensive. Skip it when there's one right answer, or when the
user wants something made rather than judged.

## Workflow

**1. Enrich, then frame.** Glob/Read for context that would make advice specific instead
of generic: `CLAUDE.md`, any `memory/` folder, files the user referenced, prior
`council-transcript-*.md` in the cwd. Cap it at 2-3 files. Then write one neutral framed
question carrying: the decision, the user's context, the workspace context (stage,
audience, constraints, numbers), and what's at stake. No opinion, no steering. If the
question is too vague to frame, ask exactly one clarifying question, then proceed.

**2. Convene.** Dispatch all 5 advisors in a single message so they run in parallel.
Prompts in [ADVISORS.md](ADVISORS.md). 150-300 words each.

**3. Peer review.** Shuffle the 5 responses into A-E (record the mapping). Dispatch 5
reviewers in parallel, each seeing all five anonymized responses. Under 200 words each.

**4. Chairman.** One agent gets the framed question, the de-anonymized responses, and all
5 reviews. Fixed five-section verdict.

**5. Render.** Write the session to JSON, then:

```bash
python3 ~/.claude/skills/llm-council/scripts/render.py session.json .
```

It emits `council-report-<timestamp>.html` and `council-transcript-<timestamp>.md` in the
cwd and prints both paths. Send the HTML to the user with SendUserFile
(`display: "render"`). JSON schema is documented at the top of the script.

## Rules

- **Parallel, always.** Sequential dispatch lets earlier responses bleed into later ones.
- **Anonymize for review.** Named advisors get deferred to by reputation, not merit.
- **Advisors do not hedge.** Each leans fully into its lens. Balance is the chairman's job.
- **The chairman may side with the minority** when the dissenter's reasoning is strongest,
  and should say why.
- **Don't council trivia.** If there's one right answer, just answer it.
