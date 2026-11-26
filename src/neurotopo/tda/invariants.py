"""Method B invariants: b0 by single linkage, persistent Betti counts, characteristic scale, chi and genus.

Global context: from a persistence diagram and a significance mask we report (reports/preregistration.md,
section 4.4-4.5): persistent counts b_k^pers (number of significant bars), Betti numbers at one stated scale
r_c, the genus only for closed surfaces (b0 = 1, b2 = 1; chi = 2 - 2g), and a Betti-number label.
- All three Betti numbers are read off the alpha complex at the same radius r_c: b0 = its components (single
  linkage at edge length 2 r_c, with the same minimum component size as the b0 rule), b1 / b2 = significant bars
  alive at r_c. Before the math fact-check (deviation D12) b0 came from the b0 rule's own cut, a different scale.
- b1(r_c) and b2(r_c) count significant bars only, so chi(r_c) = b0 - b1 + b2 is the Euler characteristic of the
  signal Betti numbers, not of the full alpha complex at r_c (which also holds the noise bars alive there).
- Betti numbers do not determine a homotopy type (the torus and S^2 v S^1 v S^1 are both (1, 2, 1); (1, 0, 0) is
  acyclic, which is weaker than contractible), so the label says "acyclic", "circle-like", "sphere-like", ...
  Homotopy-equivalent spaces (circle, annulus, solid torus) cannot be told apart by any homotopy invariant.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.sparse.csgraph import connected_components, minimum_spanning_tree
from scipy.spatial import Delaunay
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import coo_matrix


def mst_edges(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Euclidean minimum spanning tree: (edge lengths, (i, j) pairs). The MST is a subgraph of the Delaunay
    graph, so for N > 1000 in 3D we build it on Delaunay edges; small clouds use the full distance matrix."""
    p = np.asarray(points, dtype=np.float64)
    n = len(p)
    if n < 2:
        return np.zeros(0), np.zeros((0, 2), dtype=int)
    if n <= 1000 or p.shape[1] != 3:
        g = minimum_spanning_tree(squareform(pdist(p)) + 0.0)
    else:
        tri = Delaunay(p)
        e = np.concatenate([tri.simplices[:, [a, b]] for a in range(4) for b in range(a + 1, 4)])
        e = np.unique(np.sort(e, axis=1), axis=0)
        w = np.linalg.norm(p[e[:, 0]] - p[e[:, 1]], axis=1)
        g = minimum_spanning_tree(coo_matrix((w, (e[:, 0], e[:, 1])), shape=(n, n)).tocsr())
    g = g.tocoo()
    return g.data, np.c_[g.row, g.col]


def _components(w: np.ndarray, ij: np.ndarray, n: int, thr: float, min_frac: float) -> int:
    """Components of the MST graph restricted to edges of length <= thr, counting only components with at least
    max(1, ceil(min_frac * N)) points (outliers must not count). Cutting the MST gives the same components as
    cutting the full graph (single linkage)."""
    keep = w <= thr
    g = coo_matrix((np.ones(int(keep.sum())), (ij[keep, 0], ij[keep, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    return int((np.bincount(lab) >= max(1, math.ceil(min_frac * n))).sum())


def b0_from_mst(w: np.ndarray, ij: np.ndarray, n: int, tau: float, min_frac: float) -> tuple[int, float]:
    """The preregistered b0 rule: components after cutting MST edges longer than tau * median MST edge, with the
    minimum component size; returns (b0, threshold edge length)."""
    if w.size == 0:
        return int(n), 0.0
    thr = tau * float(np.median(w))
    return _components(w, ij, n, thr, min_frac), thr


def b0_at_radius(w: np.ndarray, ij: np.ndarray, n: int, r: float, min_frac: float) -> int:
    """Components of the alpha (Cech) complex at radius r, with the minimum component size: two balls of radius r
    meet iff their centres are at most 2r apart, so H0 at radius r is single linkage at edge length 2r (an alpha
    H0 bar dies at half an MST edge length)."""
    return int(n) if w.size == 0 else _components(w, ij, n, 2.0 * r, min_frac)


def b0_single_linkage(points: np.ndarray, tau: float, min_frac: float) -> tuple[int, float]:
    """b0 of a cloud by single linkage (see b0_from_mst)."""
    w, ij = mst_edges(points)
    return b0_from_mst(w, ij, len(points), tau, min_frac)


def b0_grid(points: np.ndarray, taus, fracs) -> dict:
    """b0 for every (tau, min_frac) pair, building the minimum spanning tree only once."""
    w, ij = mst_edges(points)
    return {f"{t}|{f}": b0_from_mst(w, ij, len(points), t, f)[0] for t in taus for f in fracs}


def characteristic_scale(dgms: list[np.ndarray], sig: list[np.ndarray], pvals: list[np.ndarray],
                         fallback: float) -> float:
    """r_c = sqrt(birth * death) of the most significant H1/H2 bar (smallest p, ties by larger pi), the middle of
    the bar on a log scale; `fallback` (a radius) if there is no significant H1/H2 bar."""
    best = None
    for k in (1, 2):
        if k >= len(dgms) or sig[k] is None or not np.any(sig[k]):
            continue
        idx = np.flatnonzero(sig[k])
        d = dgms[k][idx]
        pi = d[:, 1] / d[:, 0]
        for j in range(len(idx)):
            key = (pvals[k][idx[j]], -pi[j])
            if best is None or key < best[0]:
                best = (key, math.sqrt(d[j, 0] * d[j, 1]))
    return fallback if best is None else best[1]


def betti_at_scale(dgms: list[np.ndarray], sig: list[np.ndarray], r: float, mst: tuple, min_frac: float
                   ) -> tuple[int, int, int]:
    """Filtered counts at radius r: b0 = its components (mst = (edge lengths, pairs, N);
    minimum component size min_frac), b1/b2 = significant bars alive at r (birth <= r < death)."""
    w, ij, n = mst
    out = [b0_at_radius(w, ij, n, r, min_frac)]
    for k in (1, 2):
        d = dgms[k]
        alive = (d[:, 0] <= r) & (r < d[:, 1])
        out.append(int((alive & sig[k]).sum()) if d.size else 0)
    return tuple(out)


def scale_invariants(points: np.ndarray, dgms: list[np.ndarray], sig: list, pvals: list, tau: float,
                     min_frac: float) -> dict:
    """Everything Exp2 reads at one scale: the b0 rule (b0, its cut), r_c, (b0, b1, b2) at r_c, chi, genus and label.
    The b0 cut is an MST edge length, i.e. a diameter, so the fallback radius is half of it; at that radius b0(r_c)
    equals the rule's b0."""
    w, ij = mst_edges(points)
    n = len(points)
    b0, thr = b0_from_mst(w, ij, n, tau, min_frac)
    rc = characteristic_scale(dgms, sig, pvals, fallback=thr / 2.0)
    bc = betti_at_scale(dgms, sig, rc, (w, ij, n), min_frac)
    return {"b0": b0, "b0_threshold": thr, "r_c": rc, "betti_rc": bc, "chi_rc": bc[0] - bc[1] + bc[2],
            "genus_rc": genus(*bc), "label_rc": betti_label(*bc)}


def betti_label(b0: int, b1: int, b2: int) -> str:
    """Label read from Betti numbers alone. It is not a homotopy class: Betti numbers do not determine one (the
    torus and S^2 v S^1 v S^1 are both (1, 2, 1)), hence "acyclic" rather than "contractible" and "-like"."""
    table = {(1, 0, 0): "acyclic", (1, 1, 0): "circle-like", (1, 0, 1): "sphere-like", (1, 2, 1): "torus-like"}
    if (b0, b1, b2) in table:
        return table[(b0, b1, b2)]
    if b1 == 0 and b2 == 0:
        return f"{b0} components"
    return f"other ({b0},{b1},{b2})"


def genus(b0: int, b1: int, b2: int) -> int | None:
    """Genus of a closed orientable surface (b0 = 1, b2 = 1: chi = 2 - 2g, g = b1 / 2); None otherwise.
    Closed surfaces embedded in R^3 are orientable (a closed non-orientable n-manifold does not embed in R^{n+1}:
    Hatcher 2002, remark after Cor. 3.46, p. 256); an odd b1 with b2 = 1 is not a closed surface, so None.
    The value is the genus such a surface would have: Betti numbers alone do not show that the space is a surface."""
    if b0 == 1 and b2 == 1 and b1 % 2 == 0:
        return b1 // 2
    return None
