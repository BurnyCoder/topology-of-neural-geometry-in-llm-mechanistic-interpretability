"""Power simulation and validation-stream tuning, run before any persistent homology of real clouds.

Global context: reports/preregistration.md, section 8 and the addendum. Two parts:
1. Validation tuning (synthetic validation stream only, never the test set or real data): the b0 rule
   (tau, min_frac), the fixed-pi-threshold baseline (pi0_1, pi0_2), and the family-implied baseline mapping
   (family -> modal exact Betti vector), all against the exact ground truth of Exp0.
2. Power / false-positive simulation of the H1-B conditions (a)-(c) on synthetic designs that mimic the real
   cyclic sets: k concept centres x m prompts in R^D (k = 7, m = 7 like weekdays; k = 12, m = 12 like months;
   k = 113, m = 1 like grokking) arranged on a closed ring (power), an open 300-degree arc or at random
   Gaussian positions (false positives), with isotropic within-concept noise; the between-concept variance
   fraction f_B is swept over a grid that brackets the real sets' values (second-order statistics only).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from neurotopo import config
from neurotopo.data import source, synthetic
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import circular as cs
from neurotopo.tda import circular, diagrams, estimators, nulls

log = logging.getLogger(__name__)
PI_GRID = [1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]
DESIGNS = [(7, 7, 4096), (12, 12, 4096), (113, 1, 128)]       # (k concepts, m prompts per concept, D)
FB_GRID = [0.3, 0.5, 0.7, 0.9]
ARRANGEMENTS = ["ring", "arc300", "random"]
REPS, M_SIM = 40, 199


# ----------------------------------------------------------------------------- 1. validation tuning
def val_summaries() -> pd.DataFrame:
    """summarize() for every validation cloud, joined with its exact ground truth from Exp0."""
    cfg = config.load()["tda"]
    sset = synthetic.load("val")
    gt = pd.read_csv(config.path("results") / "exp0" / "synth_val_topology.csv.gz")
    rows = Parallel(n_jobs=-1, batch_size=8)(delayed(estimators.summarize)(sset.cloud(i), cfg["b0_tau_grid"],
                                                                           cfg["b0_minfrac_grid"]) for i in range(len(sset)))
    s = pd.DataFrame(rows)
    return pd.concat([gt.reset_index(drop=True), s.drop(columns=["n"])], axis=1)


def macro_exact(df: pd.DataFrame, b0: np.ndarray, b1: np.ndarray, b2: np.ndarray) -> float:
    """Exact Betti-vector accuracy macro-averaged over families (polytope scored on b0 only; prereg H5)."""
    ok = (b0 == df["b0"].to_numpy()) & ((df["family_name"].to_numpy() == "polytope") |
                                         ((b1 == df["b1"].to_numpy()) & (b2 == df["b2"].to_numpy())))
    return float(pd.Series(ok).groupby(df["family_name"].to_numpy()).mean().mean())


def tune(df: pd.DataFrame) -> dict:
    """Pick the b0 rule and the fixed-pi thresholds on resolvable validation clouds; build the family map."""
    r = df[df["resolvable"]].reset_index(drop=True)
    grid = list(r["b0_grid"].iloc[0].keys())
    acc0 = {g: float(np.mean(np.array([row[g] for row in r["b0_grid"]]) == r["b0"].to_numpy())) for g in grid}
    best0 = max(grid, key=lambda g: (acc0[g], -grid.index(g)))
    b0 = np.array([row[best0] for row in r["b0_grid"]])
    pi1 = np.array(r["pi1_top"].tolist())
    pi2 = np.array(r["pi2_top"].tolist())
    accpi = {(a, b): macro_exact(r, b0, (pi1 > a).sum(1), (pi2 > b).sum(1)) for a in PI_GRID for b in PI_GRID}
    best_pi = max(accpi, key=accpi.get)
    fam_map = {f: list(map(int, g[["b0", "b1", "b2"]].value_counts().idxmax()))
               for f, g in r.groupby("family_name")}
    tau, frac = best0.split("|")
    return {"b0_tau": float(tau), "b0_minfrac": float(frac), "b0_val_accuracy": acc0[best0],
            "pi0_1": best_pi[0], "pi0_2": best_pi[1], "pi_val_macro_accuracy": accpi[best_pi],
            "family_map": fam_map, "n_val_resolvable": int(len(r)), "n_val": int(len(df))}


# ----------------------------------------------------------------------------- 2. power simulation
def real_second_order() -> list[dict]:
    """Between-concept variance fraction and top-3 explained variance of the real cyclic sets (no topology)."""
    out = []
    for did in ["R5a_llama_weekdays", "R5b_llama_months", "R5c_llama_days_time", "R2_grokking_WE",
                "C3_llama_weekdays_init", "C3_llama_months_init"]:
        x, labels, _ = source.load_raw(did)
        con = source.concepts(did, [str(s) for s in labels])
        xc = x - x.mean(0)
        means = np.stack([xc[con.index == c].mean(0) for c in range(len(con.phase))])
        between = float((means[con.index] ** 2).sum() / (xc ** 2).sum())
        rr = source.real_results()[did]
        out.append({"id": did, "N": len(x), "D": x.shape[1], "between_fraction": between,
                    "top3_explained": rr["top3_explained"]})
    return out


def simulate_cloud(k: int, m: int, d: int, fb: float, arrangement: str, rng: np.random.Generator):
    """k centres (ring / 300-degree arc / random 3D Gaussian) in a random subspace of R^d, m noisy copies each;
    isotropic noise sized so that between-concept variance / total variance = fb."""
    if arrangement == "random":
        loc = rng.normal(size=(k, 3))
    else:
        span = 2 * np.pi if arrangement == "ring" else 2 * np.pi * 300 / 360
        t = span * np.arange(k) / (k if arrangement == "ring" else k - 1)
        loc = np.c_[np.cos(t), np.sin(t), np.zeros(k)]
    loc -= loc.mean(0)
    q, _ = np.linalg.qr(rng.normal(size=(d, 3)))
    centres = loc @ q.T
    b = float((loc ** 2).sum(1).mean())                       # between-concept variance (per point)
    s = np.sqrt(b * (1 - fb) / fb / d)                        # per-dimension noise std
    idx = np.repeat(np.arange(k), m)
    return centres[idx] + s * rng.normal(size=(k * m, d)), idx


def simulate_rep(k: int, m: int, d: int, fb: float, arrangement: str, seed: int) -> dict:
    """One replicate: H1-B (a) loop vs design null, (b) alignment p of theta_B, (c) winding."""
    rng = np.random.default_rng(seed)
    x, idx = simulate_cloud(k, m, d, fb, arrangement, rng)
    y, _ = fit_frame(x)
    dg = diagrams.alpha_diagrams(y)
    kind, groups = ("cluster", idx) if m > 1 else ("gaussian", None)
    null = nulls.null_max_ratios(x, kind, groups, m=M_SIM, seed=seed + 1, maxdim=1, n_jobs=1)
    pi1 = diagrams.max_ratio(dg[1])
    loop = bool(nulls.mc_pvalues(np.array([pi1]), null[:, 0])[0] < 0.05)
    phase = 2 * np.pi * np.arange(k) / k
    theta = circular.circular_coordinates(y)["theta"]
    if theta is None:                                          # no usable cohomology class: test fails
        p, w = 1.0, 0
    else:
        th = cs.concept_means(theta, idx, k)
        p = cs.permutation_pvalue(th, phase, exact_max_n=7, mc=999, rng=rng)
        w = cs.winding(th)
    return {"k": k, "m": m, "fb": fb, "arrangement": arrangement, "loop": loop,
            "align": bool(p < 0.05 / 6), "wind1": abs(w) == 1, "all": loop and p < 0.05 / 6 and abs(w) == 1}


def power_simulation(seed: int) -> pd.DataFrame:
    jobs = [(k, m, d, fb, a, seed * 10 ** 6 + 1000 * i + r) for i, (k, m, d) in enumerate(DESIGNS)
            for fb in FB_GRID for a in ARRANGEMENTS for r in range(REPS)]
    rows = Parallel(n_jobs=-1, batch_size=4)(delayed(simulate_rep)(*j) for j in jobs)
    return pd.DataFrame(rows)


def run() -> None:
    cfg = config.load()
    out = out_dir("power")
    env_record("power")
    df = val_summaries()
    df.to_json(out / "val_summaries.json.gz", orient="records")
    t = tune(df)
    write_json(out / "val_tuning.json", t)
    log.info("validation tuning: %s", {k: v for k, v in t.items() if k != "family_map"})
    write_json(out / "real_second_order.json", real_second_order())
    sim = power_simulation(cfg["seed"])
    sim.to_csv(out / "power_simulation.csv", index=False)
    summ = sim.groupby(["k", "m", "arrangement", "fb"])[["loop", "align", "wind1", "all"]].mean().reset_index()
    summ.to_csv(out / "power_summary.csv", index=False)
    log.info("power summary:\n%s", summ.to_string())
