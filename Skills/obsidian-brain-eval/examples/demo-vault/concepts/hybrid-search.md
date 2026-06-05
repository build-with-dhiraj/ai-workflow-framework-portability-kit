---
title: Hybrid Search
type: concept
topics:
  - "[[information-retrieval]]"
related:
  - "[[bm25]]"
  - "[[vector-search]]"
  - "[[recall-at-k]]"
---

# Hybrid Search

Hybrid search is the combination of a sparse retrieval signal (typically
[[BM25]]) and a dense retrieval signal (typically a sentence-embedding nearest
neighbour search) into a single ranked list. Each signal has a known failure
mode: BM25 misses paraphrases, vector search misses rare acronyms and product
names. A hybrid system fuses both.

The fusion can be as simple as a round-robin merge over the two top-k lists, or
as fancy as reciprocal rank fusion (RRF) with calibrated weights. For an
Obsidian vault, simple round-robin is usually enough to get past the 0.85
Recall@10 target this evaluator ships against.

The LanceDB backend bundled with this skill is a hybrid backend: it runs the
full-text search index and a BAAI/bge-small-en-v1.5 vector search in parallel,
then merges with deduplication on `vault_path`.
