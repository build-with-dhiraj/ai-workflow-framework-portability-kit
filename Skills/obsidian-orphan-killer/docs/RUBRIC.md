# Guard Rubric: the formal safety spec

`docs/SAFETY.md` is for users. This page is for contributors. Every guard ships with: a plain-language statement, the enforcement mechanism in code, the test that locks it in, and the verification recipe.

A PR that violates any of these guards is a release blocker.

---

## G1. Frontmatter-only writes

**Statement.** The orphan-killer mutates YAML frontmatter values ONLY. The body bytes of every note are identical before and after every run.

**Mechanism.** Every write goes through `obsidian_orphan_killer.fm.write_atomic(path, serialize(fm, body))`. The `body` is read from disk by `split_frontmatter()` and passed through to `serialize()` unchanged. No code path mutates `body`.

**Test.** `tests/test_resolve.py::test_resolve_body_hash_preserved`, `tests/test_anchor.py::test_anchor_body_hash_preserved`. Both compute `body_only_hash(body)` before and after a live run; assert equality.

**Verify yourself.** On any vault: `md5 (or sha256) every body slice before the run, run the tool, hash again, diff`. The diff must be empty.

---

## G2. Atomic writes

**Statement.** A partial write is never observable. The file at `path` is either the old content or the new content; never anything in between.

**Mechanism.** `write_atomic()` writes to a tempfile in the same directory as the target, calls `os.fsync()`, then `os.rename(tmp, path)`. On POSIX, `rename` is atomic within a filesystem.

**Test.** Implicit via the file I/O contract. The mechanism is the test.

**Verify yourself.** `kill -9` the process mid-write; `cat path` must show the old content.

---

## G3. Idempotency stamp

**Statement.** A re-run on an unchanged note is a no-op. Specifically, if `raw_meta.<stamp>_hash` matches the current content hash, the note is skipped.

**Mechanism.** `fm.should_skip(fm, stamp_key, stamp_hash_key, current_hash)` compares the stored hash to the recomputed hash. The resolver, anchor, and mint paths each call this before any write.

**Test.** `tests/test_resolve.py::test_resolve_idempotent`. Run resolve twice; assert that the second run's `written` count is 0 and `skipped` is >= the first run's `written`.

**Verify yourself.** Run the tool twice on the same vault, no other changes. The second run must report `written: 0` for resolve / `0` for anchor / `0` for mint.

---

## G4. Dangling-link guard

**Statement.** A plain string is rewritten to `[[slug]]` only if `slug.md` exists in one of the configured hub directories.

**Mechanism.** In `resolve._resolve_fm_fields()`:

```python
slug = table.by_norm.get(key)
if slug and slug in table.hub_slugs:  # <-- the guard
    new_items.append(f"[[{slug}]]")
```

`table.hub_slugs` is populated only from existing `.md` files in the hub dirs.

**Test.** `tests/test_resolve.py::test_resolve_never_writes_dangling_links`. Setup: a note carries a plain string `unknown-thing` with no matching hub. Assert: after a live run, the string is unchanged and `[[unknown-thing]]` does NOT appear in the frontmatter.

**Verify yourself.** Create a note with `entities: [definitely-not-a-hub]`. Run resolve. The string must still be `definitely-not-a-hub`, NOT `[[definitely-not-a-hub]]`.

---

## G5. Per-hub absorption cap

**Statement.** No single hub can absorb more than `max_per_hub` orphans in one `anchor` (or `mint`) run.

**Mechanism.** A `Counter` tracks per-hub anchor count during the run. When the count reaches the cap, the candidate is reported as `hub_capped` and skipped.

**Test.** `tests/test_anchor.py::test_anchor_max_per_hub_caps_absorption`. Setup: 5 orphans, all nearest to the same hub, `max_per_hub=2`. Assert: `anchored == 2`, `hub_capped == 3`.

**Verify yourself.** Run anchor on a vault with one strongly-magnetic hub and `--max-per-hub 5`. The stats line `hub-capped` must be > 0 if there were more than 5 candidate matches.

---

## G6. Cosine floor (no noisy matches)

**Statement.** In `anchor` mode, a candidate whose nearest-hub cosine is below the floor stays unlinked.

**Mechanism.** Direct check in `anchor.anchor_orphans()`:

```python
if best_slug is None or best_cos < floor:
    stats["below_floor"] += 1
    continue
```

**Test.** `tests/test_anchor.py::test_anchor_below_floor_leaves_unlinked`. Setup: orphan whose nearest hub cosine is 0.5, floor 0.99. Assert: orphan's `entities:` is unchanged.

**Verify yourself.** Pass `--floor 0.99` and observe that almost every candidate is reported `below_floor` and unchanged on disk.

---

## G7. Concepts-only target set (brand-leak guard)

**Statement.** By default `anchor` targets only `concepts/` hubs. `entities/` hubs are excluded from the candidate set.

**Mechanism.** In `anchor.anchor_orphans()`:

```python
if include_entities:
    hub_slugs = list(table.hub_names.keys())
else:
    hub_slugs = [s for s in table.hub_names if table.hub_kinds.get(s) == "concept"]
```

**Test.** `tests/test_anchor.py::test_anchor_concepts_only_default`. Setup: vault with concept hub + entity hub. Assert: stats report `target_hub_kind == "concepts-only"`; no sample row anchors to the entity hub.

**Verify yourself.** Run anchor without `--include-entities` on a vault with a strong entity-hub match for some orphan. The orphan should anchor to a concept (or stay unlinked), never to the entity.

---

## G8. DO_NOT_MERGE user-supplied pairs

**Statement.** The user can supply pairs that look similar but must never collapse. The embedding leg checks every candidate against this list before any rewrite.

**Mechanism.** `guards.is_forbidden_pair(a_key, b_key, do_not_merge)` returns True if the pair is in the user's list. The embedding fallback in `find_embedding_candidates()` skips candidates where this is True.

**Test.** `tests/test_guards.py::test_do_not_merge_user_pairs`. Setup: a pair `{claude-ai, claude-code}` in DO_NOT_MERGE. Assert: `is_forbidden_pair()` returns True for that pair, False for an unrelated pair.

**Verify yourself.** Add a DO_NOT_MERGE pair, run resolve with `--embed-residuals` (if enabled), and observe that the candidate is logged as blocked.

---

## G9. Mint mode requires `--experimental`

**Statement.** The `mint` subcommand refuses to do anything (even dry-run a hub creation) unless `--experimental` is passed.

**Mechanism.** In `cli._cmd_mint()`:

```python
if not args.experimental:
    log.error("mint mode requires --experimental ...")
    return 2
```

**Test.** `tests/test_cli.py::test_cli_mint_requires_experimental_flag`. Assert: `main(["mint", "--vault", ...])` returns exit code 2 and logs an error mentioning "experimental".

**Verify yourself.** `obsidian-orphan-killer mint --vault . --dry-run` (no `--experimental`) must exit with code 2.

---

## G10. Mint-side topic guards

**Statement.** A cluster's GPT-proposed hub name must pass every one of:

1. non-empty after slugify
2. not in `TOPIC_DENYLIST` (generic words like Technology, Information, Tips)
3. not in `CLUSTER_GENERIC_DENY` (single-word catch-alls like Science, Videos)
4. not a URL fragment / domain
5. has at least one significant (len >= 3) alphanumeric token

If any check fails, the cluster's orphans stay as haystack leaves.

**Mechanism.** `guards.proposed_name_is_clean(topic) -> (ok, reason)`. Called in `mint.cluster_mint()` after the LLM coherence check.

**Tests:**
- `tests/test_guards.py::test_proposed_name_clean_passes_real_topics`
- `tests/test_guards.py::test_proposed_name_rejects_denylist`
- `tests/test_guards.py::test_proposed_name_rejects_generic_cluster_words`
- `tests/test_guards.py::test_proposed_name_rejects_url_fragments`
- `tests/test_guards.py::test_proposed_name_rejects_empty`

**Verify yourself.** Open a Python REPL: `from obsidian_orphan_killer.guards import proposed_name_is_clean; proposed_name_is_clean("Science")` must return `(False, ...)`.

---

## G11. Mint-mode anti-star (per-hub cap, again)

**Statement.** Even in mint mode, no single freshly-minted hub can absorb more than `max_per_hub` orphans per run. A cluster of 200 members minting one hub will anchor at most `max_per_hub` of them; the rest are reported as `hub_capped`.

**Mechanism.** Same `per_hub_anchored` counter inside `mint.cluster_mint()`.

**Verify yourself.** Run `mint --max-per-hub 10` on a vault with a large cluster. The minted hub's `anchored` count must be <= 10.

---

## G12. Mint-mode duplicate-hub redirect

**Statement.** If the LLM proposes a name that's near-duplicate (cosine >= `dup_hub_threshold`, default 0.88) of an EXISTING concept hub, the mint is suppressed and the cluster's orphans anchor to the existing hub instead.

**Mechanism.** `_nearest_existing_concept()` inside `mint.cluster_mint()` checks the proposed name against every existing concept hub's embedded surface; on a near-duplicate, the proposal's `slug` is reassigned to the existing slug and `clusters_rejected_dup_hub` is incremented.

**Why this matters.** Without it, mint runs would slowly fragment the concept layer with siblings of existing hubs (e.g. minting `Machine Learning Models` next to an existing `Machine Learning`).

**Verify yourself.** Run mint twice. The second run should find any newly-minted hub from the first run via the dup-hub check and redirect to it.

---

## Adding a new guard

Every new guard PR must include:

1. **A plain-language statement** added to this file under a new H2.
2. **Code enforcement** in the relevant module.
3. **At least one test** that fails if the guard is removed.
4. **An update to** `docs/SAFETY.md` exposing the guard to users.
5. **An update to** `README.md`'s safety table.

The bar to add a guard is low. The bar to remove one is "explicit user discussion + a release-note paragraph explaining the new failure mode".

---

## References

The contract above is derived from a year of orphan-fixing work on a real 3,000-note vault. The specific failure modes the guards prevent (force-star formation, brand-leak, dangling-link rot, body-hash invalidation triggering a 7.5GB re-embed) are not theoretical. They have all happened on real PKM systems.
