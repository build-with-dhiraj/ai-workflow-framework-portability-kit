# Reading and auditing an existing flow

The job here is answering "what does this thing actually do", usually because a decision
depends on it. The failure mode is not being unable to read the flow. It is reading the
account of the flow instead: the person who built it, the docs, a summary someone wrote.
Those drift from the graph, and the graph is what runs.

## Why this is harder than it looks

A Flowise flow is stored as one row with a `flowData` column, and that column is a **JSON
string containing the node graph**. So the object you get from the API has a field that
looks like data but is text. Parse it or the flow looks empty.

Inside the graph, three more encodings sit between you and the meaning:

| What you want | What you get | Why |
|---|---|---|
| Prompt text | HTML with `<p>`, `<span>`, `&nbsp;`, `&quot;` | Prompts are authored in a rich-text editor that stores markup |
| Custom function code | One long line with literal `\n` | JS bodies are JSON-transported |
| Variable bindings | `<span class="variable" data-id="$flow.state.x">{{ $flow.state.x }}</span>` | The editor wraps every mention |

`scripts/flowise.mjs` handles all three. Use it rather than fetching and squinting.

## The order that works

**1. Map before you read.** `flowise.mjs nodes "<flow>"` gives every node with its kind and
its byte size. Size is a good proxy for where the logic lives: a 50KB custom function is
doing real work, a 600-byte condition node is a switch. You will usually find that two or
three nodes carry the flow and the rest are plumbing.

**2. Read the data contract next, not the prompts.** `flowise.mjs vars "<flow>"` lists every
`{{ }}` reference and which nodes touch it. This is the fastest way to understand a flow,
because state keys are named by the person who understood the problem. A key referenced by
most of the nodes is the flow's spine.

**3. Then the prompts.** `flowise.mjs prompts "<flow>"` gives every prompt field, decoded,
with its node and character count. Read the longest ones first; prompt length tracks how much
judgment was pushed into the model.

**4. Then the code, only where it matters.** `flowise.mjs code "<flow>" --node "<label>"`
gives the JS body plus the input variables it receives. The input variables are the useful
part: they tell you what state the function reads before you read a line of its logic.

## What to be suspicious of

**A prompt that asks for a judgment the payload cannot support.** This is the highest-value
thing an audit finds. Check what the model is actually given against what it is asked to
decide. A prompt saying "select the most relevant videos" while the payload carries only
titles is asking for a judgment on evidence that is not there, and no amount of prompt
tuning fixes it. Read the node that *builds* the payload, not just the node that consumes it.

**Fallback paths that run silently.** Flows often keep an older path for when the new one
throws. If nothing logs which path ran, behaviour differs between requests with no signal.
Grep the code nodes for `catch` and for comments containing "legacy", "fallback", "safety
net". Then ask whether anyone can tell, after the fact, which path served a given request.

**Instructions with no enforcement.** A prompt saying "never return more than 20" is a
request, not a constraint. Look for whether the consuming code also truncates. Where it does
not, the cap is advisory.

**Stale duplicates.** A flow named `X dev` or `[PREVIEW] X` next to `X` is common, and the
copy often has an older prompt. Before quoting a prompt as current, confirm you read the one
that serves production, and check `deployed` on the flow. If two flows differ, `flowise.mjs
diff` on two saved exports tells you exactly which nodes changed.

## Comparing two flows honestly

When the question is "why does A work better than B", resist the architectural answer. Both
usually have the same shape. The differences that matter are almost always in:

1. **What reaches the model**, per item, after any compacting step. Find the function that
   builds the candidate/context objects and read what fields survive.
2. **Whether raw human input is normalised before use.** A flow that always passes user text
   through an LLM step before searching behaves very differently from one that sometimes uses
   the text directly, and the difference only shows on the path a human touched.
3. **Whether the flow ever asks.** Disambiguation steps are invisible in a node map but
   change output quality more than any prompt wording.
4. **The corpus or filters**, which are often different even when the flows look identical.

State each of these as "verified in node X" or say you did not check it. An audit that
cannot cite the node is an opinion.

## Recording what you found

An audit is worth little if it lives in a chat. Write the extracted prompts to a file next to
your notes, with the flow id, the node label, and the date you pulled it. Prompts change
without any version history a reader can consult later, so your export is the only record
that a given prompt said a given thing on a given day. `--out` writes directly.
