"""Significance of persistence bars: the universal null and design-matched Monte Carlo nulls.

Global context: a persistence diagram always contains short "noise" bars; Method B must decide which
bars are real holes (reports/preregistration.md, section 4).
- Universal null (Bobrowski & Skraba 2023, Sci. Rep. 13:12274, doi:10.1038/s41598-023-37842-2, eqs. for
  pi, l and the left-Gumbel law): l = A log log pi + B, B = -lambda - A * mean(log log pi), p = exp(-e^l),
  Bonferroni within the diagram. Validated on large i.i.d. samples, so descriptive on real data.
- Monte Carlo nulls (primary on real data): the maximum pi of H_k over M null clouds that pass through the
  same preprocessing, in the style of the max-over-shuffles threshold of Gardner et al. 2022
  (doi:10.1038/s41586-021-04268-7). Two designs: (a) a cluster-centre null that redraws the concept means
  from a Gaussian with their covariance and keeps every point's within-concept residual (prompt-template
  designs), and (b) a full-D matched-covariance Gaussian (one point per value).
"""

from __future__ import annotations

import zlib

import numpy as np
from joblib import Parallel, delayed
from scipy.sparse.linalg import svds
from threadpoolctl import threadpool_limits

from neurotopo.geometry.pca import rms_normalise
from neurotopo.tda.diagrams import alpha_diagrams, max_ratio, ratios

EULER_GAMMA = 0.5772156649015329            # lambda in Bobrowski & Skraba 2023


# ----------------------------------------------------------------------------- universal null
def universal_pvalues(dgm: np.ndarray, A: float) -> np.ndarray:
    """Per-bar p-values under the universal null; NaN for bars with pi <= 1 or undefined pi.

    The mean L of log log pi is taken over bars with pi > 1, as in the authors' released code
    (github.com/primozskraba/PersistenceUniversality, modules/PDplot.py), since log log 1 = -inf.
    """
    pi = ratios(dgm)
    valid = np.isfinite(pi) & (pi > 1.0 + 1e-12)
    p = np.full(pi.shape, np.nan)
    if valid.sum() == 0:
        return p
    ll = np.log(np.log(pi[valid]))                 # log log pi of the valid bars
    ell = A * ll - EULER_GAMMA - A * ll.mean()     # l = A log log pi + B with B = -lambda - A * Lbar
    p[valid] = np.exp(-np.exp(ell))                # left-Gumbel tail: P(l >= x) = exp(-e^x)
    return p


def universal_significant(dgm: np.ndarray, A: float, alpha: float = 0.05) -> np.ndarray:
    """Bonferroni within the diagram: significant if p < alpha / (number of bars with pi > 1)."""
    p = universal_pvalues(dgm, A)
    n = int(np.isfinite(p).sum())
    return np.isfinite(p) & (p < alpha / max(n, 1))


# ----------------------------------------------------------------------------- Monte Carlo nulls
def dataset_seed(dataset_id: str, seed: int) -> int:
    """Stable per-dataset seed: crc32(dataset_id) + seed (reports/preregistration.md, section 4)."""
    return (zlib.crc32(dataset_id.encode()) + int(seed)) % (2 ** 32)


def mc_pvalues(pi_obs: np.ndarray, null_max: np.ndarray) -> np.ndarray:
    """Monte Carlo p-value of each observed bar against the null distribution of the maximum pi:
    p_j = (1 + #{null max >= pi_j}) / (M + 1)."""
    null_max = np.sort(np.asarray(null_max, dtype=np.float64))
    pi_obs = np.asarray(pi_obs, dtype=np.float64)
    ge = null_max.size - np.searchsorted(null_max, pi_obs, side="left")   # number of null values >= pi_j
    p = (1.0 + ge) / (null_max.size + 1.0)
    return np.where(np.isfinite(pi_obs), p, np.nan)


def _top3_scores(y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Top-3 principal scores of a centred matrix y (N x q): dense SVD for small matrices, ARPACK otherwise.
    Rotations and sign flips of the scores do not change homology, so only the subspace matters."""
    yc = y - y.mean(0)
    if min(yc.shape) <= 400:
        u, s, _ = np.linalg.svd(yc, full_matrices=False)
        k = min(3, s.size)
        sc = u[:, :k] * s[:k]
    else:
        v0 = rng.normal(size=min(yc.shape))                   # deterministic ARPACK start vector
        u, s, _ = svds(yc, k=3, v0=v0)
        sc = u * s
    if sc.shape[1] < 3:
        sc = np.concatenate([sc, np.zeros((sc.shape[0], 3 - sc.shape[1]))], 1)
    return sc


class GaussianNull:
    """(b) Full-D matched-covariance Gaussian: X* = mean + Z Xc / sqrt(N-1), Z an N x N standard normal
    matrix, so cov(X*) = Xc^T Xc / (N-1) in expectation. Xc is replaced by an exact low-rank factor
    L (N x r, r = rank) with Xc Xc^T = L L^T, which leaves the PCA scores unchanged up to rotation."""

    def __init__(self, x: np.ndarray):
        xc = np.asarray(x, dtype=np.float64)
        xc = xc - xc.mean(0)
        n, d = xc.shape
        if d <= n:
            self.L = xc
        else:
            w, u = np.linalg.eigh(xc @ xc.T)                 # Gram matrix K = Xc Xc^T (N x N)
            keep = w > w.max() * 1e-12
            self.L = u[:, keep] * np.sqrt(w[keep])           # K = L L^T
        self.n = n

    def draw_raw(self, rng: np.random.Generator) -> np.ndarray:
        """One null cloud in the coordinates of L (the original coordinates when D <= N), centred."""
        z = rng.standard_normal((self.n, self.n))
        return z @ self.L / np.sqrt(max(self.n - 1, 1))

    def draw_scores(self, rng: np.random.Generator) -> np.ndarray:
        return _top3_scores(self.draw_raw(rng), rng)


class ClusterCentreNull:
    """(a) Cluster-centre null for prompt-template designs: concept means mu_c are redrawn as
    mbar + Z Mc / sqrt(n-1) (Z an n x n standard normal matrix, Mc the centred means), and every point keeps
    its own within-concept residual x_i - mu_{c_i}. All rows are first expressed in an orthonormal basis of
    their span (exact isometry), so each draw costs O(N n q) instead of O(N n D)."""

    def __init__(self, x: np.ndarray, groups: np.ndarray):
        x = np.asarray(x, dtype=np.float64)
        g = np.asarray(groups)
        self.labels, self.idx = np.unique(g, return_inverse=True)
        means = np.stack([x[self.idx == j].mean(0) for j in range(self.labels.size)])
        resid = x - means[self.idx]
        mc = means - means.mean(0)
        q, _ = np.linalg.qr(np.concatenate([mc, resid], 0).T)   # D x (n + N) orthonormal basis of the row span
        self.mc, self.resid = mc @ q, resid @ q                 # exact coordinates in that basis
        self.n = self.labels.size

    def draw_raw(self, rng: np.random.Generator) -> np.ndarray:
        z = rng.standard_normal((self.n, self.n))
        mu = z @ self.mc / np.sqrt(max(self.n - 1, 1))
        return mu[self.idx] + self.resid

    def draw_scores(self, rng: np.random.Generator) -> np.ndarray:
        return _top3_scores(self.draw_raw(rng), rng)


def cluster_centre_draw(x: np.ndarray, groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """One cluster-centre null cloud in the original coordinates (used by tests): means redrawn, residuals kept."""
    x = np.asarray(x, dtype=np.float64)
    g = np.asarray(groups)
    labels, idx = np.unique(g, return_inverse=True)
    means = np.stack([x[idx == j].mean(0) for j in range(labels.size)])
    mc = means - means.mean(0)
    z = rng.standard_normal((labels.size, labels.size))
    return (means.mean(0) + z @ mc / np.sqrt(labels.size - 1))[idx] + (x - means[idx])


def _chunk_max_ratios(sampler, seeds: list[np.random.SeedSequence], maxdim: int) -> np.ndarray:
    """Worker: max pi of H1..H_maxdim for each null draw seeded by its own SeedSequence (order-independent)."""
    out = np.ones((len(seeds), maxdim))
    with threadpool_limits(1):                                  # one BLAS thread per worker process
        for i, ss in enumerate(seeds):
            rng = np.random.default_rng(ss)
            y = rms_normalise(sampler.draw_scores(rng))
            dg = alpha_diagrams(y, maxdim=maxdim)
            out[i] = [max_ratio(dg[k]) for k in range(1, maxdim + 1)]
    return out


def make_sampler(x: np.ndarray, kind: str, groups: np.ndarray | None):
    """Sampler for null design 'gaussian' (b) or 'cluster' (a)."""
    if kind == "gaussian":
        return GaussianNull(x)
    if kind == "cluster":
        if groups is None:
            raise ValueError("cluster-centre null needs concept groups")
        return ClusterCentreNull(x, groups)
    raise ValueError(kind)


def null_max_ratios(x: np.ndarray, kind: str, groups: np.ndarray | None, m: int, seed: int,
                    maxdim: int = 2, n_jobs: int = -1) -> np.ndarray:
    """Null distribution of the maximum pi in H1..H_maxdim: array (m, maxdim).

    Each draw has its own child SeedSequence of SeedSequence(seed), so results do not depend on n_jobs.
    """
    sampler = make_sampler(x, kind, groups)
    seeds = np.random.SeedSequence(seed).spawn(m)
    n_chunks = max(1, min(m, 64))
    chunks = [seeds[i::n_chunks] for i in range(n_chunks)]
    if n_jobs == 1 or m <= 8:
        res = [_chunk_max_ratios(sampler, c, maxdim) for c in chunks]
    else:
        res = Parallel(n_jobs=n_jobs)(delayed(_chunk_max_ratios)(sampler, c, maxdim) for c in chunks)
    out = np.ones((m, maxdim))
    for i in range(n_chunks):
        out[i::n_chunks] = res[i]                               # undo the striding: draw j keeps seed j
    return out
