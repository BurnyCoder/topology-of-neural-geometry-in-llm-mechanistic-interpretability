"""Tests for steering loops and traversal metrics (no model needed).

Global context: the steering experiment (preregistration amendment A2) builds a closed path around a detected
hole and measures whether the model's decoded answer goes around the concept cycle once as the activation is
moved around the path.
"""

import numpy as np

from neurotopo.steering import loops, metrics


def test_loop_from_coordinate_recovers_circle_and_displacement():
    t = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    y = np.c_[np.cos(t), np.sin(t), 0.1 * np.ones_like(t)]
    lp = loops.loop_from_coordinate(y, t, n_bins=14)
    assert abs(lp.radius - 1) < 0.02
    d = lp.displacement(y[:1], np.pi)                                    # half a turn: to the antipode
    assert np.allclose(y[0] + d[0], [-1, 0, 0.1], atol=0.03)


def test_traversal_perfect_and_constant():
    deltas = 2 * np.pi * np.arange(28) / 28
    phases = 2 * np.pi * np.arange(7) / 7
    # Answer advances one day every 4 steps: R ~ 1 (up to quantisation), winding 1.
    psi = phases[(np.arange(28) // 4) % 7]
    out = metrics.traversal(psi, deltas)
    assert out["winding"] == 1 and out["R"] > 0.95
    const = metrics.traversal(np.zeros(28), deltas)
    assert const["winding"] == 0 and const["R"] < 0.05


def test_random_loop_and_chord_path():
    rng = np.random.default_rng(0)
    lp, plane = loops.random_loop(np.zeros(10), 2.0, np.eye(10), rng)
    assert abs(lp.radius - 2.0) < 1e-6 and np.allclose(plane @ plane.T, np.eye(2))
    cen = np.c_[np.cos(np.arange(7) * 2 * np.pi / 7), np.sin(np.arange(7) * 2 * np.pi / 7)]
    ch = loops.chord_path(cen)
    assert np.allclose(ch(np.array([2 * np.pi * 3 / 7]))[0], cen[3])

def test_registered_loop_bins_singleton_radius_and_missing_outcomes():
    from neurotopo.steering.offline import CentroidDecoder
    assert [loops.steering_bins(n) for n in (7,12,113)] == [14,24,72]
    x = np.eye(4)
    dec = CentroidDecoder(x,np.arange(4),4,np.array([False,True,True,True]))
    assert dec.radius95==0 and dec.decode(x[:1])[1][0]>0
    assert metrics.cohort_verdict([])=="no eligible datasets"
    assert metrics.cohort_verdict([None,None])=="unmeasured"
    assert metrics.cohort_verdict([True,None])=="incomplete"
    assert metrics.cohort_verdict([True,False])=="partially supported"
