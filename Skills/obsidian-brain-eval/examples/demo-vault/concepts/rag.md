---
title: Retrieval-Augmented Generation
type: concept
related:
  - "[[information-retrieval]]"
  - "[[hybrid-search]]"
  - "[[recall-at-k]]"
---

# Retrieval-Augmented Generation

Retrieval-augmented generation (RAG) is the pattern where a generative model
answers a question by first retrieving relevant context from a knowledge base
and then conditioning its response on that context. For a personal Obsidian
vault, the knowledge base is your notes and the question is whatever you would
ask ChatGPT-but-grounded-in-my-own-thinking.

RAG has two failure modes. The retrieval layer can miss the relevant note - in
which case no amount of clever prompting will recover. Or the retrieval layer
can surface the right note and the synthesis step can still produce a wrong
answer - in which case you have a generation problem, not a retrieval problem.

Recall@10 isolates the retrieval step. If your Recall@10 is 0.6 you have a
retrieval problem and prompt engineering will not save you. If your Recall@10
is 0.95 and you are still getting bad answers, your problem is the synthesis
step or the chunking strategy, and the auditor's job is done.
