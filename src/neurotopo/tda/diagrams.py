"""Persistence diagrams: alpha complexes in R^3 (GUDHI) and Vietoris-Rips complexes (ripser.py).

Global context: Method B (reports/preregistration.md, section 4) measures the holes of a point cloud with
persistent homology. In R^3 the alpha complex has exactly the persistence of the Cech complex (union of
balls, nerve theorem) and no Rips "phantom" classes (de Silva & Ghrist 2007, doi:10.2140/agt.2007.7.339;
Adamaszek & Adams 2017, arXiv:1503.03669), so it is the primary complex for H0/H1/H2. Rips (ripser.py,
Tralie et al. 2018, doi:10.21105/joss.00925) is used for higher-dimensional checks and circular coordinates.
All diagrams are returned as lists [H0, H1, H2] of (n_k, 2) arrays (birth, death) in *radius* units.
"""

from __future__ import annotations

import gudhi
import numpy as np
from ripser import ripser


def alpha_diagrams(points: np.ndarray, maxdim: int = 2, precision: str = "safe") -> list[np.ndarray]:
    """Alpha-complex persistence diagrams H0..H_maxdim of a cloud in R^3, in radius units, over Z/2.

    GUDHI's AlphaComplex filtration values are *squared* radii (create_simplex_tree(output_squared_values=True)
    is the default; https://gudhi.inria.fr/python/latest/alpha_complex_user.html), so we take square roots.
    """
    pts = np.asarray(points, dtype=np.float64)
    st = gudhi.AlphaComplex(points=pts, precision=precision).create_simplex_tree()
    st.compute_persistence(homology_coeff_field=2, min_persistence=0.0)   # all bars, Z/2 coefficients
    out = []
    for k in range(maxdim + 1):
        iv = np.asarray(st.persistence_intervals_in_dimension(k), dtype=np.float64).reshape(-1, 2)
        iv = np.sqrt(np.clip(iv, 0.0, None))            # squared radius -> radius (inf stays inf)
        out.append(_drop_zero_length(iv))               # degenerate (co-circular) inputs create birth == death bars
    return out


def _drop_zero_length(iv: np.ndarray) -> np.ndarray:
    """Remove bars with death == birth (up to float tolerance); they carry no topology."""
    keep = (iv[:, 1] - iv[:, 0]) > 1e-12 * np.maximum(1.0, np.abs(iv[:, 0]))
    return iv[keep]


def rips_diagrams(x: np.ndarray, maxdim: int = 1, metric: str = "euclidean", coeff: int = 2,
                  distance_matrix: bool = False, n_perm: int | None = None) -> list[np.ndarray]:
    """Vietoris-Rips persistence diagrams via ripser.py, converted to radius units (ripser uses diameters).

    The Rips filtration value of an edge is the pairwise distance, i.e. twice the ball radius at which the
    balls touch; dividing by 2 makes Rips bars comparable to alpha (Cech) radii.
    """
    kw = {"maxdim": maxdim, "coeff": coeff, "distance_matrix": distance_matrix}
    if not distance_matrix:
        kw["metric"] = metric
    if n_perm is not None and n_perm < len(x):
        kw["n_perm"] = n_perm                           # greedy furthest-point subsampling (ripser.py option)
    res = ripser(np.asarray(x, dtype=np.float64), **kw)
    return [_drop_zero_length(np.asarray(d, dtype=np.float64).reshape(-1, 2) / 2.0) for d in res["dgms"]]


def ratios(dgm: np.ndarray) -> np.ndarray:
    """Multiplicative persistence pi = death / birth per bar (Bobrowski & Skraba 2023); NaN where undefined
    (birth == 0, i.e. H0 bars, or an infinite death)."""
    dgm = np.asarray(dgm, dtype=np.float64).reshape(-1, 2)
    b, d = dgm[:, 0], dgm[:, 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        pi = np.where((b > 0) & np.isfinite(d), d / b, np.nan)
    return pi


def max_ratio(dgm: np.ndarray) -> float:
    """Largest finite pi of a diagram; 1.0 (no persistence) if the diagram has no finite bar with birth > 0."""
    pi = ratios(dgm)
    pi = pi[np.isfinite(pi)]
    return float(pi.max()) if pi.size else 1.0


def alive_at(dgm: np.ndarray, r: float) -> np.ndarray:
    """Boolean mask of bars alive at scale r (birth <= r < death)."""
    dgm = np.asarray(dgm).reshape(-1, 2)
    return (dgm[:, 0] <= r) & (r < dgm[:, 1])
