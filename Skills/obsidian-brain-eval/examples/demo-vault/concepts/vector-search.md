---
title: Vector Search
type: concept
topics:
  - "[[information-retrieval]]"
related:
  - "[[hybrid-search]]"
  - "[[bm25]]"
---

# Vector Search

Vector search retrieves documents by nearest-neighbour distance in an embedding
space. A sentence-embedding model maps each document into a high-dimensional
vector; a query goes through the same model; the top-k neighbours are returned
as the candidate set.

The strength of vector search is paraphrase handling. The query "How do I
estimate the cost of a new feature?" will surface a note titled "Engineering
sizing template" even though no surface words overlap, because both texts
embed near each other in the model's semantic space.

The weakness is rare-vocabulary handling. A vault that talks about a specific
internal product code or an obscure mathematical term may fail to embed those
tokens distinctly enough for nearest-neighbour to work. That is why most
production vault-RAG stacks pair vector search with [[BM25]] in a hybrid
configuration.
