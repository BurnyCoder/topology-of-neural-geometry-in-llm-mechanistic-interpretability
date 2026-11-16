"""Tests for the worked example (experiments/toy_example.py, docs/worked_example.md).

Global context: the worked example explains the loop/ring test on a toy cloud whose answers are known in closed
form: 7 concepts (a week), each an equilateral triangle of side s around a vertex of the regular heptagon, one
corner pointing outward. These tests check the repository's own functions against those closed forms, so the
numbers that docs/worked_example.md quotes are verified, not only computed.
"""

import math

import numpy as np

from neurotopo.experiments import toy_example as toy
from neurotopo.tda import diagrams

N, S = 7, 0.1
A = 1 - S / (2 * math.sqrt(3))          # radial distance of the two inner corners (centroid minus inradius)
H = S / 2                               # their sideways offset from the radial line (half the side)


def test_toy_points_geometry():
    p, idx = toy.toy_points(N, S)
    assert p.shape == (3 * N, 2) and np.bincount(idx).tolist() == [3] * N
    means = np.stack([p[idx == c].mean(0) for c in range(N)])
    heptagon = np.stack([[math.cos(2 * math.pi * c / N), math.sin(2 * math.pi * c / N)] for c in range(N)])
    assert np.allclose(means, heptagon)                                   # concept means are the heptagon
    d = np.linalg.norm(p[:, None] - p[None], axis=-1)
    assert np.allclose(d[idx[:, None] == idx[None]].max(), S)             # every within-concept pair is one side


def test_alpha_diagram_matches_closed_form():
    p, _ = toy.toy_points(N, S)
    h1 = diagrams.alpha_diagrams(p)[1]
    pi = diagrams.ratios(h1)
    tiny = h1[pi < 1.5]
    assert len(tiny) == N and np.allclose(tiny, [S / 2, S / math.sqrt(3)])    # edge half-length -> circumradius
    big = h1[np.argmax(pi)]
    birth = A * math.sin(math.pi / N) - H * math.cos(math.pi / N)             # half the gap between neighbours
    death = math.hypot(A, H)                                                  # the 14 inner corners' circle
    assert np.allclose(big, [birth, death], atol=1e-9)
    assert math.isclose(pi.max(), death / birth, rel_tol=1e-9)


def test_analysis_on_embedded_cloud():
    p, idx = toy.toy_points(N, S)
    out = toy.analyse(toy.embed(p), idx, N, m=19, seed=0)
    num = out["numbers"]
    assert math.isclose(num["tiny_pi"], 2 / math.sqrt(3), rel_tol=1e-6)      # 3-point loop, scale free
    assert num["within_loop"] is False and math.isclose(num["connect_r"], num["big_b"], rel_tol=1e-9)
    assert num["null_min"] >= 2 / math.sqrt(3) - 1e-6                       # the null keeps the triangles
    assert math.isclose(num["heptagon_pi"], 1 / math.sin(math.pi / N), rel_tol=1e-6)
    assert math.isclose(num["R"], 1.0, abs_tol=1e-9) and abs(num["w"]) == 1
    assert math.isclose(num["p_align"], 2 * N / math.factorial(N))          # only the 14 symmetries of the week
    assert num["twice_w"] in (-2, 2) and num["twice_R"] < 1e-9
