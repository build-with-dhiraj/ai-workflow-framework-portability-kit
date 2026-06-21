# Tooling — Terminal Packages & Restore Script

This folder captures the **host-side tooling** Claude depends on: brew packages, global npm packages, and a single-prompt restore script that pulls the entire kit together on a fresh Mac.

> **Source-of-truth on the live Mac:** Whatever `brew bundle dump --force --file=-` + `npm list -g --depth=0 --json` produce right now.
> **Re-snapshotting:** Run `brew bundle dump --force --file=./Brewfile` and `npm list -g --depth=0 --json > ./npm-globals.json` from this folder periodically to keep these files current.

---

## 1. What's in this folder

| File | Purpose | How it was generated |
|---|---|---|
| `Brewfile` | Leaf packages installed via Homebrew, plus VS Code extensions and `uv` tools | `brew bundle dump --force --file=./Brewfile` |
| `npm-globals.json` | Global npm packages (excluding npm itself) | `npm list -g --depth=0 --json` |
| `restore.sh` | One-shot script that installs everything and restores the entire kit | hand-authored |

> Only **leaf** brew packages are captured — i.e., things you `brew install`'d directly. Their dependencies (several dozen transitive packages — `ffmpeg` alone pulls a large tree) come along automatically when brew bundle runs. This keeps the Brewfile small and forward-compatible across brew versions.

---

## 2. What `Brewfile` contains right now

Snapshot re-synced 2026-06-11:

| Type | Package | Why it's here |
|---|---|---|
| `brew` | `cocoapods` | iOS dependency manager (needed for `flutter-*` skills targeting iOS) |
| `brew` | `ffmpeg` | Audio/video transcode + frame/audio extraction — backs the YouTube skills (`baoyu-youtube-transcript`, `jove-youtube-feed-pipeline`) |
| `brew` | `gh` | GitHub CLI — used by many skills + Mattpocock `to-issues`, `to-prd`, `triage` |
| `brew` | `node` | Node.js + npm — runtime for Claude Code itself + npm-globals |
| `brew` | `pandoc` | Document conversion — used by `anthropic-skills:docx`, `pdf`, `xlsx` |
| `brew` | `poppler` | PDF utilities — used by `anthropic-skills:pdf` |
| `brew` | `python@3.11` | Modern Python for tools that don't work with system 3.9 (Xcode's pip) |
| `brew` | `tectonic` | Self-contained LaTeX engine — compiles `master-resume`'s CV/résumé/cover-letter `.tex` output to PDF |
| `brew` | `yt-dlp` | YouTube/video downloader — backs `baoyu-youtube-transcript` and `jove-youtube-feed-pipeline` |
| `cask` | `libreoffice` | Headless office suite — document-conversion fallback for `anthropic-skills:docx`/`pptx`/`xlsx` |
| `vscode` | `anysphere.remote-ssh` | Cursor's Remote SSH extension |
| `uv` | `notebooklm-mcp-cli` | NotebookLM CLI installed via `uv` |
| `uv` | `specify-cli` | github/spec-kit — greenfield Spec-Driven Development |
| `uv` | `youtube-studio-mcp` | YouTube Studio MCP server — analytics / upload / caption tooling behind the YouTube skills |

## 3. What `npm-globals.json` contains right now

11 global npm packages (`npm` itself is excluded from the restore loop):

| Package | Why |
|---|---|
| `@anthropic-ai/claude-code` | Claude Code itself |
| `@google/gemini-cli` | Gemini CLI — alternative agent CLI |
| `@openai/codex` | OpenAI Codex CLI — alternative agent CLI |
| `agent-browser` | Browser-automation CLI (Vercel `agent-browser` skill) |
| `defuddle` | Clean-markdown web extraction (the `defuddle` skill) |
| `docx` | docx generation library (referenced by the docx skill) |
| `pnpm` | Fast package manager used across JS projects |
| `pptxgenjs` | pptx generation library |
| `vercel` | Vercel CLI — deploys + env management |
| `zubeid-youtube-mcp-server` | YouTube MCP server — backs `baoyu-youtube-transcript` and `jove-youtube-feed-pipeline` |
| `npm` | npm itself — excluded from the restore loop |

Notably **NOT** captured globally: `nlm` (NotebookLM CLI) — it's uv-managed (`notebooklm-mcp-cli` in the Brewfile) or installed on-demand by skills.

---

## 4. How to use `restore.sh`

### Prerequisites (one-time, before running)

1. macOS with internet
2. Claude Code installed: `brew install claude-code` (or the official installer)
3. `claude login` — authenticated to your Claude subscription
4. This kit directory accessible (restore from iCloud / external drive / git remote)

### Run it

`restore.sh` self-locates — it works from wherever you place the kit, no setup needed:

```bash
bash "/path/to/Claude Agents and Skills (PORTABILITY KIT)/Tooling/restore.sh"
```

> The manual snippets elsewhere in this kit reference a `$KIT_DIR` variable. Set it once with `cd "/path/to/Claude Agents and Skills (PORTABILITY KIT)" && export KIT_DIR="$PWD"` (see BOOTSTRAP.md §0). `restore.sh` itself does **not** need it.

It prompts once for confirmation, then runs end-to-end:

| Step | What it does | Approximate time |
|---|---|---|
| 1 | Install Homebrew if missing | 30s–3min |
| 2 | `brew bundle` (formulas, casks, vscode extensions, uv tools) | 5–10min |
| 3 | Install global npm packages | 1–2min |
| 4 | Copy `CLAUDE-global.md` → `~/.claude/CLAUDE.md` and `settings.json` → `~/.claude/settings.json` | <1s |
| 5 | Restore 35 agents + 131 skills via `rsync` | <5s |
| 6 | Register 3 marketplaces + install 8 plugins | 1–3min |
| 7 | **Manual** — print instructions for MCP secrets (the script can't paste your JWT for you) | — |

The only thing the script doesn't do for you is **fill in your n8n JWT** in `MCP/mcp.template.json` — that secret lives in your password manager and you have to paste it yourself before copying to `~/.claude/mcp.json`.

### Permission flow

The first time Claude Code runs this script on the new Mac, it may prompt you to allow Bash. **Approve it once.** Then because step 4 copies the kit's `settings.json` (which has `"Bash(*)"` in `permissions.allow`) into place, every subsequent install command runs without prompting — even though the script keeps running. You give consent once; the script handles the rest.

### Idempotency

Safe to re-run if it fails partway through:

- `brew bundle` skips already-installed packages
- `npm install -g` skips already-installed packages
- `rsync` is incremental
- `claude plugin marketplace add` returns non-zero on duplicate but is wrapped in `|| true`
- `claude plugin install` skips already-installed plugins

---

## 5. Keeping these snapshots current

When you install a new tool or remove an old one on the live Mac, re-snapshot. `cd` into this kit's `Tooling/` directory first (wherever the kit lives), then:

```bash
# cd into <this kit>/Tooling first
brew bundle dump --force --file=./Brewfile
npm list -g --depth=0 --json > ./npm-globals.json
```

Commit both files (if this kit is in git) so the next restore captures the latest state.

---

## 6. What's *not* captured here

- **Shell config** (`~/.zshrc`, `~/.bash_profile`) — PATH exports, aliases, custom functions. These affect tool discovery but aren't packages.
- **Application data** — Cursor/VS Code settings, browser profiles, etc.
- **System-level tools** — `git`, `python3`, `bash`, `curl` (these come from macOS itself)
- **nvm-managed Node versions** — `nvm` is installed but no default version is set; the active Node is from Homebrew (captured)
- **Cursor IDE itself** — `anysphere.remote-ssh` extension is captured but the Cursor app has to be installed separately from cursor.sh
- **Cowork / Claude Desktop** — separate app, not a CLI package
- **API keys / OAuth secrets** — by design; they belong in 1Password
