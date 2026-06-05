# Demo vault for obsidian-orphan-killer

A tiny, intentionally-broken vault you can use to see every mode in action.

## Structure

```
demo-vault/
  entities/
    python.md
    obsidian.md
  concepts/
    knowledge-management.md
    graph-theory.md
  sources/
    learning-python-basics.md       # plain-string entities + topics, resolvable
    note-taking-thoughts.md         # all aliases, fully resolvable
    orphan-graph-thinking.md        # true orphan, anchor should attach
    orphan-random-recipe.md         # true orphan, no relevant hub
    orphan-py-data-analysis.md      # body-only orphan
    linked-already.md               # has a [[python]] link, no-op
    mixed-residual.md               # mix of resolvable + unresolvable
```

## Try it

```bash
# 1. Deterministic resolve (dry-run — change nothing)
obsidian-orphan-killer resolve --vault . --dry-run

# 2. Same but actually write
obsidian-orphan-killer resolve --vault .

# 3. Embedding anchor on the remaining orphans (dry-run)
obsidian-orphan-killer anchor --vault . --dry-run

# 4. Anchor live
obsidian-orphan-killer anchor --vault .
```

After step 2, `learning-python-basics.md` and friends will have their
plain-string entities/topics rewritten to canonical `[[wikilinks]]`. After
step 4, `orphan-graph-thinking.md` should be anchored to
`[[graph-theory]]`. `orphan-random-recipe.md` should stay unlinked (its
nearest-hub cosine is below the 0.74 floor — that's the safety behavior).

## Reset

```bash
git checkout -- .
```
