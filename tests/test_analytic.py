"""Tests for Method A: exact topology of uniquely parametrised shapes, margins and intrinsic coordinates.

Global context: the source's 13 shape families are uniquely parametrised (canonicalize/describe in
external/shape-fitting/src/neurogeom/shapes/*.py), so their Betti numbers, Euler characteristic, genus and
boundary components follow exactly from family and parameters (reports/preregistration.md, section 3).
The intrinsic coordinate on the fitted shape gives the hole coordinate theta_A of the traversal test.
"""

import math

import numpy as np
import pytest

from neurotopo.analytic import coords
from neurotopo.analytic.topology import shape_topology
from neurotopo.data import source
from neurotopo.tda import diagrams, nulls

E = np.eye(3).tolist()


def topo(family, **p):
    return shape_topology(family, {"center": [0, 0, 0], "axes": E, **p})


def test_torus_genus_one():
    t = topo("torus", R=1.0, ratio=0.4)
    assert (t["b0"], t["b1"], t["b2"], t["chi"], t["genus"]) == (1, 2, 1, 0, 1)
    assert math.isclose(t["margin"], min(2 * 0.4, 2 * 0.6))


def test_horn_and_spindle_torus():
    # Horn torus (r = R): the torus with one longitude pinched to a point, ~ S^2 v S^1, (1, 1, 1).
    # Spindle torus (r > R): its image is an outer "apple" and an inner "lemon" sphere glued at the two axis points,
    # ~ S^2 v S^2 v S^1, so (1, 1, 2) and chi = 2 (two bounded complementary regions = two voids).
    h = topo("torus", R=1.0, ratio=1.0)
    s = topo("torus", R=1.0, ratio=1.4)
    assert (h["b0"], h["b1"], h["b2"], h["chi"]) == (1, 1, 1, 1)
    assert (s["b0"], s["b1"], s["b2"], s["chi"], s["manifold"]) == (1, 1, 2, 2, False)


def test_arc_closed_vs_open():
    c = topo("arc", normal=[0, 0, 1], radius=2.0, extent_rad=2 * math.pi, closed=True, bisector=None)
    o = topo("arc", normal=[0, 0, 1], radius=2.0, extent_rad=math.pi, closed=False, bisector=[1, 0, 0])
    assert (c["b1"], c["chi"], c["margin"]) == (1, 0, 4.0)
    assert (o["b1"], o["chi"]) == (0, 1)
    assert math.isclose(o["margin"], 2 * 2.0 * math.sin(math.pi * 0.5))   # endpoint gap of a half circle = 4


def test_sphere_closed_vs_cap():
    s = topo("sphere", radius=1.5, closed=True, pole=None, cap_half_angle_rad=math.pi)
    cap = topo("sphere", radius=1.0, closed=False, pole=[0, 0, 1], cap_half_angle_rad=2.0)
    assert (s["b0"], s["b1"], s["b2"], s["chi"], s["genus"]) == (1, 0, 1, 2, 0)
    assert (cap["b2"], cap["chi"], cap["n_boundary"]) == (0, 1, 1)
    assert math.isclose(cap["margin"], 2 * math.sin(2.0))


def test_cone_frustum_vs_apex():
    f = topo("cone", r_bot=0.5, dr=1.0, half_height=1.0)
    a = topo("cone", r_bot=0.0, dr=1.0, half_height=1.0)
    assert (f["b1"], f["chi"], f["n_boundary"], f["margin"]) == (1, 0, 2, 1.0)
    assert (a["b1"], a["chi"], a["n_boundary"], a["margin"]) == (0, 1, 1, 0.0)


def test_pointsets_and_curves():
    cl = shape_topology("clusters", {"k": 3, "centroids": [[0, 0, 0], [3, 0, 0], [0, 4, 0]], "spread": 0.1})
    assert (cl["b0"], cl["chi"]) == (3, 3) and math.isclose(cl["margin"], 3 - 0.4)
    po = shape_topology("polytope", {"subtype": "square", "vertices": [[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]],
                                     "spread": 0.0})
    assert po["b0"] == 4
    for fam, p in [("helix", {"radius": 1.0, "pitch": 0.5, "turns": 2.0}),
                   ("ringing", {"a1": 1.0, "a2": 0.5, "a3": 0.2}), ("line", {"half_length": 1.0}),
                   ("disc", {"a": 1.0, "ratio": 0.5}), ("paraboloid", {"k1": 1.0, "k_ratio": 0.3, "rho": 1.0}),
                   ("blob", {"sigmas": [1, 0.5, 0.2]}), ("ellipse", {"a": 1.0, "b": 0.3})]:
        t = topo(fam, **p)
        assert t["b0"] == 1 and t["b2"] == 0
        assert t["b1"] == (1 if fam == "ellipse" else 0)
        assert t["chi"] == t["b0"] - t["b1"] + t["b2"]
    assert math.isclose(topo("ringing", a1=1.0, a2=0.5, a3=0.2)["margin"], 2 * math.hypot(1.0, 0.2))


def test_euler_characteristic_of_surfaces():
    # chi = 2 - 2g - n_boundary for every orientable surface returned.
    for fam, p in [("torus", {"R": 1, "ratio": 0.3}), ("sphere", {"radius": 1, "closed": True, "cap_half_angle_rad": math.pi}),
                   ("cone", {"r_bot": 0.2, "dr": 0.5, "half_height": 1}), ("disc", {"a": 1, "ratio": 1})]:
        t = topo(fam, **p)
        assert t["chi"] == 2 - 2 * t["genus"] - t["n_boundary"]


@pytest.mark.parametrize("fam,p", [
    ("arc", {"normal": [0, 0, 1], "radius": 1.0, "extent_rad": 2 * math.pi, "closed": True, "bisector": None}),
    ("ellipse", {"normal": [0, 0, 1], "major_axis": [1, 0, 0], "a": 1.0, "b": 0.5}),
    ("cone", {"r_bot": 0.6, "dr": 0.6, "half_height": 1.0}),
    ("torus", {"R": 1.0, "ratio": 0.35}),
    ("sphere", {"radius": 1.0, "closed": True, "pole": None, "cap_half_angle_rad": math.pi}),
])
def test_analytic_betti_match_persistent_homology_of_dense_samples(fam, p):
    # The exact Betti numbers equal the significant persistence of dense noise-free samples of the shape.
    params = {"center": [0, 0, 0], "axes": E, **p}
    pts = coords.random_samples(fam, params, n=10000, seed=0)   # dense enough that the torus void (pi ~ r / spacing) exceeds 3
    t = shape_topology(fam, params)
    d = diagrams.alpha_diagrams(pts)
    # Noise-free dense random samples (n = 10000): sampling bars have pi <= ~3.1, real features >= ~4.8.
    b1 = int((diagrams.ratios(d[1]) > 4).sum())
    b2 = int((diagrams.ratios(d[2]) > 4).sum())
    assert (b1, b2) == (t["b1"], t["b2"])


def random_pose(seed):
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 2] *= -1
    return rng.normal(size=3), q


@pytest.mark.parametrize("fam,p,key", [
    ("arc", {"radius": 1.3, "extent_rad": 2 * math.pi, "closed": True}, "theta"),
    ("ellipse", {"a": 1.2, "b": 0.5}, "theta"),
    ("cone", {"r_bot": 0.5, "dr": 0.4, "half_height": 1.0}, "theta"),
    ("torus", {"R": 1.0, "ratio": 0.4}, "theta"),
    ("helix", {"radius": 1.0, "pitch": 0.7, "turns": 2.5}, "t"),
])
def test_intrinsic_coordinates_recover_parameters(fam, p, key):
    # Points generated at known parameters (after a random rotation + translation) recover them.
    c, q = random_pose(1)
    params = {"center": c.tolist(), "axes": q.T.tolist(), "normal": q[:, 2].tolist(), "major_axis": q[:, 0].tolist(),
              "bisector": None, **p}
    grid = coords.parameter_grid(fam, params, curve_n=4096, surface_n=256)
    rng = np.random.default_rng(2)
    pick = rng.choice(len(grid["points"]), 300, replace=False)
    out = coords.intrinsic_coords(fam, params, grid["points"][pick], curve_n=4096, surface_n=256)
    truth = grid[key][pick]
    if key == "t":
        assert np.abs(out["t"] - truth).max() < 1e-2
    else:
        err = np.angle(np.exp(1j * (out["theta"] - truth)))
        assert np.abs(err).max() < 1e-2


def test_helix_axial_winding_and_closure():
    # A one-turn helix with zero pitch is a circle: azimuth goes once around and the closure gap is 0.
    params = {"center": [0, 0, 0], "axes": E, "radius": 1.0, "pitch": 0.0, "turns": 1.0}
    t = np.linspace(-math.pi, math.pi, 7, endpoint=False)
    pts = np.c_[np.cos(t), np.sin(t), np.zeros(7)]
    out = coords.intrinsic_coords("helix", params, pts)
    assert np.allclose(np.angle(np.exp(1j * (out["theta"] - t))), 0, atol=1e-2)
    assert np.allclose(out["axial"], 0)


@pytest.mark.parametrize("dataset_id", ["C1_gp_0", "C1_gp_1", "R1_gpt2_wpos", "R6_llama_years", "R5a_llama_weekdays",
                                        "R2_grokking_WE", "R7_llama_colors"])
def test_parametrisation_reproduces_source_shape_samples(dataset_id):
    # Our numpy parametrisation of each fitted family reproduces the source's dense fitted-shape samples
    # (viz JSON 'shape'): every source sample lies on our shape (implicit equations for surfaces, a fine
    # curve grid for curves), so theta_A is computed on exactly the shape the source fitted.
    rr = source.real_results()[dataset_id]
    fam, p = rr["family"], rr["params"]
    sh = source.load_viz(dataset_id)["shape"]
    scale = np.sqrt((source.load_viz(dataset_id)["points"] ** 2).sum(1).mean())
    c = np.asarray(p["center"])
    if fam == "sphere":
        err = np.abs(np.linalg.norm(sh - c, axis=1) - p["radius"])
    elif fam == "cone":
        loc = (sh - c) @ np.asarray(p["axes"]).T                 # world = c + loc @ axes -> loc = (x - c) @ axes^T
        s = (loc[:, 2] / p["half_height"] + 1) / 2
        err = np.abs(np.hypot(loc[:, 0], loc[:, 1]) - (p["r_bot"] + p["dr"] * s))
        assert s.min() >= -1e-6 and s.max() <= 1 + 1e-6
    else:
        from scipy.spatial import cKDTree
        err = cKDTree(coords.dense_samples(fam, p, n=200000)).query(sh)[0]
    assert err.max() < 1e-3 * scale
