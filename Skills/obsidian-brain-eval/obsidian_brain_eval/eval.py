"""Recall@k gold-set eval engine for Obsidian vault retrieval.

Two phases:

    generate   Sample N representative notes from the vault, ask GPT-4.1 (or any
               OpenAI-compatible client) to write ONE natural question per note
               that the note answers, and write the gold-set to a JSONL file.
               Each record pins the KNOWN-RELEVANT note(s) (the source note +
               any notes it strongly links via frontmatter). Idempotent: skips
               notes already in the gold-set unless force=True. Roughly
               $1-2 of GPT for ~40 questions.

    score      For each gold question, run a pluggable retrieval backend
               (see obsidian_brain_eval.backends) and check whether a
               known-relevant note appears in the top-k. Reports Recall@k +
               a per-question breakdown.

The gold-set is stored as JSONL so it is repeatable and reviewable.

Default target: Recall@10 >= 0.85.
"""
from __future__ import annotations

import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Protocol

import yaml

log = logging.getLogger(__name__)

DEFAULT_TARGET = 0.85
DEFAULT_K = 10
DEFAULT_MODEL = "gpt-4.1"
DEFAULT_N = 40

# Note classes worth asking questions about. Most vaults that use a "Properties as
# links" convention put curated anchors and rich source notes in folders named
# like these. Override with --folders on the CLI.
_DEFAULT_GOOD_FOLDERS = ("entities", "concepts", "themes", "notes")
_MIN_BODY_CHARS = 200  # skip stubs the model can't ground a real question in


class RetrievalBackend(Protocol):
    """A retrieval backend is anything that can score a question against a vault.

    Implementations live in ``obsidian_brain_eval.backends`` and ship with two
    defaults: ``NaiveBM25Backend`` (BM25 over the vault, no embeddings, runs
    anywhere) and ``LanceDBBackend`` (hybrid FTS + vector search).

    A backend is responsible for indexing the vault once on construction and
    then answering ``topk(question, k)`` for each gold question.
    """

    def topk(self, question: str, k: int) -> list[str]:
        """Return the top-k vault-relative paths for this question.

        Paths MUST be of the form ``"<vault.name>/<relative-path>.md"`` so they
        match the format ``generate()`` writes into ``relevant_paths``.
        """
        ...


# ---------------------------------------------------------------------------
# Frontmatter parse (same convention as the kepano "Properties as links" style)
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    try:
        fm = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return None, text
    if not isinstance(fm, dict):
        return None, text
    return fm, text[end + 5:]


def vault_path_str(vault: Path, note: Path) -> str:
    """Canonical 'vault/concepts/foo.md' string for a note inside a vault.

    Exposed publicly because custom backends need to produce paths in this exact
    shape so the scorer can match them against ``relevant_paths``.
    """
    return f"{vault.name}/{note.relative_to(vault)}"


# ---------------------------------------------------------------------------
# Phase 1 - generation
# ---------------------------------------------------------------------------

_GEN_SYSTEM = (
    "You write ONE natural search question that a person would ask their personal "
    "knowledge base, where the answer is found in the given note. The question MUST "
    "be answerable from the note's content, must NOT quote the note title verbatim, "
    "and should read like a real user query (not a quiz). Return JSON only: "
    '{"question": "..."}'
)


def _candidate_notes(vault: Path, folders: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    if folders:
        for folder in folders:
            d = vault / folder
            if not d.exists():
                continue
            for p in sorted(d.glob("*.md")):
                if p.name.startswith("_"):
                    continue
                if p not in seen:
                    out.append(p)
                    seen.add(p)
    # If no folder filter matched, fall back to the whole vault.
    if not out:
        for p in sorted(vault.rglob("*.md")):
            if p.name.startswith("_"):
                continue
            out.append(p)
    return out


def _extract_strong_links(fm: dict | None, body: str) -> list[str]:
    """Strong related notes = frontmatter entities/topics/related wikilink stems."""
    slugs: list[str] = []
    fm = fm or {}
    for key in ("entities", "topics", "related"):
        val = fm.get(key)
        if isinstance(val, str):
            val = [val]
        if isinstance(val, list):
            for item in val:
                for m in re.findall(r"\[\[([^\]]+)\]\]", str(item)):
                    stem = m.split("|")[0].strip()
                    if stem:
                        slugs.append(stem)
    return slugs


def load_gold(gold_path: Path) -> list[dict]:
    """Read a gold-set JSONL file. Empty list if missing."""
    if not gold_path.exists():
        return []
    out: list[dict] = []
    for line in gold_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def generate(
    vault: Path,
    gold_path: Path,
    n: int = DEFAULT_N,
    seed: int = 42,
    force: bool = False,
    folders: tuple[str, ...] = _DEFAULT_GOOD_FOLDERS,
    model: str = DEFAULT_MODEL,
    client: Any = None,
) -> list[dict]:
    """Generate ~n gold questions grounded in real notes. Append to gold_path.

    Args:
        vault: path to the vault root.
        gold_path: JSONL file to read/write. Created if missing.
        n: target number of NEW gold records to add.
        seed: PRNG seed for which notes get sampled.
        force: if True, overwrite the gold-set entirely (otherwise append, skip
            any source_note already represented).
        folders: subdirectories of the vault to sample from. Defaults sweep the
            common "Properties as links" folders. Empty tuple means whole-vault.
        model: OpenAI chat-completions model name.
        client: an OpenAI-compatible client (object exposing
            ``chat.completions.create``). REQUIRED. If omitted, the function
            tries to construct one via the ``openai`` package using
            ``OPENAI_API_KEY``.
    """
    if client is None:
        client = _default_openai_client()

    existing = [] if force else load_gold(gold_path)
    existing_sources = {r["source_note"] for r in existing}

    candidates = _candidate_notes(vault, folders)
    rng = random.Random(seed)
    rng.shuffle(candidates)

    new_records: list[dict] = []
    for note in candidates:
        if len(new_records) >= n:
            break
        try:
            text = note.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm, body = _split_frontmatter(text)
        if len(body.strip()) < _MIN_BODY_CHARS:
            continue
        vp = vault_path_str(vault, note)
        if vp in existing_sources:
            continue

        title = (fm or {}).get("title") or note.stem
        prompt = (
            f"Note title: {title}\n\n"
            f"Note content (truncated):\n{body.strip()[:2000]}\n\n"
            "Write the question."
        )
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _GEN_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=120,
            )
        except Exception as exc:  # noqa: BLE001
            log.warning("generation failed for %s: %s", vp, exc)
            continue

        raw = (resp.choices[0].message.content or "").strip()
        raw = re.sub(r"^```[^\n]*\n?|```$", "", raw).strip()
        try:
            question = json.loads(raw).get("question", "").strip()
        except json.JSONDecodeError:
            question = raw.strip().strip('"')
        if not question:
            continue

        # Known-relevant = the source note itself (always) plus strongly-linked
        # notes that EXIST as files (so the relevance set is never dangling).
        relevant = [vp]
        for stem in _extract_strong_links(fm, body):
            matched: Path | None = None
            for folder in folders or ():
                cand = vault / folder / f"{stem}.md"
                if cand.exists():
                    matched = cand
                    break
            if matched is None:
                # Whole-vault fallback for vaults without the kepano folders.
                for cand in vault.rglob(f"{stem}.md"):
                    matched = cand
                    break
            if matched is not None:
                rp = vault_path_str(vault, matched)
                if rp not in relevant:
                    relevant.append(rp)

        rec = {
            "question": question,
            "source_note": vp,
            "relevant_paths": relevant,
            "title": str(title),
        }
        new_records.append(rec)
        log.info("[%d/%d] %s", len(new_records), n, question[:70])

    gold_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if force else "a"
    with gold_path.open(mode, encoding="utf-8") as f:
        for rec in new_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    log.info("Wrote %d new gold records -> %s", len(new_records), gold_path)
    return new_records


def _default_openai_client() -> Any:
    """Lazy import an OpenAI client. Raises a friendly error if unavailable."""
    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "obsidian-brain-eval generate needs the `openai` package. "
            "Install with `pip install obsidian-brain-eval[generate]` or pass "
            "your own client= to generate()."
        ) from exc
    return OpenAI()


# ---------------------------------------------------------------------------
# Phase 2 - scoring (retrieval-layer Recall@k)
# ---------------------------------------------------------------------------

def score(
    gold: list[dict],
    backend: RetrievalBackend,
    k: int = DEFAULT_K,
    target: float = DEFAULT_TARGET,
) -> dict[str, Any]:
    """Run Recall@k over the gold-set using the given backend.

    Args:
        gold: list of gold records as written by ``generate()`` (or hand-curated).
        backend: anything implementing ``topk(question, k) -> list[str]``.
        k: cutoff for Recall@k.
        target: pass/fail threshold (default 0.85, the same target the upstream
            engine ships against).

    Returns:
        dict with ``k``, ``n_questions``, ``hits``, ``recall_at_k``, ``target``,
        ``pass``, and a ``per_question`` list with hit/miss/rank/matched/topk.
    """
    if not gold:
        raise ValueError("Gold-set is empty. Generate it first or pass --gold.")

    per_q: list[dict] = []
    hits = 0
    for rec in gold:
        question = rec["question"]
        relevant = set(rec["relevant_paths"])
        topk = list(backend.topk(question, k))[:k]
        found = [p for p in topk if p in relevant]
        hit = bool(found)
        if hit:
            hits += 1
        rank = next((i + 1 for i, p in enumerate(topk) if p in relevant), None)
        per_q.append({
            "question": question,
            "source_note": rec["source_note"],
            "hit": hit,
            "first_hit_rank": rank,
            "matched": found,
            "topk": topk,
        })

    n = len(gold)
    recall = round(hits / n, 4) if n else 0.0
    return {
        "k": k,
        "n_questions": n,
        "hits": hits,
        "recall_at_k": recall,
        "target": target,
        "pass": recall >= target,
        "per_question": per_q,
    }


def render_score(result: dict[str, Any]) -> str:
    """Render a human-friendly scorecard string from a score() result."""
    lines: list[str] = []
    A = lines.append
    A("=" * 64)
    A(f"  RECALL@{result['k']} - obsidian-brain-eval")
    A("=" * 64)
    A(f"  questions   {result['n_questions']}")
    A(f"  hits        {result['hits']}")
    A(f"  Recall@{result['k']}   {result['recall_at_k']:.4f}   (target >= {result['target']})")
    A(f"  status      {'PASS' if result['pass'] else 'BELOW TARGET'}")
    A("-" * 64)
    A("  MISSES")
    misses = [q for q in result["per_question"] if not q["hit"]]
    if not misses:
        A("    (none)")
    for q in misses:
        A(f"    x {q['question'][:60]}")
        A(f"      want: {q['source_note']}")
    A("-" * 64)
    A("  HITS (first-relevant rank distribution)")
    rank_counts: dict[int, int] = {}
    for q in result["per_question"]:
        if q["first_hit_rank"]:
            rank_counts[q["first_hit_rank"]] = rank_counts.get(q["first_hit_rank"], 0) + 1
    if not rank_counts:
        A("    (none)")
    for r in sorted(rank_counts):
        A(f"    rank {r:>2}: {rank_counts[r]}")
    A("=" * 64)
    return "\n".join(lines)
