# Transferring what works from one flow to another

The situation: flow A is trusted, flow B does something similar and is not. Someone asks what
to copy. This comes up constantly once an organisation has more than one AI feature, and it
is where most of the value in reading flows actually sits.

It is also where the obvious approach fails. Two flows that do "the same thing" almost always
have the same architecture, so an architectural comparison returns "they are basically the
same" and the question stays open. The differences that matter are one level down.

## Do not start from anyone's account of the flow

The person who built A will tell you what they intended, in good faith, and be wrong in a
specific way that costs you a sprint. They remember the design, not the current graph, and
flows get edited.

A real example. Asked what his curation step showed the model about each video, the owner of
a well-regarded flow answered "video title, video description, transcript, all of them". The
flow's own code reduced every candidate to three fields first:

```js
function compactCandidate(video) {
  return { id: Number(video.articleId), t: String(video.title), ty: video.articleType };
}
```

Title and type. A plan built on that answer would have spent a sprint enriching a payload
that was already identical to the other flow's. Read the graph, then ask the human about the
parts the graph does not explain, which are the reasons rather than the facts.

## Compare these layers, in this order

Architecture is the last thing to compare, not the first. Work up from the data.

**1. Input acquisition.** Where does the seed come from? A typed topic, an uploaded document,
a record in a database, another system's output. This usually differs, and it constrains
everything downstream. It is also the layer people wrongly assume is equivalent.

**2. Input normalisation, and whether it is unconditional.** Does raw human text ever reach
the retrieval step directly? A flow that always converts input into normalised search terms
through an LLM step behaves very differently from one that does so only on some paths. Check
every path, including the manual one, the edit one, and the retry one. Silent degradation on
the human-touched path is one of the most common real defects, because the happy path demos
fine and the humans who complain are the ones who edited something.

**3. Disambiguation.** Does the flow ever stop and ask? A clarification step is invisible in a
node map and changes output quality more than any prompt wording, because it converts a wrong
answer into a question. If A asks and B never asks, that is a finding on its own.

**4. Retrieval.** Endpoint, filters, corpus, and breadth expressed as queries × results per
query. Two flows hitting "the same search" often filter to different content types, so "A
works well" may not be a claim about the same library at all.

**5. Payload construction. Check this before the prompts.** Find the function that builds the
objects handed to the model and list exactly which fields survive. This is the single most
commonly missed layer, because it lives in a custom function nobody opens while the prompt is
right there and readable. A model asked to judge relevance on titles alone cannot do it,
however the instruction is worded.

**6. The instruction.** Now read the prompts. Compare what each asks for, what it forbids, and
whether it permits under-delivering rather than padding. Note that the weaker flow's prompt is
often *better written*, which is a useful signal in itself: it means the gap is not the prompt.

**7. Output contract.** Structured output, schema validation, what happens when the model
returns something unparseable, and whether a fallback path exists.

**8. The feedback loop.** What is measured, and what was tuned against it.

## The three findings this usually produces

**A step exists in one flow and not the other.** The transferable unit is a step, not prompt
text. "Add a normalisation step before retrieval" is a real recommendation; "use their prompt"
almost never is, because prompts are shaped by their surrounding steps.

**The payload differs.** Cheap to fix, large effect, and invisible from the UI.

**The quality came from a loop, not an artifact.** If A was tuned over months against real
usage, the thing that made it good is the measurement that made tuning possible. You cannot
copy that as text. If B measures nothing, then instrumenting B is a precondition for
improving it, not a follow-up task. Say this plainly, because it reframes an observability
ticket from a chore into the thing that unblocks the strategy.

## Ask what the target has that the source does not

Transfer discussions default to the target being behind. Check whether that is true at the
input layer. A flow seeded from a researcher's actual publications holds far more context than
one seeded from a typed topic. If the richer-input flow produces worse output, the problem is
not a missing recipe, it is that the extra context is being discarded somewhere. Find where.

That inversion is worth stating to whoever asked, because it changes the goal from catching up
to using what you already have.

## Write the comparison as a table of verified claims

Every row should say which node or file it was verified in, or say it was not checked. A
comparison that cannot cite the node is an opinion, and this analysis usually ends up in front
of people making scheduling decisions.

| Layer | Flow A | Flow B | Verified in |
|---|---|---|---|
| Input | typed topic | source documents | A: node 0, B: service entrypoint |
| Normalisation | always, LLM step | only on the extracted path | A: node 18, B: DTO coercion |
| Disambiguation | asks when polysemous | none | A: node 2 |
| Payload per item | id, title, type | id, title, type | A: compactCandidate, B: builder fn |
