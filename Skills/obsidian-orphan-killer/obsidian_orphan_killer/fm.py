"""Frontmatter I/O + atomic-write + body-only content hash.

The orphan-killer's hard contract:

  - Every write is FRONTMATTER-ONLY. Body bytes are never modified.
  - Every write is ATOMIC (tempfile + os.rename).
  - Every write stamps an idempotency hash so a re-run skips unchanged notes.
  - The body-only content hash is what downstream embedders use to decide
    whether a note needs re-embedding. The resolver MUST NOT touch the body, so
    re-running the resolver does NOT invalidate any downstream embedding store.

These three guarantees together are what makes auto-writing to a vault safe.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

import yaml


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return ``(fm_dict, body)`` or ``(None, text)`` if no valid frontmatter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    raw_fm = text[4:end]
    body = text[end + 5:]
    try:
        fm = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(fm, dict):
        return None, text
    return fm, body


def serialize(fm: dict, body: str) -> str:
    """Render ``fm + body`` back to a markdown file. Stable across re-runs."""
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    out = f"---\n{dumped}\n---\n{body}"
    return out if out.endswith("\n") else out + "\n"


def write_atomic(path: Path, content: str) -> None:
    """tempfile + os.rename. Crash-safe; no partial writes."""
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=".tmp-orphan-killer-", suffix=".md", dir=str(parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        os.rename(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


# ---------------------------------------------------------------------------
# Idempotency hashes.
# ---------------------------------------------------------------------------
# The KEY safety property: re-running the resolver must NOT trigger a downstream
# re-embed. Downstream embedders typically hash the BODY (or title + tldr +
# summary + body). The resolver writes ONLY frontmatter values it owns — never
# title/tldr/summary, never body — so the body-only content hash is preserved.
#
# Each mode (resolve / anchor / mint) keeps its OWN hash so the three stamps
# are independent and a note already anchored isn't re-touched on a re-resolve.

RESOLVE_FIELDS = ("entities", "topics")


def resolve_hash(fm: dict, body: str) -> str:
    """Hash over body + the entity/topic fields. Stable across resolve re-runs.

    Includes ``entities`` / ``topics`` so a re-NER'd note (whose fields changed)
    re-resolves. Excludes ``related`` / ``raw_meta`` so writing the stamp
    doesn't invalidate it.
    """
    key_fm = {k: fm.get(k) for k in RESOLVE_FIELDS}
    key = yaml.safe_dump(key_fm, sort_keys=True, allow_unicode=True) + body
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


def body_only_hash(body: str) -> str:
    """The downstream-embedder hash. Provided as a public helper so users can
    verify that an orphan-killer run leaves it unchanged.
    """
    return hashlib.md5(body.encode("utf-8")).hexdigest()[:12]


def stamp_meta(fm: dict, stamp_key: str, stamp_hash_key: str, hash_value: str,
               extras: dict | None = None) -> dict:
    """Set ``raw_meta.{stamp_key, stamp_hash_key, **extras}`` in-place; return fm."""
    from datetime import datetime, timezone
    raw_meta = fm.get("raw_meta") or {}
    if not isinstance(raw_meta, dict):
        raw_meta = {}
    raw_meta[stamp_key] = datetime.now(timezone.utc).isoformat()
    raw_meta[stamp_hash_key] = hash_value
    if extras:
        raw_meta.update(extras)
    fm["raw_meta"] = raw_meta
    return fm


def should_skip(fm: dict, stamp_key: str, stamp_hash_key: str, current_hash: str) -> bool:
    """True iff this note has already been processed AND nothing relevant changed."""
    raw_meta = fm.get("raw_meta") or {}
    if not isinstance(raw_meta, dict) or not raw_meta.get(stamp_key):
        return False
    return raw_meta.get(stamp_hash_key) == current_hash
