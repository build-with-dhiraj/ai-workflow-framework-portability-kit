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
rsync -a --exclude='README.md' "$KIT_DIR/Agents/" "$CLAUDE_HOME/agents/"
rsync -a --exclude='README.md' "$KIT_DIR/Skills/" "$CLAUDE_HOME/skills/"
echo "  Agents: $(ls "$CLAUDE_HOME/agents"/*.md | wc -l | tr -d ' ')"
echo "  Skills: $(ls -d "$CLAUDE_HOME/skills"/*/ | wc -l | tr -d ' ')"

# ─── Step 6: Plugin marketplaces and plugins ─────────────────────────
echo ""
echo "==> Step 6/7: Plugin marketplaces and plugins"
# Restore the Vercel marketplace source first (it's a local-directory source)
mkdir -p "$HOME/.cache/plugins"
rsync -a "$KIT_DIR/Plugins/vercel-marketplace-source/" \
         "$HOME/.cache/plugins/github.com-vercel-vercel-plugin/"

claude plugin marketplace add github obra/superpowers-marketplace 2>/dev/null || true
claude plugin marketplace add github forrestchang/andrej-karpathy-skills 2>/dev/null || true
claude plugin marketplace add directory \
  "$HOME/.cache/plugins/github.com-vercel-vercel-plugin" 2>/dev/null || true

for p in figma@claude-plugins-official \
         vercel-plugin@vercel-vercel-plugin \
         superpowers@superpowers-marketplace \
         superpowers-chrome@superpowers-marketplace \
         superpowers-developing-for-claude-code@superpowers-marketplace \
         superpowers-lab@superpowers-marketplace \
         andrej-karpathy-skills@karpathy-skills \
         github@claude-plugins-official; do
  echo "  Installing $p"
  claude plugin install "$p" || echo "    (skipped — already installed or unavailable)"
done

# ─── Step 7: MCP config (manual step for secrets) ────────────────────
echo ""
echo "==> Step 7/7: MCP server registry — MANUAL ACTION REQUIRED"
echo ""
echo "  This kit ships a redacted MCP template. To finish:"
echo ""
echo "    1. Edit:  $KIT_DIR/MCP/mcp.template.json"
echo "       Replace REDACTED_PUT_N8N_MCP_JWT_HERE with the live JWT"
echo "       (it lives in your password manager)."
echo ""
echo "    2. Copy into place:"
echo "       cp '$KIT_DIR/MCP/mcp.template.json' '$CLAUDE_HOME/mcp.json'"
echo ""
echo "  Account-bound connectors (Gmail, Drive, Slack, Supabase, etc.)"
echo "  reattach automatically on your next \`claude\` session. OAuth"
echo "  re-prompts will appear in the browser on first use of each."
echo ""

# ─── Summary ─────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  Restore complete."
echo "  Start a new Claude Code session and verify:"
echo "    - 31 custom agents listed"
echo "    - 8 plugins enabled (run \`claude plugin list\`)"
echo "    - Engineering Manager mode active on first prompt"
echo "═══════════════════════════════════════════════════════════════"
