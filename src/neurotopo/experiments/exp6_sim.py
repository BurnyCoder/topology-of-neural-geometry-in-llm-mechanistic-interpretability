"""Exp6-sim: simulated steering around topologically detected holes (amendment A2, step 1; no model is run).

Global context: the primary hypothesis H6 asks whether steering a concept's activation around the loop that
encircles a hole is semantically meaningful, every time topology finds a hole. Without running the LLM, we
move each held-out prompt's stored activation around loop B (fit-free, theta_B), loop A (fitted axis circle),
the chord path through concept centroids, and 100 random loops, and decode the represented concept with
decoders trained on the other prompts (offline.py). H6-sim passes for a dataset if loop B beats the random
loops (p < 0.05), the decoded concept winds exactly once for >= 50% of prompts, and the steered activations
stay on the data manifold (mean on-manifold fraction >= 0.5). Evidence type: simulation / correlational.
"""

from __future__ import annotations

import logging

import numpy as np

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import circular as cs
from neurotopo.steering import loops, metrics, offline
from neurotopo.tda import circular
from neurotopo.tda.nulls import dataset_seed

log = logging.getLogger(__name__)
M_RANDOM = 100
GROK = "R2_grokking_WE"


def theta_b(dataset_id: str) -> np.ndarray | None:
    """theta_B from Exp3's cache (results/exp3/theta_B.npz), recomputed with the same parameters if absent."""
    p = config.path("results") / "exp3" / "theta_B.npz"
    if p.exists():
        z = np.load(p)
        if dataset_id in z.files:
            return z[dataset_id]
    return circular.circular_coordinates(realdata.cloud(dataset_id)["y"])["theta"]


def fitted_loop_factory(dataset_id: str, z: np.ndarray):
    """Loop A per prompt for helix / cone fits (circle around the fitted axis at the prompt's height), else None."""
    rr = source.real_results()[dataset_id]
    if rr["family"] not in ("helix", "cone"):
        return None
    p = rr["params"]
    c, ax = np.asarray(p["center"]), np.asarray(p["axes"])
    if rr["family"] == "helix":
        rad = lambda _h: float(p["radius"])
    else:
        rad = lambda h: float(p["r_bot"]) + float(p["dr"]) * np.clip((h / float(p["half_height"]) + 1) / 2, 0, 1)
    return lambda i: loops.azimuth_loop(c, ax, rad, float((z[i] - c) @ ax[2]))


def random_null(x, fr, lb, phase, groups, deltas, decoders, seed_key, prompts=None) -> np.ndarray:
    """T for M random loops: same centre and radius as loop B, random planes in the top-10 PC space."""
    _, fr10 = fit_frame(x, k=10)
    z10 = (x - fr10["mean"]) @ fr10["basis"]
    centre10 = ((lb.pts.mean(0) @ fr["basis"].T + fr["mean"]) - fr10["mean"]) @ fr10["basis"]
    rng = np.random.default_rng(seed_key)
    out = []
    for _ in range(M_RANDOM):
        rl, _ = loops.random_loop(centre10, lb.radius, np.eye(10), rng)
        out.append(offline.evaluate(lambda i: rl, x, z10, fr10["basis"], phase, groups, deltas, decoders, prompts)["T"])
    return np.array(out)


def dataset_sim(dataset_id: str, seed: int) -> dict:
    """Simulated steering of one dataset with concept structure (7 bins for ordinal sets)."""
    c = realdata.cloud(dataset_id)
    x, fr = c["x"], c["frame"]
    z = (x - fr["mean"]) @ fr["basis"]
    con = source.concepts(dataset_id, c["labels"], n_bins=7)
    n = len(con.phase)
    k_steps = 4 * n if n <= 12 else 72
    deltas = 2 * np.pi * np.arange(k_steps) / k_steps
    groups = offline.folds(dataset_id, len(x))
    probe = dataset_id in config.load()["groups"]["cyclic_primary"] + config.load()["groups"]["cyclic_secondary"] + ["R7_llama_colors"]
    decoders = offline.build_decoders(x, con.index, con.phase, groups, probe=probe)
    th = theta_b(dataset_id)
    res = {"id": dataset_id, "n_concepts": n, "k_steps": k_steps, "variable": con.variable}
    cen = np.stack([z[con.index == k].mean(0) for k in range(n)])
    loop_set = {"chord_centroids": (lambda lp: (lambda i: lp))(loops.chord_path(cen))}
    if th is not None:
        lb = loops.loop_from_coordinate(z, th, n_bins=2 * min(n, 36))
        loop_set["B_cohomology"] = (lambda lp: (lambda i: lp))(lb)
    fa = fitted_loop_factory(dataset_id, z)
    if fa is not None:
        loop_set["A_fitted_axis_circle"] = fa
    for name, lf in loop_set.items():
        r = offline.evaluate(lf, x, z, fr["basis"], con.phase, groups, deltas, decoders)
        res[name] = {k: v for k, v in r.items() if k != "per_prompt"}
        res[name]["per_prompt"] = [{k: v for k, v in q.items()} for q in r["per_prompt"]]
        if probe:
            pr = [q["probe"] for q in r["per_prompt"]]
            res[name]["probe"] = {"T": float(np.mean([q["R"] for q in pr])),
                                  "frac_wind1": float(np.mean([abs(q["winding"]) == 1 for q in pr]))}
    if th is not None:
        t_null = random_null(x, fr, lb, con.phase, groups, deltas, decoders, dataset_seed(dataset_id + "sim", seed))
        b = res["B_cohomology"]
        res["random_null"] = {"T_random_mean": float(t_null.mean()), "T_random_q95": float(np.quantile(t_null, 0.95)),
                              "p": metrics.null_pvalue(b["T"], t_null)}
        res["H6_sim_pass"] = bool(res["random_null"]["p"] < 0.05 and b["frac_wind1"] >= 0.5 and b["vocab_mass"] >= 0.5)
    else:
        res["H6_sim_pass"] = False
    return res


def grokking_sim(seed: int) -> dict:
    """Residues mod 113 (one point each): ridge phase probe at k* (leave one residue out); on-manifold = steered
    point within the 95th percentile of nearest-neighbour distances among the embeddings."""
    c = realdata.cloud(GROK)
    x, fr = c["x"], c["frame"]
    z = (x - fr["mean"]) @ fr["basis"]
    a = np.array([int(s) for s in c["labels"]])
    th = theta_b(GROK)
    if th is None:
        return {"id": GROK, "H6_sim_pass": False}
    _, kstar, _ = cs.max_over_frequency(th, a, 113, 56)
    phase = 2 * np.pi * kstar * a / 113
    k_steps = 2 * 113
    deltas = 2 * np.pi * np.arange(k_steps) / k_steps
    from scipy.spatial import cKDTree
    nn = cKDTree(x).query(x, k=2)[0][:, 1]
    r95 = float(np.quantile(nn, 0.95))
    probes = {i: offline.PhaseProbe(x, phase, np.arange(len(x)) != i) for i in range(len(x))}
    order = np.argsort((kstar * a) % 113)
    lb = loops.loop_from_coordinate(z, th, n_bins=56)
    def run(loop_for, zz, basis):
        per = []
        for i in range(len(x)):
            h = x[i] + offline.steer_displacements(loop_for(i), zz[i], basis, deltas)
            others = np.delete(x, i, 0)
            dist = cKDTree(others).query(h)[0]
            per.append({"prompt": i, **metrics.traversal(probes[i].decode(h), deltas), "vocab_mass": float(np.mean(dist <= r95))})
        return per
    res = {"id": GROK, "k_star": int(kstar)}
    for name, lp in {"B_cohomology": lb, "chord_centroids": loops.chord_path(z[order])}.items():
        per = run(lambda i: lp, z, fr["basis"])
        res[name] = {**metrics.dataset_statistic(per), "per_prompt": per}
    fa = fitted_loop_factory(GROK, z)
    if fa is not None:
        per = run(fa, z, fr["basis"])
        res["A_fitted_axis_circle"] = {**metrics.dataset_statistic(per), "per_prompt": per}
    _, fr10 = fit_frame(x, k=10)
    z10 = (x - fr10["mean"]) @ fr10["basis"]
    centre10 = ((lb.pts.mean(0) @ fr["basis"].T + fr["mean"]) - fr10["mean"]) @ fr10["basis"]
    rng = np.random.default_rng(dataset_seed(GROK + "sim", seed))
    t_null = np.array([metrics.dataset_statistic(run(lambda i, rl=loops.random_loop(centre10, lb.radius, np.eye(10), rng)[0]: rl,
                                                     z10, fr10["basis"]))["T"] for _ in range(M_RANDOM)])
    b = res["B_cohomology"]
    res["random_null"] = {"T_random_mean": float(t_null.mean()), "T_random_q95": float(np.quantile(t_null, 0.95)),
                          "p": metrics.null_pvalue(b["T"], t_null)}
    res["H6_sim_pass"] = bool(res["random_null"]["p"] < 0.05 and b["frac_wind1"] >= 0.5 and b["vocab_mass"] >= 0.5)
    return res


def run() -> None:
    cfg = config.load()
    out = out_dir("exp6_sim")
    env_record("exp6_sim")
    g = cfg["groups"]
    ids = g["cyclic_primary"] + g["cyclic_secondary"] + ["R7_llama_colors"] + g["ordinal"] + g["init_controls"] + \
        [f"C1_{k}_{i}" for k in ("gp", "walk") for i in range(10)]
    ids = [d for d in ids if d != GROK and d != "C3_grokking_WE_init"]
    exp3 = read_json(config.path("results") / "exp3" / "method_b.json")
    res = {}
    for did in ids:
        res[did] = dataset_sim(did, cfg["seed"])
        res[did]["hole_detected_B"] = bool(exp3[did]["loop"]) if did in exp3 else None
        b = res[did].get("B_cohomology", {})
        log.info("%-26s hole=%s  B: T=%.3f wind1=%.2f on-manifold=%.2f p=%s  chord T=%.3f  pass=%s", did,
                 res[did]["hole_detected_B"], b.get("T", np.nan), b.get("frac_wind1", np.nan), b.get("vocab_mass", np.nan),
                 res[did].get("random_null", {}).get("p"), res[did]["chord_centroids"]["T"], res[did]["H6_sim_pass"])
        write_json(out / "simulated_steering.json", res)
    res[GROK] = grokking_sim(cfg["seed"])
    res[GROK]["hole_detected_B"] = bool(exp3[GROK]["loop"])
    write_json(out / "simulated_steering.json", res)
    cyc = [d for d in g["cyclic_primary"] + g["cyclic_secondary"] if res[d]["hole_detected_B"]]
    write_json(out / "summary.json", {
        "cyclic_with_hole": cyc, "cyclic_with_hole_pass": [d for d in cyc if res[d]["H6_sim_pass"]],
        "noncyclic_with_hole_pass": [d for d in res if d not in g["cyclic_primary"] + g["cyclic_secondary"] + ["R7_llama_colors"]
                                     and res[d]["hole_detected_B"] and res[d]["H6_sim_pass"]],
        "verdict": ("supported" if cyc and all(res[d]["H6_sim_pass"] for d in cyc) else
                    "partially supported" if any(res[d]["H6_sim_pass"] for d in cyc) else "not supported")})
