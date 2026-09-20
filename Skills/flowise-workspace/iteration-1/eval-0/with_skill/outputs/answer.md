# AI Playlist — what the curation model sees, what it's told, and what state the flow carries

Read from the live graph on `https://internal-host.example.com`, flow **AI Playlist**, id
`fe20a92c-9245-484b-88a9-155cbb1889cc`, type `AGENTFLOW`, 28 nodes / 29 edges,
`updatedDate = 2026-08-14`, `deployed = false`. Pulled 17 Aug 2026.

Note there is a second flow named **AI Playlist dev** (`6e4cfab8-…`). It is **not** a copy of this
one — it's an older 10-node design with 5 state keys and different node names
(`Parsing your request...`, `Re ordering playlist content...`). Don't quote one for the other.

---

## The short version

When the system decides which videos go into the playlist, the model sees **three fields per
video: the numeric article id, the title, and the article type.** That is all. No abstract, no
description, no duration, no date, no transcript, no relevance score, no thumbnail.

It is told to act as a PhD subject-matter expert and pick "the strongest teaching sequence,"
ordering videos "from simplest to most advanced" — a pedagogical judgement it is asked to make
from titles alone. The prompt is explicit that this is the evidence base: *"Use ty and t to choose
the best representative video when titles overlap."*

The richer metadata is not missing from the system — it's held back deliberately and re-attached
after the model answers. That is the design point worth having straight in the meeting.

There is also **one likely bug** in the state wiring, covered at the end. Read it before the
meeting.

---

## 1. Which node makes the decision

The curation path is three nodes:

| # | Node | Kind | Role |
|---|---|---|---|
| 04 | `Searching JoVE library...` | `customFunctionAgentflow_1` (42 KB) | Queries the catalog, **builds the payload** |
| 06 | `Organizing playlist...` | `llmAgentflow_2` (12 KB) | **The model that selects, labels and sequences** |
| 07 | `Building curated response...` | `customFunctionAgentflow_2` (53 KB) | Turns the selection back into a draft playlist |

`Organizing playlist...` runs **`gpt-5.6-luna`** via a `chatOpenAICustom` model node, with
`streaming: false`, `llmEnableMemory: false`, and a structured-output schema enforced.

Its **entire user message** is two lines:

```
curation_context:
{{ $flow.state.curation_context }}
```

So everything the model knows about the catalog comes from that one object.

---

## 2. What the model gets to see about each video

`curation_context` is built in node 04 by `buildCurationContext(...)`. Every video — whether freshly
searched or already in the user's draft — is put through this function first:

```js
function compactCandidate(video) {
  return {
    id: Number(video && video.articleId),
    t: String((video && video.title) || ""),
    ty: (video && video.articleType) || null,
  };
}
```

**Three fields:**

| Field | Content |
|---|---|
| `id` | JoVE numeric article id |
| `t` | Video title, as a string |
| `ty` | Article type — e.g. `jove_core`, `jove_education`, `science_education` |

### What the model never sees

- **No abstract, description, or excerpt.** Worth being precise about where this is lost: for
  freshly searched videos, `normalizeVideo()` in node 04 keeps only `articleId`, `title`,
  `headerImage`, `articleType`, `topic`, `isSubscribed` from the `/api/free/search/search_ai`
  response. The abstract is dropped at ingest and never enters the flow at all. For videos already
  in the draft, `draftArticlesAsVideos()` *does* carry an `excerpt` — and then `compactCandidate`
  strips it before curation. So an excerpt exists in memory and is withheld.
- **No duration, publication date, authors, journal/section, keywords, or transcript.**
- **No relevance or rank score** from the search API. Ordering by relevance is not available to it.
- **No indication of which search keyword surfaced a given video.** The subtopic list is supplied
  once at the top level, not attached per candidate — so the model can't tell which subtopic a
  video came back for.
- **No thumbnail**, and `isSubscribed` is stripped before curation (`stripSubscriptionFlag`).

### What it does get around the candidate list

`curation_context` carries these top-level fields alongside `candidates`:

- `mode` — `"new"`, `"append"`, or `"recalibrate"`
- `topic`, and `subtopics` (the keyword list from node 18, `Analyzing your Topic...`)
- `requested_count`, `available_count`; in recalibrate also `target_count`, `new_slots`,
  `direction`, `full_recreate`
- `existing_labels` and `existing_article_ids` (so it can append without duplicating)
- `must_keep_ids` — recalibrate only

### How many candidates

`candidateLimit = queries.length * perPage`. Normal mode: up to **20 queries × 24 results = 480**
candidates. First-time creates use a reduced policy (`initial_limited`): **10 × 10 = 100**. The list
is then deduplicated by article id and by a normalized title key, and filtered by subscription
category. So the model is typically choosing ~20 videos out of a few hundred title strings.

---

## 3. What instruction it is given

Full system prompt, 3,925 characters. It opens:

> "You are a Subject Matter Expert holding a PhD, assigned to create a playlist using www.jove.com
> videos for a university professor. Your task is to select, label, and sequence the strongest
> relevant teaching videos from curation_context.candidates."

**Three modes** it must branch on, read from `curation_context.mode`:

- **`new`** — build a fresh playlist from the candidates.
- **`append`** — curate only the newly searched videos; do not rewrite, remove, reorder, rename or
  regroup existing labels. Reuse an existing label title *exactly* when a new video fits it —
  matching titles are treated as merge instructions by the response builder. Avoid ids in
  `existing_article_ids`.
- **`recalibrate`** — rebuild the whole playlist to `target_count`. Every id in `must_keep_ids`
  MUST appear; up to `new_slots` additions allowed.

**Selection rules** (the judgement calls):

- "requested_count is the maximum number of videos to select for this operation" (new/append);
  `target_count` is the final size in recalibrate.
- "Prefer the strongest teaching set; do not try to create a comprehensive playlist unless the
  requested count is large enough."
- "Prefer the strongest teaching sequence over raw relevance alone."
- "Prefer introductory videos before advanced videos when both are relevant."
- "Avoid duplicate or near-duplicate titles unless they clearly cover different content."
- **"Use ty and t to choose the best representative video when titles overlap."**
- "Include specialized, procedural, applied, advanced, and teaching-adjacent videos only when they
  strengthen the selected set."

**Labelling rules:** concise, specific, learner-useful labels; generic ones ("Fundamentals",
"Methods", "Applications", "Advanced Topic") only when genuinely clearest; split labels that get
broad; every selected video in exactly one label.

**Ordering rules:** labels in best teaching flow; videos within a label simplest → most advanced;
where two are similar in level, the broader/more foundational first.

**Output rules:** JSON only; don't invent videos or ids; copy the compact candidate objects
*exactly*; preserve `id`, `t`, `ty`; do **not** add `headerImage`, `isSubscribed`, `metrics`,
`isNew` or profile fields. Required shape:

```json
{ "title": string,
  "labels": [ { "title": string, "videos": [ {id, t, ty} ] } ],
  "unlabeledVideos": [] }
```

This is backed by a real `llmStructuredOutput` JSON schema on the node, which marks `id` (number),
`t` (string) and `ty` (string) as required — so the shape is enforced, not merely requested.

### The point to make in the meeting

The prompt asks for pedagogical sequencing — foundational before advanced, simplest to most
advanced, "strongest teaching set" — and gives the model **title and type only** to do it with. For
JoVE titles, which are often long and descriptive, that may be enough; but nothing in the payload
distinguishes an introductory treatment from an advanced one except the wording of the title. The
instruction "use `ty` and `t` to choose the best representative video" is the prompt conceding this
directly. If curation quality is the agenda item, this is the lever — and it is a payload change in
node 04, not a prompt change in node 06. No amount of prompt tuning adds evidence that was never
sent.

### Why it's built this way (the defence)

It's a deliberate token-cost trade, not an oversight. `Building curated response...` re-attaches
everything afterwards — `hydrateVideo()` looks up each returned `id` in
`searchContext.candidate_videos` (the full, un-compacted list) and restores `title`, `headerImage`,
`articleType`, `topic`, `excerpt` and `url`. The model round-trips an id; the system fills in the
rest. With up to 480 candidates, sending abstracts would be a very large prompt on every turn. So
the honest framing is: *this is a cost/quality trade that was made, and it can be revisited
selectively* — e.g. sending excerpts only for a top-N shortlist.

### Two instructions that are advisory, not enforced

Worth knowing before someone asks "but doesn't it cap the count?":

- **The count cap holds in two modes out of three.** In `new` mode the builder trims
  (`trimDraftToCount(baseDraft, requested)`), and in `recalibrate` there's a hard cap
  (`if (ordered.length > targetCount) …`). In **`append` mode there is no trim** —
  `appendCurationToDraft()` accepts whatever the model returned. So "requested_count is the
  maximum" is a request, not a constraint, when appending.
- **"Do not invent ids" is only enforced in recalibrate.** `requireCandidateMembership: true` is
  passed in the recalibrate path only. In `new` and `append`, `dedupeArticles` is called without it,
  so a hallucinated id would pass through and become a stub article carrying the model's own title
  with no real metadata behind it.

---

## 4. What state the flow carries between steps

The Start node (`startAgentflow_0`) declares **37 keys**, with `startPersistState: true` and
`startInputType: chatInput`, no ephemeral memory.

`startPersistState: true` matters: state survives **across turns of a chat session**, not just
within a single execution. That's what makes the clarification loop ("which meaning of 'cell' did
you want?") work across messages.

| Group | Keys |
|---|---|
| **Playlist working set** | `draft_playlist` (the spine — touched by 16 of 28 nodes), `ui_draft_playlist`, `manual_selection_draft`, `draft_binding`, `saved_playlist`, `saved_playlists`, `bootstrap_mode` |
| **Topic & search** | `topics`, `pending_topic`, `search_keywords`, `available_count`, `requested_count`, `include_research_videos` |
| **Conversation control** | `phase` (initial value `"greeting"`), `last_intent`, `pending_action`, `clarification_response`, `turn_status`, `turn_resolution` |
| **Clarification resolver** | `resolver_context`, `resolver_status`, `resolver_option_id`, `resolver_value`, `resolver_confidence` |
| **Routing** | `validated_plan`, `validated_route` |
| **User / session** | `user_access_token`, `user_profile`, `user_access_decision`, `referrer` (defaults to `https://www.jove.com/`) |
| **Page context (inbound)** | `page_context`, `page_info`, `current_article_id`, `current_article_content`, `current_video_transcript` |
| **Misc** | `selected_lms`, `share_action` |

Three things worth knowing about how this state is used:

- **`draft_playlist` is the flow's spine.** It is read or written by 16 nodes and is explicitly
  treated as source of truth for manual UI edits — the edit prompt says "Treat it as the source of
  truth, including manual UI label changes, video removals, reorders, and prior edits."
- **`manual_selection_draft` is deliberately kept separate from `draft_playlist`.** The planner
  prompt is emphatic: when both are non-empty with different `draftId`s, never merge or discard
  either implicitly — it must ask.
- **11 declared keys are never written by any node**: `user_access_token`, `referrer`,
  `page_context`, `page_info`, `current_article_id`, `current_article_content`,
  `current_video_transcript`, `ui_draft_playlist`, `user_access_decision`,
  `include_research_videos`, `clarification_response`. These are inbound-only — the calling
  application supplies them per request. If page context ever shows up empty, the thing to check is
  the flow's **Security tab**: `overrideConfig` has been disabled by default per-property since
  Flowise 2.1.4, and a silently-ignored override is nearly always that rather than a malformed
  request body.

---

## 5. One likely bug — worth checking before the meeting

**`curation_context` is not declared in the Start node.**

- Node 04 `Searching JoVE library...` writes it: its Update Flow State sets
  `curation_context ← {{ output.curation_context_json }}`.
- Node 06 `Organizing playlist...` reads `{{ $flow.state.curation_context }}` as its **only** user
  message content.
- But `curation_context` is **not** among the 37 keys in the Start node's Flow State. I checked the
  list verbatim; it is absent.

In Agentflow V2, a node's Update Flow State can modify keys that already exist and **cannot create
new ones** — a write to an undeclared key silently does nothing. If that holds here, the curation
model receives `curation_context:` followed by nothing, and is selecting videos from an empty
candidate list.

**How confident to be.** The graph is unambiguous on all three facts above. What I can't tell from
the graph alone is whether the running behaviour matches, and this is the dev instance
(`internal-host.example.com`, every flow showing `deployed = false`), so it may not be the graph
serving users. Two cheap checks before you rely on this either way:

1. Open the Start node in the UI and confirm whether `curation_context` appears in Flow State. If
   the export is faithful, it does not.
2. Run one create-playlist request and look at the `Organizing playlist...` node's input in the
   execution trace. Either it's populated (and the platform is more permissive than documented), or
   it's empty (and this is the whole ballgame).

If it is empty, the fix is one line of configuration — add `curation_context` to the Start node's
Flow State with an empty initial value — not a code change.

**Minor, while you're in there:** node 04 line 297 has a live debug statement,
`if (!item?.isSubscribed) console.log("item", JSON.stringify(item));`, which dumps full search-API
item payloads into the Flowise logs for every non-subscribed result. Harmless but noisy, and worth
removing.

---

## Where each claim came from

| Claim | Node / function |
|---|---|
| Model sees only `id`, `t`, `ty` | node 04 `Searching JoVE library...`, `compactCandidate()` |
| Abstract never captured from search | node 04, `normalizeVideo()` |
| Excerpt exists on draft videos, then stripped | node 04, `draftArticlesAsVideos()` → `compactCandidate()` |
| Candidate volume 480 / 100 | node 04, `candidateLimit = queries.length * perPage`; `MAX_SEARCH_QUERIES = 20`, `MAX_SEARCH_RESULTS_PER_KEYWORD = 24`, `MAX_INITIAL_SEARCH_QUERIES = 10` |
| Curation prompt and modes | node 06 `Organizing playlist...`, system message (3,925 chars) |
| Model is `gpt-5.6-luna`, schema-enforced | node 06, `llmModelConfig` / `llmStructuredOutput` |
| Metadata re-attached after selection | node 07 `Building curated response...`, `hydrateVideo()` |
| Count cap enforced in new + recalibrate only | node 07, `trimDraftToCount()` / `makeRecalibratedDraft()`; absent in `appendCurationToDraft()` |
| Invented-id guard in recalibrate only | node 07, `requireCandidateMembership: true` |
| 37 state keys, `startPersistState: true` | node 00 `Start`, `startState` |
| `curation_context` undeclared | node 00 `startState` vs node 04 `customFunctionUpdateState` |
