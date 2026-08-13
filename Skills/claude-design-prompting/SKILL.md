---
name: claude-design-prompting
description: How to write effective prompts for Claude Design (claude.ai/design), for both creating new designs and editing existing prototypes, decks, or pages. Use this skill whenever the user wants to prompt Claude Design, iterate on a Claude Design project, convert feedback or a spec into Claude Design instructions, or asks for a "design prompt", "edit prompt", "prototype prompt", or paste-ready prompts for any claude.ai/design project, even if they don't name Claude Design explicitly.
---

# Claude Design prompt writing

Claude Design builds a first version you react to, then you refine in rounds. Prompts that fight this model (one giant do-everything prompt) produce worse results than prompts that work with it. Everything below is grounded in Anthropic's prompting best practices, the Claude Design support docs and tutorials, and the frontend-aesthetics cookbook.

## Pick the right channel first

Claude Design has three editing channels. Choosing wrong wastes rounds:

- **Chat prompt**: structural or repeated changes (new sections, status models, table columns, a pattern applied across the screen). This skill is about these.
- **Inline comment on an element**: one-element nits (padding, a label, one button). Don't write a chat prompt for these. Known issue: inline comments occasionally fail to persist; re-check after applying.
- **Canvas editor**: drag, resize, align. No prompt needed.

## The edit-prompt formula

One concern per prompt, delivered as a sequence. Each prompt:

1. **Scope line first.** Name the screen or region being edited, and what must not change. Claude Design edits eagerly; an explicit freeze list is the single highest-value sentence. Example: "Edit the All Labs table only. Leave the modals, tabs, and toolbar unchanged."
2. **Numbered, ordered instructions.** Sequential numbered steps, one visible change each, naming the element as the user sees it ("the Created by column", "the caption under the toolbar", "slide 3"). Never describe changes by code or file location; describe what is visible.
3. **State the why when it constrains the solution.** Claude generalizes from motivation: "the team manages 1,000+ accounts, so no plain scroll list" gets a type-ahead everywhere it matters; a bare "add search to the filter" gets one search box.
4. **Exact copy in quotes.** Any label, caption, or microcopy the design must show is given verbatim in quotes, not paraphrased.
5. **Sample data is part of the design.** If the change implies different data (a new status, a different persona in a column), say what the sample rows should now show. Claude Design edits data and layout together.
6. **Ban words explicitly, with the reason.** "Never use the word Published anywhere; it is reserved for article publishing" outperforms hoping it won't appear.

Sequence the prompts so later ones build on earlier ones, and look at the canvas between rounds. Three focused prompts with checks beat one exhaustive prompt: docs and tutorials are explicit that iterative refinement is the intended workflow.

**End the sequence with a regression check prompt**: ask Claude Design to review the whole screen, confirm the freeze list did not move, and list anything it changed that was not requested. This mirrors the tutorial's validate-before-handoff step.

## The creation-prompt formula

For a new design, cover four things in the first prompt (the support docs' own structure): the **goal** (what this is), the **layout** (arrangement, key sections), the **content** (real information to display, not lorem ipsum), and the **audience** (who uses it). Concrete beats abstract: "a settings page with sections for account, billing, notifications" beats "a settings page". Ask for "a fully-featured implementation, beyond the basics" when you want richness; Claude under-delivers on vague prompts. Flag edge states (empty, error, loading) before handoff; they don't appear unless asked.

## Design system rules

- If the project has an imported design system, reference its components **by name** ("use the Primary Button component", "the design system's chip component") and name the variant to add if one is missing ("adding an amber variant"). Output is validated against the system, so on-system asks are cheap and off-system asks fight the validator.
- No design system in the project? Prevent the AI-slop default by specifying aesthetics yourself: distinctive fonts (never Arial/Inter/Roboto), a committed palette with dominant colors and sharp accents (no purple-gradient-on-white), one orchestrated load animation over scattered micro-interactions, and backgrounds with depth. See `references/aesthetics-block.md` for the paste-ready fragment.
- Real examples teach the system more than specs: a finished page in the project shapes output more than a token list.

## What travels badly into a Design prompt

- Internal vocabulary (ticket IDs, decision numbers, meeting references, file paths). The prompt describes visible UI only.
- Backend-only requirements. If nothing on screen changes, it does not belong in the prompt.
- Unsettled decisions. Prototyping an open question makes it look decided; keep an explicit "excluded until decided" list next to your prompt sequence.
- More than one concern per prompt. If the prompt needs section headers, split it into that many prompts.

## Worked example

A meeting decides emails should replace names in a table. The prompt:

> Edit the All Labs table only; leave the modals and tabs unchanged. 1. In the "Created by" and "PI" columns, make the email address the primary line with the person's name below it as a smaller grey caption, in the same cell. Remove the hover tooltip that currently reveals the email; nothing should be hover-only. 2. Keep the dash placeholder in the PI column for unassigned rows. 3. Do not change the "Lab name" column. Update the sample rows so faculty rows show faculty emails, never staff. Use the design system's existing caption text style.

Scope guard, numbered visible changes, explicit non-change, sample data, design-system reference: every element of the formula in five sentences.

## Environment facts worth knowing (post June 17 beta)

Design systems import from GitHub, design files, or raw upload, and outputs are validated against them. Two-way Claude Code sync exists (`/design-sync` from Code, `/design` in Design). Export: HTML, PPTX, PDF. Usage draws from the same pool as chat and Claude Code. Team caveats: permissions take up to 15 minutes to apply, simultaneous multi-person editing is unreliable, and there are no audit logs of design edits. Guidance written before June 17 describes a different product; distrust it.
