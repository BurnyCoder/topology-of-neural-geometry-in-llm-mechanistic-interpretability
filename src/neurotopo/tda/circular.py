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
                         cocycle_idx: int = 0) -> dict:
    """theta_B (N,) for the most persistent Rips cohomology class, plus that class's (birth, death) in radius
    units for comparison with the alpha H1 bar. DREiMac's diagrams are Rips diameters, hence the / 2."""
    pts = np.asarray(points, dtype=np.float64)
    n_land = int(min(len(pts), max_landmarks))
    cc = CircularCoords(pts, n_landmarks=n_land, prime=prime, maxdim=1)
    dgm1 = np.asarray(cc.dgms_[1]) if hasattr(cc, "dgms_") else np.zeros((0, 2))
    try:
        theta = cc.get_coordinates(perc=perc, cocycle_idx=cocycle_idx, standard_range=True)
    except Exception as exc:  # DREiMac: "The cohomology class selected is too short" (or no H1 class at all)
        # With standard_range=True DREiMac only builds coordinates for a class that persists past twice the
        # landmark cover radius, i.e. that is non-trivial in the Cech complex used; otherwise there is no
        # usable loop and the traversal test counts as failed (reports/deviations.md D3).
        return {"theta": None, "bar": None, "n_landmarks": n_land, "error": str(exc)[:120]}
    bar = None
    if dgm1.size:
        order = np.argsort(dgm1[:, 0] - dgm1[:, 1])                  # most persistent first (DREiMac ordering)
        bar = (dgm1[order[cocycle_idx]] / 2.0).tolist()
    return {"theta": np.asarray(theta, dtype=np.float64), "bar": bar, "n_landmarks": n_land, "error": None}
