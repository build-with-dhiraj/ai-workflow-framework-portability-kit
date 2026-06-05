---
title: Recall@k
type: concept
topics:
  - "[[information-retrieval]]"
related:
  - "[[gold-set]]"
  - "[[evaluation-metrics]]"
---

# Recall@k

Recall@k is a retrieval-evaluation metric that measures whether at least one
relevant document appears in the top k results returned by a search system.
For a single query it is binary (hit or miss). Aggregated across a [[gold-set]],
it becomes the fraction of queries that had at least one known-relevant document
in the top k.

A target of Recall@10 ≥ 0.85 is the threshold this skill ships against: for at
least 85% of questions, the retrieval layer must surface a relevant note in the
top ten candidates.

Recall@k is the cleanest gate to put in front of any retrieval-augmented
generation pipeline: it isolates the retrieval step from the answer-synthesis
step, so when the answer is bad you can immediately tell whether the problem is
"the right note was not even retrieved" versus "the LLM did not synthesise the
retrieved notes well".
