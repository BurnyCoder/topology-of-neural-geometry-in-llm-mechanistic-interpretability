"""Tests for persistence diagrams, persistence ratios, the universal null and Monte Carlo nulls.

Global context: Method B (reports/preregistration.md, section 4) counts significant bars of alpha-complex
persistence diagrams. These tests pin down units (radii, not squared radii), known closed-form values
(regular n-gon), the behaviour on shapes with known Betti numbers, and the calibration of the nulls.
"""

from collections import Counter
from itertools import combinations

import numpy as np
import pytest
from scipy import stats

from neurotopo.tda import diagrams, nulls


def circle(n, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, 2 * np.pi, n)
    return np.c_[np.cos(t), np.sin(t), np.zeros(n)] + noise * rng.normal(size=(n, 3))


def sphere(n, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True) + noise * rng.normal(size=(n, 3))


def torus(n, big=1.0, small=0.4, noise=0.0, seed=0):
    # Rejection-free approximately uniform sampling on the torus surface (area element R + r cos v).
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 2 * np.pi, 4 * n)
    v = rng.uniform(0, 2 * np.pi, 4 * n)
    keep = rng.uniform(0, big + small, 4 * n) < big + small * np.cos(v)
    u, v = u[keep][:n], v[keep][:n]
    ring = big + small * np.cos(v)
    return np.c_[ring * np.cos(u), ring * np.sin(u), small * np.sin(v)] + noise * rng.normal(size=(n, 3))


def test_alpha_radius_units_two_points():
    # Two points at distance 2: the H0 bar dies at radius 1 (GUDHI returns squared radius 1.0 -> sqrt = 1).
    d = diagrams.alpha_diagrams(np.array([[0.0, 0, 0], [2.0, 0, 0]]))
    finite = d[0][np.isfinite(d[0][:, 1])]
    assert np.isclose(finite[0, 1], 1.0)


@pytest.mark.parametrize("n", [5, 7, 12])
def test_regular_ngon_ratio(n):
    # Cech/alpha H1 of a regular n-gon: born at R sin(pi/n) (half the side), dies at R -> pi = 1/sin(pi/n).
    t = 2 * np.pi * np.arange(n) / n
    d = diagrams.alpha_diagrams(np.c_[np.cos(t), np.sin(t), np.zeros(n)])
    h1 = d[1]
    assert len(h1) == 1
    assert np.isclose(diagrams.ratios(h1)[0], 1 / np.sin(np.pi / n), rtol=1e-6)


def test_cluster_ring_can_exceed_point_polygon_ratio():
    # 1/sin(pi/n) is the ratio of n point-like centres, not a ceiling for a ring of n noisy clusters: spread lets
    # neighbouring clusters connect earlier (smaller birth), so the ring's pi grows with the spread (audit D12).
    rng = np.random.default_rng(0)
    t = 2 * np.pi * np.arange(7) / 7
    c = np.c_[np.cos(t), np.sin(t), np.zeros(7)]
    pis = [diagrams.max_ratio(diagrams.alpha_diagrams(np.repeat(c, 30, 0) + 0.15 * rng.normal(size=(210, 3)))[1])
           for _ in range(9)]
    assert np.median(pis) > 1 / np.sin(np.pi / 7)


def test_persistence_can_depend_on_the_coefficient_field():
    # Each subcomplex of R^3 has torsion-free homology, but persistence can still depend on the field
    # (Obayashi & Yoshiwaki 2023, doi:10.1007/s00454-023-00544-7): a Moebius band's boundary circle winds twice
    # around its core, so boundary -> band is multiplication by 2 on H1, zero over Z/2 and an isomorphism over Z/3.
    import gudhi
    bars = {}
    for p in (2, 3):
        st = gudhi.SimplexTree()
        for i in range(5):
            st.insert([i], 0.0)
            st.insert([i, (i + 2) % 5], 0.0)                     # the boundary circle 0-2-4-1-3 enters first
        for tri in [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 0), (4, 0, 1)]:
            st.insert(list(tri), 1.0)                            # then the 5-vertex Moebius band
        st.compute_persistence(homology_coeff_field=p, persistence_dim_max=True)
        bars[p] = sorted(map(tuple, st.persistence_intervals_in_dimension(1).tolist()))
    assert bars[2] == [(0.0, 1.0), (1.0, np.inf)]
    assert bars[3] == [(0.0, np.inf)]


def test_rips_12gon_has_phantom_h2_alpha_does_not():
    # Rips on the regular 12-gon creates spurious H2 classes (Adamaszek & Adams 2017); alpha does not.
    t = 2 * np.pi * np.arange(12) / 12
    pts = np.c_[np.cos(t), np.sin(t), np.zeros(12)]
    assert len(diagrams.rips_diagrams(pts, maxdim=2)[2]) > 0
    assert len(diagrams.alpha_diagrams(pts)[2]) == 0


def closed_mod2(tris) -> bool:
    # A closed surface over Z/2: every edge of its triangles is shared by an even number of them (zero boundary).
    count = Counter(tuple(sorted(e)) for t in np.asarray(tris).tolist() for e in combinations(t, 2))
    return all(c % 2 == 0 for c in count.values())


def test_void_shell_octahedron():
    # The 6 corners of a (slightly perturbed) octahedron enclose one void: born when the last of the 8 faces enters
    # (circumradius sqrt(2/3) of a face of side sqrt(2)), filled at radius ~1. Its shell is the 8 faces (chi = 2).
    # The perturbation also leaves a near-zero bar (pi - 1 ~ 1e-6) among the tetrahedra filling the inside; skip it.
    pts = np.r_[np.eye(3), -np.eye(3)] + 1e-3 * np.random.default_rng(0).normal(size=(6, 3))
    bars, shells, _ = diagrams.alpha_h2_voids(pts)
    real = np.flatnonzero(diagrams.ratios(bars) > 1.01)
    assert len(bars) == len(shells) and len(real) == 1
    b, s = bars[real[0]], shells[real[0]]
    assert np.isclose(b[0], np.sqrt(2 / 3), atol=5e-3) and np.isclose(b[1], 1.0, atol=5e-3)
    assert s.shape == (8, 3) and set(np.unique(s)) == set(range(6)) and closed_mod2(s)


@pytest.mark.parametrize("pts", [sphere(300, 0.01), np.random.default_rng(1).normal(size=(300, 3))], ids=["sphere", "blob"])
def test_void_shells_are_born_with_the_void(pts):
    # Same voids as the diagram; each shell is a closed surface whose triangles are all in the complex at the birth
    # radius, and the last of them enters exactly at the birth radius (the triangle that closes the void).
    bars, shells, _ = diagrams.alpha_h2_voids(pts)
    assert len(bars) > 0
    assert np.allclose(np.sort(bars, axis=0), np.sort(diagrams.alpha_diagrams(pts)[2], axis=0))
    entry = {tuple(sorted(sx)): r for sx, r in diagrams.alpha_filtration(pts) if len(sx) == 3}
    for (b, _), s in zip(bars, shells):
        r = np.array([entry[tuple(t)] for t in np.sort(s, axis=1).tolist()])
        assert len(s) >= 4 and closed_mod2(s)
        assert r.max() <= b * (1 + 1e-9) and np.isclose(r.max(), b, rtol=1e-9)


def test_sphere_void_shell_is_the_sphere():
    # The big void of a noisy sphere sample is enclosed by a triangulated sphere (Euler characteristic V - E + F = 2)
    # through most of the points; points pushed outward by the noise can sit behind it (268 of 300 here are on it).
    pts = sphere(300, 0.01)
    bars, shells, _ = diagrams.alpha_h2_voids(pts)
    top = shells[int(np.argmax(diagrams.ratios(bars)))]
    edges = {tuple(sorted(e)) for t in top.tolist() for e in combinations(t, 2)}
    assert len(np.unique(top)) - len(edges) + len(top) == 2
    assert len(np.unique(top)) >= 0.8 * len(pts)


def inside_mod2(c, pts, tris, direction=(0.5377, 0.8339, -0.1258)) -> bool:
    # Point in a closed Z/2 surface: a ray from c crosses it an odd number of times (Moller-Trumbore ray-triangle
    # test, https://doi.org/10.1080/10867651.1997.10487468); a generic direction avoids grazing edges.
    a, b, d = (pts[np.asarray(tris)[:, k]] for k in range(3))
    e1, e2, r = b - a, d - a, np.asarray(direction, dtype=float)
    h = np.cross(r, e2)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = 1.0 / np.einsum("ij,ij->i", e1, h)
        s = c - a
        u = f * np.einsum("ij,ij->i", s, h)
        q = np.cross(s, e1)
        v, t = f * (q @ r), f * np.einsum("ij,ij->i", e2, q)
    return int(np.sum(np.isfinite(f) & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0))) % 2 == 1


@pytest.mark.parametrize("pts", [sphere(300, 0.01), np.random.default_rng(1).normal(size=(300, 3))], ids=["sphere", "blob"])
def test_void_centres_are_empty_and_inside_their_shell(pts):
    # Each void's centre (circumcentre of the tetrahedron that fills it) has no point closer than the death radius
    # (empty Delaunay circumsphere), so a ball of radius death - birth around it is still empty when the void is born,
    # and the centre lies inside the void's shell.
    bars, shells, centres = diagrams.alpha_h2_voids(pts)
    assert len(centres) == len(bars) > 0
    for (_, d), s, c in zip(bars, shells, centres):
        assert np.isclose(np.linalg.norm(pts - c, axis=1).min(), d, rtol=1e-6)
        assert inside_mod2(c, pts, s)


def test_octahedron_void_centre_is_the_centre():
    pts = np.r_[np.eye(3), -np.eye(3)] + 1e-3 * np.random.default_rng(0).normal(size=(6, 3))
    bars, _, centres = diagrams.alpha_h2_voids(pts)
    assert np.allclose(centres[int(np.argmax(diagrams.ratios(bars)))], 0.0, atol=1e-2)


def test_known_shapes_universal_significance():
    # Rips H1 with A = 1 detects a noisy circle; alpha H2 with A = 1/2 detects a sphere's and a torus's void;
    # Gaussian blobs give nothing. (Alpha H1 with A = 1/2 is calibrated but very conservative at N <= 1000:
    # a circle with pi = 18 among ~440 bars does not pass Bonferroni; see reports/deviations.md.)
    rng = np.random.default_rng(3)
    blob = rng.normal(size=(500, 3))
    assert nulls.universal_significant(diagrams.rips_diagrams(circle(400, 0.03))[1], A=1.0).sum() == 1
    assert nulls.universal_significant(diagrams.rips_diagrams(blob)[1], A=1.0).sum() == 0
    for pts, b2 in [(sphere(800, 0.02), 1), (torus(2500, noise=0.02), 1), (blob, 0)]:
        assert nulls.universal_significant(diagrams.alpha_diagrams(pts)[2], A=0.5).sum() == b2


def test_universal_constants_match_noise_spread():
    # Calibration of A (Bobrowski & Skraba 2023): the spread of log log pi of noise bars must equal
    # 1/A times the left-Gumbel standard deviation pi/sqrt(6): ~2.57 for alpha (A = 1/2), ~1.28 for Rips.
    rng = np.random.default_rng(9)
    x = rng.uniform(size=(1000, 3))
    lg = np.pi / np.sqrt(6)
    for dg, a in [(diagrams.alpha_diagrams(x)[1], 0.5), (diagrams.rips_diagrams(x)[1], 1.0)]:
        pi = diagrams.ratios(dg)
        ll = np.log(np.log(pi[np.isfinite(pi) & (pi > 1 + 1e-12)]))
        assert abs(ll.std() * a / lg - 1) < 0.2


def test_universal_pvalues_roughly_uniform_on_noise():
    # Under the null, the p-values of all bars in a Gaussian-noise diagram should be close to uniform
    # (Bobrowski & Skraba 2023). Loose check: KS statistic small for pooled alpha and Rips H1 p-values.
    rng = np.random.default_rng(4)
    pa, pr = [], []
    for _ in range(5):
        x = rng.normal(size=(1000, 3))
        pa.append(nulls.universal_pvalues(diagrams.alpha_diagrams(x)[1], A=0.5))
        pr.append(nulls.universal_pvalues(diagrams.rips_diagrams(x[:400], maxdim=1)[1], A=1.0))
    for p in (np.concatenate(pa), np.concatenate(pr)):
        p = p[np.isfinite(p)]
        assert stats.kstest(p, "uniform").statistic < 0.1


def test_gaussian_null_covariance_matches_input():
    # Full-D matched Gaussian null: the sample covariance of a null cloud is unbiased for the input's
    # sample covariance (averaged over draws; D <= N so draws are in the original coordinates).
    rng = np.random.default_rng(5)
    x = rng.normal(size=(60, 40)) * np.linspace(3, 0.1, 40)
    g = nulls.GaussianNull(x)
    covs = np.mean([np.cov(g.draw_raw(rng), rowvar=False) for _ in range(400)], axis=0)
    target = np.cov(x, rowvar=False)
    assert np.linalg.norm(covs - target) / np.linalg.norm(target) < 0.05


def test_mc_pvalue_bounds_and_reproducibility():
    null = np.random.default_rng(6).uniform(1, 2, 999)
    p = nulls.mc_pvalues(np.array([0.5, 1.5, 5.0]), null)
    assert np.isclose(p[0], 1.0) and np.isclose(p[2], 1 / 1000) and 0 < p[1] < 1
    a = nulls.null_max_ratios(circle(50, 0.05), "gaussian", None, m=20, seed=7)
    b = nulls.null_max_ratios(circle(50, 0.05), "gaussian", None, m=20, seed=7)
    assert np.array_equal(a, b)


def test_cluster_centre_null_keeps_within_cluster_residuals():
    # The cluster-centre null redraws concept means only; within-concept residuals are kept exactly.
    rng = np.random.default_rng(8)
    groups = np.repeat(np.arange(7), 7)
    centres = rng.normal(size=(7, 30)) * 5
    x = centres[groups] + 0.1 * rng.normal(size=(49, 30))
    y = nulls.cluster_centre_draw(x, groups, rng)
    resid_in = x - np.array([x[groups == g].mean(0) for g in range(7)])[groups]
    resid_out = y - np.array([y[groups == g].mean(0) for g in range(7)])[groups]
    assert np.allclose(resid_in, resid_out)
