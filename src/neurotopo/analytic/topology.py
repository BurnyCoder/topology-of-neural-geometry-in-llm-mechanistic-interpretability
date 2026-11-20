"""Method A: exact topology of a uniquely parametrised shape from the source's 13 families.

Global context: the source fitter returns, per cloud, one of 13 shape families with canonical parameters
(`describe()` in external/shape-fitting/src/neurogeom/shapes/*.py). Each family is a known topological
space whose homology is textbook material (Hatcher, Algebraic Topology, 2002,
https://pi.math.cornell.edu/~hatcher/AT/AT.pdf: contractible spaces, S^1, S^2, T^2, finite point sets),
and compact orientable surfaces with boundary satisfy chi = 2 - 2g - n_boundary. So Betti numbers,
Euler characteristic, genus and boundary components follow exactly from family + parameters. The
"margin" is the length of the smallest parameter change that changes the topology (e.g. closing an arc's
gap, collapsing a torus tube); divided by the cloud's noise scale it says whether the fitted topology is
resolvable from the data (reports/preregistration.md, section 3).
"""

from __future__ import annotations

import math

import numpy as np

ARC_FULL = 0.98          # source Arc.FULL: extent fraction above which the arc is a closed circle (curves.py:62)
SPHERE_FULL = 0.98       # source Sphere.FULL: cap fraction above which the sphere is closed (surfaces.py)
INF = float("inf")


def _result(b0, b1, b2, dim, homotopy, margin, n_boundary=0, genus=None, manifold=True, note=""):
    """Assemble the invariants; chi = b0 - b1 + b2 always (Euler-Poincare formula)."""
    return {"b0": int(b0), "b1": int(b1), "b2": int(b2), "chi": int(b0 - b1 + b2), "genus": genus,
            "n_boundary": n_boundary, "orientable": True, "dim": dim, "manifold": manifold,
            "homotopy": homotopy, "margin": float(margin), "note": note}


def _min_pairwise(points) -> float:
    """Smallest distance between two distinct points (inf for fewer than 2 points)."""
    p = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    if len(p) < 2:
        return INF
    d = np.linalg.norm(p[:, None] - p[None], axis=-1)
    return float(d[np.triu_indices(len(p), 1)].min())


def shape_topology(family: str, params: dict) -> dict:
    """Exact invariants of a fitted (or ground-truth) shape given its canonical describe() parameters.

    Returns b0, b1, b2, chi, genus (closed or bordered orientable surfaces; None otherwise), n_boundary
    (boundary circles of a surface, or endpoints of a curve), orientable, dim, manifold, homotopy class,
    and margin (in the parameters' length units).
    """
    p = params
    if family == "blob":
        # Gaussian null class: any level set (solid ellipsoid) is contractible; no topology change is near.
        return _result(1, 0, 0, 3, "point", INF)
    if family == "clusters":
        # k Gaussian balls: k contractible components; two merge when centroids come within ~2 sigma each.
        k = int(p["k"])
        return _result(k, 0, 0, 3, f"{k} points", _min_pairwise(p["centroids"]) - 4 * float(p["spread"]))
    if family == "polytope":
        # Vertex set of a polytope template (source Polytope family): V isolated points (+ small spread).
        v = np.asarray(p["vertices"]).reshape(-1, 3)
        return _result(len(v), 0, 0, 0, f"{len(v)} points", _min_pairwise(v) - 4 * float(p["spread"]),
                       note="template surface would be a 2-sphere")
    if family == "line":
        # Segment: contractible curve with 2 endpoints; closing it needs its endpoints to meet.
        return _result(1, 0, 0, 1, "point", 2 * float(p["half_length"]), n_boundary=2)
    if family == "arc":
        r = float(p["radius"])
        if bool(p.get("closed", False)):
            # Closed circle S^1 (b1 = 1, chi = 0); the hole disappears when the radius shrinks to 0.
            return _result(1, 1, 0, 1, "circle", 2 * r)
        frac = float(p["extent_rad"]) / (2 * math.pi)
        # Open arc: contractible; it closes when its endpoint gap 2 r sin(pi (1 - frac)) reaches 0.
        return _result(1, 0, 0, 1, "point", 2 * r * math.sin(math.pi * (1 - frac)), n_boundary=2)
    if family == "ellipse":
        # Closed ellipse = S^1; the hole collapses when the minor axis 2b reaches 0.
        return _result(1, 1, 0, 1, "circle", 2 * float(p["b"]))
    if family == "helix":
        r, h, turns = float(p["radius"]), float(p["pitch"]), float(p["turns"])
        # Endpoints at t = +-pi*turns of c + r cos t e1 + r sin t e2 + h t / (2 pi) e3 (source curves.py:154).
        t = math.pi * turns
        a = np.array([r * math.cos(t), r * math.sin(t), h * t / (2 * math.pi)])
        b = np.array([r * math.cos(-t), r * math.sin(-t), -h * t / (2 * math.pi)])
        m = float(np.linalg.norm(a - b))
        if turns > 1:
            m = min(m, abs(h))           # adjacent turns touching would turn the curve into a tube (b1 = 1)
        return _result(1, 0, 0, 1, "point", m, n_boundary=2)
    if family == "ringing":
        # c + sum_k a_k cos(k pi s) e_k on s in [0, 1] (source curves.py: Ringing.local); cos(pi s) is injective,
        # so the curve is embedded; endpoints s = 0, 1 differ by (2 a1, 0, 2 a3).
        return _result(1, 0, 0, 1, "point", 2 * math.hypot(float(p["a1"]), float(p["a3"])), n_boundary=2)
    if family in ("disc", "paraboloid"):
        # Filled ellipse / quadric patch over a disc: a disc (contractible, one boundary circle, genus 0).
        return _result(1, 0, 0, 2, "point", INF, n_boundary=1, genus=0)
    if family == "sphere":
        r = float(p["radius"])
        if bool(p.get("closed", False)):
            # Closed sphere S^2: b2 = 1 (one enclosed void), chi = 2, genus 0.
            return _result(1, 0, 1, 2, "sphere", 2 * r, genus=0)
        alpha = float(p["cap_half_angle_rad"])
        # Polar cap: a disc; it closes into a sphere when its opening 2 r sin(alpha) shrinks to 0.
        return _result(1, 0, 0, 2, "point", 2 * r * math.sin(max(alpha, math.pi / 2)), n_boundary=1, genus=0)
    if family == "cone":
        r_bot = float(p["r_bot"])
        if r_bot > 0:
            # Lateral surface of a frustum (r_top = r_bot + dr >= r_bot > 0): an annulus, two boundary circles,
            # b1 = 1 (the loop around the axis); the hole closes when the narrow end shrinks to a point.
            return _result(1, 1, 0, 2, "circle", 2 * r_bot, n_boundary=2, genus=0)
        # Apex at r_bot = 0: a cone surface is a disc (one boundary circle); margin 0 by definition.
        return _result(1, 0, 0, 2, "point", 0.0, n_boundary=1, genus=0)
    if family == "torus":
        big = float(p["R"])
        small = big * float(p["ratio"])
        if small < big:
            # Ring torus T^2: (1, 2, 1), chi = 0, genus 1; changes when the tube collapses (r -> 0) or the
            # central hole closes (r -> R, horn torus).
            return _result(1, 2, 1, 2, "torus", min(2 * small, 2 * (big - small)), genus=1)
        if small == big:
            # Horn torus: the torus with one longitude pinched to a point; attaching a disc along an essential
            # circle of T^2 gives S^2 v S^1 (not a manifold at the centre).
            return _result(1, 1, 1, 2, "sphere v circle", 0.0, manifold=False)
        # Spindle torus (r > R): the generating circle crosses the axis, so the image is an outer "apple" and an
        # inner "lemon", each a 2-sphere, glued at the two axis points: S^2 v S^2 v S^1, (1, 1, 2), chi = 2. By
        # Alexander duality its two bounded complementary regions are its two voids (Hatcher 2002, Thm 3.44).
        return _result(1, 1, 2, 2, "sphere v sphere v circle (self-intersecting spindle torus)", 0.0, manifold=False,
                       note="source caps ratio <= 0.95, so this does not occur")
    raise ValueError(f"unknown family {family!r}")


def has_hole(t: dict) -> bool:
    """A 1-cycle you can travel around exists in the fitted shape (b1 >= 1)."""
    return t["b1"] >= 1
