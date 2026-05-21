---
name: Evaluating Skill Necessity
description: Gate — assess value and redundancy of new skills before creation/import. Use FIRST when a new skill is proposed.
---

# Evaluating Skill Necessity

This skill serves as the **Mandatory First Step** before adding any new capability to the agent's library. It prevents skill bloat and ensures high-quality, non-redundant instructions.

## The Necessity Protocol
Whenever a new skill is proposed, follow this 4-step analysis:

### 1. Problem Definition
- What specific, repeatable task does this skill address?
- Is it a "Fragile" task (requires exact commands) or a "Flexible" task (requires heuristics)?

### 2. Redundancy Audit (Internal)
- Does the agent's base system prompt or model capabilities already handle this optimally?
- *Rule*: Do not create a skill for "General Writing" or "Basic Coding" as these are core model strengths.

### 3. Redundancy Audit (Library)
- Search the existing `.agent/skills/` directory for overlapping keywords.
- Does an existing skill already provide the necessary context?
- *Tip*: If an existing skill covers 80% of the need, consider **Updating** that skill instead of creating a new one.

### 4. Value Proposition
- Does this skill provide **Specific Scripts**, **Validated Workflow Checklists**, or **Design Tokens** that aren't easily hallucinated or researched?
- Does it enforce a **Mandatory Protocol** (like TDD or B.L.A.S.T.)?

## Decision Logic
- **PROCEED** (Needed): Unique operational value, specific technical constraints, or mandatory business protocols.
- **REJECT** (Redundant): General knowledge, already covered by standard model capabilities, or purely informational without actionable workflows.

## Mandatory Invocation
This skill **MUST** be invoked as the primary skill during the PLANNING phase of any "New Skill" task.
