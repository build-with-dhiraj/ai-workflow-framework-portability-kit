---
title: Information Retrieval
type: concept
related:
  - "[[recall-at-k]]"
  - "[[bm25]]"
  - "[[hybrid-search]]"
---

# Information Retrieval

Information retrieval is the discipline of finding documents in a collection
that satisfy a user's information need. The field traces back to the 1950s but
the modern Obsidian-style personal knowledge base is one of its more interesting
recent applications: the corpus is tiny by web-search standards, but the
relevance signal is sparse, idiosyncratic, and very personal.

Two ideas matter for vault retrieval. First, a sparse signal like BM25 captures
exact-keyword overlap and is invaluable when your notes use a specific
vocabulary (acronyms, product names, internal jargon). Second, a dense signal
like a sentence embedding captures paraphrase: someone searching for "how to
write a research summary" should find a note titled "literature review template"
even though the words do not overlap.

Most production vault-RAG stacks combine both via [[hybrid-search]]. That
combination is what an evaluator measures with Recall@k.
