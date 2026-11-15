"""Parametrisations of the source's shape families and intrinsic (hole) coordinates of points on a fit.

Global context: the travel-around-the-hole test needs, for every data point, a circle-valued coordinate
theta that goes once around the hole. For Method A this coordinate is read off the fitted shape itself:
each point gets the parameter of its nearest point on the shape (reports/preregistration.md, section 3).
The formulas are the source's `local()` parametrisations (external/shape-fitting/src/neurogeom/shapes/
curves.py and surfaces.py), re-implemented in numpy, mapped to the world frame exactly as the source's
`ShapeFamily.points` does (world = center + local @ rot^T, and describe() reports axes = rot^T, so
world = center + local @ axes; shapes/base.py:150-156).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.spatial import cKDTree

TWO_PI = 2 * math.pi


def frame_from_axis(e3: np.ndarray) -> np.ndarray:
    """Right-handed frame (rows e1, e2, e3) with the given third axis; e1 = projection of the x-axis (or the
    y-axis if e3 is nearly parallel to x) onto the plane orthogonal to e3, as in the source's frame_from_axis.
    Only used where the shape is rotationally symmetric about e3, so the choice of e1 is immaterial."""
    e3 = np.asarray(e3, dtype=np.float64)
    e3 = e3 / np.linalg.norm(e3)
    ref = np.array([1.0, 0, 0]) if abs(e3[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = ref - np.dot(ref, e3) * e3
    e1 /= np.linalg.norm(e1)
    return np.stack([e1, np.cross(e3, e1), e3])


def frame(family: str, p: dict) -> tuple[np.ndarray, np.ndarray]:
    """Centre (3,) and frame rows (3, 3) = (e1, e2, e3) of a shape from its describe() parameters."""
    c = np.asarray(p.get("center", [0, 0, 0]), dtype=np.float64)
    if family == "arc":
        e3 = np.asarray(p["normal"], dtype=np.float64)
        if p.get("bisector") is not None:                # open arc: e1 bisects the arc (source Arc docstring)
            e1 = np.asarray(p["bisector"], dtype=np.float64)
            return c, np.stack([e1, np.cross(e3, e1), e3])
        return c, frame_from_axis(e3)                     # closed circle: any in-plane e1
    if family == "ellipse":
        e3, e1 = np.asarray(p["normal"], float), np.asarray(p["major_axis"], float)
        return c, np.stack([e1, np.cross(e3, e1), e3])
    if family == "sphere":
        return c, (frame_from_axis(p["pole"]) if p.get("pole") is not None else np.eye(3))
    if family == "line":
        f = frame_from_axis(p["direction"])               # rows (a, b, direction); the segment runs along e1
        return c, np.stack([f[2], f[0], f[1]])
    return c, np.asarray(p["axes"], dtype=np.float64)    # rows e1, e2, e3 (describe: axes = rot^T)


def _local(family: str, p: dict, u: np.ndarray, v: np.ndarray | None) -> tuple[np.ndarray, dict]:
    """Local-frame points of a family at parameters u (curves) or (u, v) (surfaces), plus named parameters."""
    if family == "arc":
        ext = TWO_PI if p.get("closed") else float(p["extent_rad"])
        t = ext * (u - 0.5) if not p.get("closed") else TWO_PI * u   # source: t = 2 pi frac (u - 1/2)
        r = float(p["radius"])
        return np.c_[r * np.cos(t), r * np.sin(t), 0 * t], {"theta": t}
    if family == "ellipse":
        t = TWO_PI * u
        a, b = float(p["a"]), float(p["b"])
        return np.c_[a * np.cos(t), b * np.sin(t), 0 * t], {"theta": t}
    if family == "helix":
        turns, r, h = float(p["turns"]), float(p["radius"]), float(p["pitch"])
        t = math.pi * turns * (2 * u - 1)                 # source: t in [-pi turns, pi turns]
        return np.c_[r * np.cos(t), r * np.sin(t), h * t / TWO_PI], {"t": t, "theta": np.angle(np.exp(1j * t)),
                                                                     "axial": h * t / TWO_PI}
    if family == "ringing":
        a1, a2, a3 = (float(p[k]) for k in ("a1", "a2", "a3"))
        return np.c_[a1 * np.cos(math.pi * u), a2 * np.cos(TWO_PI * u), a3 * np.cos(3 * math.pi * u)], {"s": u}
    if family == "line":
        return np.c_[float(p["half_length"]) * (2 * u - 1), 0 * u, 0 * u], {"s": u}
    if family == "cone":
        ph, s = TWO_PI * u, v                              # source: r(s) = r_bot + dr s, height hh (2 s - 1)
        r = float(p["r_bot"]) + float(p["dr"]) * s
        return np.c_[r * np.cos(ph), r * np.sin(ph), float(p["half_height"]) * (2 * s - 1)], {"theta": ph, "height": s}
    if family == "torus":
        a, b = TWO_PI * u, TWO_PI * v                      # source: ((R + r cos v) cos u, (R + r cos v) sin u, r sin v)
        big = float(p["R"])
        small = big * float(p["ratio"])
        ring = big + small * np.cos(b)
        return np.c_[ring * np.cos(a), ring * np.sin(a), small * np.sin(b)], {"theta": a, "theta2": b}
    if family == "sphere":
        alpha = math.pi if p.get("closed") else float(p["cap_half_angle_rad"])
        z = 1 - (1 - math.cos(alpha)) * u                  # source: uniform in z (Archimedes)
        sxy = np.sqrt(np.clip(1 - z * z, 0, None))
        ph = TWO_PI * v
        r = float(p["radius"])
        return np.c_[r * sxy * np.cos(ph), r * sxy * np.sin(ph), r * z], {"theta": ph, "height": z}
    if family == "disc":
        rho, t = np.sqrt(u), TWO_PI * v
        a = float(p["a"])
        b = a * float(p["ratio"]) if "ratio" in p else float(p["b"])
        return np.c_[a * rho * np.cos(t), b * rho * np.sin(t), 0 * t], {}
    if family == "paraboloid":
        rr, t = float(p["rho"]) * np.sqrt(u), TWO_PI * v
        x, y = rr * np.cos(t), rr * np.sin(t)
        k1 = float(p["k1"])
        k2 = k1 * float(p["k_ratio"])
        return np.c_[x, y, 0.5 * (k1 * x * x + k2 * y * y)], {}
    raise ValueError(f"no parametrisation for {family!r}")


SURFACES = {"cone", "torus", "sphere", "disc", "paraboloid"}


def parameter_grid(family: str, p: dict, curve_n: int = 4096, surface_n: int = 256) -> dict:
    """Dense world-frame samples of a shape on a regular parameter grid, with the parameter of every sample."""
    if family in SURFACES:
        uu, vv = np.meshgrid((np.arange(surface_n) + 0.5) / surface_n, (np.arange(surface_n) + 0.5) / surface_n,
                             indexing="ij")
        loc, named = _local(family, p, uu.ravel(), vv.ravel())
    else:
        u = np.linspace(0.0, 1.0, curve_n, endpoint=family not in ("ellipse",) and not (family == "arc" and p.get("closed")))
        loc, named = _local(family, p, u, None)
    c, ax = frame(family, p)
    out = {"points": c + loc @ ax}                         # world = center + local @ axes
    out.update(named)
    return out


def dense_samples(family: str, p: dict, n: int = 4000) -> np.ndarray:
    """About n dense noise-free world-frame samples on a regular parameter grid (for coverage checks)."""
    side = int(math.ceil(math.sqrt(n)))
    return parameter_grid(family, p, curve_n=n, surface_n=side)["points"]


def _area_weight(family: str, p: dict, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Area element of the parametrisation up to a constant (source `local()` weights): the sphere and disc
    parametrisations are already area-uniform; the cone's element is r(s), the torus's R + r cos v."""
    if family == "cone":
        return float(p["r_bot"]) + float(p["dr"]) * v + 1e-9
    if family == "torus":
        return float(p["R"]) * (1 + float(p["ratio"]) * np.cos(TWO_PI * v))
    return np.ones_like(u)


def random_samples(family: str, p: dict, n: int, seed: int = 0) -> np.ndarray:
    """n noise-free samples uniform in arc length / area (rejection on the area element), world frame.

    Regular parameter grids create anisotropic cells whose alpha complexes have long spurious H1 bars
    (pi ~ 4 on a torus grid, ~17 near a sphere grid's poles), so persistence checks use random samples.
    """
    rng = np.random.default_rng(seed)
    if family not in SURFACES:
        g = parameter_grid(family, p, curve_n=max(20 * n, 20000))
        pts = g["points"]
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)          # arc-length element of the fine grid
        w = np.r_[seg, seg[-1]] + 1e-12
        return pts[rng.choice(len(pts), n, replace=True, p=w / w.sum())]
    out = []
    while sum(len(o) for o in out) < n:
        u, v = rng.uniform(size=4 * n), rng.uniform(size=4 * n)
        w = _area_weight(family, p, u, v)
        keep = rng.uniform(size=w.size) * w.max() < w
        loc, _ = _local(family, p, u[keep], v[keep])
        out.append(loc)
    c, ax = frame(family, p)
    return c + np.concatenate(out)[:n] @ ax


def intrinsic_coords(family: str, p: dict, points: np.ndarray, curve_n: int = 4096, surface_n: int = 256) -> dict:
    """Parameters of the nearest grid point on the fitted shape for every data point (theta_A etc.).

    Returns the named parameters of the nearest sample (e.g. 'theta' for the hole angle, 'theta2' for a torus
    meridian, 't' and 'axial' for a helix) and 'dist', the point-to-shape distance.
    """
    grid = parameter_grid(family, p, curve_n, surface_n)
    dist, idx = cKDTree(grid["points"]).query(np.asarray(points, dtype=np.float64))
    out = {k: v[idx] for k, v in grid.items() if k != "points"}
    out["dist"] = dist
    return out
