"""8-dimension Grade-A rubric for Obsidian vault audits.

Thresholds are defaults from the PKM / network-science canon. Citations live in
``docs/RUBRIC.md`` next to each dimension.

A vault that passes all 8 dimensions is "Grade A". Each dimension is independently
graded A/B/C/D/F by where the measurement falls relative to the configured cutoffs.

Override the defaults by passing ``--threshold-config thresholds.yaml`` on the
CLI, where ``thresholds.yaml`` looks like::

    link_density:
      a: 4.0
      d: 1.0
    orphan_pct:
      a: 10.0
      d: 30.0
    # ... (any subset of the 8 dimensions)
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

GRADES: tuple[str, str, str, str, str] = ("A", "B", "C", "D", "F")


# ---------------------------------------------------------------------------
# Per-dimension threshold dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _MinThresholds:
    """Dimension is graded by ``value >= a`` (higher = better)."""
    a: float
    b: float
    c: float
    d: float

    def grade(self, v: float) -> str:
        if v >= self.a:
            return "A"
        if v >= self.b:
            return "B"
        if v >= self.c:
            return "C"
        if v >= self.d:
            return "D"
        return "F"


@dataclass(frozen=True)
class _MaxThresholds:
    """Dimension is graded by ``value <= a`` (lower = better)."""
    a: float
    b: float
    c: float
    d: float

    def grade(self, v: float) -> str:
        if v <= self.a:
            return "A"
        if v <= self.b:
            return "B"
        if v <= self.c:
            return "C"
        if v <= self.d:
            return "D"
        return "F"


@dataclass(frozen=True)
class _RangeThresholds:
    """Dimension is graded by how close the value is to a target range ``[a_lo, a_hi]``."""
    a_lo: float
    a_hi: float
    b_lo: float
    b_hi: float
    c_lo: float
    c_hi: float

    def grade(self, v: float) -> str:
        if self.a_lo <= v <= self.a_hi:
            return "A"
        if self.b_lo <= v <= self.b_hi:
            return "B"
        if self.c_lo <= v <= self.c_hi:
            return "C"
        # Below b_lo or above c_hi
        return "D" if v >= self.c_lo / 2 else "F"


# ---------------------------------------------------------------------------
# Default thresholds (citations live in docs/RUBRIC.md)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Thresholds:
    """The 8-dimension default rubric.

    Citations: see ``docs/RUBRIC.md`` for the source of each cutoff. In summary:
      - **link density 4-10:** network-science consensus for well-connected
        small-world graphs; kepano "Properties as links".
      - **orphan rate <10%:** PKM-as-graph convention (Konik). Beyond 10%, your
        capture-to-connection ratio is broken.
      - **near-orphan <15%:** derived complement of orphan threshold.
      - **connected_2plus >75%:** derived, three-quarters of notes should be
        actually integrated.
      - **top-hub edge-share <5%:** power-law avoidance / Milo motifs, vault
        shouldn't be a force-star around one mega-hub.
      - **top:next ratio <2.0:** healthy power-law tail, not a single dominant.
      - **Louvain modularity 0.4-0.65:** Newman / Paranyushkin (InfraNodus) -
        below 0.4 = no coherent communities; above 0.65 = siloed islands.
      - **frontmatter-wikilink adoption >80%:** kepano "Properties as links"
        convention, typed metadata participates in the graph.
    """
    link_density: _MinThresholds = field(default_factory=lambda: _MinThresholds(a=4.0, b=2.5, c=1.5, d=0.8))
    orphan_pct: _MaxThresholds = field(default_factory=lambda: _MaxThresholds(a=10.0, b=20.0, c=30.0, d=40.0))
    near_orphan_pct: _MaxThresholds = field(default_factory=lambda: _MaxThresholds(a=15.0, b=25.0, c=35.0, d=45.0))
    connected_2plus_pct: _MinThresholds = field(default_factory=lambda: _MinThresholds(a=75.0, b=60.0, c=45.0, d=30.0))
    top_hub_edge_share_pct: _MaxThresholds = field(default_factory=lambda: _MaxThresholds(a=5.0, b=10.0, c=15.0, d=20.0))
    top_hub_next_ratio: _MaxThresholds = field(default_factory=lambda: _MaxThresholds(a=2.0, b=3.0, c=5.0, d=8.0))
    modularity: _RangeThresholds = field(default_factory=lambda: _RangeThresholds(
        a_lo=0.40, a_hi=0.65,
        b_lo=0.30, b_hi=0.75,
        c_lo=0.20, c_hi=0.85,
    ))
    fm_wikilink_adoption_pct: _MinThresholds = field(default_factory=lambda: _MinThresholds(a=80.0, b=60.0, c=40.0, d=20.0))


DEFAULT_THRESHOLDS = Thresholds()


# ---------------------------------------------------------------------------
# Loader for user-supplied threshold YAML
# ---------------------------------------------------------------------------

def load_thresholds(path: Path | None) -> Thresholds:
    """Load thresholds from a YAML file, merged onto the defaults.

    If ``path`` is ``None`` or the file is empty, returns ``DEFAULT_THRESHOLDS``.
    """
    if path is None:
        return DEFAULT_THRESHOLDS
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"threshold-config must be a YAML mapping, got {type(data).__name__}")

    defaults = asdict(DEFAULT_THRESHOLDS)
    fields: dict[str, Any] = {}
    for name, default_val in defaults.items():
        override = data.get(name)
        if override is None:
            fields[name] = _rehydrate(name, default_val)
            continue
        if not isinstance(override, dict):
            raise ValueError(f"threshold-config['{name}'] must be a mapping")
        merged = {**default_val, **override}
        fields[name] = _rehydrate(name, merged)
    return Thresholds(**fields)


def _rehydrate(name: str, payload: dict[str, float]):
    """Return the right dataclass for ``name`` from a flat dict."""
    if name == "modularity":
        return _RangeThresholds(**payload)
    # All MinThresholds dimensions have a > b > c > d.
    min_dims = {"link_density", "connected_2plus_pct", "fm_wikilink_adoption_pct"}
    if name in min_dims:
        return _MinThresholds(**payload)
    return _MaxThresholds(**payload)


# ---------------------------------------------------------------------------
# Scoring + overall grade
# ---------------------------------------------------------------------------

# Map metric-dict keys to (Thresholds attr, "min"|"max"|"range") for the grader.
_METRIC_TO_DIM: dict[str, str] = {
    "link_density": "link_density",
    "orphan_pct": "orphan_pct",
    "near_orphan_pct": "near_orphan_pct",
    "connected_2plus_pct": "connected_2plus_pct",
    "top_hub_edge_share_pct": "top_hub_edge_share_pct",
    "top_hub_next_ratio": "top_hub_next_ratio",
    "modularity": "modularity",
    "fm_wikilink_adoption_pct": "fm_wikilink_adoption_pct",
}


def grade(metrics: dict[str, Any], thresholds: Thresholds = DEFAULT_THRESHOLDS) -> dict[str, str]:
    """Return ``{metric_key: 'A'..'F', ..., 'overall': 'A'..'F'}``.

    ``metrics`` is the dict returned by ``auditor.audit()``. Missing metrics are
    skipped. ``top_hub_next_ratio == None`` (the only-one-hub edge case) is
    treated as Grade A (no concentration problem possible), but only if other
    metrics exist; an empty ``metrics`` dict still grades overall F.
    """
    out: dict[str, str] = {}
    # Track which dims came from real measurements (vs the None-ratio shortcut)
    # so an empty metrics dict can't pass purely on the shortcut.
    has_real_measurement = False
    for metric_key, dim_name in _METRIC_TO_DIM.items():
        v = metrics.get(metric_key)
        if v is None:
            continue
        try:
            v_f = float(v)
        except (TypeError, ValueError):
            continue
        dim = getattr(thresholds, dim_name)
        out[metric_key] = dim.grade(v_f)
        has_real_measurement = True
    # Special: only-one-hub edge case. Auditor reports top_hub_next_ratio=None
    # when there is no second hub. That's not a problem, Grade A, BUT only
    # if we actually have other measurements to anchor on.
    if has_real_measurement and "top_hub_next_ratio" in metrics and metrics["top_hub_next_ratio"] is None:
        out["top_hub_next_ratio"] = "A"
    out["overall"] = _overall(out)
    return out


def _overall(per_dim: dict[str, str]) -> str:
    """Worst-of-the-non-overall keys is the overall grade.

    A vault is Grade A only if EVERY dimension is A. A single F drags overall to F.
    This is intentional: an auditor's job is to surface the weakest link.
    """
    letters = [v for k, v in per_dim.items() if k != "overall"]
    if not letters:
        return "F"
    order = {g: i for i, g in enumerate(GRADES)}
    worst = max(letters, key=lambda x: order.get(x, 99))
    return worst


def score(metrics: dict[str, Any], thresholds: Thresholds = DEFAULT_THRESHOLDS) -> float:
    """Return a numeric score 0.0-100.0 (mean of per-dimension grade GPA).

    GPA mapping: A=4, B=3, C=2, D=1, F=0. Scaled to 100.
    """
    gpa = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    g = grade(metrics, thresholds)
    letters = [v for k, v in g.items() if k != "overall"]
    if not letters:
        return 0.0
    mean = sum(gpa[g] for g in letters) / len(letters)
    return round(mean * 25.0, 2)
