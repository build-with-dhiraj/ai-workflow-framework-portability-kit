# ADOPT v2 — Code-Backed Install Decision

**Generated:** 2026-06-21

## Layered stack

| Layer | Pick | Evidence |
|-------|------|----------|
| Harness | Claude Code `/loop`, `/goal` | Anthropic docs + corpus ingest |
| Loop tooling | `cobusgreyling/loop-engineering` | ingest/github-code/cobusgreyling__loop-engineering/code-audit.md — 201 files read |

### cobusgreyling/loop-engineering (code score 9.62)
- Files read: 201, lines: 11790
- Audit: `ingest/github-code/cobusgreyling__loop-engineering/code-audit.md`

### earendil-works/pi (code score 9.62)
- Files read: 843, lines: 243355
- Audit: `ingest/github-code/earendil-works__pi/code-audit.md`

### valkor-ai/loom (code score 9.62)
- Files read: 295, lines: 80117
- Audit: `ingest/github-code/valkor-ai__loom/code-audit.md`

## Quick start

```bash
npm install -g @cobusgreyling/loop-init @cobusgreyling/loop-audit
loop-init --pattern daily-triage --tool claude
```
