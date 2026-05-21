#!/usr/bin/env python3
"""Codex hook adapters for Token Optimizer.

Codex currently supports a smaller hook surface than Claude Code. This bridge
keeps the existing measurement engine intact and adapts the outputs Codex can
actually consume today: SessionStart continuity context and UserPromptSubmit
quality nudges.
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import codex_session
import measure
from hook_io import read_stdin_hook_input


def _capture_stdout(func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            func(*args, **kwargs)
    except Exception as exc:
        print(f"[Token Optimizer] Codex hook helper failed: {exc}", file=sys.stderr)
        return ""
    return buffer.getvalue()


def _emit_additional_context(event_name: str, text: str) -> None:
    text = text.strip()
    if not text:
        return
    print(
        json.dumps(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": text,
                },
            }
        )
    )


def _collect_system_messages(raw_output: str) -> str:
    messages: list[str] = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = payload.get("systemMessage")
        if isinstance(message, str) and message.strip():
            messages.append(message.strip())
    return "\n\n".join(messages)


def _extract_prompt_text(hook_input: dict[str, Any]) -> str:
    for key in ("prompt", "user_prompt", "message", "input"):
        value = hook_input.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    messages = hook_input.get("messages")
    if isinstance(messages, list):
        for item in reversed(messages):
            if not isinstance(item, dict):
                continue
            content = item.get("content") or item.get("message")
            if isinstance(content, str) and content.strip():
                return content.strip()
    return ""


def _has_matching_checkpoint(session_id: str | None) -> bool:
    if not session_id:
        return False
    safe_session_id = measure.sanitize_session_id(session_id)
    for checkpoint in measure.list_checkpoints(max_age_minutes=60 * 24):
        if safe_session_id in checkpoint.get("filename", ""):
            return True
    return False


def handle_session_start() -> None:
    hook_input = read_stdin_hook_input()
    session_id = hook_input.get("session_id")
    source = str(hook_input.get("source", "")).strip().lower()

    # Keep existing self-healing behavior even when no context is injected.
    _capture_stdout(measure.run_ensure_health)

    if source == "resume" and _has_matching_checkpoint(session_id):
        context = _capture_stdout(
            measure.compact_restore,
            session_id=session_id,
            is_compact=True,
        )
    elif source == "clear":
        context = _capture_stdout(
            measure.compact_restore,
            session_id=session_id,
            new_session_only=True,
        )
    else:
        context = ""

    _emit_additional_context("SessionStart", context)


def handle_user_prompt_submit() -> None:
    hook_input = read_stdin_hook_input()
    transcript_path = hook_input.get("transcript_path")
    if transcript_path and not codex_session.is_codex_session_path(transcript_path):
        transcript_path = None
    session_id = hook_input.get("session_id")
    raw_output = _capture_stdout(
        measure.quality_cache,
        quiet=True,
        session_jsonl=transcript_path,
    )
    additional_context = _collect_system_messages(raw_output)
    prompt_text = _extract_prompt_text(hook_input)
    cwd = hook_input.get("cwd")
    if not cwd and transcript_path:
        try:
            cwd = str(Path(transcript_path).parent)
        except TypeError:
            cwd = None
    try:
        hint_context = measure.codex_prompt_hints(
            prompt_text=prompt_text,
            session_id=session_id,
            cwd=cwd,
        )
    except Exception as exc:
        print(f"[Token Optimizer] Codex hint helper failed: {exc}", file=sys.stderr)
        hint_context = ""
    if hint_context:
        additional_context = "\n\n".join(part for part in (additional_context, hint_context.strip()) if part)
    _emit_additional_context("UserPromptSubmit", additional_context)


def main() -> int:
    try:
        if len(sys.argv) < 2:
            return 0

        command = sys.argv[1].strip().lower()
        if command == "session-start":
            handle_session_start()
        elif command == "user-prompt-submit":
            handle_user_prompt_submit()
    except Exception as exc:
        print(f"[Token Optimizer] Codex hook bridge failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
