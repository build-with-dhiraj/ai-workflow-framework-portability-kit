# How obsidian-brain-eval Compares

> Feature matrix and qualitative comparison against the established Obsidian-RAG and retrieval-eval tooling. Updated 2026-06.

Most of the 2025-26 PKM tutorial wave on "RAG over my Obsidian vault" ships a *retrieval system* but never a way to *measure if it works*. This skill is the missing eval layer.

This page documents the trade-offs against:

- **Anecdotal vault chat** (ChatGPT / Claude / Gemini with your vault dumped in)
- **[Smart Connections](https://smartconnections.app/)** (Brian Petro's plugin, AI-native search)
- **[Obsidian Copilot](https://github.com/logancyang/obsidian-copilot)** (Logan Yang's plugin, full RAG)
- **Generic LLM eval pipelines** (LangChain `evaluate`, LlamaIndex `RagEvaluator`, ragas, DeepEval)
- **[obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor)** (the sibling skill — measures vault graph topology, not retrieval)

---

## Feature matrix

| Feature | obsidian-brain-eval | Anecdotal vault chat (ChatGPT/Claude/Gemini) | [Smart Connections](https://smartconnections.app/) | [Obsidian Copilot](https://github.com/logancyang/obsidian-copilot) | Generic RAG eval (ragas / LangChain) | [obsidian-graph-auditor](https://github.com/build-with-dhiraj/obsidian-graph-auditor) |
|---|---|---|---|---|---|---|
| Recall@k gate against gold-set | **yes** | no | no | no | yes (generic) | n/a |
| Vault-aware gold-set generator | **yes** | no | no | no | no (generic data only) | n/a |
| Pluggable retrieval backends | **yes** | no | no | partial | yes | n/a |
| Ships a zero-infra BM25 baseline | **yes** | no | no | no | partial | n/a |
| Default pass/fail threshold | **yes (0.85)** | no | no | no | no (you choose) | yes (8-dim) |
| CLI / scriptable | **yes** | no | no | partial | yes | yes |
| Cross-CLI skill compat | **yes** | no | no | no | no | yes |
| Before / after CI gate | **yes** | no | no | no | yes | yes |
| No GPT for the score step | **yes** | n/a | n/a | n/a | rarely | yes |
| Read-only | yes | n/a | yes | yes | yes | yes |
| Open source MIT | yes | no | yes (GPL) | yes (AGPL) | varies | yes (MIT) |
| Works on Logseq / Foam / Quartz | **yes** | partial | no | no | yes | yes |

---

## When to use each

### Use **obsidian-brain-eval** when you want:

- A **single number** for "is my vault chat working" and a graded PASS / BELOW TARGET report.
- A **CI gate** that fails when a retrieval system regresses.
- A **scriptable command-line** workflow that runs in any agentic CLI (Claude Code, Cursor, Gemini CLI, Codex).
- To **benchmark** Smart Connections vs Obsidian Copilot vs your own custom backend on YOUR vault, not some generic dataset.
- A vault-aware gold-set that catches the failure modes specific to *your* notes.

### Use **anecdotal vault chat** when you want:

- A quick gut-check that the vault is at least readable by an LLM.
- No commitment to a measurement methodology.

**Trade-off.** Anecdotal chat tells you nothing about whether the retrieval layer is working. It tells you whether *that single example* worked. The brain-eval gold-set turns the anecdote into a regression test.

### Use **Smart Connections** when you want:

- An **in-app, on-device, AI-native search and chat experience** that lives where you live (the Obsidian sidebar).
- Smart Connections is a *retrieval system*. obsidian-brain-eval is a *measurement layer*. They are **complementary**: run Smart Connections in your vault, then run brain-eval to measure whether Smart Connections' retrieval is actually returning the right notes on your gold-set. (You'd need a thin custom backend adapter — the skill ships the protocol; you bring the bridge.)

### Use **Obsidian Copilot** when you want:

- An **in-vault RAG chat** with hybrid retrieval and configurable embeddings (Logan Yang's plugin).
- Same dynamic as Smart Connections: Copilot is the retrieval+answer system, brain-eval is the eval gate.

### Use **generic RAG eval pipelines** (ragas, DeepEval, LangChain evaluate, LlamaIndex RagEvaluator) when you want:

- LLM-as-judge **answer-quality** evaluation (faithfulness, answer relevance, context precision).
- Multi-metric harnesses with calibrated judges.

**Trade-off.** Generic harnesses are vault-agnostic. They expect you to bring your own gold-set and your own retrieval system. obsidian-brain-eval is the **opinionated, vault-aware** generator + scorer that sits one layer below. A reasonable workflow is to use brain-eval for the retrieval gate and ragas for the answer-quality gate, once retrieval is passing.

### Use **obsidian-graph-auditor** when you want:

- A graded report of **vault graph topology** (link density, orphan rate, modularity, top-hub force-star).
- A different question: "is my vault *structurally* healthy?" (graph-auditor) vs "is my vault *answering* well?" (brain-eval).

The two tools are **complementary**. graph-auditor measures whether your second brain is well-connected; brain-eval measures whether it is well-retrievable. A vault can pass one and fail the other.

---

## What brain-eval does NOT replace

- **Smart Connections / Obsidian Copilot** for the actual retrieval and chat experience. brain-eval doesn't answer questions; it tells you whether the system that answers them is finding the right notes.
- **ragas / DeepEval** for answer-quality LLM-as-judge metrics. brain-eval stops at retrieval. Answer quality is a different problem.
- **obsidian-graph-auditor** for graph-topology audits. The two skills measure independent properties of the same vault.

A reasonable workflow:

1. Run **obsidian-graph-auditor** to baseline your vault's graph topology. Fix orphans, force-stars, modularity.
2. Set up a retrieval system (Smart Connections, Copilot, custom LanceDB stack).
3. Run **obsidian-brain-eval generate** to create a 40-question gold-set from your vault.
4. Run **obsidian-brain-eval score** to baseline Recall@10. Cross 0.85 before declaring victory.
5. Once retrieval clears the gate, run **ragas** or **DeepEval** for answer-quality eval.
6. Wire the brain-eval score into CI as a regression gate.

---

## Why this tool exists

The PKM ecosystem in 2025-26 has *retrieval systems* (Smart Connections, Obsidian Copilot, dozens of bespoke vault-RAG repos), *answer-quality harnesses* (ragas, DeepEval), and *graph audits* (obsidian-graph-auditor), but **nothing in between** that publishes a methodology and a default pass/fail threshold for "does the retrieval layer of your vault chat actually surface the right note?". There was no vault-aware gold-set generator and no opinionated Recall@k gate that ran from the command line in any agentic CLI. obsidian-brain-eval fills that gap.

The skill is also the **only tool in this list that you can run on a non-Obsidian vault** (Logseq, Foam, Quartz, or any markdown-with-wikilinks directory), because the gold-set generator and the scorer are both tool-agnostic.
