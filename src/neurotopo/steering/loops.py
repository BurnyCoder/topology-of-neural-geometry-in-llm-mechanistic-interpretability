"""Closed steering paths around a detected hole, and the activation displacement that moves along them.

Global context: manifold steering (Wurgaft et al. 2026, arXiv:2605.05115, section 3: cubic splines through
concept centroids, pi_m(t) = s((1 - t) u0 + t u1)) moves activations along a fitted concept manifold. Here the
path is the loop that encircles a hole found by topology (preregistration amendment A2):
- Loop B (primary, fit-free): points ordered by their persistent-cohomology coordinate theta_B, averaged in
  equal-width theta_B bins in the top-3 PCA coordinates, and joined by a periodic cubic spline
  (scipy.interpolate.CubicSpline(bc_type="periodic")). No concept labels are used.
- Loop A: the fitted shape's own circle around its hole (cone frustum: the azimuth circle at the point's
  height; helix: the azimuth circle around the axis at the point's axial coordinate, descriptive).
- Controls: random loops (same centre and mean radius, random 2D plane in the top-k PC space) and linear
  chord paths through concept centroids (the linear-steering baseline of manifold steering).
A point is steered by moving its top-3 component along the loop by an angle Delta and keeping everything
else (the off-loop residual), h(Delta) = h + scale * (gamma(phi + Delta) - gamma(phi)) @ basis^T.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree

TWO_PI = 2 * np.pi


class Loop:
    """A closed curve gamma(phi), phi in [0, 2 pi), in some coordinate space, sampled densely for lookup."""

    def __init__(self, fn, n_dense: int = 4096):
        self.fn = fn
        self.phi = np.linspace(0, TWO_PI, n_dense, endpoint=False)
        self.pts = fn(self.phi)
        self.tree = cKDTree(self.pts)

    def __call__(self, phi: np.ndarray) -> np.ndarray:
        return self.fn(np.mod(phi, TWO_PI))

    def param(self, y: np.ndarray) -> np.ndarray:
        """Loop parameter of the nearest dense loop sample to each point."""
        return self.phi[self.tree.query(np.atleast_2d(y))[1]]

    def displacement(self, y: np.ndarray, delta: float) -> np.ndarray:
        """gamma(phi(y) + Delta) - gamma(phi(y)) for each point (same coordinates as the loop)."""
        p = self.param(y)
        return self(p + delta) - self(p)

    @property
    def radius(self) -> float:
        return float(np.linalg.norm(self.pts - self.pts.mean(0), axis=1).mean())


def loop_from_coordinate(y: np.ndarray, theta: np.ndarray, n_bins: int) -> Loop:
    """Loop B: mean of the points in n_bins equal-width bins of a circle-valued coordinate theta, joined by a
    periodic cubic spline in the coordinates of y. Empty bins are skipped (the spline knots stay ordered)."""
    t = np.mod(theta, TWO_PI)
    edges = np.linspace(0, TWO_PI, n_bins + 1)
    idx = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, n_bins - 1)
    knots, means = [], []
    for b in range(n_bins):
        m = idx == b
        if m.any():
            knots.append(np.angle(np.exp(1j * t[m]).mean()) % TWO_PI)    # circular mean angle of the bin
            means.append(y[m].mean(0))
    order = np.argsort(knots)
    k, mu = np.asarray(knots)[order], np.asarray(means)[order]
    k = np.r_[k, k[0] + TWO_PI]                                          # periodic: repeat the first knot
    mu = np.r_[mu, mu[:1]]
    cs = CubicSpline(k, mu, bc_type="periodic")
    return Loop(lambda phi: cs(np.where(phi < k[0], phi + TWO_PI, phi)))


def azimuth_loop(center: np.ndarray, axes: np.ndarray, radius_fn, height: float) -> Loop:
    """Loop A for an axially symmetric fit (cone, helix): circle around the axis e3 at axial height `height`,
    radius radius_fn(height); axes rows (e1, e2, e3) as in the source's describe() (world = c + local @ axes)."""
    c, ax = np.asarray(center, float), np.asarray(axes, float)
    r = float(radius_fn(height))
    return Loop(lambda phi: c + np.c_[r * np.cos(phi), r * np.sin(phi), np.full_like(phi, height)] @ ax)


def random_loop(center: np.ndarray, radius: float, basis_k: np.ndarray, rng: np.random.Generator) -> tuple[Loop, np.ndarray]:
    """Random control: circle of the given radius around `center` in a uniformly random 2D plane of the
    top-k PC space (basis_k: k x k identity for normalised top-k coordinates). Returns the loop in top-k
    coordinates and the plane (2 x k)."""
    q, _ = np.linalg.qr(rng.normal(size=(basis_k.shape[0], 2)))
    plane = (basis_k @ q).T                                              # 2 x k orthonormal rows
    c = np.asarray(center, float)
    return Loop(lambda phi: c + radius * (np.c_[np.cos(phi), np.sin(phi)] @ plane)), plane


def chord_path(centroids: np.ndarray) -> Loop:
    """Linear-steering baseline: the closed polygon through ordered concept centroids, parametrised by
    phi = 2 pi c / n at centroid c (straight segments in between)."""
    cen = np.asarray(centroids, float)
    n = len(cen)

    def fn(phi):
        s = np.mod(phi, TWO_PI) * n / TWO_PI
        i = np.floor(s).astype(int) % n
        f = (s - np.floor(s))[:, None]
        return (1 - f) * cen[i] + f * cen[(i + 1) % n]
    return Loop(fn)
