---
name: phy6-brand-assets
description: >-
  phy6.ai brand asset loop — favicons, PWA icons, OG images, and visual QA
  grounded in the Renaissance First Principles design system. Use when generating
  favicons, wiring Next.js metadata/icons, syncing Claude Design with the repo,
  or verifying brand assets at 16/32/180px.
---

# phy6 brand assets

Orchestrates favicon + social asset generation for **phy6.ai** using the repo's
existing design system (not a generic template).

## Source of truth (read before generating)

| Asset | Path |
| --- | --- |
| Design tokens & rules | `brand/design-system.md` |
| Live CSS tokens | `src/app/globals.css` (`:root`, `@theme inline`) |
| Manifesto voice | `brand/manifesto.md` |
| Logo / mark candidates | `Design assets/Renaissance aesthetics/mila-okta-safitri-w2fiznlSojQ-unsplash.svg` (golden-ratio spiral), wordmark "phy6" in Cormorant |
| Next metadata | `src/app/layout.tsx` |

**Palette for assets:** parchment `#F8F3ED`, ink `#1A1410`, lapis `#1E3A8A`, gold `#C9A24A`.

## Recommended toolchain

1. **web-asset-generator** (same folder tree in `~/.cursor/skills/` and `~/.claude/skills/`)
   — favicons, PWA icons, `manifest.json`, OG images, Next.js wiring.
2. **Playwright MCP** — visual verification at 16×16 / 32×32 / 180×180 on localhost.
3. **Claude Design (native)** — `/design-sync` and `/design` for full-page canvas work;
   no user-installable MCP. Run `/update` and start a **new session** if missing.

**Do not use:** `e-brokenc0de/claude-design-mcp` (CDP hack, breaks often).

## Workflow: ship favicon + icons

### 0. Dependencies

```bash
python3 -m pip install Pillow
```

Run: `python3 ~/.claude/skills/web-asset-generator/scripts/check_dependencies.py`

### 1. Generate

Invoke **web-asset-generator**. Typical phy6 request:

> Generate a complete web asset package for phy6.ai from the golden-ratio spiral SVG
> (or a lapis "6" on parchment). Include favicon.ico, apple-touch-icon, PWA 192/512,
> and OG 1200×630. **iOS: solid parchment background — no transparency.**

### 2. Wire Next.js App Router

- Place icons under `src/app/` (`icon.png`, `apple-icon.png`) or `public/` per script output.
- Extend `metadata` in `src/app/layout.tsx`: `icons`, `openGraph.images`, `twitter.images`.
- Add `public/manifest.webmanifest` if PWA icons generated.
- Keep `metadataBase: https://phy6.ai`.

### 3. Verify

Ask explicitly: *"Use Playwright MCP to verify favicon at 16/32/180px on localhost."*

## Workflow: Claude Design round-trip

1. **`/design-sync`** — import this repo so canvas work uses real tokens.
2. Build on **claude.ai/design** or **`/design`** in terminal.
3. Hand off bundle to Claude Code for implementation.
4. Re-run Playwright visual checks.

## phy6-specific constraints

- Restraint rule: *if in doubt, omit.*
- Favicon must read at **16×16**.
- After asset changes: `npm run build` must pass.

## Stitch (optional)

Stitch MCP is available separately. Use for new screen mockups, not favicons.
phy6 tokens already live in the repo.
