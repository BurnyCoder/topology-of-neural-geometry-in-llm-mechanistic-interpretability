"""`run.py toy`: the worked example of the loop/ring test, on a 21-point toy cloud with known answers.

Global context: docs/worked_example.md (and its interactive version on the explorer site) walks through every
step behind the plain-language example figure (report/figures.py, fig_examples): the top-3 PCA frame, alpha
persistence, the persistence ratio, the design-matched Monte Carlo null, loop localisation, the cohomology
coordinate theta_B and the traversal statistics. The toy is small enough to check by hand: 7 concepts (a week)
with 3 prompts each, every concept a small equilateral triangle around a vertex of the regular heptagon. It is
analysed with exactly the functions used on the 44 real clouds (no model, no stored activations), and
tests/test_toy_example.py checks the results against closed forms.
"""

from __future__ import annotations

import logging
import math

import gudhi
import numpy as np

from neurotopo import config
from neurotopo.experiments.alignment import passes
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.experiments.exp7_audit import bar_scale
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import circular as cs
from neurotopo.tda import diagrams, nulls
from neurotopo.tda.circular import circular_coordinates

log = logging.getLogger(__name__)

N_CONCEPTS, SIDE = 7, 0.1                       # a week; triangle side, small against the heptagon's side 0.87
DIM, SPREAD = 8, 3.0                            # the toy "activations" live in a random plane of R^8, scaled by 3
NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
POLYGONS = (3, 4, 6, 7, 12)                     # regular k-gons whose persistence ratio 1/sin(pi/k) is quoted


def toy_points(n: int = N_CONCEPTS, s: float = SIDE) -> tuple[np.ndarray, np.ndarray]:
    """(3n, 2) points and (3n,) concept ids. Concept c is an equilateral triangle of side s centred on
    v_c = (cos 2 pi c/n, sin 2 pi c/n), one corner pointing radially outward. Its corners lie on a circle of
    radius s/sqrt(3) (the triangle's circumradius) at 0, 120 and 240 degrees from the outward direction."""
    pts, idx = [], []
    for c in range(n):
        a = 2 * np.pi * c / n
        rad = np.array([np.cos(a), np.sin(a)])                 # outward unit vector (and the concept mean)
        tan = np.array([-np.sin(a), np.cos(a)])                # sideways unit vector
        for k in range(3):
            b = 2 * np.pi * k / 3                              # corner angle measured from the outward direction
            pts.append(rad + s / np.sqrt(3) * (np.cos(b) * rad + np.sin(b) * tan))
            idx.append(c)
    return np.array(pts), np.array(idx)


def embed(p: np.ndarray, dim: int = DIM, spread: float = SPREAD, seed: int = 0) -> np.ndarray:
    """Toy activations x_i = m + spread * (p_i1 a + p_i2 b) in R^dim, with a random mean m and random orthonormal
    directions a, b (QR of a Gaussian matrix), so the PCA step has real work to do."""
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(dim, 2)))            # dim x 2, orthonormal columns a, b
    return rng.normal(scale=5.0, size=dim) + spread * p @ q.T


def filtration_events(y2: np.ndarray, tol: float = 1e-7) -> list[dict]:
    """The radii at which simplices enter the alpha filtration of a planar cloud, with the number of edges and
    triangles entering at each. GUDHI's filtration values are squared radii
    (https://gudhi.inria.fr/python/latest/alpha_complex_user.html); ties within tol are merged."""
    st = gudhi.AlphaComplex(points=np.asarray(y2, dtype=np.float64)).create_simplex_tree()
    vals = sorted((math.sqrt(max(f, 0.0)), len(sx) - 1) for sx, f in st.get_filtration() if len(sx) > 1)
    ev: list[dict] = []
    for r, dim in vals:
        if not ev or r - ev[-1]["r"] > tol * max(1.0, r):
            ev.append({"r": r, "edges": 0, "triangles": 0})
        ev[-1]["edges" if dim == 1 else "triangles"] += 1
    return ev


def analyse(x: np.ndarray, idx: np.ndarray, n: int, m: int, seed: int, dataset_id: str = "toy_weekdays") -> dict:
    """Run the real-data pipeline on one toy cloud. Returns {"numbers": flat dict quoted by the docs,
    "data": arrays for the interactive page}. The steps mirror Exp2 (loop test), the audit (localisation)
    and Exp3 (theta_B traversal); the cluster-centre null is the one used for prompt-template designs."""
    # 1. The source's top-3 PCA frame (centre, eigenvectors, skewness signs, RMS radius 1).
    y, fr = fit_frame(x)
    # 2-3. Alpha persistence of the normalised cloud and the ratio pi = death / birth of every loop.
    dg = diagrams.alpha_diagrams(y)
    pi = diagrams.ratios(dg[1])
    top = int(np.nanargmax(pi))
    tiny = int(np.nanargmin(pi))
    # 4. Design-matched Monte Carlo null: the max pi of M cluster-centre null clouds, same preprocessing.
    nm = nulls.null_max_ratios(x, "cluster", idx, m=m, seed=nulls.dataset_seed(dataset_id, seed))[:, 0]
    p_loop = float(nulls.mc_pvalues(pi[[top]], nm)[0])
    q95 = float(np.quantile(nm, 0.95))                         # numpy's default linear interpolation
    # 5. Localisation: does the top loop die before two concepts' balls ever touch?
    loc = bar_scale(y, idx, dg[1])
    # 6. theta_B: DREiMac circular coordinate of the most persistent Rips cohomology class (preregistered settings).
    cc = circular_coordinates(y)
    theta = cc["theta"]
    # 7. Traversal: concept circular means against the semantic phases 2 pi c / n.
    phase = 2 * np.pi * np.arange(n) / n
    tc = cs.concept_means(theta, idx, n)
    r_align, orient = cs.alignment(tc, phase)
    p_align = cs.permutation_pvalue(tc, phase)
    w = cs.winding(tc)
    twice = cs.wrap(2 * tc)                                    # counter-example: each concept two places further
    # Planar view for the event table and the figures: PC3 is zero up to rounding for this planar toy.
    if np.abs(y[:, 2]).max() > 1e-9:
        raise RuntimeError("toy cloud is not planar after PCA")
    events = filtration_events(y[:, :2])
    means = np.stack([y[idx == c].mean(0) for c in range(n)])
    cov_means = np.cov(toy_points(n)[0].reshape(n, 3, 2).mean(1).T)    # sample covariance of the 7 centres, toy units
    num = {
        "n": n, "s": SIDE, "N": len(x), "dim": x.shape[1], "spread": SPREAD,
        "outer_r": 1 + SIDE / math.sqrt(3), "inner_radial": 1 - SIDE / (2 * math.sqrt(3)),
        "inner_r": math.hypot(1 - SIDE / (2 * math.sqrt(3)), SIDE / 2),
        "eig1": float(fr["eigvals"][0]), "eig2": float(fr["eigvals"][1]), "eig3": float(fr["eigvals"][2]),
        "scale": float(fr["scale"]), "rms": float(fr["scale"] / SPREAD), "pc3_max": float(np.abs(y[:, 2]).max()),
        "tiny_b": float(dg[1][tiny, 0]), "tiny_d": float(dg[1][tiny, 1]), "tiny_pi": float(pi[tiny]),
        "n_tiny": int(np.sum(pi < 1.5)), "big_b": float(dg[1][top, 0]), "big_d": float(dg[1][top, 1]),
        "big_pi": float(pi[top]), "n_h1": int(len(pi)), "n_h2": int(len(dg[2])),
        "heptagon_pi": float(loc["means_top_pi1"]),
        "null_m": int(m), "null_q95": q95, "null_p": p_loop, "null_max": float(nm.max()), "null_min": float(nm.min()),
        "null_floor_pct": int(round(100 * np.mean(nm < pi[tiny] + 1e-6))), "null_ratio": float(pi[top] / q95),
        "null_n_ge": int(np.sum(nm >= pi[top])), "null_seed": int(nulls.dataset_seed(dataset_id, seed)),
        "cov_means": float(cov_means[0, 0]), "sd_means": float(math.sqrt(cov_means[0, 0])),
        "connect_r": float(loc["connect_radius"]), "within_loop": bool(loc["within_concept_loop"]),
        "rips_b": 2 * float(cc["bar"][0]), "rips_d": 2 * float(cc["bar"][1]),
        "rips_ratio": float(cc["bar"][1] / cc["bar"][0]), "standard_range_ok": bool(cc["bar"][1] >= 2 * cc["bar"][0]),
        "R": float(r_align), "orient": int(orient), "p_align": float(p_align), "n_perm": math.factorial(n),
        "perm_count": int(round(p_align * math.factorial(n))), "w": int(w),
        "step_deg": float(np.degrees(np.mean(cs.wrap(np.roll(tc, -1) - tc)))),
        "passes": bool(passes({"p": p_align, "winding": w})),
        "twice_R": float(cs.alignment(twice, phase)[0]), "twice_w": int(cs.winding(twice)),
        "twice_step_deg": float(np.degrees(np.mean(cs.wrap(np.roll(twice, -1) - twice)))),
    }
    for c in range(n):
        num[f"theta_c{c}"] = float(np.round(np.degrees(tc[c]), 6) % 360)    # round first: -1e-9 deg is 0, not 360
    for k, e in enumerate(events):
        num[f"ev{k}.r"], num[f"ev{k}.edges"], num[f"ev{k}.triangles"] = e["r"], e["edges"], e["triangles"]
    for k in POLYGONS:
        num[f"poly{k}"] = 1 / math.sin(math.pi / k)
    data = {"points": np.round(y[:, :2], 6).tolist(), "concept": idx.tolist(), "names": NAMES[:n],
            "theta": np.round(theta, 6).tolist(), "concept_theta": np.round(tc, 6).tolist(),
            "means": np.round(means[:, :2], 6).tolist(), "h0": np.round(dg[0], 6).tolist(),
            "h1": np.round(dg[1], 6).tolist(), "events": events, "null_max": np.round(nm, 5).tolist()}
    return {"numbers": num, "data": data}


def run() -> None:
    cfg = config.load()
    out = out_dir("toy")
    env_record("toy")
    p, idx = toy_points()
    res = analyse(embed(p), idx, N_CONCEPTS, m=cfg["tda"]["mc_draws"], seed=cfg["seed"])
    write_json(out / "summary.json", res)
    num = res["numbers"]
    log.info("toy: top loop [%.4f, %.4f] pi=%.3f; null q95=%.3f p=%.4f; connect r=%.4f; R=%.3f p=%.4f w=%d",
             num["big_b"], num["big_d"], num["big_pi"], num["null_q95"], num["null_p"], num["connect_r"],
             num["R"], num["p_align"], num["w"])
