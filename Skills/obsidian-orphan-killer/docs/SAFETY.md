# Safety contract

What `obsidian-orphan-killer` will, and will not, do to your vault.

This is a tool that writes to your notes. Trust has to be earned, not asserted. Every claim on this page is locked in by a test in [`tests/`](../tests/). If any test fails, the safety claim it enforces is broken and the release is held.

---

## The contract

### 1. Frontmatter-only writes

The orphan-killer mutates YAML frontmatter values ONLY. The body bytes (title, headings, paragraphs, code blocks, images, attachments) are never modified.

**Enforced by:** `obsidian_orphan_killer/fm.py::body_only_hash()` is computed before and after every run; if it changes, the tests fail.

**Tests that lock this in:**
- `tests/test_resolve.py::test_resolve_body_hash_preserved`
- `tests/test_anchor.py::test_anchor_body_hash_preserved`

This guarantee is what lets downstream embedders (LanceDB, Pinecone, Chroma, any vector store) keep their content hash valid across orphan-killer runs. **No re-embed is ever triggered by an orphan-killer run.**

---

### 2. Atomic writes

Every write goes through `tempfile.mkstemp` + `os.rename`. The OS guarantees `os.rename` is atomic on POSIX filesystems. If the process is killed mid-write, the original file is intact; if the rename completes, the new file is complete.

**Enforced by:** `obsidian_orphan_killer/fm.py::write_atomic()`. No path in the codebase writes to a `.md` file directly; every write routes through `write_atomic`.

---

### 3. Idempotency stamps

Every write records two pieces of metadata in `raw_meta`:

- a UTC timestamp (`resolved_at` / `anchored_at` / `clustered_at`)
- a content hash (`resolved_hash` / `anchor_hash` / `cluster_hash`)

The hash is over the body + the entity/topic fields. On a re-run, if the hash matches, the note is skipped. This means:

- **Running `resolve` twice in a row is a no-op on the second run.**
- **You can re-run after a partial failure** (e.g. you killed the process); only the un-stamped notes are re-processed.
- Pass `--force` to override the stamp (useful after an alias change).

**Tests that lock this in:**
- `tests/test_resolve.py::test_resolve_idempotent`
- `tests/test_resolve.py::test_resolve_honors_force_flag`
- `tests/test_anchor.py::test_anchor_idempotent`

---

### 4. Dangling-link guard

A plain string is rewritten to `[[slug]]` ONLY IF `slug.md` exists in a hub directory. If the alias table claims a hub but the file is gone, the rewrite is skipped and the plain string stays.

**Why this matters:** the alternative (writing `[[some-deleted-hub]]`) would create a phantom link in Obsidian's graph view that looks like a hub but doesn't resolve. The orphan-killer refuses to do that.

**Tests that lock this in:**
- `tests/test_resolve.py::test_resolve_never_writes_dangling_links`

---

### 5. Per-hub absorption cap (anti-star)

The `anchor` mode has a `--max-per-hub` parameter (default 50). No single hub can absorb more than this many orphans per run. If a hub is the nearest match for, say, 200 candidates, only the first 50 anchor; the rest are reported as `hub_capped` in the stats and left unlinked.

**Why this matters:** even a degenerate embedding space (e.g. a hub whose name happens to be a stop-word in the model's training) cannot rebuild a force-star. The cap forces you to mint additional hubs or accept that some orphans don't belong anywhere.

**Tests that lock this in:**
- `tests/test_anchor.py::test_anchor_max_per_hub_caps_absorption`

---

### 6. Cosine floor (no noisy matches)

The `anchor` mode has a `--floor` parameter (default 0.74). Below the floor, the orphan stays unlinked. The default is calibrated for `BAAI/bge-small-en-v1.5` at `max_length=256` against a real 3,000-note vault: above 0.74 the matches are reliably topical, below it the false-positive rate rises sharply.

**Why this matters:** the right safety behavior for a low-confidence match is "leave it alone", not "force-link it to something". The orphan stays an orphan, and the user knows.

**Tests that lock this in:**
- `tests/test_anchor.py::test_anchor_below_floor_leaves_unlinked`

---

### 7. Concepts-only target set (brand-leak guard)

By default the `anchor` mode targets only `concepts/` hubs, not `entities/` hubs. This prevents the brand-leak class: a generic note about "spreadsheet formulas" would otherwise anchor to `[[microsoft-excel]]` (an entity hub), creating a false brand association.

Pass `--include-entities` to opt in. Most users should not.

**Tests that lock this in:**
- `tests/test_anchor.py::test_anchor_concepts_only_default`

---

### 8. DO_NOT_MERGE pairs

Cosine similarity is high between things that are obviously distinct in the real world: `Claude AI` and `Claude Code` are not the same thing, but their embeddings are close. The same is true of `JoVE` vs `JoVE Labs`, `Gemini AI` vs `Gemini Pro`, and many others.

The lexical guard catches some of this. The user can also supply explicit DO_NOT_MERGE pairs (frozensets of normalized keys that must never collapse onto each other). The embedding leg checks every candidate against this list before any rewrite.

**Tests that lock this in:**
- `tests/test_guards.py::test_do_not_merge_user_pairs`

---

### 9. Mint mode requires `--experimental`

The `mint` subcommand writes NEW notes (new concept hubs). This is qualitatively different from modifying frontmatter on existing notes. The orphan-killer refuses to do it unless the user passes `--experimental` explicitly.

If you run `obsidian-orphan-killer mint --vault ...` without the flag, the tool exits with code 2 and a message telling you what's missing.

**Tests that lock this in:**
- `tests/test_cli.py::test_cli_mint_requires_experimental_flag`

---

## The dry-run convention

Every mode supports `--dry-run`. Always use it first.

```bash
obsidian-orphan-killer resolve --vault ~/vault --dry-run
obsidian-orphan-killer anchor  --vault ~/vault --dry-run
obsidian-orphan-killer mint    --vault ~/vault --experimental --dry-run
```

A dry-run:
- writes nothing
- spends no LLM credits (mint mode skips its LLM calls in dry-run)
- prints the same stats the live run would
- in `anchor` and `mint` modes, writes a per-candidate **audit TSV** to `<vault>/orphan_killer_audit/<mode>.tsv` showing every decision the tool would have made

**Read the TSV before the live run.** Sort by cosine descending. Spot-check the borderline rows (near the floor). If anything looks wrong, lower the floor, raise the threshold, or skip the affected notes via `--path` filtering.

---

## Recovery

If something surprises you after a live run:

```bash
# See what changed.
cd ~/vault
git diff

# Revert one file.
git checkout -- sources/some-note.md

# Revert everything from the orphan-killer run.
git checkout -- .

# Or, if you committed the changes:
git revert HEAD
```

Because every write is a single-line YAML frontmatter mutation, the diffs are small and human-readable. There's no obfuscation, no opaque cache file, no metadata format that requires the orphan-killer to interpret.

**If you have ever doubted what the tool did to a note**, run:

```bash
git log --oneline -p sources/some-note.md | head -50
```

The full audit trail is in your repository.

---

## What the orphan-killer does NOT do

- It does not call out to any network service in `resolve` mode.
- It does not call out to any network service in `anchor` mode (after the one-time fastembed model download).
- It does not modify the body bytes of any note, ever.
- It does not write a wikilink to a hub that doesn't exist on disk.
- It does not force a noisy match. Below the cosine floor, the orphan stays unlinked.
- It does not anchor to entity (brand) hubs by default. The concepts-only default avoids the brand-leak failure mode.
- It does not collapse `DO_NOT_MERGE` pairs even when their cosine is high.
- It does not write new notes outside of `mint` mode, which is gated behind `--experimental`.
- It does not silently overwrite a stamped note. `--force` is required.

---

## If you find a safety bug

File an issue using the bug template at [`.github/ISSUE_TEMPLATE/bug.md`](../.github/ISSUE_TEMPLATE/bug.md). Mark it with `safety`. We treat any violation of the above contract as a release blocker.

Specifically, if any of the following happens and you can reproduce it on a minimal vault, please file IMMEDIATELY:

- A body byte was modified.
- A non-existent hub was written as a wikilink.
- A note already stamped with `resolved_at` was rewritten without `--force`.
- An LLM-named hub passed the guard list and wrote a denylisted name.
- The audit TSV claimed a decision that doesn't match what was actually written.

The fix is a release-blocking patch and a new test that pins the failure.
