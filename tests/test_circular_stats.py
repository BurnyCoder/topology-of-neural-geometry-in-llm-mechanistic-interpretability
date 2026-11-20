"""Tests for the travel-around-the-hole statistics (shared by Method A and Method B).

Global context: given a circle-valued coordinate theta per point and concepts with semantic phases phi_c
(e.g. Monday..Sunday at 2 pi c / 7), the test asks whether the concepts' order around the hole follows the
semantic cycle exactly once (reports/preregistration.md, section 5).
"""

import math

import numpy as np

from neurotopo.stats import circular


def test_concept_means_are_circular():
    theta = np.array([3.1, -3.1, 0.1, -0.1])          # two concepts straddling +-pi and 0
    idx = np.array([0, 0, 1, 1])
    m = circular.concept_means(theta, idx, 2)
    assert abs(abs(m[0]) - math.pi) < 1e-9 and abs(m[1]) < 1e-9


def test_perfect_ring_alignment_exact_p():
    # Seven concepts placed exactly at their phases (reversed orientation and rotated): R = 1, p = 14/7!.
    phase = 2 * np.pi * np.arange(7) / 7
    tb = -phase + 0.7
    r, s = circular.alignment(tb, phase)
    assert math.isclose(r, 1.0) and s == -1
    p = circular.permutation_pvalue(tb, phase, exact_max_n=7)
    assert math.isclose(p, 14 / math.factorial(7))
    assert abs(circular.winding(tb)) == 1
    assert circular.cyclic_order_matches(tb)
    assert math.isclose(circular.cyclic_order_p(7), 2 / math.factorial(6))


def test_shuffled_order_not_significant():
    rng = np.random.default_rng(0)
    phase = 2 * np.pi * np.arange(12) / 12
    tb = phase[rng.permutation(12)]
    p = circular.permutation_pvalue(tb, phase, mc=9999, rng=np.random.default_rng(1))
    assert p > 0.05
    assert not circular.cyclic_order_matches(tb)


def test_winding_counts_turns():
    # A helix that goes around 3 times over its 12 concepts has winding 3 in its azimuth.
    t = np.linspace(0, 3 * 2 * np.pi, 12, endpoint=False)
    assert circular.winding(np.angle(np.exp(1j * t))) == 3
    assert circular.winding(np.zeros(12)) == 0


def test_grokking_max_over_frequency():
    # Residues mod 113 placed on the circle of key frequency k = 14: max-over-k statistic finds k = 14.
    a = np.arange(113)
    theta = np.angle(np.exp(1j * 2 * np.pi * 14 * a / 113))
    r, k, s = circular.max_over_frequency(theta, a, 113, kmax=56)
    assert k == 14 and math.isclose(r, 1.0)
    p = circular.max_over_frequency_pvalue(theta, a, 113, kmax=56, mc=999, rng=np.random.default_rng(2))
    assert p <= 2 / 1000


def test_closure_ratio():
    # Points equally spaced on a circle close (ratio 1); on an open 300 deg arc the closing step is longer.
    phase = 2 * np.pi * np.arange(7) / 7
    ring = np.c_[np.cos(phase), np.sin(phase)]
    assert math.isclose(circular.closure_ratio(ring, metric="euclidean"), 1.0)
    arc = np.c_[np.cos(phase * 300 / 360), np.sin(phase * 300 / 360)]
    assert circular.closure_ratio(arc, metric="euclidean") > 1.0


def test_monotone_arc_is_not_a_cyclic_order():
    # Audit regression: concepts ordered along a short arc (0.38 rad, winding 0) must not count as cyclic.
    th = np.linspace(0.0, 0.38, 7)
    assert circular.winding(th) == 0
    assert not circular.cyclic_order_matches(th)
    assert circular.cyclic_order_matches(np.linspace(0, 2 * np.pi, 7, endpoint=False))


def test_cyclic_order_p_is_an_upper_bound():
    # Null rate of cyclic_order_matches under random relabelling of a fixed set of concept angles (independent math
    # fact-check): 2/(n-1)! when every circular gap is below pi, and 0 when the angles fit in a half circle (then the
    # closing step wraps the wrong way), so cyclic_order_p is exact in the first case and conservative in the second.
    import itertools
    n = 6
    rng = np.random.default_rng(0)
    spread = np.sort(2 * np.pi * (np.arange(n) + 0.3 * rng.random(n)) / n)   # gaps about 2 pi / n < pi
    half = np.sort(0.9 * np.pi * rng.random(n))                              # all angles within 0.9 pi
    rates = [np.mean([circular.cyclic_order_matches(th[list(p)]) for p in itertools.permutations(range(n))])
             for th in (spread, half)]
    assert math.isclose(rates[0], circular.cyclic_order_p(n))
    assert rates[1] == 0.0
