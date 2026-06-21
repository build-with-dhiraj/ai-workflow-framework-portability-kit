#!/usr/bin/env bash
# Sync GitHub repo "About" description with live kit counts (Agents/ + Skills/).
# Safe to run locally (gh auth required) or from .github/workflows/sync-repo-about.yml.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${GITHUB_REPOSITORY:-build-with-dhiraj/ai-workflow-framework-portability-kit}"

AGENTS=$(find "$KIT_DIR/Agents" -maxdepth 1 -name '*.md' ! -name 'README.md' | wc -l | tr -d ' ')
SKILLS=$(find "$KIT_DIR/Skills" -mindepth 1 -maxdepth 1 -type d ! -name '.archive*' | wc -l | tr -d ' ')

NEW_DESC="Portable, self-contained snapshot of a complete Claude Code setup — ${AGENTS} specialist agents, ${SKILLS} skills, plugins, MCP servers & host tooling. Clone, claude login, run one script, restore the whole orchestration stack in ~20 min."

if ! command -v gh >/dev/null 2>&1; then
  echo "error: gh CLI required" >&2
  exit 1
fi

CURRENT=$(gh repo view "$REPO" --json description -q .description 2>/dev/null || echo "")

if [ "$CURRENT" = "$NEW_DESC" ]; then
  echo "About already up to date (${AGENTS} agents, ${SKILLS} skills)."
  exit 0
fi

echo "Updating About: ${AGENTS} agents, ${SKILLS} skills"
gh repo edit "$REPO" --description "$NEW_DESC"
echo "Done."
