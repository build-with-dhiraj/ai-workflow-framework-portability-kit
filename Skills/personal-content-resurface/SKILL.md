---
name: personal-content-resurface
description: Decide which saved personal content (saved YouTube videos, Instagram reels, WhatsApp self-messaged links/files, LinkedIn saved posts) should re-surface today, based on time-since-last-surface plus relevance to the user's current context. Returns a ranked list with reasons. Teaches three algorithms (SM-2, FSRS, custom context-aware hybrid) — the implementer picks at build time. Decision math only, not surfacing UX. Use when the user asks "what should I re-look at today", "resurface saved content", "spaced repetition for my saved stuff", "Connecting Dots prioritization", "second brain re-surfacing", "what saved content matters right now", "personalized content scheduling", or any variant of "I save things and never re-look at them — what should I look at now?"
---

# Personal-content re-surface decision math

## What this skill does

Given (a) a corpus of saved personal content, (b) a static user profile, and (c) the user's recent activity, decide **which N items to re-surface today** and **why**. Output is a ranked list with one-line reasons. Does NOT define the UX (push notif vs daily digest vs dashboard widget) — that lives in product code.

## Inputs

| Signal | Shape | Source |
|---|---|---|
| **Corpus item** | `{id, source, captured_at, text/embedding, tags, last_surfaced_at, surface_count, useful_score}` | Obsidian vault, Pinecone, or Supabase — whatever the store is |
| **Static user profile** | `{interests[], role, current_projects[], stated_priorities[]}` | User-authored, lives in Obsidian or app DB |
| **Dynamic recent activity** | `{queries_this_week[], content_consumed_this_week[], current_focus_topic}` | Activity log of last 7 days |

## Output

```json
[
  { "item_id": "yt_abc123", "score": 0.87, "reason": "topic match with current focus + 14d since last surface" },
  { "item_id": "wa_xyz", "score": 0.81, "reason": "high useful_score + 60d dormant" }
]
```

Rank descending. Cap at N (default 5). Each item carries a one-line `reason` for transparency.

## Three algorithms — pick at build time

### 1. SM-2 (classic Anki) — day-1, no personalization needed

Decay-only. Each item has `interval` and `ease_factor`. When marked useful, `interval` grows. Re-surface when `now > last_surfaced_at + interval`. Zero LLM in the loop. Cheapest compute.

**Use when:** MVP day-1, corpus <100 items, no feedback signal yet.

### 2. FSRS (Free Spaced Repetition Scheduler) — modern, accurate

Three latent variables per item: difficulty, stability, retrievability. Updates via maximum-likelihood estimation. Outperforms SM-2 in benchmarks.

**Use when:** corpus >500 items AND ≥30 useful/not-useful events accumulated to train the model.

### 3. Custom context-aware hybrid — the Connecting-Dots moat

```
score = 0.5 × time_decay + 0.3 × relevance_to_recent_activity + 0.2 × static_profile_match
```

- `time_decay`: forgetting curve, sigmoid over days-since-surface
- `relevance_to_recent_activity`: cosine sim between item embedding and embedding of last 7d activity
- `static_profile_match`: cosine sim between item embedding and embedding of user profile

**Use when:** corpus >100 items AND user has authored a meaningful profile. **The recommended path for Connecting Dots specifically** — pure spaced-rep misses the "this is suddenly relevant" signal that recent activity unlocks.

See [references/algorithms.md](references/algorithms.md) for exact formulas, half-life tuning, and edge cases.

## Decision matrix

| Stage | Corpus | Feedback events | Algorithm |
|---|---|---|---|
| MVP day 1 | <100 | 0 | SM-2 |
| MVP weeks 2–4 | 100–500 | <30 | Custom hybrid (no FSRS training data yet) |
| Mature | 500+ | 30+ | FSRS + hybrid signal — ensemble |

## Common pitfalls

- **Cold start**: day-1 has no feedback. Default to SM-2 with `ease=2.5, interval=1`. Don't attempt FSRS.
- **Recency bias**: if only dynamic activity drives the score, old gold gets buried. The `time_decay` term fights this.
- **Echo chamber**: if `relevance_to_recent_activity` weights too high, the user only sees more-of-the-same. Cap that term at 0.5; force diversity sampling for top-N.
- **Surface fatigue**: enforce `min_days_between_surface = 7` regardless of score — same item every day is annoying.
- **Feedback bootstrap**: cold-start the `useful_score` to 0.5 (neutral), update on user signal. Never let it drop below 0.1 — that's bandit-style starvation.

## What this skill does NOT do

- Pull content from source platforms — that's `baoyu-youtube-transcript`, `integrate-whatsapp`, `superpowers-chrome:browsing`, etc.
- Store content — that's `obsidian-vault`, `memory-router`, or `supabase`.
- Extract entities/topics from content — that's `ner-content-pipeline`.
- Render the surface UX — that's product code (Obsidian dashboard, web app, push notif daemon).
- Build the RAG pipeline that answers queries — that's `rag-patterns`.

It only answers: "Given everything you have, what should I look at today?"
