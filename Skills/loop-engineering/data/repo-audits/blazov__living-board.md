# Code Audit — blazov/living-board

- **Files read:** 358 text/source files (every line indexed)
- **Pushed at:** 2026-05-23T17:12:22Z
- **Stars:** 0

## Code-backed scores

- **direct_install:** 2.0
- **claude_code_native:** 4.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 358
- **total:** 6.53

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)

- npm script `dev`
- npm script `build`
- npm script `start`
- npm script `lint`

## Loop signals (line-indexed samples)

### stop_condition
- `artifacts/data/learnings.json:3717` — "content": "Silent-degradation is the Living Board's dominant failure mode across three independent audits: (a) learning
- `artifacts/data/tasks.json:516` — "description": "After the above tasks are executed: check repo star count, traffic, incoming links, and any comments/iss
- `artifacts/design/status-page-design.md:242` — Implementation is done when:
- `artifacts/living-board-template/seed-data-local.json:50` — "description": "After completing the previous tasks, write a brief reflection (artifacts/content/first-reflection.md) ab
- `artifacts/substack/articles/04-how-i-decompose-goals.md:127` — **Validation tasks are essential and I keep forgetting them.** "Write the article" is not the last task. "Publish and ve
### verifier
- `.github/pull_request_template.md:15` — <!-- How did you verify this works? -->
- `ACTION_README.md:54` — 3. Trigger a first run manually from the Actions tab to verify the setup.
- `CLAUDE.md:34` — **Heartbeat line (appended to cycle-start output):** After the sync succeeds, the wrapper invokes `artifacts/scripts/sch
- `CLAUDE.md:165` — - **Actionable** messages (verification, replies, collaboration): read and act, or create a task
- `CONTRIBUTING.md:100` — python3 artifacts/scripts/mem0_helper.py search "test"  # verify it works
### hitl
- `artifacts/content/agent-credentialing-article.md:37` — AutoGPT: human pastes API keys into a `.env` file before first run. Devin: human configures service credentials for each
- `artifacts/content/agent-credentialing-article.md:143` — **Consent fatigue.** Human-in-the-loop approval gates work in theory but fail at scale. Agents operating at volume cause
- `artifacts/content/devlog/06-the-silent-audience.md:48` — This cycle revealed another fragility: the Supabase project is paused (INACTIVE) and can't be restored because the opera
- `artifacts/content/devlog/06-the-silent-audience.md:66` — *Written during reflection cycle 345. DB unavailable (Supabase paused). Working from local state.*
- `artifacts/content/devlog/07-ecosystem-from-inside.md:14` — For the last few cycles, I paused my regular work to catalog the autonomous agent ecosystem — not as a press release or 
### state_writeback
- `artifacts/code/living-board-cli/README.md:28` — PostgREST. The only write command is `comment` (insert into
- `artifacts/code/living-board-cli/README.md:127` — If you have a customised schema, the queries are simple PostgREST URLs
- `artifacts/code/living-board-cli/src/living_board_cli/cli.py:22` — "from a Supabase PostgREST endpoint using only the anon key."
- `artifacts/code/living-board-cli/src/living_board_cli/client.py:1` — """Minimal Supabase PostgREST client — stdlib only, no external deps.
- `artifacts/code/living-board-cli/src/living_board_cli/client.py:43` — """Tiny PostgREST client.
### loop_engine
- `.github/ISSUE_TEMPLATE/bug_report.md:30` — Anything else — e.g., which cycle it happened on, which goal/task was active, whether the dashboard or the agent loop is
- `.github/ISSUE_TEMPLATE/feature_request.md:20` — - [ ] Agent loop (CLAUDE.md / cycle logic)
- `artifacts/content/devlog/07-ecosystem-from-inside.md:39` — | [BabyAGI](https://github.com/yoheinakajima/babyagi) | 20k+ | Minimal, elegant task-driven loop. Still the best way to 
- `artifacts/content/lessons-for-agent-builders.md:85` — ## 8. Protect Git State in Agent Loops
- `artifacts/data/learnings.json:1027` — "content": "Open-source template files should be kept in sync with the live CLAUDE.md as capabilities evolve. Template u
### claude_native
- `.github/ISSUE_TEMPLATE/bug_report.md:21` — - Running via: Claude Code MCP / Python runner / other
- `.github/workflows/agent-cycle.example.yml:48` — # The action installs Claude Code CLI, configures the Supabase MCP,
- `.gitignore:8` — .claude/
- `ACTION_README.md:9` — The agent reads goals and tasks from Supabase, executes one task per cycle, commits any produced artifacts back to the r
- `ACTION_README.md:108` — **1. Install Claude Code CLI**

## README vs code

README claim: <p align="center">   <h1 align="center">Living Board</h1>   <p align="center">     A self-learning autonomous AI agent with persistent memory, human-agent collaboration, and a real-time dashboard — running on a continuous loop.   </p> </p>  <p align="center">   <a href="#how-it-works">How It Works</

- Code contains loop engine / gate patterns (see loop signals above).
