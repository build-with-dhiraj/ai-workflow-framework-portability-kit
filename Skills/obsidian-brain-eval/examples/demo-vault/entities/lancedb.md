---
title: LanceDB
type: entity
topics:
  - "[[information-retrieval]]"
  - "[[hybrid-search]]"
related:
  - "[[vector-search]]"
---

# LanceDB

LanceDB is an embedded, columnar vector database that ships with first-class
full-text search alongside vector search. The two ingredients you need for a
[[hybrid-search]] retrieval stack are in one library, on local disk, with no
server to run.

The reason it shows up in this skill specifically: the canonical
LanceDB backend assumes a table named `items` with columns `vault_path`,
`text`, and a `vector` column populated with embeddings from
BAAI/bge-small-en-v1.5. That is the exact shape the upstream Connecting Dots
engine writes, so the LanceDB backend in this skill is a drop-in evaluator for
any vault-RAG stack that follows the same convention.

If you do not have a LanceDB table, use the naive BM25 backend instead. It
needs no external index.
