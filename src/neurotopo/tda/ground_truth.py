"""Noise-and-coverage scale of a cloud relative to a shape, and resolvability of the shape's topology.

Global context: an exact topology (Method A) is only observable in data if the smallest parameter change
that would alter it (the margin m) is large compared with the cloud's noise and sampling gaps. The
preregistration (section 3) defines
    nu = median(distance from each data point to the shape) + q95(distance from each shape sample to its
         nearest data point),
the first term measuring noise, the second the largest coverage gaps, and calls the topology resolvable when
rho_A = m / (2 nu) >= 1. The same definition is used for real clouds (shape = fitted shape) and synthetic
clouds (shape = noise-free ground truth), so Exp1's "resolvable" subset and the real data's margin ratios
are comparable.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree


def noise_scale(points: np.ndarray, shape_samples: np.ndarray, point_to_shape: np.ndarray | None = None) -> dict:
    """nu and its two terms. point_to_shape: optional exact point-to-shape distances (e.g. from a fine
    parameter grid); otherwise distances to the nearest shape sample are used."""
    pts = np.asarray(points, dtype=np.float64)
    shp = np.asarray(shape_samples, dtype=np.float64)
    d_ps = point_to_shape if point_to_shape is not None else cKDTree(shp).query(pts)[0]
    d_sp = cKDTree(pts).query(shp)[0]
    med, q95 = float(np.median(d_ps)), float(np.quantile(d_sp, 0.95))
    return {"nu": med + q95, "noise": med, "coverage": q95}


def margin_ratio(margin: float, nu: float) -> float:
    """rho_A = m / (2 nu); inf for shapes whose topology cannot change (blob, disc, paraboloid)."""
    if not np.isfinite(margin):
        return float("inf")
    return float(margin / (2 * nu)) if nu > 0 else float("inf")
