---
title: Evaluation Metrics
type: concept
related:
  - "[[recall-at-k]]"
  - "[[gold-set]]"
---

# Evaluation Metrics

A retrieval system without evaluation is a guess. The three metrics every
vault-RAG pipeline should track are Recall@k, Mean Reciprocal Rank (MRR), and
NDCG. The skill obsidian-brain-eval focuses on Recall@k because it is the
simplest, cleanest gate to put in front of an answer-synthesis layer.

- Recall@k: did at least one relevant document appear in the top k?
- MRR: what was the rank of the FIRST relevant document?
- NDCG: how well does the ranked order match the ideal order?

For a single-relevant-document setup (the cleanest gold-set shape) all three
collapse to functions of the rank of the top hit. Recall@k turns rank into a
binary, MRR turns it into a smooth penalty, and NDCG generalises to multiple
relevance grades.

A useful diagnostic: when Recall@10 is high but MRR is low, your retrieval is
finding the right note but ranking it tenth. The fix is reranking, not more
retrieval candidates.
