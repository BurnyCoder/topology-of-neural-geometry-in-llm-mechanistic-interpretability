"""PCA normalisation identical to the source project's `fit_frame` (numpy, float64).

Global context: the source project (`external/shape-fitting/src/neurogeom/geometry/preprocess.py`,
`normalize_batch`) maps every activation cloud to "top-3 PCA coordinates": centre -> project on the top-3
eigenvectors of the covariance -> flip each axis so its skewness is >= 0 -> for D == 3 force a right-handed
frame -> divide by the RMS radius. Topology is invariant to all of these steps except the projection, but
re-implementing them exactly lets us (i) check bit-for-bit that our clouds equal the source's stored clouds
and (ii) push every null draw through exactly the same pipeline. `k` generalises to the top-k PCs used by
the robustness checks (top-5/top-10).
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
