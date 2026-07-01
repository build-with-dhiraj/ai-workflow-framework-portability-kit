# Phase 1 — OLD Mac: prepare & back up

Goal: capture a **complete, checksummed, restorable** snapshot of everything that
makes this machine *your* environment, so it comes back on a new Mac under a
possibly-different username. Work top-down; confirm each decision with the user.

## 1. Deadline, redundancy posture, and staying awake

- If the Mac is being **returned, sold, or factory-reset**, get the hard cutoff time and work backward — uploads of tens of GB are slow.
- Run `caffeinate -dis &` so sleep doesn't stall the upload.
- Aim for **more than one copy** during the gap: the cloud bundle *plus* live git remotes *plus* (ideally) an external disk. During the migration window the bundle may be the only copy of gitignored data — treat it as precious.

## 2. Hardening — "is Claude (or my chosen tool) the only bridge?"

Users often fixate on removing a specific editor/tool (e.g. a work-licensed Cursor) before a wipe. Audit it, but reframe: a tool is usually **a leaf, not a hub**. Check whether anything *depends* on it:

- Shell/PATH: `~/.zshrc`, `~/.zprofile`, `/etc/paths*`.
- Background automation: `launchctl list`, `~/Library/LaunchAgents/*.plist`, `crontab -l`, repo `.git/hooks`.
- Claude wiring: `~/.claude.json`, `~/.claude/mcp.json`, MCP server command paths.
- Other editors' configs.

The **real** risk runs the other way: the factory reset destroys (a) the entire `~/.claude` setup, (b) secrets that exist only on disk, and (c) un-pushed git work + local automations. Point the effort there.

## 3. Inventory — decide what to back up

Get an explicit **folder list** from the user (a Finder tag such as Green is a good census — `mdfind "kMDItemUserTags == 'Green'"`). For each folder, split:

- **Regenerable (EXCLUDE):** `node_modules`, `.venv`, `__pycache__`, `.next`, `dist`, `build`, `target`, `.DS_Store`, and in-flight `.claude/worktrees` (commit anything uncommitted in them first — `git worktree list`).
- **Irreplaceable (INCLUDE):** source, the whole `.git/` (carries remotes + stashes + un-pushed commits), and **gitignored data** — Obsidian/RAG **vaults + their `.lancedb` indexes**, generated datasets, `.env`/secrets you actually need.

Measure sizes (`du -sh`) so the user knows the upload cost and which regenerables dominate. Surface any **already-lost** data honestly (e.g. a vault with no backup and no Time Machine) rather than pretending the bundle covers it.

## 4. Make code cloud-safe (redundancy, not a replacement)

Where it makes sense, push the code repos to remotes — it gives redundancy and sidesteps username rewrites *for the code*. But be explicit: **this does not cover gitignored vaults/`.lancedb`, stashes, or no-remote repos**, which is exactly why doctrine 1 (extract, never clone) exists. Note per-repo working branches so they can be checked out on the new Mac.

## 5. Build the bundle (`scripts/migrate-out.sh`)

Edit the config block at the top of `migrate-out.sh` (your home dir, the project folders + their clean target names, any extra dotfiles). It then produces, into a staging dir:

- **One `.tgz` per project** — regenerables excluded, `.git` + gitignored vaults/`.lancedb` included.
- **`claude-config.tgz`** — `~/.claude` + `~/.claude.json`, stripping transient dirs (`projects`, `plugins/cache`, `cache`, `shell-snapshots`, `telemetry`, `sessions`, `debug`, `backups`). Preserves the skill **symlinks as symlinks** (don't dereference).
- **`agents-skills-source.tgz`** — `~/.agents` (the target of those symlinks). **Skipping this is the classic mistake** — the symlinked skills restore broken without it.
- **`claude-history.tgz`** — `~/.claude/projects` (chat transcripts). Large; can be dropped if time runs out, but this is your Claude Code / Desktop chat history.
- **`claude-desktop-sessions.tgz`** — `~/Library/Application Support/Claude/` session store (`local-agent-mode-sessions`, `claude-code-sessions`, IndexedDB, Local/Session Storage). Relative paths, but its session `.json` metadata contains absolute `cwd`s that WILL need rewriting on restore.
- **`claude_desktop_config.json`** — copied raw (contains MCP server defs; may hold live tokens — flag for the user).
- **Dotfiles/secrets** — `.ssh`, `.gitconfig`, `.zshrc`, `.config`, plus any app auth you rely on (`~/.codex`, `~/.gemini`, MCP OAuth caches). Keep secret archives *separate* from data archives so they can be handled/deleted independently later.
- **`manifest.json`** — records `OLD_USER`, `OLD_HOME`, the project→clean-name map, and the list of intentionally-omitted secrets. The restore script reads this so it isn't guessing the old username.

## 6. Checksums + verify the round-trip

Generate `CHECKSUMS.txt` with `shasum -a 256 *`. Upload the staging dir to cloud/external. **Then re-download one archive and run `shasum -a 256 -c CHECKSUMS.txt`** — silent corruption on a large upload is the failure that quietly ruins a migration. Draining of the local staging copy (for cloud apps that offload) is a decent "upload complete" signal, but byte-size verification on the cloud side is better.

## 7. Runbook + the intentional omissions

Write a short `NEW-MAC-SETUP.md` for future-you: the one rule (extract, never clone), the vault→project→repo table, the phase order, the plugin/marketplace list, and the code-only-clone fallback (with its warning that it loses gitignored data). Record explicitly what is **NOT** in the bundle and why:

- `gh` token and OAuth client keys — live in Keychain / were never re-supplied; re-auth by hand on the new Mac.
- MCP logins — only the server *definitions* travel; each re-auths in the browser on first use.

## 8. The pre-reset gate — do NOT wipe until all pass

- ⛔ Cloud shows the bundle **fully uploaded** — verify byte sizes of the big files, not just a spinner. Confirm the small irreplaceable archives first (they upload fast); the biggest project `.tgz` is the safest to not fully wait on *only if* that project's code is also on a git remote and its vault is in another copy.
- Credentials written down: Apple ID + password, Google account + 2FA, GitHub login, every MCP service login.
- A personal sweep of `~/Downloads`, `~/Documents`, `~/Pictures`, `~/Movies`, `~/Music` for anything not in the bundle.
- If you'll have any say over the new account's short name, **create it identical to the old one** — it deletes the entire path-rewrite phase.
