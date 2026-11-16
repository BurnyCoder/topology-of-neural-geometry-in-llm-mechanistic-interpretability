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


def alpha_filtration(points: np.ndarray, maxdim: int = 2) -> list[tuple[tuple[int, ...], float]]:
    """Every simplex of the alpha complex (up to dimension maxdim) with the radius at which it enters, in
    filtration order. GUDHI stores squared radii, hence the square root. Used to show the complex growing."""
    st = gudhi.AlphaComplex(points=np.asarray(points, dtype=np.float64)).create_simplex_tree()
    return [(tuple(sx), float(np.sqrt(max(f, 0.0)))) for sx, f in st.get_filtration() if len(sx) - 1 <= maxdim]


def alpha_edges(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Edges (E, 2) of the alpha complex and their entry radii (E,), sorted by radius."""
    e = [(sx, r) for sx, r in alpha_filtration(points, maxdim=1) if len(sx) == 2]
    return np.array([sx for sx, _ in e], dtype=int).reshape(-1, 2), np.array([r for _, r in e], dtype=np.float64)


def alpha_h1_cycles(points: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    """Loops (H1 bars in radius units, zero-length bars dropped) of the alpha complex, each with one representative
    cycle for display: the edge whose entry creates the loop (its birth simplex in GUDHI's persistence_pairs), closed
    by the shortest path between its two ends through edges that entered earlier (Dijkstra, scipy.sparse.csgraph).
    That cycle exists in the complex at the birth radius but not just before it, so it represents the new loop up to
    older loops; representatives are not unique. Cycles are vertex index arrays (the closing edge is implicit)."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra
    pts = np.asarray(points, dtype=np.float64)
    st = gudhi.AlphaComplex(points=pts).create_simplex_tree()
    st.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    rank, edges = {}, []
    for sx, _ in st.get_filtration():                       # edges in filtration order (ties as GUDHI orders them)
        if len(sx) == 2:
            rank[tuple(sorted(sx))] = len(edges)
            edges.append(sx)
    e = np.array(edges, dtype=int).reshape(-1, 2)
    w = np.linalg.norm(pts[e[:, 0]] - pts[e[:, 1]], axis=1)
    bars, cycles = [], []
    for birth, death in st.persistence_pairs():
        if len(birth) != 2 or len(death) != 3:              # H1 pairs: an edge creates the loop, a triangle fills it
            continue
        b, d = np.sqrt(max(st.filtration(birth), 0.0)), np.sqrt(max(st.filtration(death), 0.0))
        if d - b <= 1e-12 * max(1.0, b):
            continue
        k = rank[tuple(sorted(birth))]
        g = csr_matrix((w[:k], (e[:k, 0], e[:k, 1])), shape=(len(pts), len(pts)))
        _, pred = dijkstra(g, directed=False, indices=birth[0], return_predecessors=True)
        path = [birth[1]]
        while path[-1] != birth[0] and pred[path[-1]] >= 0:
            path.append(int(pred[path[-1]]))
        bars.append((b, d))
        cycles.append(np.array(path, dtype=int))
    return np.array(bars, dtype=np.float64).reshape(-1, 2), cycles


def alpha_h2_voids(points: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    """Voids (H2 bars in radius units, zero-length bars dropped) of the alpha complex, each with one representative
    shell for display: the closed surface of triangles around the empty region the void encloses when it is born.

    In R^3 a void of the complex is a bounded region of its complement (Alexander duality; Edelsbrunner & Harer 2010,
    Computational Topology, ch. V; GUDHI's alpha complex holds every Delaunay tetrahedron and triangle). Right after
    the void's birth triangle enters (GUDHI's filtration order, ties as GUDHI orders them), the region is found by a
    flood fill from the void's death tetrahedron (both from persistence_pairs) through triangles that have not entered
    yet; the triangles where the fill stops are the shell. The shell holds the birth triangle and only triangles that
    entered before it, so it exists at the birth radius but not just before; it is the boundary of tetrahedra that all
    enter by the death tetrahedron, so it is filled in exactly at the death radius. Representatives are not unique.
    Shells are (F, 3) arrays of vertex indices, one row per triangle."""
    from itertools import combinations
    pts = np.asarray(points, dtype=np.float64)
    st = gudhi.AlphaComplex(points=pts).create_simplex_tree()
    st.compute_persistence(homology_coeff_field=2, min_persistence=0.0)
    rank, cofaces = {}, {}                                  # simplex -> filtration position; triangle -> its 1-2 tetrahedra
    for i, (sx, _) in enumerate(st.get_filtration()):
        key = tuple(sorted(sx))
        rank[key] = i
        if len(key) == 4:                                   # combinations of a sorted tuple are sorted: same keys as rank
            for f in combinations(key, 3):
                cofaces.setdefault(f, []).append(key)
    bars, shells = [], []
    for birth, death in st.persistence_pairs():
        if len(birth) != 3 or len(death) != 4:              # H2 pairs: a triangle closes the void, a tetrahedron fills it
            continue
        b, d = np.sqrt(max(st.filtration(birth), 0.0)), np.sqrt(max(st.filtration(death), 0.0))
        if d - b <= 1e-12 * max(1.0, b):
            continue
        cut, start = rank[tuple(sorted(birth))], tuple(sorted(death))
        seen, stack, odd = {start}, [start], set()          # odd: triangles met from an odd number of region tetrahedra
        while stack:
            for f in combinations(stack.pop(), 3):
                if rank[f] <= cut:                          # already in the complex: a wall of the region
                    odd ^= {f}                              # a wall with region on both sides cancels (Z/2 boundary)
                elif len(cofaces[f]) == 1:                  # an open hull triangle: the region would reach infinity
                    raise ValueError("void region is unbounded; filtration order differs from GUDHI's pairing")
                else:
                    for t in cofaces[f]:                    # cross the open triangle into the neighbouring tetrahedron
                        if t not in seen:
                            seen.add(t)
                            stack.append(t)
        bars.append((b, d))
        shells.append(np.array(sorted(odd), dtype=int).reshape(-1, 3))
    return np.array(bars, dtype=np.float64).reshape(-1, 2), shells


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
