# Phase 2 — NEW Mac: restore & reconcile

Goal: turn the bundle back into a working environment under this Mac's (possibly
different) username, then fix the things a config-only restore leaves broken.
Always `--dry-run` before the real run, and confirm usernames first.

## 1. Sanity + the identity decision (do this before anything else)

```bash
whoami; echo "$HOME"; df -h /
```
- Need ample free space (bundle + extracted projects can be tens of GB).
- **If `whoami` ≠ the old username:** you will rewrite paths. Decide:
  - **Best:** have the new account's *short name* set to the old username (deletes the rewrite entirely). On a managed/corporate Mac this may need IT.
  - **Otherwise:** proceed and rewrite. **Derive the target from `$HOME`, not `whoami`** — during an account rename they can disagree (e.g. home already moved to `/Users/Dhiraj` while `whoami` still returns `pranav`). The bundled `migrate-in.sh` does this.
- If a short-name rename is planned, do it **before** the restore and confirm `whoami` matches `basename $HOME` afterward, or you'll bake in the wrong path twice.

## 2. Prerequisites

Homebrew → `brew install git gh node uv` (+ `rust` via rustup / `go` if projects need them) → `brew install --cask obsidian` (for vault re-add) → `gh auth login`. Toolchains do **not** travel in the bundle. (Homebrew + brew packages live in `/opt/homebrew` and survive an account recreate; things in `$HOME` like rustup and `gh` auth do not — install those after any rename.)

## 3. Get + verify the bundle

Copy the whole bundle folder from cloud/external to local disk (this forces a full download off online-only stubs). Then:
```bash
cd <bundle> && shasum -a 256 -c CHECKSUMS.txt   # every line must say OK
```
If anything fails, re-download — do not proceed on a corrupt archive.

## 4. Dry-run, then run `scripts/migrate-in.sh`

```bash
./scripts/migrate-in.sh <bundle> --dry-run     # show the full plan, change nothing
./scripts/migrate-in.sh <bundle>               # real run (prompts to confirm the new username)
```
It: verifies checksums (aborts on mismatch) → restores dotfiles/SSH (fixes perms) → restores `~/.claude` + `~/.agents` + history + Desktop sessions → extracts projects into `~/dev` under clean names → **rewrites all `/Users/<old>` paths (identity from `$HOME`), including the Desktop config, the Desktop session `cwd`s, and the history slugs** → **aligns each chat transcript with its session's cwd slug (step 7b — fixes "Session history unavailable")** → prunes worktrees → prints a per-repo deps + vault + MCP re-auth checklist.

**Extract, never clone** (doctrine 1): the archives are the only source of gitignored vaults, `.lancedb`, stashes, and no-remote repos. Only clone a repo you've verified is fully pushed and has no gitignored data.

## 5. Reconcile the completeness gaps (the hard-won part)

A config-only rewrite leaves `/Users/<old>` in places that break things. The bundled script handles these, but **verify** them — and know how to fix them by hand when debugging a partial migration:

### (a) Project source code
`grep -rlI "/Users/<old>" ~/dev` will usually still hit. Rewrite with the same two-pass transform (user rename, then project-root relocation into `~/dev/<clean>`), **back up first**, and commit the diff per repo. Watch for word-boundary over-matches (`invest` vs `investments`).

### (b) Bare `/Users/<old>` (no trailing slash)
Trailing-slash-only rules miss `"/Users/<old>"` used as a whole value — e.g. a project key in `~/.claude.json` or `"projectPath"` in `installed_plugins.json`. Handle the bare form explicitly.

### (c) Claude Desktop session metadata — the cause of "Working directory no longer exists"
This is the subtle one. Each session `.json` under
`~/Library/Application Support/Claude/claude-code-sessions/…` and
`…/local-agent-mode-sessions/…` stores absolute `cwd` / `originCwd` /
`worktreePath` (and `outputs`) fields. If those point at a now-gone
`/Users/<old>/…` (or a deleted worktree), the chat throws **"Working directory no
longer exists"** on resume. Fix = for every session path field, resolve to the
real new location:
- old project root → `~/dev/<clean>` (collapse dead worktree subpaths to the repo root)
- home-level folder that moved → its new home (e.g. handover folders under `~/transition`)
- a folder that was never restored → create an empty placeholder so the chat at least opens, or leave it if abandoned
- bare `/Users/<old>` → `~` (`/Users/<new>`)

### (c-bis) Transcript slug alignment — the cause of "Session history unavailable"
This is the sibling bug to (c), and it appears *after* you've fixed the cwds. A
chat shows its messages only if `slug(session.cwd)` names a dir in
`~/.claude/projects/` that actually contains that session's `<id>.jsonl`. The slug
is the cwd with **every char except `[A-Za-z0-9.]` turned to `-`** — so `/`, space,
`_`, `(`, `)` and even `-` all become `-`, while the **dot is kept** (`phy6.ai` →
`phy6.ai`, `Pm_research_starter` → `Pm-research-starter`). Repairing a session's
cwd in (c) can therefore *move* it to a slug that no longer matches where the
migration filed its transcript — the folder is valid, the chat opens, but history
is **empty** and Desktop shows **"Session history unavailable."** Common causes:
the transcript was filed under a pruned-worktree slug, the old bare-user slug
(`-Users-<old>`), or an underscore/paren folder.

The bundled `migrate-in.sh` now fixes this automatically in **step 7b** (runs right
after the cwd repair): for every session it reads the *valid* cwd, computes
`slug(cwd)`, and if the transcript lives under a different slug it **copies** it
(and any per-session subdir) into the matching one — additive, never deletes. To do
it by hand instead: point `cwd` at the path whose slug matches the existing
transcript (symlink to the real files if needed), or copy the transcript dir to
match the cwd. Either way, `verify.sh` check **[4b]** counts sessions still
misplaced (want `0`). **Restart Claude Desktop** after editing sessions — it caches
`cwd`s in memory.

> If you're inside Claude Desktop while doing this, you can't quit it (that kills
> your session). Back up the session store first, edit only the *other* (old)
> sessions, and have the user restart at the end.

## 6. Deps, vaults, MCP

- Per-repo installs (`npm install`, `uv sync`/`uv venv && uv pip install`, `cargo build`, etc.) — node_modules/.venv/target were excluded from the bundle by design.
- Re-add each Obsidian vault in the app ("Open folder as vault") — the vault folders + `.lancedb` are already on disk from the extract.
- Re-auth MCP servers from the printed list (browser OAuth for most; CLI login for some). **Verify assumptions**: some "lost" secrets may actually have ridden inside a project archive (e.g. an app's `.secrets/` under a repo) — test before re-doing OAuth.

## 7. Verify + establish redundancy

Run `scripts/verify.sh`. It should report: no `/Users/<old>` in config/code, **no broken skill symlinks**, the expected `.lancedb` count, **zero session `cwd`s pointing at a missing dir** ([4]), **zero misplaced transcripts** ([4b] — else re-run `migrate-in.sh` so step 7b aligns them), and chat history present. Confirm stashes + no-remote repos survived (`git stash list`, `git log` on the no-remote repo).

Then **doctrine 5 — make it redundant.** Get the irreplaceable data (vaults, `.lancedb`, no-remote repos, stashes) onto a second location (external SSD / Time Machine), *especially* before deleting the cloud bundle and *especially* if this is a corporate/MDM machine that can be wiped remotely. Note that secrets are often woven *inside* the data archives (a repo's `.env`/`.secrets/`), so you can't cleanly "keep data, delete secrets" file-by-file — rotating the secrets is what actually neutralizes the bundle's copies. Finally, replace hard-coded `/Users/<old>` hook paths in `~/.claude/settings.json` with `$HOME`/`~`.
