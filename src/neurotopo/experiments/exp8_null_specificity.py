"""Exp8 (post hoc, deviation D9): does the real-data loop test detect holes, or only non-Gaussian structure?

Global context: every real-data "loop" verdict (Method B condition (a), reports/preregistration.md section 4.3)
compares the cloud's largest H1 persistence ratio pi = death / birth with a Monte Carlo null that is Gaussian:
(b) a covariance-matched Gaussian for one-point-per-value designs, or (a) Gaussian concept means plus the
observed within-concept residuals for prompt-template designs. Such a null rejects "a Gaussian blob", which is
not the same hypothesis as "no hole". The third independent audit (reports/exp8_audit3.md) found that Exp1's
3D matched-Gaussian estimator, which is the design-(b) sampler applied to a rank-3 cloud, flags loops on many
hole-free synthetic shapes. This phase measures that, using stored results and CPU-only simulations (no model):
1. synthetic_specificity: hole sensitivity and false-loop rate of every Exp1 estimator on clouds of known
   topology (results/exp1), per family and N bin, with cluster-bootstrap CIs, split by an outlier flag.
2. sampler_equivalence: on rank-3 clouds, the real-data Gaussian sampler (nulls.GaussianNull) and Exp1's
   3D sampler (estimators.gaussian3d_null_max) give the same null distribution, so check 1 applies to design (b).
3. cluster_specificity: the design-(a) cluster-centre null on concept centres in hole-free arrangements (a
   hemisphere cap, a planar lattice) next to a ring, an open arc and Gaussian centres, at the real sets'
   between-concept variance (the corrected power simulation's design, experiments/power.py, D6).
4. centre_projections: the loops of the day / month centres in 2D, 3D and their own top-k PCs.
5. torus_check: why Exp0's dense check misses the void of 3 ground-truth tori.
Decision rule (fixed before running, reports/exp8_audit3.md): for each design (k = 7, 12) the loop test is
"hole-specific" if every hole-free arrangement (cap, grid) passes with an exact 95% upper bound <= 0.10 at the
cell nearest the real top-3 variance share, "not hole-specific" if any lower bound is > 0.05, else "undetermined".
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from neurotopo import config
from neurotopo.analytic.topology import shape_topology
from neurotopo.data import source, synthetic
from neurotopo.experiments import exp0_analytic, exp1_synthetic, realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.experiments.power import DESIGNS_V2, FRING_GRID
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats.tests import binom_ci, cluster_bootstrap
from neurotopo.tda import diagrams, estimators, nulls
from neurotopo.tda.ground_truth import far_points

log = logging.getLogger(__name__)
ESTIMATORS = {"P_alpha_universal": "P", "S_rips_universal": "S", "Ba_fixed_pi": "Ba", "MC_gaussian3d": "MC"}
ARRANGEMENTS = ["ring", "arc300", "cap", "grid", "random"]     # ring = positive control, random = calibration
HOLE_FREE = ["cap", "grid"]                                    # the hole-free arrangements the decision rule uses
REPS, M_SIM = 40, 199                                          # as in the power simulations (power.REPS, M_SIM)
REAL = {7: "R5a_llama_weekdays", 12: "R5b_llama_months"}       # the real set each simulated design mimics


# ----------------------------------------------------------------------------- 1. synthetic specificity
def _rate(hit: np.ndarray, chunks: np.ndarray, nb: int) -> dict:
    """Mean of a boolean per-cloud indicator with a cluster-bootstrap CI over generator chunks (prereg H5)."""
    if hit.size == 0:
        return {"rate": None, "ci": [None, None], "n": 0}
    est, lo, hi = cluster_bootstrap(hit.astype(float), chunks, np.mean, n_boot=nb)
    return {"rate": est, "ci": [lo, hi], "n": int(hit.size)}


def synthetic_specificity() -> tuple[dict, pd.DataFrame]:
    """Sensitivity (true b1 >= 1 detected as >= 1 significant H1 bar) and false-loop rate (true b1 = 0, >= 1 bar)
    of P, S, Ba (all resolvable clouds and the 3,120-cloud subset) and MC (subset only), from Exp1's stored results."""
    cfg = config.load()
    res = config.path("results") / "exp1"
    df = pd.read_csv(res / "per_cloud.csv.gz", low_memory=False)
    pi = np.load(res / "pi_top.npz")
    df["pi1_top"], df["pi2_top"] = list(pi["pi1"]), list(pi["pi2"])    # predictions() needs the top-pi lists
    preds = exp1_synthetic.predictions(df, read_json(res / "summary.json")["tuning"])
    sub = df["b1_mc"].notna().to_numpy()                               # MC was run on the baseline subset only
    loop = {k: preds[k][:, 1] >= 1 for k in ("P_alpha_universal", "S_rips_universal", "Ba_fixed_pi")}
    loop["MC_gaussian3d"] = df["b1_mc"].fillna(0).to_numpy() >= 1
    resolv = df["resolvable"].to_numpy()
    hole, free = df["b1"].to_numpy() >= 1, df["b1"].to_numpy() == 0
    chunks, fam, nbin = df["chunk"].to_numpy(), df["family_name"].to_numpy(), df["n_bin"].to_numpy()
    nb = cfg["synthetic"]["bootstrap"]
    # Outlier flag (deviation D7 proxy): a point farther than far_factor x the cloud's median distance to the GT shape.
    sset = synthetic.load("test")
    k_far = cfg["outliers"]["far_factor"]
    idx = np.flatnonzero(sub)
    far = np.zeros(len(df), bool)
    far[idx] = np.array(Parallel(n_jobs=-1, batch_size=64)(delayed(far_points)(sset.cloud(i), sset.gt(i), k_far)
                                                            for i in idx)) > 0
    out, rows = {}, []
    for name, short in ESTIMATORS.items():
        for scope, base in (("all", resolv), ("subset", resolv & sub)):
            if short == "MC" and scope == "all":
                continue                                               # MC has no predictions outside the subset
            m_h, m_f = base & hole, base & free
            out[f"{short}|{scope}"] = {"sensitivity": _rate(loop[name][m_h], chunks[m_h], nb),
                                       "false_loop": _rate(loop[name][m_f], chunks[m_f], nb),
                                       "false_loop_by_n_bin": {int(b): float(loop[name][m_f & (nbin == b)].mean())
                                                               for b in range(4)}}
        base = resolv & sub                                            # per-family rows on the common subset
        b1 = df["b1"].to_numpy()
        for f in synthetic.FAMILIES:
            for b in np.unique(b1[base & (fam == f)]):                 # arcs and cones mix open/closed and apex/frustum
                m = base & (fam == f) & (b1 == b)
                rows.append({"estimator": short, "family": f, "true_b1": int(b), "n": int(m.sum()),
                             "loop_rate": float(loop[name][m].mean())})
    mf = resolv & sub & free
    p1 = pi["pi1"][:, 0]                                               # largest alpha H1 pi of every cloud
    flagged, detected = mf & loop["MC_gaussian3d"], resolv & sub & hole & loop["MC_gaussian3d"]
    out["MC_flagged_hole_free_pi1_q10_50_90"] = np.quantile(p1[flagged], [0.1, 0.5, 0.9]).tolist()
    out["MC_detected_holes_pi1_q10_50_90"] = np.quantile(p1[detected], [0.1, 0.5, 0.9]).tolist()
    out["MC_false_loop_by_outlier_flag"] = {"outlier": _rate(loop["MC_gaussian3d"][mf & far], chunks[mf & far], nb),
                                            "clean": _rate(loop["MC_gaussian3d"][mf & ~far], chunks[mf & ~far], nb)}
    return out, pd.DataFrame(rows)


# ----------------------------------------------------------------------------- 2. sampler equivalence
def _pair(x: np.ndarray, seed: int, m: int) -> dict:
    """q95 of the max H1 pi under the real-data Gaussian sampler and under Exp1's 3D sampler, same cloud."""
    from scipy.stats import ks_2samp
    a = nulls.null_max_ratios(x, "gaussian", None, m=m, seed=seed, maxdim=1, n_jobs=1)[:, 0]
    b = estimators.gaussian3d_null_max(x, m, seed + 1)[:, 0]
    return {"n": len(x), "q95_real_sampler": float(np.quantile(a, 0.95)), "q95_exp1_sampler": float(np.quantile(b, 0.95)),
            "ks_p": float(ks_2samp(a, b).pvalue)}


def sampler_equivalence(n_clouds: int = 20, m: int = M_SIM) -> dict:
    """On rank-3 clouds X, GaussianNull draws Z Xc / sqrt(N-1), i.e. N(0, cov(X)) rows, and Exp1 draws
    N(0, cov(rms_normalise(X))): equal after RMS normalisation. Checked on stored synthetic paraboloid clouds
    spread over the 12 cells of the baseline subset."""
    sset = synthetic.load("test")
    idx = np.flatnonzero(synthetic.baseline_subset(sset.meta) & (sset.meta["family_name"] == "paraboloid").to_numpy())
    idx = idx[:: max(1, len(idx) // n_clouds)][:n_clouds]
    rows = Parallel(n_jobs=-1)(delayed(_pair)(sset.cloud(i), 900000 + int(i), m) for i in idx)
    rel = np.array([r["q95_real_sampler"] / r["q95_exp1_sampler"] - 1 for r in rows])
    return {"clouds": rows, "median_abs_rel_diff_q95": float(np.median(np.abs(rel))),
            "max_abs_rel_diff_q95": float(np.abs(rel).max()),
            "frac_ks_p_below_005": float(np.mean([r["ks_p"] < 0.05 for r in rows]))}


# ----------------------------------------------------------------------------- 3. cluster-centre null on hole-free centres
def centres(k: int, arrangement: str, rng: np.random.Generator) -> np.ndarray:
    """k concept centres (k, 3) in one of five arrangements, before scaling.
    ring: a regular k-gon (has a hole); arc300: an open 300-degree arc (no hole, nearly closed);
    cap: evenly spread on a hemisphere (Fibonacci lattice; a hole-free curved surface);
    grid: a planar lattice (k = 7: a centred hexagon; otherwise rows x cols; hole-free);
    random: Gaussian centres (the null's own model; calibration). cap and grid get a small jitter."""
    if arrangement in ("ring", "arc300"):
        span = 2 * np.pi if arrangement == "ring" else 2 * np.pi * 300 / 360
        t = span * np.arange(k) / (k if arrangement == "ring" else k - 1)
        return np.c_[np.cos(t), np.sin(t), np.zeros(k)]
    if arrangement == "cap":
        z = (np.arange(k) + 0.5) / k                                   # equal-area heights on the upper hemisphere
        phi = np.arange(k) * np.pi * (3 - np.sqrt(5))                  # golden-angle azimuths (Fibonacci lattice)
        r = np.sqrt(1 - z ** 2)
        return np.c_[r * np.cos(phi), r * np.sin(phi), z] + 0.05 * rng.normal(size=(k, 3))
    if arrangement == "grid":
        if k == 7:                                                     # centre + 6 neighbours: triangulated, no hole
            t = 2 * np.pi * np.arange(6) / 6
            xy = np.r_[[[0.0, 0.0]], np.c_[np.cos(t), np.sin(t)]]
        else:
            rows = int(np.floor(np.sqrt(k)))
            cols = int(np.ceil(k / rows))
            xy = np.array([[i, j] for i in range(rows) for j in range(cols)], dtype=float)[:k]
        return np.c_[xy, np.zeros(k)] + 0.05 * rng.normal(size=(k, 3)) * np.array([1, 1, 0])
    if arrangement == "random":
        return rng.normal(size=(k, 3))
    raise ValueError(arrangement)


def simulate_cloud(k: int, m: int, d: int, fb: float, fs: float, arrangement: str, rng: np.random.Generator):
    """Corrected power simulation design (power.simulate_cloud_v2), with 3D structured centres: the arrangement
    carries variance share fs, random per-concept offsets in 20 further dimensions carry fb - fs, and isotropic
    within-concept noise carries 1 - fb, all in a random 23-dimensional subspace of R^d."""
    loc = centres(k, arrangement, rng)
    loc -= loc.mean(0)
    loc *= np.sqrt(fs / (loc ** 2).sum(1).mean())                      # structured variance share fs (per point)
    q, _ = np.linalg.qr(rng.normal(size=(d, 23)))                      # 3 structure dims + 20 offset dims
    off = rng.normal(size=(k, 20))
    off -= off.mean(0)
    off *= np.sqrt(max(fb - fs, 0) / max((off ** 2).sum(1).mean(), 1e-12))
    idx = np.repeat(np.arange(k), m)
    x = (np.c_[loc, off] @ q.T)[idx] + np.sqrt(max(1 - fb, 0) / d) * rng.normal(size=(k * m, d))
    return x, idx


def simulate_rep(k, m, d, fb, fs, arrangement, seed) -> dict:
    """One replicate of condition (a): the cloud's top alpha H1 pi vs the cluster-centre null (M = 199)."""
    rng = np.random.default_rng(seed)
    x, idx = simulate_cloud(k, m, d, fb, fs, arrangement, rng)
    y, fr = fit_frame(x)
    pi1 = diagrams.max_ratio(diagrams.alpha_diagrams(y, maxdim=1)[1])
    null = nulls.null_max_ratios(x, "cluster", idx, m=M_SIM, seed=seed + 1, maxdim=1, n_jobs=1)
    p = float(nulls.mc_pvalues(np.array([pi1]), null[:, 0])[0])
    means = np.stack([y[idx == c].mean(0) for c in range(k)])
    return {"k": k, "arrangement": arrangement, "fs": fs, "top3": float(fr["eigvals"][:3].sum() / fr["total_var"]),
            "pi1": pi1, "means_pi1": diagrams.max_ratio(diagrams.alpha_diagrams(means, maxdim=1)[1]), "p": p,
            "loop": p < 0.05}


def cluster_specificity(seed: int) -> tuple[dict, pd.DataFrame]:
    so = {r["id"]: r for r in read_json(config.path("results") / "power" / "real_second_order.json")}
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    jobs = [(k, m, d, fb, fs, a, seed * 10 ** 6 + 800000 + 10000 * i + 1000 * j + 100 * ai + r)
            for i, (k, m, d, fb) in enumerate(DESIGNS_V2) if m > 1            # cluster designs only (k = 7, 12)
            for j, fs in enumerate(FRING_GRID) for ai, a in enumerate(ARRANGEMENTS) for r in range(REPS)]
    sim = pd.DataFrame(Parallel(n_jobs=-1, batch_size=4)(delayed(simulate_rep)(*jb) for jb in jobs))
    out = {}
    for k, real_id in REAL.items():
        real_top3, real_pi = so[real_id]["top3_explained"], float(inv.loc[real_id, "top_pi1"])
        s = sim[sim["k"] == k]
        cell = s.groupby("fs")["top3"].mean()
        fs_near = float(cell.index[np.argmin(np.abs(cell.to_numpy() - real_top3))])   # cell nearest the real share
        arr = {}
        for a in ARRANGEMENTS:
            t = s[(s["arrangement"] == a) & (s["fs"] == fs_near)]
            n_pass = int(t["loop"].sum())
            lo, hi = binom_ci(n_pass, len(t))
            arr[a] = {"pass": n_pass / len(t), "n_pass": n_pass, "n": int(len(t)), "ci": [lo, hi],
                      "pass_max_over_cells": float(s[s["arrangement"] == a].groupby("fs")["loop"].mean().max()),
                      "frac_pi_ge_real": float((t["pi1"] >= real_pi).mean()),
                      "n_pi_ge_real_all_cells": int((s[s["arrangement"] == a]["pi1"] >= real_pi).sum()),
                      "n_all_cells": int((s["arrangement"] == a).sum()), "median_pi1": float(t["pi1"].median()),
                      "median_means_pi1": float(t["means_pi1"].median())}
        his = [arr[a]["ci"][1] for a in HOLE_FREE]
        los = [arr[a]["ci"][0] for a in HOLE_FREE]
        verdict = "hole-specific" if max(his) <= 0.10 else "not hole-specific" if max(los) > 0.05 else "undetermined"
        out[f"k{k}"] = {"real_id": real_id, "real_top3": real_top3, "real_top_pi1": real_pi, "fs_nearest": fs_near,
                        "sim_top3_nearest": float(cell.loc[fs_near]), "arrangements": arr, "verdict": verdict}
    return out, sim


# ----------------------------------------------------------------------------- 4. centre loops in other projections
def centre_projections() -> dict:
    """Largest H1 pi of the concept centres: in the cloud's PC1-PC2 plane and 3D frame (alpha), and in the centres'
    own top-k PCs (k = 2 alpha; k = 2..6 Rips). Tests whether "no loop of day centres" hinges on PC3."""
    out = {}
    for d in ("R5a_llama_weekdays", "R5b_llama_months", "R5c_llama_days_time"):
        c = realdata.cloud(d)
        idx = source.concepts(d, c["labels"]).index
        n = int(idx.max()) + 1
        my = np.stack([c["y"][idx == j].mean(0) for j in range(n)])    # centres in the cloud's normalised top-3 frame
        mx = np.stack([c["x"][idx == j].mean(0) for j in range(n)])    # centres in the full activation space
        steps = np.linalg.norm(np.roll(my[:, :2], -1, 0) - my[:, :2], axis=1)
        rec = {"pc12_alpha_pi": diagrams.max_ratio(diagrams.alpha_diagrams(my[:, :2], maxdim=1)[1]),
               "pc123_alpha_pi": diagrams.max_ratio(diagrams.alpha_diagrams(my, maxdim=1)[1]),
               "pc12_last_step_over_median": float(steps[-1] / np.median(steps))}
        for k in range(2, 7):
            yk, fr = fit_frame(mx, k=k)                                # the centres' own top-k PCs, RMS radius 1
            rec[f"own_top{k}_rips_pi"] = diagrams.max_ratio(diagrams.rips_diagrams(yk, maxdim=1)[1])
        rec["own_eig_shares"] = (fr["eigvals"] / fr["total_var"]).tolist()   # top-6 variance shares of the centres
        out[d] = rec
    return out


# ----------------------------------------------------------------------------- 5. dense-check tori
def torus_check() -> list[dict]:
    """For each ground-truth torus whose dense check found no void: the void bar, the counting cut (margin / 4),
    and which term sets the margin, min(2r, 2(R - r)). Same dense samples as Exp0 (exp0_analytic.dense_points)."""
    dc = pd.read_csv(config.path("results") / "exp0" / "dense_check.csv")
    bad = dc[(dc["family"] == "torus") & ~dc["agree"].astype(bool)]
    sset = synthetic.load("test")
    meta = sset.meta
    out = []
    for sid in bad["id"]:
        i = int(np.flatnonzero((meta["sample_id"] == sid).to_numpy() & (meta["family_name"] == "torus").to_numpy())[0])
        p = sset.params[i]
        t = shape_topology("torus", p)
        big, small = float(p["R"]), float(p["R"]) * float(p["ratio"])
        d2 = diagrams.alpha_diagrams(exp0_analytic.dense_points("torus", p))[2]
        top = d2[int(np.nanargmax(diagrams.ratios(d2)))]                # the most persistent H2 bar (the void)
        out.append({"id": sid, "R": big, "r": small, "margin": t["margin"],
                    "margin_term": "2(R - r)" if 2 * (big - small) < 2 * small else "2r",
                    "cut": t["margin"] / 4, "void_birth": float(top[0]), "void_death": float(top[1]),
                    "void_pi": float(top[1] / top[0]), "born_above_cut": bool(top[0] >= t["margin"] / 4)})
    return out


def run() -> None:
    cfg = config.load()
    out = out_dir("exp8_audit3")
    env_record("exp8_audit3")
    res = {}
    res["synthetic"], fam = synthetic_specificity()
    fam.to_csv(out / "synthetic_by_family.csv", index=False)
    mc = res["synthetic"]["MC|subset"]
    log.info("MC null on synthetic clouds: hole sensitivity %.3f, false-loop rate %.3f [%.3f, %.3f] (n=%d)",
             mc["sensitivity"]["rate"], mc["false_loop"]["rate"], *mc["false_loop"]["ci"], mc["false_loop"]["n"])
    res["sampler_equivalence"] = sampler_equivalence()
    log.info("sampler equivalence: median |q95 ratio - 1| = %.3f, KS p < 0.05 in %.2f of clouds",
             res["sampler_equivalence"]["median_abs_rel_diff_q95"], res["sampler_equivalence"]["frac_ks_p_below_005"])
    res["cluster"], sim = cluster_specificity(cfg["seed"])
    sim.to_csv(out / "cluster_null_simulation.csv", index=False)
    for k, v in res["cluster"].items():
        log.info("%s (%s-like, top-3 %.3f vs sim %.3f): %s; pass rates %s", k, v["real_id"], v["real_top3"],
                 v["sim_top3_nearest"], v["verdict"], {a: round(r["pass"], 3) for a, r in v["arrangements"].items()})
    res["centres"] = centre_projections()
    res["tori"] = torus_check()
    for t in res["tori"]:
        log.info("torus %s: margin %s = %.3f, cut %.3f, void born %.3f (pi %.1f) -> born above cut: %s", t["id"],
                 t["margin_term"], t["margin"], t["cut"], t["void_birth"], t["void_pi"], t["born_above_cut"])
    write_json(out / "summary.json", res)
    log.info("wrote %s", out / "summary.json")
