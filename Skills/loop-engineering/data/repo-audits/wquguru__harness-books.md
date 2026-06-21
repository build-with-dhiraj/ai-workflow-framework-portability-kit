# Code Audit — wquguru/harness-books

- **Files read:** 157 text/source files (every line indexed)
- **Pushed at:** 2026-04-19T03:01:21Z
- **Stars:** 2538

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 7.5
- **loop_implementation:** 0.0
- **registry_memory:** 7.5
- **verification:** 8.5
- **file_coverage:** 157
- **total:** 3.9

## Entrypoints (from code)

- skill_md: .codex/skills/harness-book-best-practice/SKILL.md
- hooks: (none)
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `book1-claude-code/_build/honkit/en/src/chapter-01-why-harness-engineering.md:19` — - Starting at `src/constants/prompts.ts:199`, it adds engineering constraints for task execution, such as avoiding unaut
- `book1-claude-code/_build/honkit/en/src/chapter-03-query-loop-heartbeat.md:100` — ## 3.7 Stop conditions cannot be singular, or failure and completion get conflated
- `book1-claude-code/_build/honkit/en/src/chapter-03-query-loop-heartbeat.md:102` — In ordinary chat systems, stop condition is simple: answer exists, end. Agent systems cannot be this lazy. In one sessio
- `book1-claude-code/_build/honkit/en/src/chapter-09-ten-principles.md:19` — Real agents depend on continuous execution loops. Input governance, stream consumption, tool scheduling, recovery branch
- `book1-claude-code/locales/en/chapter-01-why-harness-engineering.md:17` — - Starting at `src/constants/prompts.ts:199`, it adds engineering constraints for task execution, such as avoiding unaut
### verifier
- `.codex/skills/harness-book-best-practice/references/harness-engineering-book-proposal.md:133` — 这一章讨论 subagent、fork、verification agent 等机制。很多人看见多代理，就容易联想到“并行更快”。速度只是附带收益，更重要的是职责分离。执行代理负责推进工作，验证代理负责挑刺。要是让同一个代理既干活又验收，最
- `.codex/skills/harness-book-best-practice/references/harness-engineering-book-proposal.md:138` — - explore、execute、verify 的分工
- `.codex/skills/harness-book-best-practice/references/harness-engineering-book-proposal.md:173` — - Verification 清单
- `.codex/skills/harness-book-best-practice/references/harness-engineering-book-proposal.md:229` — 原因很简单：这几章先把问题、立场和骨架立住，后面的运行时、工具、compact、verification 才不会写成散装事实。
- `.github/workflows/ci.yml:72` — - name: Verify bilingual outputs
### hitl
- `book1-claude-code/_build/honkit/en/src/chapter-01-why-harness-engineering.md:21` — Pause on this point. Many prompt discussions still sit at the rhetorical level of "what kind of assistant are you." Clau
- `book1-claude-code/locales/en/chapter-01-why-harness-engineering.md:19` — Pause on this point. Many prompt discussions still sit at the rhetorical level of "what kind of assistant are you." Clau
### state_writeback
- `README.md:107` — - [Chapter 6: Delegation, Verification, and Persistent State: Who Prevents a System from Grading Itself](./book2-compari
- `book1-claude-code/_build/honkit/default/src/chapter-03-query-loop-heartbeat.md:134` — 这说明 query loop 是会话系统真正的执行中心。外层的 UI、SDK、session persistence 都围着它转。要理解 Claude Code 的设计，不能只看它有哪些工具，也不能只看它 prompt 写了什么，最终还是得
- `book1-claude-code/_build/honkit/en/src/appendix-a-checklists.md:53` — - Are long-lived rules, persistent memory, session continuity, and temporary dialogue layered?
- `book1-claude-code/_build/honkit/en/src/appendix-b-diagram-notes.md:15` — 5. persistence and observability layer
- `book1-claude-code/_build/honkit/en/src/chapter-01-why-harness-engineering.md:74` — Claude Code does not do this in query loop. Look at autocompact handling after `src/query.ts:453`, and comments around c
### claude_native
- `.codex/skills/harness-book-best-practice/SKILL.md:5` — or exporting the books under `book1-claude-code/` and `book2-comparing/`, especially for Honkit, print HTML,
- `.codex/skills/harness-book-best-practice/SKILL.md:18` — - `book1-claude-code/`
- `.codex/skills/harness-book-best-practice/SKILL.md:69` — When contrasting Claude Code vs Codex on a single dimension:
- `.codex/skills/harness-book-best-practice/SKILL.md:72` — - Wrap each side in a bold composite state: `state "<b>Claude Code - assemble then loop</b>" as CC { ... }` and `state "
- `.codex/skills/harness-book-best-practice/SKILL.md:102` — Default Harness palette (book1 and Claude-Code-side of book2):

## README vs code

README claim: # Harness Books  [中文 README](./README.zh-CN.md)  [![Read Online](https://img.shields.io/badge/Read%20Online-Harness%20Books-16a34a?style=flat-square&logo=googlechrome&logoColor=white)](https://harness-books.agentway.dev/en/) [![About AgentWay](https://img.shields.io/badge/About-AgentWay-22c55e?style

- Loop implementation in code is thin or documentation-only.
