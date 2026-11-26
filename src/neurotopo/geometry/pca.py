"""Float64 NumPy implementation of the source study's single-cloud PCA convention.

The upstream PyTorch implementation centres the observations, projects onto leading principal
axes, fixes signs using skewness, restores a right-handed frame for a three-dimensional input,
and divides by the projected RMS radius. This code also accepts k for the projection checks.
Translation, orthogonal changes of basis and positive uniform scaling preserve the topology of
the represented set. Scaling changes filtration radii, and projection can change which holes
are detected. The source and replay can differ in floating-point rounding or the choice of
basis inside a repeated eigenspace.

Source: https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability/blob/4c5f3b665381380c81af22827bb3959032dac417/src/neurogeom/geometry/preprocess.py
The independent replay records observed ratios and null differences in results/science/null_replay.csv.
"""

from __future__ import annotations

import numpy as np


def fit_frame(x: np.ndarray, k: int = 3) -> tuple[np.ndarray, dict]:
    """Normalise one cloud x (N, D) to its top-k principal coordinates with RMS radius 1.

    Returns y (N, k) and a frame dict {mean (D,), basis (D, k), scale, eigvals (top 6), total_var}, with
    y = ((x - mean) @ basis) / scale, exactly as in the source's normalize_batch.
    """
    x = np.asarray(x, dtype=np.float64)
    n, d = x.shape
    mean = x.mean(0)                                    # centroid (source: masked mean, no padding here)
    xc = x - mean                                       # centred cloud
    if d <= 512:
        # Source branch for D <= 512: eigh of the population covariance in float64.
        cov = xc.T @ xc / n
        evals, evecs = np.linalg.eigh(cov)              # ascending eigenvalues
        evals, evecs = evals[::-1], evecs[:, ::-1]      # descending, as after torch's flip(-1)
    else:
        # Source branch for D > 512: SVD of the centred data (cheaper than a D x D eigh).
        _, s, vh = np.linalg.svd(xc, full_matrices=False)
        evals, evecs = s ** 2 / n, vh.T
    kk = min(k, d)
    basis = evecs[:, :kk].copy()
    if kk < k:                                          # degenerate D < k: pad with zero directions
        basis = np.concatenate([basis, np.zeros((d, k - kk))], 1)
    scores = xc @ basis
    # Skewness sign rule (source `_sign_fix`): sign of the third moment of each axis, ties -> +1.
    sgn = np.sign((scores ** 3).sum(0))
    sgn[sgn == 0] = 1.0
    scores, basis = scores * sgn, basis * sgn
    if d == 3 and k == 3:
        # Right-handed frame for 3D inputs (source: only when D == 3), so helix handedness is preserved.
        if np.dot(np.cross(basis[:, 0], basis[:, 1]), basis[:, 2]) < 0:
            basis[:, 2] *= -1.0
            scores[:, 2] *= -1.0
    scale = max(float(np.sqrt((scores ** 2).sum(1).mean())), 1e-12)   # RMS radius of the projected cloud
    y = scores / scale
    return y, {"mean": mean, "basis": basis, "scale": scale, "eigvals": evals[: min(6, d)].copy(),
               "total_var": float(evals.sum())}


def rms_normalise(y: np.ndarray) -> np.ndarray:
    """Centre and scale a low-dimensional cloud to RMS radius 1 (used for null draws, where rotations and
    sign flips are irrelevant to homology)."""
    y = np.asarray(y, dtype=np.float64)
    y = y - y.mean(0)
    return y / max(float(np.sqrt((y ** 2).sum(1).mean())), 1e-12)
