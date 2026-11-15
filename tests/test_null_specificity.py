"""Tests for the third audit's null-specificity checks (experiments/exp8_null_specificity.py, deviation D9).

Global context: the real-data loop test compares a cloud's largest H1 persistence ratio with a Gaussian null. The
audit asks whether that test is specific to holes. These tests pin the simulated concept-centre arrangements
(which have a hole by construction and which do not), the variance shares of the simulation, and the claim that
the real-data Gaussian sampler and Exp1's 3D sampler are the same distribution on a rank-3 cloud.
"""

import numpy as np

from neurotopo.experiments.exp8_null_specificity import centres, simulate_cloud
from neurotopo.tda import diagrams, estimators, nulls


def test_arrangements_have_the_intended_topology():
    rng = np.random.default_rng(0)
    ring, arc, cap, grid = (centres(12, a, rng) for a in ("ring", "arc300", "cap", "grid"))
    assert all(c.shape == (12, 3) for c in (ring, arc, cap, grid))
    assert np.all(cap[:, 2] > -0.2) and np.allclose(grid[:, 2], 0)      # cap: upper hemisphere; grid: planar
    # The regular 12-gon has a persistent loop (pi = 1 / sin(pi / 12) ~ 3.9); the planar lattice does not reach it.
    assert diagrams.max_ratio(diagrams.alpha_diagrams(ring, maxdim=1)[1]) > 3.5
    assert diagrams.max_ratio(diagrams.alpha_diagrams(grid[:, :2], maxdim=1)[1]) < 2.0
    hexagon = centres(7, "grid", rng)                                   # centre + 6 neighbours: triangulated
    assert diagrams.max_ratio(diagrams.alpha_diagrams(hexagon[:, :2], maxdim=1)[1]) < 1.3


def test_simulated_variance_shares_match_targets():
    # Between-concept share fb and structured share fs are set exactly per point (noise share 1 - fb in expectation).
    rng = np.random.default_rng(1)
    x, idx = simulate_cloud(12, 12, 512, 0.9, 0.45, "cap", rng)
    xc = x - x.mean(0)
    means = np.stack([xc[idx == c].mean(0) for c in range(12)])
    between = (means[idx] ** 2).sum() / (xc ** 2).sum()
    assert abs(between - 0.9) < 0.03


def test_real_gaussian_sampler_equals_exp1_sampler_on_rank3_cloud():
    # GaussianNull draws Z Xc / sqrt(N - 1); Exp1 draws N(0, cov(X)); after RMS normalisation they agree, so the
    # q95 of the max H1 pi differs only by Monte Carlo error.
    rng = np.random.default_rng(2)
    x = rng.normal(size=(60, 3)) * np.array([3.0, 1.0, 0.3])
    a = nulls.null_max_ratios(x, "gaussian", None, m=300, seed=5, maxdim=1, n_jobs=1)[:, 0]
    b = estimators.gaussian3d_null_max(x, 300, seed=6)[:, 0]
    assert abs(np.quantile(a, 0.95) / np.quantile(b, 0.95) - 1) < 0.12
