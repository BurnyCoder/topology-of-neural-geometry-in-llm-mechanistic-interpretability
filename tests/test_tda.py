"""Tests for persistence diagrams, persistence ratios, the universal null and Monte Carlo nulls.

Global context: Method B (reports/preregistration.md, section 4) counts significant bars of alpha-complex
persistence diagrams. These tests pin down units (radii, not squared radii), known closed-form values
(regular n-gon), the behaviour on shapes with known Betti numbers, and the calibration of the nulls.
"""

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


def test_rips_12gon_has_phantom_h2_alpha_does_not():
    # Rips on the regular 12-gon creates spurious H2 classes (Adamaszek & Adams 2017); alpha does not.
    t = 2 * np.pi * np.arange(12) / 12
    pts = np.c_[np.cos(t), np.sin(t), np.zeros(12)]
    assert len(diagrams.rips_diagrams(pts, maxdim=2)[2]) > 0
    assert len(diagrams.alpha_diagrams(pts)[2]) == 0


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
