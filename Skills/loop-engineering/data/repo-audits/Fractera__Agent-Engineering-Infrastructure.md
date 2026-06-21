# Code Audit — Fractera/Agent-Engineering-Infrastructure

- **Files read:** 389 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T00:30:26Z
- **Stars:** 27

## Code-backed scores

- **direct_install:** 3.0
- **claude_code_native:** 4.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 389
- **total:** 6.78

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
- npm script `postinstall:mac`
- npm script `install:all`

## Loop signals (line-indexed samples)

### stop_condition
- `docs/platforms/codex/best-practices.md:20` — - **Done when:** What should be true before the task is complete, such as tests passing, behavior changing, or a bug no 
- `docs/platforms/kimi-code/keyboard-shortcuts.md:3` — Kimi Code CLI shell mode supports the following keyboard shortcuts. Press Ctrl-D to exit when the input box is empty; pr
- `docs/platforms/qwen-code/agent-arena.md:110` — "maxRoundsPerAgent": 50,
- `docs/platforms/qwen-code/agent-arena.md:119` — | `arena.maxRoundsPerAgent` | Maximum reasoning rounds per agent | `50` |
- `docs/platforms/qwen-code/agent-arena.md:179` — - Lower `arena.maxRoundsPerAgent` if agents are spending too many rounds
### verifier
- `README.md:151` — Most traditional scaffolding tools provide empty, "Hello World" skeletons. Fractera reverses this by landing a massive, 
- `README.md:281` — 3. **Commit the Architectural Increments:** Push your verified agent modifications, new features, or business logic upda
- `README.md:442` — 3. Push your verified changes back to your GitHub repository origin.
- `README.md:487` — 9. **Instant Production Sync:** Your web site updates automatically after each verified engineering cycle with zero manu
- `bridges/app/_components/coding-workspace/auth-flow-descriptors.ts:64` — modalDescription: 'Open the link in your browser and authorize Kimi Code. The verification code is already included in t
### hitl
- `README.md:413` — * **Data Sovereignty:** If you pause your active development, your databases do not vanish. Create an immutable environm
- `docs/platforms/codex/cli-reference.md:19` — | `--ask-for-approval, -a` | untrusted \| on-request \| never | Control when Codex pauses for human approval before runn
- `docs/platforms/codex/config-advanced.md:245` — Pick approval strictness (affects when Codex pauses) and sandbox level (affects file/network access).
- `docs/platforms/codex/config-basics.md:50` — Control when Codex pauses to ask before running generated commands.
- `docs/platforms/gemini-cli/notifications.md:55` — tool approval. This helps you know when the CLI has paused and needs you to
### state_writeback
- `.gitignore:14` — app/database.sqlite
- `.gitignore:15` — app/database.sqlite-shm
- `.gitignore:16` — app/database.sqlite-wal
- `.gitignore:17` — app/data/*.sqlite
- `.gitignore:18` — app/data/*.sqlite-shm
### loop_engine
- `deploy-loop.md:132` — while true; do
- `docs/platforms/claude-code/overview.md:190` — - [`/loop`](/en/scheduled-tasks) repeats a prompt within a CLI session for quick polling
- `docs/platforms/gemini-cli/hooks-reference.md:68` — | `continue` | `boolean` | If `false`, stops the entire agent loop immediately. |
- `docs/platforms/gemini-cli/hooks-reference.md:103` — - `continue`: Set to `false` to **kill the entire agent loop** immediately.
- `docs/platforms/gemini-cli/hooks-reference.md:126` — - `continue`: Set to `false` to **kill the entire agent loop** immediately.
### claude_native
- `README.md:35` — <img src="https://img.shields.io/badge/Claude_Code-Anthropic-d4a017?style=flat-square" alt="Claude Code"/>
- `README.md:267` — *   **The Unified Multi-Agent Control Room:** The top cockpit matrix maps low-latency browser PTY (Pseudo-Teletype) node
- `README.md:294` — | **5 AI Coding Engines** | *Claude Code*, *OpenAI Codex*, *Gemini CLI*, *Qwen Code*, and *Kimi Code* initialized in par
- `README.md:378` — The real cost driver in AI-assisted development is not the number of requests—it is **context window inflation**. Every 
- `README.md:401` — * **LightRAG Coordination:** All five execution platforms share the same persistent vector memory graph, allowing you to

## README vs code

README claim: <h1 align="center">Fractera: Agent Engineering Infrastructure</h1>  <p align="center"><strong>Stop vibe coding. Start engineering. Fractera delivers a production-grade multi-agent development environment that configures itself on your own hardware. Automatically deploy a 50,000-line Next.js enterpri

- Code contains loop engine / gate patterns (see loop signals above).
