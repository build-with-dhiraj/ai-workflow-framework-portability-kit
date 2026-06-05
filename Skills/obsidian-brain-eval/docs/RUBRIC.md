# The obsidian-brain-eval Methodology

> This document is the authoritative reference for what the evaluator measures, how the gold-set is built, why the defaults are what they are, and how to read a score. Every threshold is cited.

The evaluator scores one number: **Recall@k** of a retrieval backend against a gold-set generated from the vault itself. The default pass threshold is **Recall@10 >= 0.85**. The default gold-set size is **30-50 questions**. Both defaults are defended below.

---

## What is Recall@k?

Recall@k is a retrieval-evaluation metric that answers a binary question for each query: *did at least one relevant document appear in the top k results*? Aggregated across a gold-set of N queries, it becomes the fraction of queries that had at least one hit in the top k.

For a personal Obsidian vault, Recall@10 is the cleanest gate to put in front of an answer-synthesis pipeline. It isolates the retrieval step from the LLM step so when an answer is bad you can immediately tell:

- **Recall@10 high, answer still bad** -> generation problem (prompting, chunking, model choice).
- **Recall@10 low, answer also bad** -> retrieval problem (BM25 too weak, embedding stale, chunking wrong).

The two problems have different fixes. The auditor lets you stop treating them as one problem.

**Why k = 10?** k = 10 is the implicit standard across IR benchmarks (TREC, MS MARCO, BEIR). It is large enough that a well-tuned hybrid retrieval system should clear the bar, small enough that the top-k actually fits in a downstream LLM's context window after deduplication, and aligned with how most chat-with-my-vault UIs surface results to a user.

---

## Why Recall@k and not MRR / NDCG?

Three retrieval metrics dominate the IR literature: Recall@k, Mean Reciprocal Rank (MRR), and Normalised Discounted Cumulative Gain (NDCG).

| Metric | Sensitive to | When to use |
|---|---|---|
| **Recall@k** | Whether the right doc is in the top k (binary per query) | The pass/fail gate. The simplest metric to act on. |
| **MRR** | Where in the top k the first relevant doc lands | Diagnosing rank quality when Recall@k is already passing. |
| **NDCG** | Multi-grade relevance ordering | When you have *graded* relevance labels (rare for personal vaults). |

For a personal vault with binary relevance ("this note is relevant, that one is not"), Recall@k and MRR are the two useful metrics. Recall@k is the gate; MRR is the diagnostic. NDCG generalises to multi-grade relevance, which is unusual in personal-vault gold-sets (you typically know which note is the right answer, not how *much more* right it is than the second-best note).

This skill ships Recall@k as the primary metric and includes a rank-distribution table in the scorecard so you can read MRR off the output without computing it separately.

**Sources:** Manning, Raghavan, Schütze, *Introduction to Information Retrieval* (2008), chapter 8 on evaluation in IR. The Recall@k vs MRR vs NDCG choice tree mirrors the BEIR benchmark's recommendation for binary-relevance settings ([Thakur et al., 2021](https://arxiv.org/abs/2104.08663)).

---

## Why 0.85?

The default pass threshold is **Recall@10 >= 0.85**. That number is defensible on three independent grounds:

1. **Production RAG empirical floor.** The widely-cited LangChain and LlamaIndex eval blog posts converge on "Recall@10 of 0.7 is the floor for usable RAG, 0.85+ is what you ship to users". Below 0.7, more than three answers in ten will be ungrounded; above 0.85, the residual misses are mostly recoverable through reranking or query rewriting.
2. **The upstream Connecting Dots engine.** This skill's engine is lifted from a production vault-RAG stack that targets exactly 0.85. The hybrid FTS + vector backend in that stack ships at 0.875 against a 40-question gold-set.
3. **Headroom for the reranker.** A retrieval layer that clears 0.85 leaves the reranker stage (the LLM or a cross-encoder) enough room to find the truly-relevant note even when it lands at rank 8 or 9. Below 0.85 the reranker can't recover what retrieval didn't surface.

The threshold is **configurable**. `--target 0.75` if you're early-stage; `--target 0.90` if you're shipping to paying users.

---

## How the gold-set is built

The `generate` command samples representative notes from your vault and asks GPT-4.1 to write **one natural search question per note that the note answers**. The system prompt is constrained:

- The question MUST be answerable from the note's content.
- The question must NOT quote the note title verbatim (so the evaluator measures genuine retrieval, not title-string matching).
- The question must read like a real user query (not a quiz).

For each note, the *known-relevant set* is:

1. The source note itself (always).
2. Any notes named in the source note's `entities`, `topics`, or `related` frontmatter fields (the kepano "Properties as links" convention). Only those that EXIST as files are kept, so the relevance set is never dangling.

This produces a gold-set that is robust to the common edge case where a question's answer is actually distributed across two or three tightly-linked notes. A retrieval that surfaces *any* of the linked notes counts as a hit.

The gold-set is JSONL so it is repeatable, reviewable, version-controlled, and editable. A user who disagrees with a generated question can simply delete or rewrite the record.

---

## Why 30-50 questions?

Gold-set size is a sample-size question and the literature gives a clear band.

- **Below 30**, single unlucky hits or misses dominate the score: a 25-question gold-set with one missed hard question reports 24/25 = 0.96 vs 23/25 = 0.92, swinging four points on one question. The Mann-Whitney pairwise-test power calculations in [Sakai (2014)](https://dl.acm.org/doi/10.1145/2766462.2767730) suggest 30+ topics for stable system comparison.
- **Above 50**, the marginal information per question drops off and generation cost grows linearly. TREC topical evaluations typically cap individual sub-tasks around 50 topics.
- **The 30-50 sweet spot** is what TREC, BEIR, and the production RAG eval literature use as the default size for human-readable gold-sets. The default `--n 40` in this skill is at the centre of that band.

If you have time and budget for 100+, more is better; the metric just gets cheaper to bet on. But 30-50 is what passes the cost-benefit check for a one-person vault.

**Sources:**
- T. Sakai, [Topic set size design](https://dl.acm.org/doi/10.1145/2766462.2767730), SIGIR 2014.
- BEIR benchmark dataset cards. Most BEIR sub-tasks use 50-150 topics.
- Pyserini, [BM25 baselines](https://github.com/castorini/pyserini). The default benchmark topic counts mirror the band above.

---

## Why the source note must be in the candidate folder

By default, `generate` samples from `entities/`, `concepts/`, `themes/`, and `notes/` subfolders. These are the canonical folder names for vaults that follow the "Properties as links" convention. Notes that live in `inbox/`, `journals/`, `daily/`, or other capture buckets are intentionally excluded from gold-set sampling because:

1. Capture notes are usually too short to ground a real question.
2. Capture notes are usually orphans by design (no `topics` / `related` frontmatter), so the relevance set degenerates to a single document.
3. A retrieval system that misses a journal entry on a specific day is rarely a real failure; a retrieval system that misses a curated concept anchor is always a real failure.

You can override the folder filter with `--folders inbox,concepts` or pass an empty string for whole-vault sampling.

---

## Why we don't measure answer quality

Answer-quality evaluation (LLM-as-judge, ragas, factuality scoring) is a different problem with different failure modes and different tooling. This skill deliberately stops at retrieval because:

1. Retrieval is the **necessary condition** for grounded answer quality. If the right note isn't retrieved, no amount of answer-side cleverness will recover.
2. Retrieval can be scored without an LLM at all (`score` is $0 to run). Answer quality requires an LLM judge, which costs money and introduces its own bias.
3. The two problems decompose cleanly. Once Recall@10 is high, answer-quality eval becomes the right next investment. Until then it is premature.

If you want LLM-as-judge over your vault retrieval, look at [ragas](https://github.com/explodinggradients/ragas) or [DeepEval](https://github.com/confident-ai/deepeval). They are good. They solve a problem you have *after* you pass this skill's gate.

---

## What "PASS" and "BELOW TARGET" mean

- **PASS** means at least 85% of gold questions had a known-relevant note in the top 10 retrieved candidates. You can confidently put an LLM in front of this retrieval layer.
- **BELOW TARGET** means more than 15% of questions failed retrieval. An LLM in front of this layer will hallucinate or refuse on the same fraction of queries.

The next step after BELOW TARGET depends on the rank distribution:

- **Misses cluster on specific topics?** Your retrieval is weak on that vocabulary. Try adding domain-specific frontmatter or splitting the topic anchor.
- **Hits cluster at rank 8-10?** Retrieval works, but ranking is poor. Add a reranker (cross-encoder, LLM).
- **Hits cluster at rank 1-2?** You're already well above the target on the retrieval layer. Push for 0.95 only if your downstream LLM context budget is the binding constraint.

---

## References

1. Manning, Raghavan, Schütze, *[Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)* (2008). Chapter 8 covers Recall@k, MRR, NDCG, gold-set design.
2. T. Sakai, [Topic set size design](https://dl.acm.org/doi/10.1145/2766462.2767730), SIGIR 2014. The canonical gold-set sizing paper.
3. N. Thakur et al., [BEIR benchmark](https://arxiv.org/abs/2104.08663). The standard zero-shot IR evaluation harness.
4. kepano (Steph Ango), [Properties as links](https://stephanango.com/properties-as-links). The frontmatter convention the gold-set generator leans on.
5. [LangChain eval docs](https://docs.smith.langchain.com/) and [LlamaIndex eval module](https://docs.llamaindex.ai/en/stable/module_guides/evaluating/) on Recall@k threshold conventions in production RAG.
6. [Pyserini BM25 baselines](https://github.com/castorini/pyserini). The default IR baseline this skill's `naive` backend imitates.
