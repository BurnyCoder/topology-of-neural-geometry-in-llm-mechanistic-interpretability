"""Betti-number estimators of Method B applied to one normalised 3D cloud (used by Exp1, Exp2 and tuning).

Global context: H5 (reports/preregistration.md, section 6) compares estimators of (b0, b1, b2) against the
registered catalog targets of synthetic clouds:
- the preregistered primary estimator: alpha diagrams + universal null (A = 1/2), b0 by single linkage;
- the secondary estimator added in reports/deviations.md D1: Rips H1 + universal null (A = 1);
- a fixed-pi-threshold baseline (count bars with pi > pi0_k, pi0 tuned on the validation stream);
- a Monte Carlo 3D matched-Gaussian null (on the baseline subset).
`summarize` computes everything an estimator needs once per cloud, so tuning and evaluation reuse it.
"""

from __future__ import annotations

import numpy as np

from neurotopo.tda import diagrams, invariants, nulls
from neurotopo.geometry.pca import rms_normalise


def summarize(points: np.ndarray, tau_grid, minfrac_grid, rips: bool = True, top: int = 12) -> dict:
    """Per-cloud statistics: universal-null counts (alpha H1/H2, Rips H1), top pi values per dimension,
    b0 for every (tau, min_frac) grid point."""
    y = rms_normalise(points)
    d = diagrams.alpha_diagrams(y)
    out = {"n": len(y)}
    for k in (1, 2):
        out[f"b{k}_alpha_univ"] = int(nulls.universal_significant(d[k], A=0.5).sum())
        pi = np.sort(diagrams.ratios(d[k]))[::-1]
        pi = pi[np.isfinite(pi)][:top]
        out[f"pi{k}_top"] = np.r_[pi, np.ones(top - pi.size)].tolist()        # padded with 1 (no bar)
    if rips:
        dr = diagrams.rips_diagrams(y, maxdim=1)
        out["b1_rips_univ"] = int(nulls.universal_significant(dr[1], A=1.0).sum())
    out["b0_grid"] = invariants.b0_grid(y, tau_grid, minfrac_grid)
    return out


def gaussian3d_null_max(points: np.ndarray, m: int, seed: int) -> np.ndarray:
    """Null distribution (m, 2) of max pi in H1/H2 for 3D Gaussian clouds with the cloud's covariance and N
    (synthetic clouds are only available in 3D, so the matched Gaussian is drawn in 3D)."""
    y = rms_normalise(points)
    cov = np.cov(y, rowvar=False)
    rng = np.random.default_rng(seed)
    out = np.ones((m, 2))
    for j in range(m):
        z = rms_normalise(rng.multivariate_normal(np.zeros(3), cov, size=len(y)))
        dg = diagrams.alpha_diagrams(z)
        out[j] = [diagrams.max_ratio(dg[1]), diagrams.max_ratio(dg[2])]
    return out


def mc_counts(points: np.ndarray, null_max: np.ndarray, alpha: float = 0.05) -> tuple[int, int]:
    """Number of H1 / H2 bars whose Monte Carlo p-value against the max-pi null is below alpha."""
    d = diagrams.alpha_diagrams(rms_normalise(points))
    return tuple(int((nulls.mc_pvalues(diagrams.ratios(d[k]), null_max[:, k - 1]) < alpha).sum()) for k in (1, 2))
