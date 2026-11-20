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


def two_circles(gap: float = 10.0, n: int = 60) -> np.ndarray:
    # Two unit circles whose centres are `gap` apart: two pieces and two loops at small radii, one piece and no
    # loop once the balls are larger than both the circles and half the gap.
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c = np.c_[np.cos(t), np.sin(t), 0 * t]
    return np.concatenate([c, c + [gap, 0, 0]])


def test_b0_at_radius_equals_alpha_h0_alive():
    # H0 of the alpha (Cech) complex at radius r = components of the graph of edges <= 2r = single linkage at 2r.
    rng = np.random.default_rng(3)
    x = np.concatenate([rng.normal(size=(40, 3)), rng.normal(size=(40, 3)) + [6, 0, 0]])
    w, ij = invariants.mst_edges(x)
    h0 = diagrams.alpha_diagrams(x)[0]
    for r in (0.05, 0.3, 0.8, 2.0, 4.0):
        assert invariants.b0_at_radius(w, ij, len(x), r, 0.0) == int(diagrams.alive_at(h0, r).sum())


def test_betti_at_scale_reads_all_three_numbers_at_one_radius():
    # b0, b1 and b2 all come from the same radius (audit D12: b0 used to be the single-linkage b0 at another scale).
    x = two_circles()
    d = diagrams.alpha_diagrams(x)
    sig = [None, np.ones(len(d[1]), bool), np.ones(len(d[2]), bool)]
    w, ij = invariants.mst_edges(x)
    assert invariants.betti_at_scale(d, sig, 0.5, (w, ij, len(x)), 0.0) == (2, 2, 0)
    assert invariants.betti_at_scale(d, sig, 6.0, (w, ij, len(x)), 0.0) == (1, 0, 0)


def test_scale_invariants_fallback_is_a_radius():
    # Without a significant bar, r_c falls back to the b0 cut. The cut is an MST edge length (a diameter), so the
    # radius is half of it, and b0 at r_c then equals the single-linkage b0.
    x = two_circles()
    d = diagrams.alpha_diagrams(x)
    none = [None, np.zeros(len(d[1]), bool), np.zeros(len(d[2]), bool)]
    pv = [None, np.ones(len(d[1])), np.ones(len(d[2]))]
    s = invariants.scale_invariants(x, d, none, pv, tau=3.0, min_frac=0.0)
    assert np.isclose(s["r_c"], s["b0_threshold"] / 2)
    assert s["betti_rc"][0] == s["b0"] == 2
    assert s["chi_rc"] == 2 and s["label_rc"] == "2 components"


def test_betti_labels_do_not_claim_a_homotopy_type():
    # Betti numbers do not determine the homotopy type (T^2 and S^2 v S^1 v S^1 are both (1, 2, 1); (1, 0, 0) is
    # acyclic, not necessarily contractible), so Method B's labels say "-like" / "acyclic".
    assert invariants.betti_label(1, 0, 0) == "acyclic"
    assert invariants.betti_label(1, 1, 0) == "circle-like"
    assert invariants.betti_label(1, 0, 1) == "sphere-like"
    assert invariants.betti_label(1, 2, 1) == "torus-like"
    assert invariants.betti_label(3, 0, 0) == "3 components"
    assert invariants.betti_label(12, 1, 0) == "other (12,1,0)"
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
