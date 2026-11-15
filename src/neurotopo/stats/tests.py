"""Generic statistics: exact binomial CIs, Fisher/McNemar exact tests, cluster bootstrap, Holm and BH.

Global context: the preregistration (reports/preregistration.md, section 6) fixes these procedures:
Holm over the 6 co-primary alignment p-values, Benjamini-Hochberg within the exploratory list, exact
binomial (Clopper-Pearson) CIs for rates over few datasets, exact McNemar for paired criteria, and a
cluster bootstrap over generator chunks of 25 synthetic clouds (clouds in a chunk share N and the
embedding draw in the source generator, so they are not independent).
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def binom_ci(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Clopper-Pearson exact CI for a proportion k/n (scipy.stats.binomtest(...).proportion_ci)."""
    if n == 0:
        return (float("nan"), float("nan"))
    ci = stats.binomtest(k, n).proportion_ci(confidence_level=level, method="exact")
    return (float(ci.low), float(ci.high))


def mcnemar_exact(a_only: int, b_only: int) -> float:
    """Exact McNemar test: two-sided binomial test of the discordant counts against p = 1/2."""
    n = a_only + b_only
    return 1.0 if n == 0 else float(stats.binomtest(a_only, n, 0.5).pvalue)


def fisher_exact(table) -> float:
    """One-sided Fisher exact test (greater) for a 2x2 table [[a, b], [c, d]]."""
    return float(stats.fisher_exact(table, alternative="greater")[1])


def holm(pvals) -> np.ndarray:
    """Holm step-down adjusted p-values (Holm 1979), monotone and capped at 1; NaNs are passed through."""
    p = np.asarray(pvals, dtype=np.float64)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    q = p[ok]
    order = np.argsort(q)
    m = q.size
    adj = np.maximum.accumulate((m - np.arange(m)) * q[order])
    res = np.empty(m)
    res[order] = np.minimum(adj, 1.0)
    out[ok] = res
    return out


def bh(pvals) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (q-values); NaNs passed through."""
    p = np.asarray(pvals, dtype=np.float64)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    q = p[ok]
    m = q.size
    order = np.argsort(q)
    adj = q[order] * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    res = np.empty(m)
    res[order] = np.minimum(adj, 1.0)
    out[ok] = res
    return out


def cluster_bootstrap(values: np.ndarray, clusters: np.ndarray, stat, n_boot: int = 2000, seed: int = 0,
                      level: float = 0.95) -> tuple[float, float, float]:
    """Percentile CI of stat(rows) when rows are resampled by whole clusters (generator chunks).

    values: (n,) or (n, k) per-cloud data; clusters: (n,) cluster id; stat: function of a row subset.
    Returns (estimate on all rows, CI low, CI high).
    """
    values = np.asarray(values)
    clusters = np.asarray(clusters)
    ids, inv = np.unique(clusters, return_inverse=True)
    members = [np.flatnonzero(inv == j) for j in range(ids.size)]
    rng = np.random.default_rng(seed)
    est = float(stat(values))
    boots = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, ids.size, ids.size)
        boots[b] = stat(values[np.concatenate([members[j] for j in pick])])
    lo, hi = np.nanpercentile(boots, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
    return est, float(lo), float(hi)
