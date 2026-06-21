# Code Audit — ChaoYue0307/awesome-loop-engineering

- **Files read:** 108 text/source files (every line indexed)
- **Pushed at:** 2026-06-21T05:05:19Z
- **Stars:** 11

## Code-backed scores

- **direct_install:** 4.0
- **claude_code_native:** 4.5
- **loop_implementation:** 10
- **registry_memory:** 7.5
- **verification:** 10
- **file_coverage:** 108
- **total:** 7.03

## Entrypoints (from code)

- skill_md: (none)
- hooks: (none)
- loop_scripts: examples/runnable/test-repair-loop.sh, packages/loop-contract-schema/bin/cli.js, packages/loop-contract-schema/index.js, packages/loop-contract-schema/validate.js, scripts/check_loop_contract_examples.py, scripts/preview_loop_contract.py
- main_files: (none)

## Install facts (from manifests)

- bins: loop-contract-validate
- npm script `prepack`
- npm script `test`

## Loop signals (line-indexed samples)

### stop_condition
- `MANIFESTO.md:19` — - **Bound autonomy.** Loops need budgets, allowed actions, disallowed actions, stop conditions, and escalation paths.
- `README.md:484` — - 📄 **Paper** [Verified Multi-Agent Orchestration: A Plan-Execute-Verify-Replan Framework](https://arxiv.org/abs/2603.11
- `examples/cost-control-loop.json:28` — "responsibility": "Inspect traces for context bloat, repeated failures, and missing stop conditions."
- `examples/runnable/claude-desktop-scheduled-task.md:34` — Stop conditions:
- `examples/runnable/claude-loop.md:32` — Stop conditions:
### verifier
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:44` — placeholder: Explorer identifies blockers, Implementer patches, Reviewer checks scope, Judge decides next action.
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:48` — id: verification
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:50` — label: Verification gates
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:52` — placeholder: Required checks pass, examples run, dashboard thresholds hold, reviewer approves, trace grader passes.
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:86` — - label: The pattern includes trigger, intake, delegation, verification, durable state, budget, escalation, and exit.
### hitl
- `README.md:379` — - 🔁 **Pattern** [12 Factor Agents](https://github.com/humanlayer/12-factor-agents) - Operating principles for production
- `README.md:470` — - 🧰 **Tool** [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based framework for controllable agent workf
- `README.md:477` — - 📚 **Docs** [Temporal for AI](https://temporal.io/solutions/ai) - Durable execution for long-running agent workflows: c
- `examples/deploy-verifier-loop.json:53` — "stop_without_success": "The deploy is rolled back, paused, or handed to an incident owner."
- `patterns/deploy-verifier.md:57` — - Stop when the deploy is stable, rolled back, paused, or handed to an incident owner.
### state_writeback
- `.github/ISSUE_TEMPLATE/resource-suggestion.yml:35` — - State, Memory, And Context Persistence
- `.github/pull_request_template.md:21` — Explain how this PR relates to the new AI/coding-agent meaning of Loop Engineering: the layer above prompt, context, and
- `.github/pull_request_template.md:34` — - [ ] State, Memory, And Context Persistence
- `.github/workflows/publish-package.yml:31` — registry-url: "https://npm.pkg.github.com"
- `AGENTS.md:7` — Include resources that help readers design, run, verify, evaluate, or critique recurring AI-agent systems that sit above
### loop_engine
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:2` — description: Suggest a recurring AI-agent loop pattern for the pattern library.
- `.github/ISSUE_TEMPLATE/pattern-suggestion.yml:84` — - label: This is a recurring AI-agent loop, not a one-off prompt or generic automation.
- `.github/ISSUE_TEMPLATE/resource-suggestion.yml:33` — - Coding-Agent Loop Systems
- `.github/ISSUE_TEMPLATE/resource-suggestion.yml:103` — - label: This is about AI/coding-agent Loop Engineering or a direct foundation for recurring agent systems.
- `.github/pull_request_template.md:32` — - [ ] Coding-Agent Loop Systems
### claude_native
- `QUOTES.md:29` — Source: [I Now Just Write Loops To Prompt Claude Code: Claude Code Creator Boris Cherny](https://officechai.com/ai/i-now
- `README.de.md:52` — | Context           | Welches dauerhafte Wissen wird geladen?          | `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, docs     
- `README.de.md:80` — - [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks) - Offizielle Mechanik für `/loop`, geplan
- `README.es.md:52` — | Context           | ¿Qué conocimiento durable debe cargar?     | `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, docs           
- `README.es.md:80` — - [Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks) - Mecánica oficial para `/loop`, tareas p

## README vs code

README claim: <p align="center">   <img src="assets/awesome-loop-engineering-cover.png" alt="Awesome Loop Engineering cover" width="100%"> </p>  <h1 align="center">Awesome Loop Engineering</h1>  <p align="center">   <img src="assets/awesome-loop-engineering-logo.svg" alt="Awesome Loop Engineering logo" width="112

- Code contains loop engine / gate patterns (see loop signals above).
