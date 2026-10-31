"""Entry filters and the point-in-time helpers features are built from (docs/OPTIMIZE.md has the contracts).

A filter vetoes an entry at the signal bar; it never changes a strategy's signal state. Every helper here gives
the value at bar i from bar i and earlier bars only.
"""

from dataclasses import dataclass

import numpy as np

OPS = ("min", "max")


@dataclass(frozen=True)
class Filter:
    feature: str
    op: str  # "min": value >= threshold, "max": value <= threshold
    threshold: float

    def __post_init__(self):
        if self.op not in OPS:
            raise ValueError(f"filter op must be one of {OPS}")

    def passes(self, values: np.ndarray) -> np.ndarray:
        """NaN fails an enabled filter."""
        with np.errstate(invalid="ignore"):
            return (values >= self.threshold) if self.op == "min" else (values <= self.threshold)

    def __str__(self) -> str:
        return f"{self.feature} {'>=' if self.op == 'min' else '<='} {self.threshold:g}"


def as_filter(f) -> Filter:
    """A Filter from a Filter, a (feature, op, threshold) tuple or a JSON dict."""
    if isinstance(f, Filter):
        return f
    if isinstance(f, dict):
        return Filter(f["feature"], f["op"], float(f["threshold"]))
    feature, op, threshold = f
    return Filter(feature, op, float(threshold))


def gate(filters: tuple[Filter, ...], values: dict[str, np.ndarray], n: int) -> np.ndarray:
    """True where every filter passes (all True with no filters)."""
    ok = np.ones(n, dtype=bool)
    for f in filters:
        if f.feature not in values:
            raise KeyError(f"unknown feature {f.feature!r}; known: {sorted(values)}")
        ok &= f.passes(values[f.feature])
    return ok


def carry_forward(idx: np.ndarray, vals: np.ndarray, n: int) -> np.ndarray:
    """Pine `var` set at bars idx (ascending): value of the latest idx <= i, NaN before the first."""
    out = np.full(n, np.nan)
    if len(idx) == 0:
        return out
    pos = np.searchsorted(idx, np.arange(n), side="right") - 1
    ok = pos >= 0
    out[ok] = np.asarray(vals, dtype=float)[pos[ok]]
    return out


def prior_range(h: np.ndarray, l: np.ndarray, idx: np.ndarray, length: int) -> np.ndarray:
    """At each bar a in idx: highest(high, length)[1] - lowest(low, length)[1], the `length` bars before a.
    NaN when fewer than `length` bars precede a."""
    out = np.full(len(idx), np.nan)
    for k, a in enumerate(idx.tolist()):
        if a >= length:
            out[k] = float(h[a - length: a].max() - l[a - length: a].min())
    return out


def ratio_to_trailing_mean(x: np.ndarray, count: int) -> np.ndarray:
    """x[k] / mean of the `count` previous non-NaN values of x (Pine: compare, then push into a `var` array of
    the last `count`). NaN until `count` earlier values exist, or when the mean is not positive."""
    out = np.full(len(x), np.nan)
    hist: list[float] = []
    for k, v in enumerate(x.tolist()):
        if v == v:
            if len(hist) == count:
                m = sum(hist) / count
                if m > 0:
                    out[k] = v / m
            hist.append(v)
            if len(hist) > count:
                hist.pop(0)
    return out
