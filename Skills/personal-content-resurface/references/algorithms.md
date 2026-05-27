# Re-surface algorithms — detailed specs

Detailed formulas and tuning notes for the three algorithms described in [`../SKILL.md`](../SKILL.md). Implementation-language-agnostic; pseudocode only.

---

## SM-2 (SuperMemo 2)

Per-item state:

```
{
  ease: float = 2.5,
  interval: int (days) = 1,
  repetitions: int = 0,
  last_review: timestamp
}
```

### Update on user feedback

Feedback `q ∈ {0..5}` where 5 = perfect recall, 0 = blackout.

For personal-content re-surfacing, simplify to binary feedback:
- "useful" / kept reading → `q = 4`
- "not useful" / dismissed → `q = 2`
- ignored / no signal → no update; recompute next surface based on existing interval

```
if q < 3:
    repetitions = 0
    interval = 1
else:
    repetitions += 1
    if repetitions == 1: interval = 1
    elif repetitions == 2: interval = 6
    else: interval = round(prev_interval × ease)
    ease = max(1.3, ease + 0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
```

### Next-surface check

```
should_surface = now > last_review + interval days
```

### Tuning for content (not flashcards)

- Initial `ease = 2.5` is fine; let it self-adjust.
- Cap `interval ≤ 90 days` so very stable items still re-appear quarterly.
- Floor `ease ≥ 1.3` per the classic spec — prevents thrashing.

---

## FSRS (Free Spaced Repetition Scheduler)

Per-item state:

```
{
  difficulty: float [1..10],
  stability: float (days),
  retrievability: float [0..1],
  last_review: timestamp,
  reviews: int
}
```

### Core formulas

```
retrievability(t) = (1 + t / (9 × stability))^(-1)
    where t = days since last review

# After a review with rating r (1=Again, 2=Hard, 3=Good, 4=Easy):
new_stability = stability × (1 + e^w × (11 - difficulty) × stability^-w × (e^((1 - retrievability) × w) - 1))
    where w is a learned parameter vector
new_difficulty = clamp(difficulty + Δ_d(r), 1, 10)
```

The `w` parameter vector (17 weights) is trained per-user via maximum-likelihood estimation against the user's feedback history. Need ≥30 reviews to converge to better-than-SM-2 accuracy.

### When to schedule next surface

```
target_retrievability = 0.9  # the desired probability of recall
days_to_next = stability × (target^(-1/9) - 1) × 9
next_surface_at = last_review + days_to_next
```

### Training the w vector

Use the FSRS reference implementation in Python (`fsrs-optimizer` package on PyPI). Train weekly on accumulated feedback; persist `w` per user in DB.

For Connecting Dots: don't try to implement FSRS from scratch — install `fsrs-optimizer` and call it. FSRS is mature enough to be a dependency.

---

## Custom context-aware hybrid (the Connecting-Dots moat)

```
score(item) = w_t × time_decay(item) + w_r × relevance(item) + w_p × profile_match(item)
              + diversity_penalty(item, already_selected)
```

Default weights: `w_t = 0.5, w_r = 0.3, w_p = 0.2`.

### Time decay component

```
half_life = 14  # days; tune per user — see notes below
days_since = (now - last_surfaced_at).days
time_decay = 1 - sigmoid((days_since - half_life) / (half_life / 4))
                # peaks near half_life; saturates after ~2× half_life
```

For very stale items (`days_since > 90`), boost `time_decay` to `1.0` regardless — these are "gold someone forgot." Manual nudge to fight pure-recency bias.

**Half-life tuning per user:**
- Heavy savers (>50 items/week): `half_life = 7d` (faster rotation)
- Light savers (<10 items/week): `half_life = 21d` (slower rotation)
- Default: 14d

### Relevance to recent activity

```
activity_embedding = mean_pool(embed(queries_this_week) + embed(content_consumed_this_week) × 0.5)
relevance = cosine_similarity(item.embedding, activity_embedding)
relevance = max(0, min(1, relevance))  # clamp; cosine can be negative
```

The `× 0.5` weight on consumed content prevents the system from over-weighting passive reading. Active queries (what the user actively asked about) get full weight.

### Static profile match

```
profile_embedding = embed(json_stringify({interests, role, current_projects, stated_priorities}))
profile_match = cosine_similarity(item.embedding, profile_embedding)
profile_match = max(0, min(1, profile_match))
```

Re-embed the profile only when the user updates it (rare). Cache.

### Diversity penalty

After selecting top-K candidates by raw score, apply MMR (Maximal Marginal Relevance):

```
final_score(item) = λ × raw_score(item) - (1 - λ) × max(cosine_similarity(item, prev_selected))
λ = 0.7  # tune; lower = more diversity
```

Prevents the top-5 from all being about the same topic.

### Cold-start defaults

When a signal is missing:
- No `last_surfaced_at` → treat as `90 days ago` (fresh, surface freely)
- No `useful_score` → `0.5` (neutral)
- No recent activity → fall back to `w_t = 0.7, w_r = 0, w_p = 0.3` (just time + profile)
- No profile → fall back to `w_t = 0.8, w_r = 0.2, w_p = 0` (just time + recent activity)

### Surface-fatigue guard

Hard constraint, evaluated BEFORE scoring:

```
if (now - item.last_surfaced_at).days < 7:
    skip this item entirely
```

Without this, items can surface daily once score is high — annoying.

---

## When to switch algorithms

```
if corpus_size < 100 OR feedback_events == 0:
    use SM-2
elif corpus_size < 500 AND feedback_events < 30:
    use custom hybrid (FSRS not yet trainable)
elif feedback_events >= 30:
    use ensemble: 0.6 × hybrid_score + 0.4 × FSRS_recall_probability
```

Switch is automatic; no user intervention. The skill's caller should re-check the active algorithm on each surface batch.

---

## Evaluation

Track these metrics per user, weekly:

| Metric | Target | If miss |
|---|---|---|
| `useful_rate` (% of surfaced items user marked useful) | >40% | tune weights; check echo-chamber |
| `surface_diversity` (unique topics in top-5) | ≥3 of 5 | lower MMR λ |
| `staleness_recovery` (% of >60d items re-surfaced in last month) | >20% | raise w_t |
| `dismiss_then_resurface` (% of dismissed items resurfacing in <30d) | <5% | feedback isn't decreasing scores enough |

Use these in `evaluate-rag` and `langfuse` instrumentation downstream.
