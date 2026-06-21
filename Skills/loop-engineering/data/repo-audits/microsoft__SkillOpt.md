# Code Audit — microsoft/SkillOpt

- **Files read:** 286 text/source files (every line indexed)
- **Pushed at:** 2026-06-20T14:26:43Z
- **Stars:** 8483

## Code-backed scores

- **direct_install:** 0.0
- **claude_code_native:** 10
- **loop_implementation:** 3.2
- **registry_memory:** 7.5
- **verification:** 9.0
- **file_coverage:** 286
- **total:** 5.28

## Entrypoints (from code)

- skill_md: ckpt/alfworld/gpt5.5_skill.md, ckpt/docvqa/gpt5.5_skill.md, ckpt/livemath/gpt5.5_skill.md, ckpt/officeqa/gpt5.5_skill.md, ckpt/searchqa/gpt5.5_skill.md, ckpt/spreadsheetbench/gpt5.5_skill.md, plugins/claude-code/skills/skillopt-sleep/SKILL.md, plugins/codex/skills/skillopt-sleep/SKILL.md
- hooks: plugins/claude-code/hooks/hooks.json
- loop_scripts: (none)
- main_files: (none)

## Install facts (from manifests)


## Loop signals (line-indexed samples)

### stop_condition
- `docs/guide/configuration.md:48` — max_analyst_rounds: 3          # Max rounds of analyst reflection
- `docs/guideline.html:767` — <tr><td><code>max_analyst_rounds</code></td><td>int</td><td class="def">3</td><td>Max rounds of analyst reflection per s
- `docs/reference/config.md:36` — | `gradient.max_analyst_rounds` | int | 3 | Max rounds of analyst reflection |
### verifier
- `ckpt/README.md:9` — > tool. They're here so you can verify the reported numbers and use the
- `ckpt/README.md:15` — > cleaned and verified.
- `ckpt/alfworld/gpt5.5_skill.md:65` — - **Premature termination**: Do not stop the episode until all goal conditions are verified as met.
- `ckpt/livemath/gpt5.5_skill.md:22` — - For threshold conditions, verify the exact sign and endpoint: distinguish \(\mu_0\) from \(-\mu_0\), \(<\) from \(\le\
- `ckpt/livemath/gpt5.5_skill.md:24` — - Verify the hypotheses and domain carefully. Distractors often keep the theorem shape but alter the required assumption
### hitl
- `plugins/openclaw/README.md:98` — SkillOpt-Sleep adds a 4th option: **validated self-evolution**. The skill is the training target, the engine is the opti
- `plugins/openclaw/tests/research-cron-tasks.json:72` — "reference": "1) DO MORE: AI citation / LLM-mention topics \u2014 the 0.9% CTR at position 9.4 means we're visible but n
- `plugins/openclaw/tests/research-cron-tasks.json:75` — "intent": "Performance \u2192 Strategy feedback loop. Last week's top blog post was 'AI Citation Audit: Does Your Site A
### state_writeback
- `ckpt/alfworld/gpt5.5_skill.md:40` — - Keep a persistent **searched set** of receptacle instances, e.g. `drawer 1`, `shelf 3`, `countertop 2`. Once an observ
- `ckpt/spreadsheetbench/gpt5.5_skill.md:31` — | Bulk data transformation, aggregation, sorting | `pandas` → write back with `openpyxl` |
- `docs/guide/local-env-smoke.md:136` — When adding a custom environment to the registry, avoid side effects for existing benchmarks:
- `docs/guide/new-backend.md:90` — BACKEND_REGISTRY = {
- `docs/guide/new-benchmark.md:292` — _ENV_REGISTRY["docfaithful"] = DocFaithfulAdapter
### loop_engine
- `skillopt/optimizer/appendix.py:126` — while True:
- `skillopt/optimizer/slow_update.py:62` — while True:
- `skillopt_sleep/memory.py:33` — while True:
- `skillopt_sleep/slow_update.py:49` — while True:
### claude_native
- `README.md:12` — - **[2026-06-15]** 😴 **SkillOpt-Sleep (preview)** — a nightly offline self-evolution companion for local coding agents (
- `README.md:34` — The deployed artifact is a compact `best_skill.md` (typically 300–2,000
- `README.md:37` — chat, Codex CLI, Claude Code CLI), SkillOpt is best or tied-best on **all
- `README.md:40` — the Codex agentic loop, and +19.1 inside Claude Code**. Optimized skill
- `README.md:41` — artifacts transfer across model scales, between Codex and Claude Code

## README vs code

README claim: # SkillOpt: Executive Strategy for Self-Evolving Agent Skills  *Train agent skills like you train neural networks — with epochs, (mini-)batchsize, learning rates, and validation gates — but without touching model weights.*  [![Project Page](https://img.shields.io/badge/Project%20Page-SkillOpt-8dbb3c

- Code contains loop engine / gate patterns (see loop signals above).
