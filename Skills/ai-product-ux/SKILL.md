---
name: ai-product-ux
description: Design AI-native UX — streaming, multi-turn state, fallbacks, onboarding, loading/error states for LLM features.
dispatch_to: frontend-developer
---

# AI Product UX

Reference implementation: https://github.com/vercel/ai-chatbot (Next.js App Router + Vercel AI SDK + shadcn/ui)

This skill covers the UX design layer — what to show, when, and why. For SDK mechanics see `vercel-plugin:ai-sdk`. For chat SDK wiring see `vercel-plugin:chat-sdk`.

## 1. AI UX Primitives

**Typing indicator** — show immediately on send, before the first token arrives. Three-dot pulse or skeleton. Never leave the user staring at nothing.

**Streaming text** — render tokens as they arrive using `useChat` from `@ai-sdk/react`. Sentence-boundary rendering (buffer until `.`/`?`/`!`) works better for TTS or screen readers; character-level is fine for visual chat.

**Error recovery** — always surface a retry button inline with the failed message, not as a toast. The message is the context; that's where the action belongs.

**Retry affordance** — for transient failures, auto-retry once silently, then surface the error. For content-filter hits, explain without alarming: "I can't help with that specific question — try rephrasing."

## 2. Multi-Turn State

**Persist:** message array (role + content + id + timestamp), conversation ID, model/persona used per turn.

**Derive, don't persist:** loading state, error state, scroll position, whether a message is streaming.

**Context window awareness:** when conversation grows long, show a subtle "Summarizing earlier context…" notice rather than silently truncating. Users notice when AI "forgets."

## 3. Optimistic UI for AI

Send the user's message to the UI immediately (optimistic insert) before the API call resolves. If the call fails, mark the optimistic message as failed and show retry — do not remove it. Removing it disorients the user.

For file uploads or tool calls, show a pending state on the attachment/tool card, not a spinner over the whole chat.

## 4. Streaming Display Patterns

```
character-level  → feels alive, best for general chat
sentence-level   → better for accessibility, TTS integration
paragraph-level  → best for long-form content (essay, explanation)
```

For EdTech step-by-step explanations, stream paragraph-level and visually separate each step as it completes (card or numbered block snaps in). Prevents the wall-of-text effect.

Scroll behavior: auto-scroll to bottom while streaming, pause auto-scroll if the user scrolls up, resume when they scroll back to bottom.

## 5. Tool-Call Transparency

Show tool calls when they add trust (search, calculator, citation lookup). Hide them when they're infrastructure (formatting, routing).

Pattern for "Claude is searching…":
```
[search icon] Looking up NEET 2024 cutoffs…  ← visible while tool runs
[result card] Source: NTA Official            ← replaces spinner on completion
```

Never show raw tool call JSON to users. Map tool names to plain-language status: `web_search` → "Searching the web", `get_practice_questions` → "Finding practice questions".

## 6. Error States — User-Facing Copy

| Error | Copy | Do not say |
|---|---|---|
| Rate limit | "You've sent a lot of questions — wait a moment and try again." | "429 Too Many Requests" |
| Timeout | "That took too long. Try a shorter question or tap Retry." | "Request timed out" |
| Content filter | "I can't answer that specific question. Try rephrasing." | "Content policy violation" |
| Model unavailable | "AI is temporarily unavailable. Your question is saved — try again shortly." | "503 Service Unavailable" |

Always save the user's unsent or failed message locally so they don't retype it.

## 7. Onboarding Flow

First AI interaction is high-stakes. Pattern:

1. **Starter prompts** — 3–4 tappable suggestion chips ("Explain photosynthesis", "Help me practice Integration"). Remove once the user sends their first message.
2. **Persona introduction** — one line, first message only: "I'm your NEET prep tutor. Ask me anything."
3. **Capability signal** — show what AI can do through the starter prompts, not through a feature list modal.

For returning users: restore last conversation or offer "Start fresh" — don't auto-start a new session and lose context.

## 8. Mobile AI UX (Flutter)

- Keyboard-aware scroll: `resizeToAvoidBottomInset: true` + auto-scroll to bottom on keyboard open.
- Message input: sticky bottom bar, not inline. Matches native messaging app muscle memory.
- Streaming on mobile: throttle renders to 60fps max — Flutter rebuilds on every token can drop frames. Batch updates every 50ms.
- Haptic feedback on send (`HapticFeedback.lightImpact`), subtle. Not on every token.
- Long-press message → copy, share, "Ask follow-up" context menu.
- Offline state: disable send button, show banner "No connection — answers will resume when online."

Web patterns (starter prompts, tool-call cards) apply to mobile but use bottom sheet instead of inline expansion for tool-call details.

## 9. EdTech-Specific Patterns

**Step-by-step explanation display:**
Stream each step as a numbered card that snaps in on paragraph completion. Allow "Explain this step more" as an inline action on each card — appends to the same conversation thread.

**Confidence indicators:**
Only show if the model explicitly returns a confidence signal. Do not fake confidence UI. When shown: green = "I'm confident", amber = "Double-check this". Never red (implies the AI is always wrong, which is worse than no indicator).

**Q&A flow for exam prep:**
```
Student asks question
→ AI gives answer + 1-line "why this matters for NEET/JEE"
→ Inline: "Practice a similar question" chip
→ On tap: new question generated in same thread
```

Keep Q&A tight — avoid multi-paragraph answers unless student explicitly asks to "explain in detail."

## 10. Accessibility

**Screen reader support for streaming text:**
Use `aria-live="polite"` on the streaming container. `aria-live="assertive"` interrupts the user — avoid it. Announce completion with a visually-hidden "Response complete" cue.

**Keyboard navigation:**
- Enter to send (Shift+Enter for newline)
- Tab through starter prompt chips
- Focus trap in modal tool-call detail views

**Motion preferences:**
Respect `prefers-reduced-motion` — disable typing pulse animation and smooth-scroll snap. Show text immediately instead of streaming animation for reduced-motion users.

**Contrast:**
AI-generated text must meet WCAG AA (4.5:1). Streaming grey (#999 on white) fails — use #666 minimum or stream in the final text color.

## Implementation Checklist

- [ ] Optimistic message insert on send
- [ ] Inline retry on failure (not toast)
- [ ] Starter prompts removed after first message
- [ ] `aria-live="polite"` on streaming container
- [ ] User message saved on failure/timeout
- [ ] Tool calls mapped to plain-language status
- [ ] Auto-scroll pauses on user scroll-up
- [ ] `prefers-reduced-motion` handled
- [ ] Mobile: 50ms render throttle for streaming
