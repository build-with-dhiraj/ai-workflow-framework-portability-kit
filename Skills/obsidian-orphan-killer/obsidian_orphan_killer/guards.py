"""Safety guards — denylists, lexical guard, URL-fragment / DO_NOT_MERGE.

These exist to prevent the resolver from coining a junk hub or merging two
distinct real-world entities. Every guard here is a HARD reject: a candidate
that fails any one of them is left as a plain string (or, in the experimental
mint mode, as a haystack leaf).

Decoupled from any vault-specific assumption — these lists are derived from
common PKM noise patterns (URL fragments, generic catch-alls) and are augmented
by the per-vault DO_NOT_MERGE pairs the user can supply at runtime.
"""
from __future__ import annotations

import re

from obsidian_orphan_killer.slug import normalize

# ---------------------------------------------------------------------------
# Topic denylist — overly generic concept names that should never become hubs.
# ---------------------------------------------------------------------------
TOPIC_DENYLIST: set[str] = {
    "content", "information", "technology", "tech", "software", "platform",
    "product", "service", "services", "system", "systems", "data", "results",
    "analysis", "management", "development", "performance", "process",
    "strategy", "review", "update", "news", "article", "video", "post",
    "market", "sector", "industry", "business", "company", "companies",
    "startup", "startups", "overview", "introduction", "guide", "tutorial",
    "tips", "tricks", "best practices", "how to", "what is",
    "general", "other", "misc", "various",
}

# ---------------------------------------------------------------------------
# Generic catch-alls a clustering pass must never coin (the cluster-mint mode
# layers this on top of TOPIC_DENYLIST as a hard backstop in case the LLM
# returns a single-word grab-bag).
# ---------------------------------------------------------------------------
CLUSTER_GENERIC_DENY: set[str] = {
    normalize(w) for w in (
        "science", "sciences", "videos", "video", "topic", "topics", "subject",
        "subjects", "knowledge", "education", "learning", "academic", "academia",
        "research", "study", "studies", "things", "stuff", "thoughts", "ideas",
        "media", "channel", "channels", "playlist", "playlists", "clip", "clips",
        "shorts", "vlog", "vlogs", "podcast", "podcasts", "interview", "interviews",
    )
}

# ---------------------------------------------------------------------------
# URL-fragment / domain-leak denylist.
# ---------------------------------------------------------------------------
URL_FRAGMENT_DENYLIST: set[str] = {
    "www", "http", "https", "com", "html", "org", "net",
}

_URL_FRAGMENT_RE = re.compile(
    r"""(?ix)
    ^(?:https?://|www\.)             # explicit URL prefix, OR
    | \b[a-z0-9-]+\.(?:com|net|org|io|in|st|co|ai|gov|edu|me|app|dev|xyz)\b
    """,
)
_SPACE_TOKENIZED_TLDS: set[str] = {"com", "net", "org"}


def is_url_fragment(name: str) -> bool:
    """True if a surface form is a URL fragment / domain / junk token."""
    n = name.strip().lower()
    if not n:
        return True
    if n in URL_FRAGMENT_DENYLIST:
        return True
    if _URL_FRAGMENT_RE.search(n):
        return True
    parts = n.split()
    if len(parts) == 2 and parts[-1] in _SPACE_TOKENIZED_TLDS:
        return True
    return False


# ---------------------------------------------------------------------------
# Lexical guard — prevents merging two strings that have no token overlap.
# ---------------------------------------------------------------------------

def _token_set(name: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", name.lower()))


def lexical_guard_passes(a: str, b: str) -> bool:
    """True iff a and b share enough lexical overlap to plausibly be aliases.

    The embedding leg uses this AFTER the cosine gate as a mandatory backstop.
    Cosine alone can be high between semantically-related but distinct things
    (e.g. "OpenAI" vs "Anthropic" are both AI labs). The guard accepts:

      - substring on the lowercase form ("Python" in "Python 3");
      - substring on the normalized form ("openai" matches "open ai" because
        ``normalize("Open AI") == normalize("OpenAI") == "openai"``);
      - any shared significant (len≥3) token;
      - token-set Jaccard ≥ 0.6.
    """
    a_lo = a.lower().strip()
    b_lo = b.lower().strip()
    if a_lo in b_lo or b_lo in a_lo:
        return True
    # Hyphen / space variants collapse via ``normalize`` (which strips hyphens).
    a_norm = normalize(a)
    b_norm = normalize(b)
    if a_norm and b_norm and (a_norm in b_norm or b_norm in a_norm):
        return True
    ta = _token_set(a)
    tb = _token_set(b)
    ta_sig = {t for t in ta if len(t) >= 3}
    tb_sig = {t for t in tb if len(t) >= 3}
    if not ta_sig or not tb_sig:
        return False
    if ta_sig & tb_sig:
        return True
    union = ta_sig | tb_sig
    if not union:
        return False
    return len(ta_sig & tb_sig) / len(union) >= 0.6


# ---------------------------------------------------------------------------
# DO_NOT_MERGE — user-supplied pairs that look similar but are distinct.
# ---------------------------------------------------------------------------

def is_forbidden_pair(a_key: str, b_key: str, do_not_merge: list[frozenset[str]]) -> bool:
    """True if the pair (a_key, b_key) is in the user's DO_NOT_MERGE list."""
    pair = frozenset({a_key, b_key})
    return any(pair == g for g in do_not_merge if len(g) == 2)


def proposed_name_is_clean(topic: str) -> tuple[bool, str | None]:
    """Apply the mint-side guards to a proposed hub name (for cluster-mint mode).

    Returns ``(ok, reject_reason)``. The cluster-mint mode requires that the
    proposed concept name pass ALL of:
      - non-empty after slugify
      - not in TOPIC_DENYLIST
      - not in CLUSTER_GENERIC_DENY
      - not a URL fragment
      - at least one significant (len≥3) alphanumeric token
    """
    if not topic:
        return False, "empty topic"
    from obsidian_orphan_killer.slug import slugify
    slug = slugify(topic)
    if not slug:
        return False, "empty slug"
    norm = normalize(topic)
    denylist_norm = {normalize(t) for t in TOPIC_DENYLIST}
    if norm in denylist_norm or slug in TOPIC_DENYLIST:
        return False, f"denylisted ({topic!r})"
    if norm in CLUSTER_GENERIC_DENY:
        return False, f"generic catch-all ({topic!r})"
    if is_url_fragment(topic):
        return False, f"url-fragment ({topic!r})"
    sig_tokens = [t for t in re.findall(r"[a-z0-9]+", topic.lower()) if len(t) >= 3]
    if not sig_tokens:
        return False, f"no significant token ({topic!r})"
    return True, None
