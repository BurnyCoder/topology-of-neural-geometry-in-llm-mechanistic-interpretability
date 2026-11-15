"""Method B invariants: b0 by single linkage, persistent Betti counts, characteristic scale, chi and genus.

Global context: from a persistence diagram and a significance mask we report (reports/preregistration.md,
section 4.4-4.5): persistent counts b_k^pers (number of significant bars), Betti numbers at one stated scale
r_c (so chi(r_c) = b0 - b1 + b2 is the Euler characteristic of one complex, not a mix of scales), the genus
only for closed surfaces (b0 = 1, b2 = 1; chi = 2 - 2g), and a homotopy-class label. Homology cannot tell a
circle from an annulus or a solid torus; that limitation is stated in every report.
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


def b0_from_mst(w: np.ndarray, ij: np.ndarray, n: int, tau: float, min_frac: float) -> tuple[int, float]:
    """Components after cutting MST edges longer than tau * median MST edge, counting only components with
    at least max(1, ceil(min_frac * N)) points (outliers must not count); returns (b0, threshold length)."""
    if w.size == 0:
        return int(n), 0.0
    thr = tau * float(np.median(w))
    keep = w <= thr
    g = coo_matrix((np.ones(int(keep.sum())), (ij[keep, 0], ij[keep, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    sizes = np.bincount(lab)
    return int((sizes >= max(1, math.ceil(min_frac * n))).sum()), thr


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
    """r_c = sqrt(birth * death) of the most significant H1/H2 bar (smallest p, ties by larger pi);
    the b0 threshold scale if there is no significant H1/H2 bar."""
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


def betti_at_scale(dgms: list[np.ndarray], sig: list[np.ndarray], r: float, b0: int) -> tuple[int, int, int]:
    """Betti numbers at scale r: b0 from single linkage, b1/b2 = significant bars alive at r."""
    out = [b0]
    for k in (1, 2):
        d = dgms[k]
        alive = (d[:, 0] <= r) & (r < d[:, 1])
        out.append(int((alive & sig[k]).sum()) if d.size else 0)
    return tuple(out)


def homotopy_label(b0: int, b1: int, b2: int) -> str:
    """Homotopy-class label from Betti numbers (homology cannot separate a circle from an annulus or a
    solid torus, nor a point from a disc or a ball)."""
    table = {(1, 0, 0): "contractible", (1, 1, 0): "circle-like", (1, 0, 1): "sphere", (1, 2, 1): "torus"}
    if (b0, b1, b2) in table:
        return table[(b0, b1, b2)]
    if b1 == 0 and b2 == 0:
        return f"{b0} components"
    return f"other ({b0},{b1},{b2})"


def genus(b0: int, b1: int, b2: int) -> int | None:
    """Genus of a closed orientable surface (b0 = 1, b2 = 1: chi = 2 - 2g, g = b1 / 2); None otherwise.
    Surfaces in R^3 are orientable; an odd b1 with b2 = 1 is not a closed surface, so None."""
    if b0 == 1 and b2 == 1 and b1 % 2 == 0:
        return b1 // 2
    return None
