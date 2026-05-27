---
name: llm-eval
description: Build LLM eval suites, run prompt regression tests, score AI outputs with deepeval. Triggers on "eval this prompt", "build eval suite", "hallucination check".
dispatch_to: ai-engineer
license: MIT
metadata:
  author: priyanshu
  version: "1.0.0"
  date: May 2026
  abstract: Teaches Claude how to build LLM evaluation suites using deepeval (confident-ai/deepeval), wire results into Langfuse for persistence, and surface metrics in Metabase. Covers core metrics, pytest structure, LLM-as-judge custom rubrics, and CI integration. Designed for Ask AI / Chakra AI EdTech context with locked SME rubrics.
---

# LLM Eval with deepeval

## When to Use deepeval vs Spot-Checking

| Situation | Approach |
|---|---|
| New prompt variant before ship | deepeval regression suite |
| >20 test cases or automated CI | deepeval + Langfuse persistence |
| One-off "does this look right?" | Manual spot-check |
| SME rubric that must be locked and versioned | deepeval G-Eval + Langfuse dataset |
| RAG pipeline (Ask AI / Chakra AI) | Faithfulness + ContextualPrecision + Hallucination |

Rule of thumb: if you'd manually check the same thing twice, automate it.

## Installation

```bash
pip install -U deepeval langfuse
deepeval login   # optional: connects to Confident AI dashboard
```

## Core Metrics — Use These First

```python
from deepeval.metrics import (
    GEval,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)
from deepeval.test_case import LLMTestCase, SingleTurnParams

# 1. G-Eval — custom rubric (SME-locked criteria go here)
sme_rubric = GEval(
    name="CurriculumCorrectness",
    criteria=(
        "The answer must be factually accurate per NCERT Class 10 syllabus. "
        "Penalise any out-of-syllabus content or incorrect formulae."
    ),
    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
        SingleTurnParams.EXPECTED_OUTPUT,
    ],
    threshold=0.75,
)

# 2. Answer Relevancy — does the response address the question?
relevancy = AnswerRelevancyMetric(threshold=0.7)

# 3. Faithfulness — response grounded in retrieved context (RAG)
faithfulness = FaithfulnessMetric(threshold=0.8)

# 4. Hallucination — detects contradictions with context
hallucination = HallucinationMetric(threshold=0.2)  # lower = stricter
```

## Dataset Format

```python
LLMTestCase(
    input="What is the formula for kinetic energy?",          # user query
    actual_output=your_llm_response,                          # live LLM call
    expected_output="KE = 0.5 * m * v^2",                    # golden answer
    retrieval_context=["Kinetic energy is the energy ..."],   # RAG chunks; omit if non-RAG
)
```

## Pytest-Style Test Structure

```python
# tests/test_chakra_ai.py
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from your_app import get_ai_answer  # your production call

CASES = [
    ("What is KE formula?", "KE = 0.5mv²", ["...context chunk..."]),
    ("Define photosynthesis", "Process by which plants...", ["...chunk..."]),
]

@pytest.mark.parametrize("question,expected,context", CASES)
def test_curriculum_answers(question, expected, context):
    response = get_ai_answer(question)
    tc = LLMTestCase(
        input=question,
        actual_output=response,
        expected_output=expected,
        retrieval_context=context,
    )
    assert_test(tc, [sme_rubric, faithfulness, hallucination])
```

Run with:
```bash
deepeval test run tests/test_chakra_ai.py
# or standard pytest (deepeval hooks in automatically)
pytest tests/test_chakra_ai.py -v
```

## Langfuse Export Integration

deepeval does not natively push to Langfuse. Bridge via Langfuse SDK after evaluation:

```python
from deepeval import evaluate
from langfuse import Langfuse

lf = Langfuse()  # reads LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST from env

test_cases = [...]  # list of LLMTestCase
results = evaluate(test_cases, [sme_rubric, relevancy, faithfulness, hallucination])

for result in results.test_results:
    lf.score(
        trace_id=result.test_case.input,  # use your actual trace_id if available
        name=result.name,
        value=result.score,
        comment=result.reason,
    )
lf.flush()
```

If your production LLM calls already go through Langfuse tracing (`@observe()` decorator or SDK), capture `trace_id` at call time and pass it into `LLMTestCase` as a custom field, then use it as the `trace_id` in `lf.score()`. This links eval scores to the exact trace in Langfuse → queryable in Metabase.

## LLM-as-Judge for Locked SME Rubrics

For Chakra AI's locked SME rubric pattern — where subject experts define pass/fail criteria that must not drift:

```python
# evals/rubrics/physics_g10.py  — version-controlled, SME-owned
PHYSICS_G10 = GEval(
    name="PhysicsG10",
    criteria="""
    Score 1.0: Correct formula, correct units, matches NCERT exactly.
    Score 0.7: Correct concept, minor unit error.
    Score 0.3: Partially correct, missing key term.
    Score 0.0: Wrong or hallucinated.
    """,
    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
        SingleTurnParams.EXPECTED_OUTPUT,
    ],
    threshold=0.7,
    model="gpt-4o",  # judge model — keep separate from the model under test
)
```

Keep rubric files in `evals/rubrics/` under version control. SMEs edit the criteria string; engineers wire it into tests. Never auto-generate rubric content from the model being evaluated.

## CI Integration (GitHub Actions)

```yaml
# .github/workflows/llm-eval.yml
name: LLM Eval Suite
on:
  pull_request:
    paths: ["prompts/**", "evals/**", "src/ai/**"]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -U deepeval langfuse
      - run: deepeval test run tests/test_chakra_ai.py --exit-on-first-failure
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
          LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
          LANGFUSE_HOST: ${{ secrets.LANGFUSE_HOST }}
```

Gate PRs on eval pass. Scores land in Langfuse automatically via the export step above, then Metabase queries the `scores` table for trend dashboards.

## Metabase Query (Langfuse scores table)

```sql
-- Average eval scores by metric over time (Langfuse Postgres)
SELECT
    date_trunc('day', created_at) AS day,
    name AS metric,
    round(avg(value)::numeric, 3) AS avg_score,
    count(*) AS n
FROM scores
WHERE created_at > now() - interval '30 days'
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

## References

- https://github.com/confident-ai/deepeval
- https://docs.confident-ai.com/
- https://langfuse.com/docs/scores/custom
