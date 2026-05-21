---
name: Evaluating Agent Behavior
description: Build agent behavioral evals — tool choice, steerability, constraint compliance. Triggers on "behavioral eval".
---

# Evaluating Agent Behavior

Behavioral evaluations (evals) validate the agent's decision-making, such as tool choice and steerability.

## Workflow Decision Tree
1. **Does it need validation?**: If a prompt or tool change affects decision-making, it requires an eval.
2. **Choosing the Rig**:
   - **appEvalTest (AppRig)**: For UI-heavy or complex interactive flows.
   - **evalTest (TestRig)**: For logic-focused behavior.
3. **Policy Setting**:
   - **USUALLY_PASSES**: For new tests.
   - **ALWAYS_PASSES**: For established tests to lock in regressions.

## Checklist
- **Setup Workspace**: Initialize the test environment.
- **Write Assertions**: Define the expected tool calls or behavioral markers.
- **Verify**: Run the eval suite and analyze failures.
---
[google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
