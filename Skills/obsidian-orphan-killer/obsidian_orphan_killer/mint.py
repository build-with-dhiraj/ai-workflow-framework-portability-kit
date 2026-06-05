"""Cluster-mint mode — EXPERIMENTAL. Mints new concept hubs from orphan clusters.

Anchor mode (the safe default) can only attach an orphan to a hub that
ALREADY exists. If the vault has no hub for a topic, those orphans stay
unlinked no matter how coherent the cluster is. Cluster-mint closes that gap:

  1. Census the same true-orphan set anchor mode uses.
  2. Embed each orphan (title + body slice) with the same wide-window model.
  3. Cluster deterministically (cosine-similarity graph → greedy-modularity
     communities, reproducible).
  4. For each cluster with ≥ ``min_cluster`` members, ask an LLM to NAME the
     shared topic from ~8 sample titles AND judge coherence. Incoherent
     clusters are REJECTED (left as haystack).
  5. Apply the mint-side guards (TOPIC_DENYLIST, URL fragment, generic
     catch-all backstop) to the proposed name. Reject anything that fails.
  6. Mint each surviving cluster as a concept hub (concepts-only — never a
     brand entity hub), capped at ``max_hubs``.
  7. Anchor each cluster's members to its newly-minted hub IFF the member
     clears ``anchor_floor`` cosine to the HUB's own surface (not the cluster
     centroid).

THIS MODE IS EXPERIMENTAL because it writes NEW notes to the vault. Always
dry-run first. Always read the audit TSV before approving. The mode is
disabled by default and gated behind ``--experimental`` in the CLI.

Hard safety guards (in addition to anchor mode's):

  - ``min_cluster`` size floor (default 5) before a cluster qualifies.
  - LLM coherence reject (a NO leaves the whole cluster as haystack).
  - Mint-side name guards (denylist / URL-fragment / generic catch-all).
  - Concepts-only mint — never an entities/ brand hub.
  - ``max_hubs`` cap on NEW hubs per run.
  - ``dup_hub_threshold`` — if a proposed name is near-duplicate of an
    existing concept hub, redirect anchors to the existing hub instead of
    minting a sibling.
  - ``max_spread`` deterministic backstop — clusters with high intra-cluster
    cosine spread are grab-bags and rejected before the LLM call.
  - Per-hub absorption cap (anti-star).
  - Idempotency stamps + frontmatter-only writes (same as anchor mode).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from obsidian_orphan_killer.alias_table import AliasTable
from obsidian_orphan_killer.alias_table import build as build_alias_table
from obsidian_orphan_killer.anchor import (
    _body_slice,
    _cosine,
    _iter_all_vault_notes,
    _load_embedder,
    _note_link_keys,
    all_wikilinks,
)
from obsidian_orphan_killer.fm import (
    resolve_hash,
    serialize,
    should_skip,
    split_frontmatter,
    stamp_meta,
    write_atomic,
)
from obsidian_orphan_killer.guards import proposed_name_is_clean
from obsidian_orphan_killer.resolve import DEFAULT_SCOPE_DIRS, discover_notes
from obsidian_orphan_killer.slug import slugify

log = logging.getLogger(__name__)


_CLUSTER_PROMPT_SYSTEM = (
    "You name topical hubs for a personal knowledge vault. You are given ~8 "
    "sample note TITLES that an embedding model grouped into one cluster. Decide "
    "if they share a SINGLE coherent topic specific enough to be a useful hub.\n"
    "Reply with STRICT minified JSON and nothing else:\n"
    '{"coherent": true|false, "topic": "<2-4 word Title Case topic>"}\n'
    "Rules:\n"
    "- coherent=false if the titles are a grab-bag with no shared subject, or "
    "the only commonality is a generic format (e.g. all are 'shorts', 'vlogs', "
    "'podcasts', 'tutorials') rather than a subject.\n"
    "- The topic must be a SUBJECT (e.g. 'Protein Crystallization', 'Startup "
    "Fundraising'), never a generic catch-all ('Science', 'Technology', "
    "'Videos', 'Content', 'Tips', 'News').\n"
    "- Prefer the most specific subject that still covers most of the titles.\n"
    "- If unsure, coherent=false (a missed cluster is cheap; a junk hub is not)."
)


@dataclass
class ClusterProposal:
    members: list[Path]
    centroid: list[float]
    sample_titles: list[str]
    topic: str | None = None
    slug: str | None = None
    coherent: bool | None = None
    reject_reason: str | None = None
    spread: float | None = None
    anchored: int = 0

    @property
    def size(self) -> int:
        return len(self.members)


def _centroid(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    n = len(vectors)
    dim = len(vectors[0])
    acc = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            acc[i] += v[i]
    return [x / n for x in acc]


def _cluster_by_similarity_graph(
    vectors: list[list[float]], *, sim_threshold: float,
) -> list[list[int]]:
    """Deterministic cosine-graph greedy-modularity community detection."""
    import networkx as nx
    from networkx.algorithms import community as nx_comm

    n = len(vectors)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            c = _cosine(vectors[i], vectors[j])
            if c >= sim_threshold:
                g.add_edge(i, j, weight=c)
    if g.number_of_edges() == 0:
        return [[i] for i in range(n)]
    communities = nx_comm.greedy_modularity_communities(g, weight="weight")
    return [sorted(c) for c in communities]


# ---------------------------------------------------------------------------
# LLM naming (pluggable: OpenAI / Anthropic / any callable)
# ---------------------------------------------------------------------------

def _default_llm_namer(sample_titles: list[str]) -> tuple[bool, str | None]:
    """Built-in OpenAI namer. Returns ``(coherent, topic)``; ``(False, None)``
    on any error so a failure leaves the cluster as haystack.

    Reads ``OPENAI_API_KEY`` from the environment. The user can supply a
    different ``llm_namer`` callable via ``cluster_mint(..., llm_namer=...)``
    to plug in Anthropic, a local Ollama, or anything else with the same
    signature.
    """
    import json
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        log.warning("[cluster-mint] openai package not installed; clusters "
                    "cannot be named. Supply llm_namer= or skip cluster-mint.")
        return False, None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.warning("[cluster-mint] OPENAI_API_KEY not set; clusters cannot "
                    "be named. Supply llm_namer= or skip cluster-mint.")
        return False, None
    try:
        client = OpenAI(api_key=api_key)
        titles_block = "\n".join(f"- {t}" for t in sample_titles)
        resp = client.chat.completions.create(
            model=os.environ.get("ORPHAN_KILLER_LLM_MODEL", "gpt-4o-mini"),
            temperature=0,
            max_tokens=40,
            messages=[
                {"role": "system", "content": _CLUSTER_PROMPT_SYSTEM},
                {"role": "user", "content": f"Sample titles:\n{titles_block}"},
            ],
        )
        raw = (resp.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw[raw.find("{"):]
        data = json.loads(raw)
        coherent = bool(data.get("coherent"))
        topic = data.get("topic")
        if isinstance(topic, str):
            topic = topic.strip()
        else:
            topic = None
        return coherent, topic
    except Exception as exc:  # pragma: no cover - network-dependent
        log.warning("[cluster-mint] LLM naming failed: %s", exc)
        return False, None


def _hub_embed_surface(
    slug: str, topic: str | None, sample_titles: list[str], concepts_dir: Path,
) -> str:
    """Text representing a hub for the anchor-gate embedding.

    Gates members on cosine to THIS string (the hub's own surface), not the
    cluster centroid — so a tight-but-mislabeled cluster can't sneak through.
    """
    existing = concepts_dir / f"{slug}.md"
    if existing.exists():
        try:
            fm, body = split_frontmatter(existing.read_text(encoding="utf-8", errors="replace"))
            disp = topic or (fm or {}).get("title") or slug.replace("-", " ")
            return f"topic: {disp}. {_body_slice(body)}"
        except OSError:
            pass
    name = topic or slug.replace("-", " ")
    tail = ". ".join(t for t in sample_titles[:5])
    return f"topic: {name}. {tail}"


def _write_cluster_concept_note(
    concepts_dir: Path, slug: str, topic: str,
    sample_titles: list[str], n_members: int, *, dry_run: bool,
) -> bool:
    """Mint a concept hub note. Returns True iff (would be) created."""
    note_path = concepts_dir / f"{slug}.md"
    if note_path.exists():
        return False
    fm = {
        "type": "concept",
        "aliases": [topic] if topic and slugify(topic) != slug else [],
        "created": datetime.now(timezone.utc).date().isoformat(),
        "status": "active",
        "tags": ["type/concept"],
    }
    fm_text = yaml.safe_dump(
        fm, sort_keys=False, allow_unicode=True, default_flow_style=False,
    ).rstrip()
    examples = "\n".join(f"- {t}" for t in sample_titles[:5])
    body = (
        f"## Overview\n\n"
        f"{topic} is a recurring topic across {n_members} notes in this "
        f"vault, surfaced by clustering previously-unlinked source notes. "
        f"Representative notes include:\n\n{examples}\n\n"
        f"## Appears in\n\n"
        f"> Obsidian automatically shows backlinks in the sidebar. "
        f"Notes that link to this concept appear there.\n"
    )
    content = f"---\n{fm_text}\n---\n{body}"
    if not content.endswith("\n"):
        content += "\n"
    if not dry_run:
        write_atomic(note_path, content)
    return True


def cluster_mint(
    vault_root: Path,
    note_paths: list[Path] | None = None,
    *,
    table: AliasTable | None = None,
    hub_dirs: tuple[str, ...] | None = None,
    scope_dirs: tuple[str, ...] = DEFAULT_SCOPE_DIRS,
    concepts_dir_name: str = "concepts",
    dry_run: bool = False,
    force: bool = False,
    min_cluster: int = 5,
    max_hubs: int = 80,
    cluster_sim: float = 0.83,
    anchor_floor: float = 0.74,
    max_per_hub: int = 50,
    max_spread: float = 0.18,
    dup_hub_threshold: float = 0.88,
    min_body_chars: int = 200,
    limit: int | None = None,
    llm_namer=None,
    name_sample: int | None = None,
    embedder=None,
    embedder_max_length: int = 256,
    sample: int = 15,
    dump_tsv: Path | None = None,
) -> dict:
    """De-orphan clusterable orphans by minting per-cluster concept hubs.

    See the module docstring for the full safety contract.

    Args:
        concepts_dir_name: Name of the concepts subdirectory under
            ``vault_root`` where new hubs will be written. Defaults to
            ``"concepts"``.
        llm_namer: Optional callable ``(sample_titles) -> (coherent, topic)``
            to plug in any LLM provider. Defaults to the built-in OpenAI
            namer reading ``OPENAI_API_KEY``; if neither is configured every
            cluster will be reported as not-named (safe).
        name_sample: Cap on LLM naming calls (the N largest clusters get
            named; the rest are reported as 'qualifying but not yet named').
            Use this for cost control on a dry-run. Set to None for a live
            run that names every qualifying cluster.

    Returns:
        Stats dict.
    """
    if table is None:
        if hub_dirs is None:
            table = build_alias_table(vault_root)
        else:
            table = build_alias_table(vault_root, hub_dirs=hub_dirs)
    concepts_dir = vault_root / concepts_dir_name
    existing_slugs = set(table.hub_slugs)
    if llm_namer is None:
        llm_namer = _default_llm_namer

    notes = discover_notes(vault_root, note_paths, scope_dirs)

    # ---- Pass 1a: whole-vault inbound target set ----
    inbound_targets: set[str] = set()
    for p in _iter_all_vault_notes(vault_root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, body = split_frontmatter(text)
        for t in all_wikilinks(fm or {}, body):
            inbound_targets.add(t.lower())

    # ---- Pass 1b: parse candidate leaves ----
    parsed: dict[Path, tuple[dict, str]] = {}
    leaf_keys: dict[Path, set[str]] = {}
    for p in notes:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("cannot read %s: %s", p, exc)
            continue
        fm, body = split_frontmatter(text)
        if fm is None:
            continue
        parsed[p] = (fm, body)
        leaf_keys[p] = _note_link_keys(p, fm)

    def _is_orphan(p: Path, fm: dict, body: str) -> bool:
        if all_wikilinks(fm, body):
            return False
        if leaf_keys.get(p, set()) & inbound_targets:
            return False
        return True

    # ---- Pass 2: select embeddable orphans ----
    candidates: list[tuple[Path, dict, str]] = []
    n_thin = 0
    for p, (fm, body) in parsed.items():
        if not _is_orphan(p, fm, body):
            continue
        bslice = _body_slice(body)
        title = str(fm.get("title") or "")
        if len((title + bslice).strip()) < min_body_chars:
            n_thin += 1
            continue
        candidates.append((p, fm, body))

    if limit is not None:
        candidates = candidates[:limit]

    stats: dict = {
        "orphan_candidates": len(candidates),
        "thin_skipped": n_thin,
        "clusters_total": 0,
        "clusters_qualifying": 0,
        "clusters_coherent": 0,
        "clusters_rejected_incoherent": 0,
        "clusters_rejected_guard": 0,
        "clusters_rejected_spread": 0,
        "clusters_rejected_dup_hub": 0,
        "hubs_minted": 0,
        "hubs_capped_out": 0,
        "orphans_anchored": 0,
        "orphans_below_anchor_floor": 0,
        "hub_capped": 0,
        "orphans_haystack": 0,
        "written": 0,
        "errors": 0,
        "min_cluster": min_cluster,
        "max_hubs": max_hubs,
        "cluster_sim": cluster_sim,
        "anchor_floor": anchor_floor,
        "max_per_hub": max_per_hub,
        "max_spread": max_spread,
        "dup_hub_threshold": dup_hub_threshold,
        "experimental": True,
    }
    sample_rows: list[dict] = []
    if not candidates:
        stats["sample"] = sample_rows
        return stats

    # ---- Pass 3: embed all orphan candidates ----
    if embedder is None:
        embedder = _load_embedder(max_length=embedder_max_length)
    surfaces = [
        f"topic: {str(fm.get('title') or '')}. {_body_slice(body)}"
        for (_p, fm, body) in candidates
    ]
    cand_vecs = [v.tolist() for v in embedder.embed(surfaces)]

    # ---- Pass 4: cluster deterministically ----
    cluster_idx = _cluster_by_similarity_graph(cand_vecs, sim_threshold=cluster_sim)
    path_to_idx = {candidates[i][0]: i for i in range(len(candidates))}
    stats["clusters_total"] = sum(1 for c in cluster_idx if len(c) >= 2)

    # Build qualifying proposals.
    proposals: list[ClusterProposal] = []
    haystack_count = 0
    for members in cluster_idx:
        if len(members) < min_cluster:
            haystack_count += len(members)
            continue
        mvecs = [cand_vecs[i] for i in members]
        mpaths = [candidates[i][0] for i in members]
        cen = _centroid(mvecs)
        member_cos = [_cosine(v, cen) for v in mvecs]
        spread = (max(member_cos) - min(member_cos)) if member_cos else 0.0
        ranked = sorted(
            range(len(members)),
            key=lambda k: (-member_cos[k], candidates[members[k]][0].as_posix()),
        )
        sample_titles: list[str] = []
        for k in ranked[:8]:
            t = str(candidates[members[k]][1].get("title") or "").strip()
            if t:
                sample_titles.append(t[:120])
        proposals.append(ClusterProposal(
            members=mpaths, centroid=cen, sample_titles=sample_titles,
            spread=round(spread, 4),
        ))

    stats["clusters_qualifying"] = len(proposals)
    proposals.sort(key=lambda pr: (-pr.size, pr.members[0].as_posix()))

    # ---- Pass 5: name + guard + cap ----
    concept_slugs = [s for s in table.hub_names if table.hub_kinds.get(s) == "concept"]
    concept_names = [table.hub_names[s] for s in concept_slugs]
    concept_vecs = (
        [v.tolist() for v in embedder.embed([f"topic: {n}" for n in concept_names])]
        if concept_names else []
    )

    def _nearest_existing_concept(topic: str) -> tuple[str | None, float]:
        if not concept_vecs:
            return None, 0.0
        tvec_iter = embedder.embed([f"topic: {topic}"])
        tvec = next(iter(tvec_iter)).tolist()
        best_slug, best_cos = None, 0.0
        for s, hvec in zip(concept_slugs, concept_vecs, strict=True):
            c = _cosine(tvec, hvec)
            if c > best_cos:
                best_cos, best_slug = c, s
        return best_slug, best_cos

    minted: list[ClusterProposal] = []
    minted_slugs_this_run: set[str] = set()
    named_calls = 0
    stats["clusters_named_capped"] = 0
    stats["dup_hub_redirects"] = []
    for pr in proposals:
        if len(minted) >= max_hubs:
            stats["hubs_capped_out"] += 1
            haystack_count += pr.size
            pr.reject_reason = "hub-cap"
            continue
        if pr.spread is not None and pr.spread > max_spread:
            stats["clusters_rejected_spread"] += 1
            haystack_count += pr.size
            pr.reject_reason = f"spread {pr.spread:.3f}>{max_spread}"
            continue
        if name_sample is not None and named_calls >= name_sample:
            stats["clusters_named_capped"] += 1
            haystack_count += pr.size
            pr.reject_reason = "name-sample-cap"
            continue
        named_calls += 1
        coherent, topic = llm_namer(pr.sample_titles)
        pr.coherent = coherent
        pr.topic = topic
        if not coherent or not topic:
            stats["clusters_rejected_incoherent"] += 1
            haystack_count += pr.size
            pr.reject_reason = "incoherent"
            continue
        ok, why = proposed_name_is_clean(topic)
        if not ok:
            stats["clusters_rejected_guard"] += 1
            haystack_count += pr.size
            pr.reject_reason = why
            continue
        slug = slugify(topic)
        if slug in minted_slugs_this_run:
            haystack_count += pr.size
            pr.reject_reason = "dup-slug-this-run"
            continue
        if slug not in existing_slugs:
            near_slug, near_cos = _nearest_existing_concept(topic)
            if near_slug is not None and near_cos >= dup_hub_threshold:
                stats["clusters_rejected_dup_hub"] += 1
                stats["dup_hub_redirects"].append(
                    {"proposed": topic, "existing": near_slug,
                     "cosine": round(near_cos, 4), "members": pr.size}
                )
                pr.reject_reason = f"dup-hub->{near_slug}@{near_cos:.3f}"
                pr.slug = near_slug
                pr.topic = table.hub_names.get(near_slug, topic)
                minted.append(pr)
                minted_slugs_this_run.add(near_slug)
                continue
        pr.slug = slug
        stats["clusters_coherent"] += 1
        minted.append(pr)
        minted_slugs_this_run.add(slug)

    # ---- Pass 6: mint hubs + anchor members ----
    hub_surfaces = [
        _hub_embed_surface(pr.slug, pr.topic, pr.sample_titles, concepts_dir)
        for pr in minted
    ]
    hub_vecs = (
        [v.tolist() for v in embedder.embed(hub_surfaces)] if hub_surfaces else []
    )
    dump_rows: list[tuple[str, str, float, str]] = []

    for pr_i, pr in enumerate(minted):
        slug = pr.slug
        assert slug is not None
        hub_vec = hub_vecs[pr_i]
        per_hub_anchored = 0
        is_new = slug not in existing_slugs
        if is_new:
            if _write_cluster_concept_note(
                concepts_dir, slug, pr.topic or slug, pr.sample_titles, pr.size,
                dry_run=dry_run,
            ):
                stats["hubs_minted"] += 1
                if not dry_run:
                    stats["written"] += 1
        anchor_target_slugs = existing_slugs | minted_slugs_this_run

        for mp in pr.members:
            fm, body = parsed[mp]
            rel = mp.relative_to(vault_root).as_posix()
            cos_to_hub = _cosine(cand_vecs[path_to_idx[mp]], hub_vec)
            if max_per_hub and per_hub_anchored >= max_per_hub:
                stats["hub_capped"] += 1
                dump_rows.append((rel, slug, round(cos_to_hub, 4), "hub_capped"))
                continue
            if cos_to_hub < anchor_floor:
                stats["orphans_below_anchor_floor"] += 1
                dump_rows.append((rel, slug, round(cos_to_hub, 4), "below_anchor_floor"))
                continue
            if slug not in anchor_target_slugs:
                dump_rows.append((rel, slug, round(cos_to_hub, 4), "not_a_hub"))
                continue
            ch = resolve_hash(fm, body)
            if not force and should_skip(fm, "clustered_at", "cluster_hash", ch):
                dump_rows.append((rel, slug, round(cos_to_hub, 4), "skipped_idempotent"))
                continue
            stats["orphans_anchored"] += 1
            per_hub_anchored += 1
            dump_rows.append((rel, slug, round(cos_to_hub, 4), "anchored"))
            if len(sample_rows) < sample:
                sample_rows.append({
                    "topic": pr.topic, "slug": slug, "members": pr.size,
                    "titles": pr.sample_titles[:3],
                })
            if dry_run:
                continue
            new_fm = dict(fm)
            ents = list(new_fm.get("entities") or []) if isinstance(new_fm.get("entities"), list) else []
            link = f"[[{slug}]]"
            if link not in ents:
                ents.append(link)
            new_fm["entities"] = ents
            new_hash = resolve_hash(new_fm, body)
            new_fm = stamp_meta(
                new_fm, "clustered_at", "cluster_hash", new_hash,
                extras={"cluster_hub": slug, "cluster_cosine": round(cos_to_hub, 4)},
            )
            try:
                write_atomic(mp, serialize(new_fm, body))
                stats["written"] += 1
            except OSError as exc:
                log.warning("cannot write %s: %s", mp, exc)
                stats["errors"] += 1
        pr.anchored = per_hub_anchored

    stats["orphans_haystack"] = haystack_count
    stats["gpt_naming_calls"] = named_calls
    stats["sample"] = sample_rows
    stats["minted_clusters"] = [
        {"topic": pr.topic, "slug": pr.slug, "members": pr.size,
         "anchored": pr.anchored, "spread": pr.spread,
         "titles": pr.sample_titles[:3]}
        for pr in minted if pr.reject_reason is None
    ]
    stats["max_hub_absorption"] = max((pr.anchored for pr in minted), default=0)
    stats["rejected_clusters"] = [
        {"reason": pr.reject_reason, "members": pr.size,
         "topic": pr.topic, "titles": pr.sample_titles[:3]}
        for pr in proposals if pr.reject_reason and pr.reject_reason != "hub-cap"
    ][:20]

    if dump_tsv is not None:
        try:
            dump_tsv.parent.mkdir(parents=True, exist_ok=True)
            lines = ["cosine\tdecision\thub\tnote"]
            for rel, hub, cos, decision in sorted(dump_rows, key=lambda r: -r[2]):
                lines.append(f"{cos:.4f}\t{decision}\t{hub}\t{rel}")
            dump_tsv.write_text("\n".join(lines) + "\n", encoding="utf-8")
            stats["dump_tsv"] = str(dump_tsv)
            stats["dump_rows"] = len(dump_rows)
        except OSError as exc:
            log.warning("could not write cluster dump TSV %s: %s", dump_tsv, exc)
    return stats
