# Spec-Driven Development (greenfield only)

The `specify` CLI from github/spec-kit is installed globally for Spec-Driven Development. Use ONLY in greenfield projects (new repo, no existing `docs/agents/` / `docs/adr/` / `CONTEXT.md`).

### When to use spec-kit
- Starting a NEW project from zero where no toolchain conventions exist yet
- Want a portable spec/plan/task layout (`.specify/` directory) consumable by other AI tools (Copilot, Cursor) too
- Want a project constitution (`.specify/memory/constitution.md`) as an enforced gate, not just convention

### When NOT to use spec-kit
- Existing brownfield repo → use mattpocock toolchain (`to-prd`, `to-issues`, `triage`) and `gepetto` per existing precedence
- Single-feature change in a project that already has CONTEXT.md / docs/adr/ → continue with `improve-codebase-architecture` + `gepetto`

### Phase mapping (greenfield path)
Within a `specify init` project, run phases in this order with these handoffs:

| spec-kit phase | What it does | Handoff rule |
|---|---|---|
| `/speckit.constitution` | Writes `.specify/memory/constitution.md` | Use as project source-of-truth; if PRD-on-tracker is also needed, run `to-prd` downstream |
| `/speckit.specify` | Writes `.specify/specs/<feature>/spec.md` | Same — run `to-prd` if a tracker artifact is also needed |
| `/speckit.plan` | Writes `plan.md` | For substantive features, hand `plan.md` to `gepetto` for multi-LLM review BEFORE moving to `/speckit.tasks` |
| `/speckit.tasks` | Writes `tasks.md` | If you also need independently-grabbable tracker tickets, run `mattpocock to-issues` against `tasks.md` |
| `/speckit.implement` | **BYPASS — never run.** | Always dispatch via Engineering Manager → specialist (`engineering-senior-developer`, etc.) per top-of-file rule. Our specialist roster is richer than spec-kit's generic execution. |

### Override rule (MANDATORY)
**Never run `/speckit.implement`.** That command would invoke spec-kit's generic execution loop, bypassing our domain specialists (Solidity, WeChat Mini Program, Feishu, Senior Dev, etc.). Engineering Manager mode dispatches to the right specialist instead. If a future spec-kit version makes this command harder to disable, add an explicit deny in settings.json.

### Community extensions
spec-kit has an active community-extension catalog (`catalog.community.json`). Each extension is a separate install, each requiring its own `evaluating-skill-necessity` pass before being added. Do NOT install community extensions implicitly.
