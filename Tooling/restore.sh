#!/usr/bin/env bash
# restore.sh — One-shot Mac-replacement restoration for the Claude capability kit.
#
# Run this ONCE on a fresh Mac after:
#   1. Installing Claude Code (`brew install claude-code` or the official installer)
#   2. Running `claude login` and authenticating
#
# It is idempotent — safe to re-run if it fails partway through.
# Total runtime: ~10-15 minutes (dominated by `brew bundle`).

set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_HOME="$HOME/.claude"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Claude capability-kit restore"
echo "  Source: $KIT_DIR"
echo "  Target: $CLAUDE_HOME"
echo "═══════════════════════════════════════════════════════════════"
echo ""
read -r -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# ─── Step 1: Homebrew ────────────────────────────────────────────────
echo ""
echo "==> Step 1/7: Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "  Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Make brew available on Apple Silicon
  eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || true
else
  echo "  Homebrew already installed ($(brew --version | head -1))"
fi

# ─── Step 2: Brew bundle (formulas, casks, vscode extensions, uv tools) ──
echo ""
echo "==> Step 2/7: Installing brew packages from Brewfile"
brew bundle --file="$KIT_DIR/Tooling/Brewfile"

# ─── Step 3: Global npm packages ─────────────────────────────────────
echo ""
echo "==> Step 3/7: Installing global npm packages"
if ! command -v node >/dev/null 2>&1; then
  echo "  ERROR: node not on PATH after brew install. Open a new shell and re-run."
  exit 1
fi
node -e '
  const list = require("'"$KIT_DIR"'/Tooling/npm-globals.json").dependencies || {};
  Object.keys(list).filter(n => n !== "npm").forEach(n => console.log(n));
' | while read -r pkg; do
  [ -z "$pkg" ] && continue
  echo "  npm install -g $pkg"
  npm install -g "$pkg"
done

# ─── Step 4: Claude Code global config ───────────────────────────────
echo ""
echo "==> Step 4/7: Restoring global Claude Code config"
mkdir -p "$CLAUDE_HOME"
cp "$KIT_DIR/CLAUDE-global.md" "$CLAUDE_HOME/CLAUDE.md"
cp "$KIT_DIR/settings.json" "$CLAUDE_HOME/settings.json"
echo "  Wrote $CLAUDE_HOME/CLAUDE.md ($(wc -l <"$CLAUDE_HOME/CLAUDE.md") lines)"
echo "  Wrote $CLAUDE_HOME/settings.json"

# ─── Step 5: Custom agents and skills ────────────────────────────────
echo ""
echo "==> Step 5/7: Restoring agents and skills"
mkdir -p "$CLAUDE_HOME/agents" "$CLAUDE_HOME/skills"
rsync -a --exclude='/README.md' "$KIT_DIR/Agents/" "$CLAUDE_HOME/agents/"
rsync -a --exclude='/README.md' "$KIT_DIR/Skills/" "$CLAUDE_HOME/skills/"
echo "  Agents: $(ls "$CLAUDE_HOME/agents"/*.md | wc -l | tr -d ' ')"
echo "  Skills: $(ls -d "$CLAUDE_HOME/skills"/*/ | wc -l | tr -d ' ')"

# ─── Step 6: Plugin marketplaces and plugins ─────────────────────────
echo ""
echo "==> Step 6/8: Plugin marketplaces and plugins"

# Two marketplaces are local-directory sources — their contents must exist on
# disk BEFORE the marketplace can be registered.
mkdir -p "$HOME/.cache/plugins" "$HOME/.claude/plugins/local-src"
rsync -a "$KIT_DIR/Plugins/vercel-marketplace-source/" \
         "$HOME/.cache/plugins/github.com-vercel-vercel-plugin/"
rsync -a "$KIT_DIR/Plugins/claude-seo-source/" \
         "$HOME/.claude/plugins/local-src/claude-seo/"

# SYNTAX: `marketplace add` takes a bare owner/repo, URL, or path. The
# `github` / `git` / `directory` keyword forms are NOT valid and fail with
# "Invalid marketplace source format" — verified against CLI 2.1.223.
# Failures here are not fatal on their own, but every plugin install below
# depends on them, so report rather than swallow.
add_marketplace() {
  if claude plugin marketplace add "$1" >/dev/null 2>&1; then
    echo "  marketplace ok: $1"
  else
    echo "  marketplace SKIPPED (already added, or unreachable): $1"
  fi
}
add_marketplace obra/superpowers-marketplace
add_marketplace forrestchang/andrej-karpathy-skills
add_marketplace anthropics/knowledge-work-plugins
add_marketplace https://github.com/DietrichGebert/ponytail.git
add_marketplace "$HOME/.cache/plugins/github.com-vercel-vercel-plugin"
add_marketplace "$HOME/.claude/plugins/local-src/claude-seo"

for p in figma@claude-plugins-official \
         vercel-plugin@vercel-vercel-plugin \
         superpowers@superpowers-marketplace \
         superpowers-chrome@superpowers-marketplace \
         superpowers-developing-for-claude-code@superpowers-marketplace \
         superpowers-lab@superpowers-marketplace \
         andrej-karpathy-skills@karpathy-skills \
         github@claude-plugins-official \
         ponytail@ponytail \
         youdotcom-agent-skills@claude-plugins-official \
         claude-seo@agricidaniel-seo \
         productivity@knowledge-work-plugins \
         cowork-plugin-management@knowledge-work-plugins; do
  echo "  Installing $p"
  claude plugin install "$p" || echo "    (skipped — already installed or unavailable)"
done
# NOTE: vercel-plugin is installed but disabled in settings.json ("enabledPlugins" false).
# Installing it keeps parity with the source machine; flip the flag to activate.
#
# claude-seo ships as a directory marketplace, NOT as a skill. It is a plugin
# (25 skills + 18 agents) that used to sit loose in ~/.claude/skills/ and load
# by accidental auto-discovery as "claude-seo@skills-dir". Registering it
# properly is what makes it reproducible here.

# ─── Step 7: MCP config ──────────────────────────────────────────────
echo ""
echo "==> Step 7/8: MCP server registry"
cp "$KIT_DIR/MCP/mcp.template.json" "$CLAUDE_HOME/mcp.json"
echo "  Wrote $CLAUDE_HOME/mcp.json"
echo ""
echo "  This snapshot carries NO secrets — the only locally-registered"
echo "  server launches over stdio via npx, so the copy above is complete."
echo "  If a future snapshot adds an HTTP server with an Authorization"
echo "  header, it ships redacted and you must paste the live token from"
echo "  your password manager into $CLAUDE_HOME/mcp.json by hand."
echo ""
echo "  Account-bound connectors (Gmail, Drive, Slack, Supabase, etc.)"
echo "  reattach automatically on your next \`claude\` session. OAuth"
echo "  re-prompts will appear in the browser on first use of each."
echo ""

# ─── Step 8: Private capability overlay (folder-only, never in the repo) ──
echo ""
echo "==> Step 8/8: Private capability overlay"
PRIV="$KIT_DIR/Private"
if [ -d "$PRIV" ]; then
  # 7 skills withheld from the public repo
  rsync -a --exclude='/README.md' "$PRIV/Skills/" "$CLAUDE_HOME/skills/"
  # second config root (work profile); its agents are identical to the default
  # profile's, so they come from Agents/ rather than being stored twice
  JOVE="$HOME/.claude-jove"
  mkdir -p "$JOVE/agents" "$JOVE/skills" "$JOVE/plugins"
  cp "$PRIV/work-profile/CLAUDE.md"     "$JOVE/CLAUDE.md"
  cp "$PRIV/work-profile/SPEC-KIT.md"   "$JOVE/SPEC-KIT.md"
  cp "$PRIV/work-profile/settings.json" "$JOVE/settings.json"
  cp "$PRIV/work-profile/installed_plugins.json"  "$JOVE/plugins/"
  cp "$PRIV/work-profile/known_marketplaces.json" "$JOVE/plugins/"
  rsync -a --exclude='/README.md' "$KIT_DIR/Agents/" "$JOVE/agents/"
  rsync -a "$KIT_DIR/Skills/" "$JOVE/skills/"
  rsync -a "$PRIV/Skills/"    "$JOVE/skills/"
  rsync -a "$PRIV/work-profile/skills-delta/" "$JOVE/skills/"
  echo "  Default profile skills: $(ls -1 "$CLAUDE_HOME/skills" | grep -v '^\.' | wc -l | tr -d ' ') (expect 155)"
  echo "  Work profile skills:    $(ls -1 "$JOVE/skills" | grep -v '^\.' | wc -l | tr -d ' ') (expect 157)"
else
  echo "  No Private/ overlay found — skipping."
  echo "  This is EXPECTED if you git-cloned the repo instead of copying the folder."
  echo "  Consequence: 7 work-specific skills and the ~/.claude-jove profile are"
  echo "  absent. The public layers above are complete and usable on their own."
fi

# ─── Summary ─────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Restore complete."
echo "  Start a new Claude Code session and verify:"
echo "    - 36 custom agents listed"
echo "    - 148 skills from the repo (155 with the Private/ overlay)"
echo "    - 13 plugins installed, 12 enabled (run \`claude plugin list\`)"
echo "    - Engineering Manager mode active on first prompt"
echo ""
echo "  Account-side capability (app-delivered plugins, claude.ai skills,"
echo "  connectors) is NOT restored by this script and does not need to be —"
echo "  it reattaches on \`claude login\`. See Plugins/README.md §Delivery tiers."
echo "═══════════════════════════════════════════════════════════════"
