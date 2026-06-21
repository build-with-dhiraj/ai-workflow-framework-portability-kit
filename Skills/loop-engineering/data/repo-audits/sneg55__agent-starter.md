# Code Audit — sneg55/agent-starter

- **Files read:** 60 text/source files (every line indexed)
- **Pushed at:** 2026-06-16T21:52:12Z
- **Stars:** 10

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 0.8
- **registry_memory:** 7.5
- **verification:** 7.5
- **file_coverage:** 60
- **total:** 4.45

## Entrypoints (from code)

- skill_md: skills/adopt-project/SKILL.md, skills/commit/SKILL.md, skills/commit-push-pr/SKILL.md, skills/dream/SKILL.md, skills/new-project/SKILL.md, skills/reflect/SKILL.md, skills/remember/SKILL.md, skills/simplify/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### verifier
- `ADOPT.md:113` — - **mypy in use** → don't add pyright without asking; two type checkers
- `ADOPT.md:155` — ## Step 5: Verify
- `AGENT.md:188` — ## Step 3: Verify Output
- `README.md:54` — Complete reference for Claude Code's hook system - all 4 hook types, all 27 events, exit code behavior, configuration fo
- `README.md:133` — Per-project self-improvement - reads the `.harness` ledger and `feedback` memories, clusters recurring mistakes, and pro
### state_writeback
- `ADOPT.md:56` — - **Patterns already present:** central error registry? env boundary? Result
- `ADOPT.md:117` — - env boundary (`env.ts` / `env.py`), error registry (`errorIds.ts` /
- `ADOPT.md:133` — - Touching a `throw` / `raise` site → route it through the error registry
- `ADOPT.md:134` — (`guides/error-id-registry.md`).
- `AGENT.md:113` — For Python projects, also offer the Python foundation templates: `templates/env.py` (env boundary), `templates/error_ids
### loop_engine
- `guides/prompt-caching.md:65` — A healthy agent loop runs **> 0.85** hit rate steady-state. Below 0.5 means the prefix is unstable - go find the timesta
### claude_native
- `.claude-plugin/marketplace.json:2` — "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
- `.claude-plugin/marketplace.json:25` — "claude-code",
- `.claude-plugin/plugin.json:2` — "$schema": "https://json.schemastore.org/claude-code-plugin.json",
- `.claude-plugin/plugin.json:13` — "claude-code",
- `.gitignore:1` — .claude/

## README vs code

README claim: # agent-starter  A toolkit of skills, templates, and guides for bootstrapping AI-agent-friendly projects.  It **started** as Anthropic's own engineering patterns - extracted from the Claude Code CLI source and packaged into reusable form. It has since been **extended** with additional best practices

- Loop implementation in code is thin or documentation-only.
