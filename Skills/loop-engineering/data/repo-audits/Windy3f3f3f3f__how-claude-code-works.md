# Code Audit — Windy3f3f3f3f/how-claude-code-works

- **Files read:** 45 text/source files (every line indexed)
- **Pushed at:** 2026-05-05T15:39:49Z
- **Stars:** 2688

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 4.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 45
- **total:** 6.03

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `docs/14-system-prompt-design.md:2556` — >   - `"remove"` — delete the worktree directory and its branch. Use this for a clean exit when the work is done or aban
- `en/docs/02-agent-loop.md:205` — Attach --> Stop{Stop condition check}
- `en/docs/02-agent-loop.md:476` — ## 2.10 Stop Conditions
### verifier
- `README_EN.md:23` — This project is the answer. We've distilled **14 topic-specific documents** (338K characters total) covering every criti
- `README_EN.md:78` — 3. **9-phase parallel startup** — Independent initialization tasks run in parallel, compressing the critical path to ~23
- `README_EN.md:148` — | 11 | [Task Management System](./en/docs/15-task-system.md) | File-level storage with concurrency locking, 3-layer chan
- `docs/03-context-engineering.md:619` — CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.
- `docs/04-tool-system.md:657` — | Git 安全旁路 | `--no-verify` | "may skip safety hooks" |
### hitl
- `docs/14-system-prompt-design.md:3821` — >    - NEVER use `Read-Host`, `Get-Credential`, `Out-GridView`, `$Host.UI.PromptForChoice`, or `pause`
- `docs/14-system-prompt-design.md:3862` — >    - 永远不要使用 `Read-Host`、`Get-Credential`、`Out-GridView`、`pause`
- `en/docs/01-overview.md:88` — - **Callback pattern**: Classic Node.js style, prone to "callback hell." More importantly, it cannot elegantly handle ba
- `en/docs/01-overview.md:330` — **Step 3: The 4-level compression pipeline runs.** Note -- compression doesn't run just once at the start of the convers
- `en/docs/03-context-engineering.md:990` — Claude Code has a built-in five-level compression pipeline that automatically triggers as the context approaches the win
### state_writeback
- `docs/03-context-engineering.md:477` — <persisted-output>
- `docs/03-context-engineering.md:483` — </persisted-output>
- `docs/06-hooks-extensibility.md:560` — **异步模式（`async: true`）**：Hook 进程在后台运行，通过 `registerPendingAsyncHook()` 注册到全局的 `AsyncHookRegistry`，立即返回 success。Agent Loop 
- `docs/06-hooks-extensibility.md:567` — // asyncRewake hooks 绕过 AsyncHookRegistry
- `docs/08-memory-system.md:620` — Contents of ~/.claude/projects/a1b2c3d4/memory/MEMORY.md (user's auto-memory, persists across conversations):
### loop_engine
- `README.md:145` — | 2 | [系统主循环](./docs/02-agent-loop.md) | Agent 循环的双层架构、7 种 Continue Sites 故障恢复、工具预执行、StreamingToolExecutor 并发机制 |
- `README.md:185` — → 按顺序读 [主循环](./docs/02-agent-loop.md) → [上下文工程](./docs/03-context-engineering.md) → [工具系统](./docs/04-tool-system.md)
- `README_EN.md:23` — This project is the answer. We've distilled **14 topic-specific documents** (338K characters total) covering every criti
- `README_EN.md:84` — When a conversation exceeds the context window, it doesn't pop up an error dialog — it silently compresses the context a
- `README_EN.md:139` — | 2 | [Agent Loop](./en/docs/02-agent-loop.md) | How the agent "think-act-observe" loop works, how it handles interrupti
### claude_native
- `README.md:3` — # How Claude Code Works
- `README.md:7` — [![GitHub stars](https://img.shields.io/github/stars/Windy3f3f3f3f/how-claude-code-works?style=flat-square&logo=github)]
- `README.md:8` — [![GitHub forks](https://img.shields.io/github/forks/Windy3f3f3f3f/how-claude-code-works?style=flat-square&logo=github)]
- `README.md:10` — [![TypeScript](https://img.shields.io/badge/Source-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)]
- `README.md:15` — [**📘 在线阅读文档**](https://windy3f3f3f3f.github.io/how-claude-code-works/#/)

## README vs code

README claim: <div align="center">  # How Claude Code Works  **深入解读当前最成功的 AI 编程 Agent 的源码架构**  [![GitHub stars](https://img.shields.io/github/stars/Windy3f3f3f3f/how-claude-code-works?style=flat-square&logo=github)](https://github.com/Windy3f3f3f3f/how-claude-code-works) [![GitHub forks](https://img.shields.io/gi

- Code contains loop engine / gate patterns (see loop signals above).
