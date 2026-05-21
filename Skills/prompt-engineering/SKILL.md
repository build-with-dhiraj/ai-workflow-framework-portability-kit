---
name: prompt-engineering
description: Design, iterate, or debug LLM prompts — system prompts, few-shot, chain-of-thought, tool-use, eval rubrics. Triggers on "write a better prompt", "improve this prompt".
license: MIT
metadata:
  author: ai-engineer
  version: "1.0.0"
  date: May 2026
  abstract: Reference guide for prompt engineering covering anatomy, zero-shot to chain-of-thought progression, tool-use patterns, classification templates, RAG prompts, and versioning discipline. Based on the dair-ai Prompt Engineering Guide. Optimised for Claude models and SME rubric classifier use cases.
---

# Prompt Engineering Reference

Based on the [dair-ai Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide).

## When to Apply

- Writing or refining system prompts for Claude features
- Designing few-shot examples or CoT demonstrations
- Building classification prompts with locked SME rubrics
- Structuring RAG retrieval prompts
- Debugging LLM outputs that miss intent
- Instrumenting prompts for eval before shipping

---

## 1. Prompt Anatomy

Every effective prompt has four addressable slots:

| Slot | Purpose | Required? |
|---|---|---|
| **Instruction** | What the model must do | Always |
| **Context** | Background the model needs | Usually |
| **Input** | The actual data to process | Usually |
| **Output format** | Shape of the expected response | Always |

Omitting output format is the single most common source of inconsistent LLM behaviour.

```
[SYSTEM / INSTRUCTION]
You are a classification assistant. Given a customer message, return a JSON object
with keys `category` (string) and `confidence` (0–1 float). No prose.

[CONTEXT]
Categories: billing, technical_support, general_inquiry, escalation.

[INPUT]
Customer message: "{{message}}"

[OUTPUT FORMAT]
{"category": "...", "confidence": 0.0}
```

---

## 2. Zero-shot → Few-shot → Chain-of-Thought Progression

Escalate only when the simpler technique fails.

| Technique | When to use | Trade-off |
|---|---|---|
| **Zero-shot** | Simple, well-defined tasks; model has strong priors | Fastest, cheapest |
| **Few-shot** | Task needs format adherence or domain nuance | +tokens per call |
| **CoT (standard)** | Multi-step reasoning; math; rubric scoring | Much larger context |
| **Zero-shot CoT** | CoT benefit without writing examples | Slightly less precise than standard CoT |

Rule of thumb: start zero-shot, add few-shot if format drifts, add CoT if reasoning is wrong.

---

## 3. Chain-of-Thought (CoT)

### Standard CoT — include worked examples
```
Q: A rubric has 4 criteria each scored 1–5. Score: [3, 4, 2, 5]. Is the overall
   score above 14?
A: Sum = 3+4+2+5 = 14. 14 is not above 14. Answer: No.

Q: Score: [4, 4, 3, 5]. Is the overall score above 14?
A: [model continues reasoning]
```

### Zero-shot CoT — append the trigger phrase
```
Evaluate this response against the SME rubric. Think step by step before giving
your final score.
```

### CoT for locked rubrics (Ask AI / Chakra pattern)
When scoring against a fixed SME rubric, force the model to cite the rubric criterion
before assigning a score. This prevents hallucinated justifications.

```
For each criterion below, quote the relevant excerpt from the response, then
assign a score (1–5). Only after scoring all criteria give the aggregate.
```

---

## 4. Tool-Use / Function-Calling Prompts

Claude's tool-use depends on crisp tool descriptions. Treat each tool description as a mini prompt.

```python
tools = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Search the internal knowledge base for information relevant to a user question. "
            "Use when the user asks about product features, pricing, or policies. "
            "Do NOT use for general world knowledge — only internal docs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Concise search query, max 15 words"}
            },
            "required": ["query"]
        }
    }
]
```

Key rules:
- State what the tool does AND when NOT to use it
- Constrain input fields with descriptions and formats
- One tool per responsibility — avoid Swiss-army tool descriptions

---

## 5. Classification Prompt Template (SME Rubric)

```
[SYSTEM]
You are a strict evaluator using the rubric below. Return only valid JSON.
Do not infer intent beyond what is stated in the rubric.

RUBRIC (locked — do not modify):
{{rubric_text}}

[USER]
Evaluate the following response.

Response: """{{response_text}}"""
Reference answer: """{{reference_text}}"""

Output format:
{
  "scores": {"criterion_1": <int 1-5>, "criterion_2": <int 1-5>, ...},
  "aggregate": <float>,
  "reasoning": "<one sentence per criterion>"
}
```

Failure modes to avoid:
- Leaking the rubric-modification instruction into the user turn
- Asking for scores and prose in the same turn without a separator
- Omitting the reference answer when the rubric is comparative

---

## 6. RAG Prompt Template

```
[SYSTEM]
Answer the user's question using ONLY the provided context.
If the context does not contain sufficient information, say "I don't have enough
information to answer that." Do not fabricate facts.

[CONTEXT]
{{retrieved_chunks}}

[USER QUESTION]
{{question}}
```

Checklist before shipping a RAG prompt:
- [ ] Grounding instruction is in the SYSTEM turn, not user turn
- [ ] Model is told what to say when context is insufficient
- [ ] Retrieved chunks are clearly delimited (e.g., `---` between chunks)
- [ ] Output format is specified if structured output is needed

---

## 7. Common Failure Modes

| Failure | Symptom | Fix |
|---|---|---|
| **Under-specification** | Output length/format varies wildly | Add explicit output format slot |
| **Conflicting instructions** | Model alternates between behaviours | Audit system + user turns for contradictions; put the authoritative rule in SYSTEM |
| **Role confusion** | Model breaks character or ignores persona | Define role with negative examples: "You are X. Do not do Y." |
| **Prompt injection** | User input overrides system instructions | Delimit user content: `User input: """{{input}}"""` |
| **Hallucinated tool calls** | Model invents tool arguments | Add `"required"` fields + description constraints to input schema |
| **Rubric drift** | Scores shift across runs with same input | Pin temperature to 0; add CoT + cite-before-score pattern |

---

## 8. Prompt Versioning Discipline

Treat prompts as code. A prompt change without an eval is a blind deploy.

```
prompts/
  classifier/
    v1.0.0.md       # baseline
    v1.1.0.md       # added CoT
    v1.2.0.md       # tightened output format
  rag/
    v1.0.0.md
```

Checklist before shipping a prompt change:
- [ ] New version file committed (never overwrite in place)
- [ ] Eval run on held-out set (same set across versions for comparability)
- [ ] Delta metrics recorded: accuracy, format compliance, latency, cost
- [ ] Rollback path tested (old version still in repo and deployable)
- [ ] Change summarised in commit message: what changed and why

For Claude models, also record: model version pinned, `temperature`, `max_tokens`, and any `top_p` / `top_k` settings — these affect output distribution as much as the prompt text.

---

## References

- https://github.com/dair-ai/Prompt-Engineering-Guide
- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- https://www.promptingguide.ai/
