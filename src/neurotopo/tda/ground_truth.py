"""Noise-and-coverage scale of a cloud relative to a shape, and resolvability of the shape's topology.

Method A compares a family-specific feature-size proxy m with twice a sampled noise-and-coverage
scale. The registered cutoff is a heuristic eligibility criterion. Proposition 3.1 of
Niyogi, Smale & Weinberger requires a dense sample from a submanifold with a reach bound
(https://doi.org/10.1007/s00454-008-9053-2). We do not estimate reach. For real data the
distance reference is a sampled fit. For synthetic data it is the recorded noise-free design.
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


def far_points(points: np.ndarray, shape_samples: np.ndarray, factor: float) -> int:
    """Number of points farther from the shape than `factor` x the cloud's median point-to-shape distance.

    Outlier proxy of deviation D7: the source generator replaces a random fraction of points by uniform draws
    from the padded bounding box (neurogeom/data/nuisance.py::add_outliers) but does not store which ones.
    This distance proxy depends on shape sampling, dimension and cloud size. Either false flags
    or missed injections are possible. The exported data contain no per-point injection truth.
    """
    d = cKDTree(np.asarray(shape_samples, dtype=np.float64)).query(np.asarray(points, dtype=np.float64))[0]
    return int((d > factor * np.median(d)).sum())
