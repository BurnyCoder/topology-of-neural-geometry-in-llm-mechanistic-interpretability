"""Tests for Method B invariants, circular coordinates and the generic statistics.

Global context: b0 by single linkage with a minimum component size (outliers must not count as
components), Betti numbers at one characteristic scale, genus only for closed surfaces, DREiMac circular
coordinates that recover the angle of a noisy circle, and the multiple-testing / CI helpers fixed by the
preregistration.
"""

import math

import numpy as np

from neurotopo.stats import circular as cs
from neurotopo.stats import tests as st
from neurotopo.tda import circular, diagrams, invariants


def test_b0_three_clusters_with_outliers():
    rng = np.random.default_rng(0)
    centres = np.array([[0, 0, 0], [5, 0, 0], [0, 5, 0]])
    x = np.concatenate([c + 0.2 * rng.normal(size=(200, 3)) for c in centres])
    out = rng.uniform(-3, 8, size=(30, 3))                 # 5% scattered outliers
    b0, _ = invariants.b0_single_linkage(np.concatenate([x, out]), tau=6, min_frac=0.02)
    assert b0 == 3


def test_betti_at_scale_and_genus():
    t = np.linspace(0, 2 * np.pi, 60, endpoint=False)
    d = diagrams.alpha_diagrams(np.c_[np.cos(t), np.sin(t), 0 * t])
    sig = [None, np.ones(len(d[1]), bool), np.ones(len(d[2]), bool)]
    assert invariants.betti_at_scale(d, sig, 0.5, 1) == (1, 1, 0)
    assert invariants.homotopy_label(1, 1, 0) == "circle-like"
    assert invariants.genus(1, 2, 1) == 1 and invariants.genus(1, 0, 1) == 0 and invariants.genus(1, 1, 0) is None


def test_dreimac_recovers_circle_angle():
    rng = np.random.default_rng(1)
    t = rng.uniform(0, 2 * np.pi, 300)
    x = np.c_[np.cos(t), np.sin(t), 0.3 * np.cos(t) ** 2] + 0.03 * rng.normal(size=(300, 3))
    out = circular.circular_coordinates(x)
    r = max(abs(np.mean(np.exp(1j * (out["theta"] - t)))), abs(np.mean(np.exp(1j * (out["theta"] + t)))))
    assert r > 0.99


def test_seven_cluster_ring_end_to_end():
    # Seven concepts x 7 points on a ring: theta_B -> concept means -> R = ~1, exact p = 1/360, winding 1.
    rng = np.random.default_rng(2)
    idx = np.repeat(np.arange(7), 7)
    phase = 2 * np.pi * np.arange(7) / 7
    x = np.c_[np.cos(phase[idx]), np.sin(phase[idx]), np.zeros(49)] + 0.05 * rng.normal(size=(49, 3))
    th = cs.concept_means(circular.circular_coordinates(x)["theta"], idx, 7)
    assert cs.alignment(th, phase)[0] > 0.99
    assert math.isclose(cs.permutation_pvalue(th, phase), 14 / math.factorial(7))
    assert abs(cs.winding(th)) == 1


def test_holm_bh_and_ci():
    p = np.array([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(st.holm(p), [0.04, 0.09, 0.09, 0.5])
    assert np.allclose(st.bh(p), [0.04, 0.0533333, 0.0533333, 0.5])
    lo, hi = st.binom_ci(7, 12)
    assert 0.27 < lo < 0.29 and 0.84 < hi < 0.86            # source README: 7/12 -> 28-85%
    est, lo, hi = st.cluster_bootstrap(np.r_[np.ones(50), np.zeros(50)], np.repeat(np.arange(4), 25), np.mean,
                                       n_boot=500)
    assert est == 0.5 and lo <= 0.5 <= hi


def test_far_points_outlier_proxy():
    # D7 proxy: points farther than 6 x the median point-to-shape distance. A noisy circle has none; five
    # points placed at radius 3 (distance 2 from the unit circle, ~40 x the noise) are all flagged.
    from neurotopo.tda.ground_truth import far_points
    rng = np.random.default_rng(0)
    t = rng.uniform(0, 2 * np.pi, 300)
    circle = np.c_[np.cos(t), np.sin(t), np.zeros_like(t)]
    shape = np.c_[np.cos(np.linspace(0, 2 * np.pi, 4000)), np.sin(np.linspace(0, 2 * np.pi, 4000)), np.zeros(4000)]
    noisy = circle + 0.05 * rng.standard_normal(circle.shape)
    assert far_points(noisy, shape, 6.0) == 0
    a = rng.uniform(0, 2 * np.pi, 5)
    far = np.c_[3 * np.cos(a), 3 * np.sin(a), np.zeros(5)]
    assert far_points(np.r_[noisy, far], shape, 6.0) == 5
