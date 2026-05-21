# Agents — Roster & Dispatch Logic

34 custom specialist agents live in this folder — 30 engineering implementers (the `engineering-*` files), 1 cross-session-continuity advisor (`agency-kernel-steward`), and 3 consultative expert advisors (`llm-architect`, `prompt-engineer`, `qa-expert`). The engineering implementers are the **implementation tier** of the architecture described in [../CLAUDE.md](../CLAUDE.md). The advisors are dispatched for counsel, not implementation. The orchestrator (top-level Claude Code session) dispatches them all via the `Task` tool; the orchestrator itself never writes code.

> **Where they live on the live Mac:** `~/.claude/agents/`
> Restoration: copy every `*.md` in this folder back to that location. That's it — Claude Code auto-discovers them at session start.

---

## 1. The dispatch contract

Every specialist obeys the same contract when dispatched:

- **Receives:** goal, constraints, relevant files, expected deliverable
- **May:** run Bash, edit files, run tests, commit code, open PRs
- **Returns:** a single message summarizing the work and outcome
- **MUST NOT:** self-refuse citing "Engineering Manager mode" — that rule binds the orchestrator, not them

The full subagent override clause is in `../CLAUDE-global.md` under the "Specialist Behavior" heading. Permissions are pre-allowed globally (`Bash(*)`, `Edit(*)`, `Write(*)` in `../settings.json`).

---

## 2. Org chart — five tiers

```
                              ORCHESTRATOR
                                    │
   ┌──────────────┬─────────────────┼─────────────────┬──────────────┐
   ▼              ▼                 ▼                 ▼              ▼
 PLANNING    IMPLEMENTATION    OPERATIONS         SUPPORT       SPECIALIZED
```

### 2a. Planning tier — picks the approach

| Agent | Use when |
|---|---|
| `engineering-software-architect` | System design, DDD, architectural patterns, scalable/maintainable decisions |
| **Plan** *(built-in)* | Quick "give me a step-by-step plan for X" without research |

(The richer planning workflow is **skill-driven** — `gepetto` for multi-LLM-reviewed plans, `to-prd` for tracker artifacts. See [../Skills/README.md](../Skills/README.md).)

### 2b. Implementation tier — does the work

Generalists:

| Agent | Domain |
|---|---|
| `engineering-senior-developer` | Premium full-stack — Laravel, Livewire, FluxUI, advanced CSS, Three.js integration |
| `engineering-frontend-developer` | Modern frontend — React/Vue/Angular, UI implementation, perf |
| `engineering-backend-architect` | Scalable system design, APIs, cloud infrastructure |
| `engineering-rapid-prototyper` | Ultra-fast MVP, throwaway proofs of concept |
| `engineering-minimal-change-engineer` | Minimum-viable diffs, anti-scope-creep |
| `engineering-mobile-app-builder` | Native iOS/Android + cross-platform |

Domain specialists:

| Agent | Domain |
|---|---|
| `engineering-ai-engineer` | ML model development, AI features, AI pipelines |
| `engineering-ai-data-remediation-engineer` | Self-healing data pipelines, anomaly fixing — SLM-powered |
| `engineering-data-engineer` | ETL/ELT, Spark, dbt, streaming, lakehouse |
| `engineering-database-optimizer` | Schema design, query tuning, indexing — PostgreSQL/MySQL/Supabase/PlanetScale |
| `engineering-cms-developer` | Drupal + WordPress (themes, plugins, content architecture) |
| `engineering-filament-optimization-specialist` | Filament PHP admin interface restructuring |
| `engineering-embedded-firmware-engineer` | ESP32, STM32, Nordic nRF, ARM Cortex-M, FreeRTOS, Zephyr |
| `engineering-solidity-smart-contract-engineer` | EVM contracts, gas optimization, proxy patterns, DeFi |
| `engineering-wechat-mini-program-developer` | WXML/WXSS/WXS, WeChat API, payment, subscription messaging |
| `engineering-feishu-integration-developer` | Lark/Feishu bots, Bitable, message cards, SSO, workflows |
| `engineering-email-intelligence-engineer` | Structured data extraction from email threads |
| `engineering-voice-ai-integration-engineer` | Whisper-style ASR pipelines, transcripts, diarization, subtitles |

### 2c. Operations tier — keeps prod alive

| Agent | Use when |
|---|---|
| `engineering-devops-automator` | Infrastructure-as-code, CI/CD pipelines, cloud ops |
| `engineering-sre` | SLOs, error budgets, observability, chaos engineering, toil reduction |
| `engineering-incident-response-commander` | Live production incident handling, post-mortems, on-call design |
| `engineering-git-workflow-master` | Branching strategies, conventional commits, rebasing, worktrees |
| `engineering-security-engineer` | Threat modeling, secure code review, security architecture, IR |
| `engineering-threat-detection-engineer` | SIEM rules, MITRE ATT&CK mapping, detection-as-code, alert tuning |

### 2d. Support tier — orthogonal helpers

| Agent | Use when |
|---|---|
| `engineering-code-reviewer` | Constructive PR/code review focused on correctness, security, maintainability |
| `engineering-technical-writer` | Developer docs, API references, READMEs, tutorials |
| `engineering-codebase-onboarding-engineer` | Mapping unfamiliar codebases for a new engineer (fact-grounded) |
| `engineering-tabular-data-analyst` | Cold-folder triage of CSV/XLSX/TSV/JSONL — schema, PKs, relationships (read-only) |
| `agency-kernel-steward` | Maintains `<workspace>/.kernel/KERNEL.md` for long projects — compaction, fork checkpoints, integrity recovery |
| **Explore** *(built-in)* | Fast read-only search to locate code |
| **general-purpose** *(built-in)* | Catch-all when no specialist fits |

### 2e. Specialized tier — meta and platform

| Agent | Use when |
|---|---|
| `engineering-autonomous-optimization-architect` | Shadow-testing APIs with strict cost + security guardrails |
| **statusline-setup** *(built-in)* | Configure Claude Code status line |
| **claude-code-guide** *(built-in)* | Answer "how does Claude Code itself work?" questions (CLI, hooks, MCP, plugins) |
| **vercel-plugin:ai-architect**, **deployment-expert**, **performance-optimizer** *(plugin-provided)* | Vercel-specific architectural work |

---

## 3. When to dispatch in parallel

Send a single message with multiple `Task` tool uses when:

- Work spans two or more domains with no shared state (e.g., frontend + backend, security audit + perf audit)
- You're running independent investigations (two specialists analyzing different files)
- You're doing a fan-out review (code-reviewer + security-engineer + sre on the same PR)

The orchestration skill for this pattern: `superpowers:dispatching-parallel-agents`. The skill for executing an already-written plan with checkpoints: `superpowers:subagent-driven-development`.

**Do not** dispatch sequentially when work is genuinely independent — it wastes wall-clock time. Conversely, **do not** parallelize when output of agent A feeds into agent B's prompt.

---

## 4. Anti-patterns (taken from the global CLAUDE.md)

- ❌ Orchestrator calls Bash to run tests itself → ✅ Dispatch the right specialist
- ❌ Dispatch `general-purpose` when a domain specialist exists → ✅ Pick the specialist
- ❌ Specialist refuses to run Bash citing Engineering Manager mode → ✅ Specialist runs the task (rule doesn't apply to dispatched subagents)
- ❌ Use `superpowers:test-driven-development` → ✅ Use Mattpocock's `tdd` skill instead (precedence)
- ❌ Use `superpowers:systematic-debugging` → ✅ Use Mattpocock's `diagnose` skill instead (precedence)

---

## 5. File inventory

The 34 agent files in this folder, alphabetically:

```
agency-kernel-steward.md
engineering-ai-data-remediation-engineer.md
engineering-ai-engineer.md
engineering-autonomous-optimization-architect.md
engineering-backend-architect.md
engineering-cms-developer.md
engineering-code-reviewer.md
engineering-codebase-onboarding-engineer.md
engineering-data-engineer.md
engineering-database-optimizer.md
engineering-devops-automator.md
engineering-email-intelligence-engineer.md
engineering-embedded-firmware-engineer.md
engineering-feishu-integration-developer.md
engineering-filament-optimization-specialist.md
engineering-frontend-developer.md
engineering-git-workflow-master.md
engineering-incident-response-commander.md
engineering-minimal-change-engineer.md
engineering-mobile-app-builder.md
engineering-rapid-prototyper.md
engineering-security-engineer.md
engineering-senior-developer.md
engineering-software-architect.md
engineering-solidity-smart-contract-engineer.md
engineering-sre.md
engineering-tabular-data-analyst.md
engineering-technical-writer.md
engineering-threat-detection-engineer.md
engineering-voice-ai-integration-engineer.md
engineering-wechat-mini-program-developer.md
```

### Consultative Expert Advisors (added 2026-05-15)

Installed for the LLM-eval workstream on Ask AI / Chakra AI / Video Copilot — dispatch these for **counsel**, not implementation. The user authors locked domain artifacts (judge prompts, axial agents) themselves; these advisors collaborate.

| Agent | Use when | Source |
|---|---|---|
| `llm-architect` | Whole-system design questions — panel-of-agents architecture, model routing, inference cost, serving infra, RAG | [VoltAgent 05-data-ai](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/05-data-ai/llm-architect.md) |
| `prompt-engineer` | Per-code sub-judge prompt design — system prompts, few-shot selection, CoT, structured output, A/B testing | [VoltAgent 05-data-ai](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/05-data-ai/prompt-engineer.md) |
| `qa-expert` | Eval discipline counsel — test strategy, coverage targets, calibration (TPR/TNR), regression prevention | [VoltAgent 04-quality-security](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/04-quality-security/qa-expert.md) |

Source repo: `VoltAgent/awesome-claude-code-subagents` (19.8k ⭐ MIT, verified 2026-05-15). Resync command: `curl -s -o <name>.md https://raw.githubusercontent.com/VoltAgent/awesome-claude-code-subagents/main/categories/<cat>/<name>.md`.

Built-in agents (provided by Claude Code itself, no file needed): `Plan`, `Explore`, `general-purpose`, `statusline-setup`, `claude-code-guide`, `superpowers-chrome:browser-user`.

Plugin-provided agents (re-installed via the marketplace in [../BOOTSTRAP.md](../BOOTSTRAP.md)): `vercel-plugin:ai-architect`, `vercel-plugin:deployment-expert`, `vercel-plugin:performance-optimizer`.
