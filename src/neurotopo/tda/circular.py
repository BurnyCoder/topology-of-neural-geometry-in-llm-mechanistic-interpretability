"""Method B hole coordinate theta_B: circular coordinates from persistent cohomology (DREiMac).

Global context: de Silva, Morozov & Vejdemo-Johansson (2011, doi:10.1007/s00454-011-9344-x) turn a persistent
cohomology class into a circle-valued map theta: X -> S^1 that goes once around the corresponding hole.
DREiMac (Perea, Scoccola & Tralie, JOSS 2023, doi:10.21105/joss.05791; github.com/scikit-tda/DREiMac) implements
sparse circular coordinates on landmarks. The traversal test (stats/circular.py) then asks whether concepts
sit around theta_B in their semantic order. Parameters are fixed by the preregistration (section 4.6):
prime 47, n_landmarks = min(N, 200), perc = 0.5, cocycle_idx = 0 (most persistent class).
"""

from __future__ import annotations

import numpy as np
from dreimac import CircularCoords


def circular_coordinates(points: np.ndarray, prime: int = 47, max_landmarks: int = 200, perc: float = 0.5,
                         cocycle_idx: int = 0, standard_range: bool = True) -> dict:
    """theta_B (N,) for the most persistent Rips cohomology class, plus that class's (birth, death) in radius
    units for comparison with the alpha H1 bar. DREiMac's diagrams are Rips diameters, hence the / 2."""
    pts = np.asarray(points, dtype=np.float64)
    n_land = int(min(len(pts), max_landmarks))
    cc = CircularCoords(pts, n_landmarks=n_land, prime=prime, maxdim=1)
    dgm1 = np.asarray(cc.dgms_[1]) if hasattr(cc, "dgms_") else np.zeros((0, 2))
    if dgm1.size == 0:                                   # no H1 class at all (DREiMac would raise IndexError)
        return {"theta": None, "bar": None, "n_landmarks": n_land, "error": "no H1 class"}
    try:
        # standard_range=True (preregistered) requires Rips death >= 2 x birth (DREiMac EMCoords.get_cover_radius),
        # which guarantees the class is non-trivial in the Cech complex; False only guarantees it in the Rips complex.
        theta = cc.get_coordinates(perc=perc, cocycle_idx=cocycle_idx, standard_range=standard_range)
    except Exception as exc:
        # Only DREiMac's "class too short" refusal means "no usable loop" (deviations D3); anything else is a bug.
        if "too short" not in str(exc):
            raise
        return {"theta": None, "bar": None, "n_landmarks": n_land, "error": str(exc)[:120]}
    bar = None
    if dgm1.size:
        order = np.argsort(dgm1[:, 0] - dgm1[:, 1])                  # most persistent first (DREiMac ordering)
        bar = (dgm1[order[cocycle_idx]] / 2.0).tolist()
    return {"theta": np.asarray(theta, dtype=np.float64), "bar": bar, "n_landmarks": n_land, "error": None}
