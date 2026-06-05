---
title: Gold Set
type: concept
topics:
  - "[[evaluation-metrics]]"
related:
  - "[[recall-at-k]]"
  - "[[bm25]]"
---

# Gold Set

A gold-set is a list of question / known-relevant-document pairs used as the
ground truth in a retrieval evaluation. Each record says "for this question,
THIS document is the right answer", so the scoring step can mechanically check
whether the retrieval system returned that document.

For an Obsidian vault, a natural gold-set generator samples representative notes
from your curated folders (entities, concepts, themes), asks an LLM to write
one natural question per note that the note answers, and stores each record as
JSONL. Frontmatter wikilinks let you expand the relevance set beyond the source
note: if a note declares `topics: [[information-retrieval]]`, the retrieval
layer is also rewarded for surfacing the topic anchor.

Thirty to fifty questions is the typical sweet spot. Below thirty, single
unlucky hits or misses dominate the score and the metric becomes noisy. Above
fifty, the marginal information is small and generation cost dominates.
