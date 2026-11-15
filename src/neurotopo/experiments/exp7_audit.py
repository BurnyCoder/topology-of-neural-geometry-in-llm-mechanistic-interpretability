"""Exp7 (post hoc, deviation D8): checks added by the second independent audit, on stored data only.

Global context: the audit (reports/exp7_audit.md) found that several plain-language claims rest on readings the
preregistered statistics cannot support, and that one preregistered descriptive statistic was never reported.
Each check below targets one claim; none changes a preregistered verdict, and none runs a model.
1. Colour stimulus baseline: the 900 colour prompts sample HLS with saturation >= 0.4, so the stimulus set in RGB
   space already surrounds the grey axis. Method B on the prompts' own RGB values asks whether the activation
   ring is already present in the input (a confounder for "the model represents hue as a circle").
2. Bar-scale localisation: for prompt-template (cluster) designs, the max-pi statistic can be won by a small loop
   *inside* one concept's cluster rather than by a loop *through* the concept clusters.
3. Closure ratio (preregistration section 5, descriptive; implemented but never reported before D8).
4. PCA diagnostics: near-equal top eigenvalues make the top-3 subspace unstable under subsampling
   (Davis-Kahan; Yu, Wang & Samworth 2015, doi:10.1093/biomet/asv008); grokking W_E Fourier power per frequency
   (Nanda et al. 2023, arXiv:2301.05217, find a few "key frequencies").
5. Subsample stability against a threshold computed at the subsample size (Exp2 used the full-size null).
6. Post hoc theta_B (D5): does the relaxed-range Rips class overlap the significant alpha bar (the preregistered
   check of section 4.6), and is the coordinate constant on whole concepts (DREiMac leaves uncovered or
   cocycle-free regions at 0)?
7. Power simulation v2 (D6): exact binomial CIs and linear interpolation at the real top-3 variance share.
"""

from __future__ import annotations

import colorsys
import logging

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import alignment, realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import circular as cs
from neurotopo.stats.tests import binom_ci
from neurotopo.tda import circular, diagrams, nulls

log = logging.getLogger(__name__)
CLUSTERED = ["R5a_llama_weekdays", "R5b_llama_months", "R5c_llama_days_time", "R7_llama_colors",
             "C3_llama_weekdays_init", "C3_llama_months_init"]                 # the preregistered cluster designs
STABILITY = ["R7_llama_colors", "R5b_llama_months", "R2_grokking_WE", "R5c_llama_days_time"]   # sets with a 3D loop
KEY = ["R5a_llama_weekdays", "R5b_llama_months", "R2_grokking_WE", "R5c_llama_days_time", "R7_llama_colors"]
POWER_REPS = 40                                                                 # replicates per cell (power.REPS)


# ----------------------------------------------------------------------------- 1. colour stimulus baseline
def colour_stimuli() -> tuple[np.ndarray, list[str]]:
    """RGB values (0-255, as written in the hex codes) and labels "hue|sat|lum" of the 900 colour prompts.

    Copied from the source's prompt builder (external/shape-fitting/src/neurogeom/realdata/llm_sets.py,
    bhalla_prompts, lines 51-56), which cannot be imported here because that module imports torch."""
    rgb, labels = [], []
    for h in range(36):                                          # 36 hues, 10 degrees apart
        for s in (0.4, 0.55, 0.7, 0.85, 1.0):                    # 5 saturations, all >= 0.4: the grey axis is excluded
            for lum in (0.25, 0.375, 0.5, 0.625, 0.75):          # 5 lightnesses
                r, g, b = colorsys.hls_to_rgb(h / 36, lum, s)     # same call and argument order as the source
                rgb.append([int(round(r * 255)), int(round(g * 255)), int(round(b * 255))])   # the hex digits' values
                labels.append(f"{h * 10}|{s}|{lum}")             # the source's label format
    return np.asarray(rgb, dtype=np.float64), labels


def loop_test(x: np.ndarray, groups: np.ndarray, seed_key: str, m: int) -> dict:
    """Method B condition (a) on any cloud x (N, D): alpha top H1 pi of the normalised top-3 cloud vs the
    cluster-centre null (same sampler, preprocessing and p-value as realdata.mc_significance)."""
    y, _ = fit_frame(x)                                          # top-3 PCA, RMS radius 1 (source fit_frame)
    d1 = diagrams.alpha_diagrams(y)[1]
    pi = diagrams.ratios(d1)
    top = int(np.nanargmax(pi))                                  # the most persistent alpha H1 bar
    nm = nulls.null_max_ratios(x, "cluster", groups, m=m, seed=nulls.dataset_seed(seed_key, 0), maxdim=1)
    return {"top_pi1": float(pi[top]), "top_bar": d1[top].tolist(), "null_q95": float(np.quantile(nm[:, 0], 0.95)),
            "p_loop": float(nulls.mc_pvalues(np.array([pi[top]]), nm[:, 0])[0]), "m": m, "y": y}


def traversal(y: np.ndarray, labels: list[str]) -> dict:
    """theta_B (preregistered and relaxed DREiMac range) and the hue alignment records, as in Exp3 / D5."""
    out = {}
    for name, std in (("prereg", True), ("relaxed", False)):
        cc = circular.circular_coordinates(y, standard_range=std)
        rec = alignment.records("R7_llama_colors", cc["theta"], labels)[0] if cc["theta"] is not None else None
        out[name] = {"error": cc["error"], "rips_bar": cc["bar"],
                     "record": None if rec is None else {k: rec[k] for k in ("R", "p", "winding", "order_match")}}
    return out


def colour_baseline(m: int) -> dict:
    """Method B on the prompts' RGB values, side by side with the Llama colour activations (Exp2/Exp3)."""
    rgb, labels = colour_stimuli()
    hue = source.concepts("R7_llama_colors", labels).index      # concept = hue, exactly as for the activations
    lt = loop_test(rgb, hue, "RGB_stimulus", m)
    y = lt.pop("y")
    means = np.stack([y[hue == c].mean(0) for c in range(36)])  # the 36 hue means in the normalised top-3 frame
    ang = np.arctan2(means[:, 1] - means[:, 1].mean(), means[:, 0] - means[:, 0].mean())   # angle in PC1-PC2
    phase = 2 * np.pi * np.arange(36) / 36
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id").loc["R7_llama_colors"]
    return {"rgb": {**lt, "loop_freq": subsample_freq(rgb, lt["null_q95"]),
                    "means_top_pi1": diagrams.max_ratio(diagrams.alpha_diagrams(means)[1]),
                    "means_pc12_R": cs.alignment(ang, phase)[0], "means_pc12_winding": cs.winding(ang),
                    "traversal": traversal(y, labels)},
            "llama": {"top_pi1": float(inv["top_pi1"]), "null_q95": float(inv["null_q95_pi1"]),
                      "p_loop": float(inv["p_top_loop"]), "loop_freq": float(inv["loop_freq"])}}


def subsample_freq(x: np.ndarray, thr: float, reps: int = 200, frac: float = 0.8) -> float:
    """Fraction of 80% subsamples whose top alpha H1 pi exceeds thr (Exp2's stability rule and seed)."""
    rng = np.random.default_rng(0)                               # the source's subsample seed (Exp2)
    n = len(x)
    hits = 0
    for _ in range(reps):
        sub = rng.choice(n, int(round(frac * n)), replace=False)
        y, _ = fit_frame(x[sub])
        hits += diagrams.max_ratio(diagrams.alpha_diagrams(y)[1]) > thr
    return hits / reps


# ----------------------------------------------------------------------------- 2. bar-scale localisation
def bar_scale(y: np.ndarray, idx: np.ndarray, dgm1: np.ndarray) -> dict:
    """Where the most persistent alpha H1 bar lives relative to the concept clusters (normalised top-3 cloud).

    connect_radius: half the smallest distance between points of *different* concepts. Below this radius the
    balls of different concepts are disjoint, so a bar that dies at or below it is carried by one concept's
    points alone (an exact sufficient condition for a loop inside a cluster, not through the clusters).
    within_radius: mean distance of a point to its concept mean; centre_gap: median distance from each concept
    mean to its nearest other mean (descriptive). means_top_pi1: the largest H1 ratio of the concept means alone."""
    pi = diagrams.ratios(dgm1)
    top = dgm1[int(np.nanargmax(pi))]
    n = int(idx.max()) + 1
    means = np.stack([y[idx == c].mean(0) for c in range(n)])
    within = float(np.mean([np.linalg.norm(y[idx == c] - means[c], axis=1).mean() for c in range(n)]))
    pd_all = cdist(y, y)
    connect = float(pd_all[idx[:, None] != idx[None, :]].min() / 2)   # first contact between two concepts' balls
    dm = cdist(means, means)
    np.fill_diagonal(dm, np.inf)                                 # ignore each mean's distance to itself
    steps = np.linalg.norm(np.roll(means, -1, 0) - means, axis=1)   # consecutive concepts c -> c+1 (cyclic)
    return {"top_bar": top.tolist(), "top_pi1": float(np.nanmax(pi)), "within_radius": within,
            "connect_radius": connect, "centre_gap_median": float(np.median(dm.min(1))),
            "within_concept_loop": bool(top[1] <= connect),
            "means_top_pi1": diagrams.max_ratio(diagrams.alpha_diagrams(means)[1]),
            "last_first_step_over_median": float(steps[-1] / np.median(steps))}


def localisation() -> dict:
    out = {}
    for d in CLUSTERED:
        c = realdata.cloud(d)
        out[d] = bar_scale(c["y"], source.concepts(d, c["labels"]).index, realdata.alpha(d)[1])
    return out


# ----------------------------------------------------------------------------- 3. closure ratio (prereg section 5)
def closure_rows() -> list[dict]:
    """Closure ratio d(last, first) / median d(c, c+1) of the concept means in the full activation space (cosine),
    for every dataset with concept structure: the concept variable, or 7 and 12 value bins for ordinal sets."""
    g = config.load()["groups"]
    ids = (g["cyclic_primary"] + g["cyclic_secondary"] + ["R7_llama_colors"] + g["ordinal"] + g["init_controls"]
           + [f"C1_{k}_{i}" for k in ("gp", "walk") for i in range(10)])
    rows = []
    for d in ids:
        c = realdata.cloud(d)
        for var, nb in alignment.variables(d):
            if var not in (None, "bins", "day"):                 # concept variable only (no time / mod-10 / mod-100)
                continue
            con = source.concepts(d, c["labels"], variable=None if var == "bins" else var, n_bins=nb or 7)
            means = np.stack([c["x"][con.index == k].mean(0) for k in range(len(con.phase))])
            rows.append({"id": d, "variable": con.variable, "n": len(con.phase),
                         "closure_ratio": cs.closure_ratio(means, "cosine")})
    return rows


# ----------------------------------------------------------------------------- 4. PCA diagnostics
def pca_rows() -> list[dict]:
    """Top-6 eigenvalue shares and the gap between the 3rd and 4th (small gap = unstable top-3 subspace)."""
    rows = []
    for d in KEY:
        fr = realdata.cloud(d)["frame"]
        sh = fr["eigvals"] / fr["total_var"]                     # share of total variance per principal axis
        rows.append({"id": d, **{f"l{i + 1}": float(v) for i, v in enumerate(sh)}, "gap34": float(sh[2] / sh[3])})
    return rows


def grok_fourier() -> dict:
    """Share of the grokked W_E variance per Fourier frequency over the residues (k and 113 - k pooled by rfft)."""
    c = realdata.cloud("R2_grokking_WE")
    a = np.array([int(s) for s in c["labels"]])
    x = c["x"][np.argsort(a)]                                    # rows in residue order 0..112
    p = (np.abs(np.fft.rfft(x - x.mean(0), axis=0)) ** 2).sum(1)  # power per frequency, summed over embedding dims
    p = p[1:] / p[1:].sum()                                      # drop k = 0 (the mean), normalise
    top = np.argsort(-p)[:8]
    return {"top_frequencies": [int(k + 1) for k in top], "shares": [float(p[k]) for k in top]}


# ----------------------------------------------------------------------------- 5. size-matched stability
def matched_stability(d: str, m: int = 199, n_null: int = 5) -> dict:
    """Exp2's subsample stability, but against a null threshold computed on subsamples of the same size:
    the mean null q95 over n_null 80% subsamples (m draws each, the dataset's own design)."""
    c = realdata.cloud(d)
    x, n = c["x"], len(c["x"])
    g = realdata.groups(d, c["labels"])
    rng = np.random.default_rng(1)
    q = []
    for j in range(n_null):
        sub = rng.choice(n, int(round(0.8 * n)), replace=False)
        nm = nulls.null_max_ratios(x[sub], realdata.design(d), None if g is None else g[sub], m=m,
                                   seed=nulls.dataset_seed(f"{d}_sub{j}", 0), maxdim=1)
        q.append(float(np.quantile(nm[:, 0], 0.95)))
    thr = float(np.mean(q))
    return {"q95_full": float(realdata.mc_significance(d, 0)["null_q95"][0]), "q95_sub": thr,
            "freq_full_threshold": float(pd.read_csv(config.path("results") / "exp2" / "invariants.csv")
                                         .set_index("id").loc[d, "loop_freq"]),
            "freq_matched_threshold": subsample_freq(x, thr)}


# ----------------------------------------------------------------------------- 6. post hoc theta_B checks
def posthoc_checks() -> dict:
    """For every relaxed-range theta_B (D5) of the key sets: overlap of its Rips class with the most persistent
    alpha H1 bar, and the number of concepts whose circular mean is exactly 0 (a constant coordinate)."""
    ph = read_json(config.path("results") / "exp3" / "posthoc_relaxed_range.json")
    out = {}
    for d in KEY:
        d1 = realdata.alpha(d)[1]
        top = d1[int(np.nanargmax(diagrams.ratios(d1)))]
        for dim in ("3d", "top10"):
            v = ph[d][dim]
            bar = v["rips_bar"]
            rec = (v["records"] or [{}])[0]
            out[f"{d}|{dim}"] = {
                "rips_bar": bar, "alpha_top_bar": top.tolist() if dim == "3d" else None,
                "overlap": None if bar is None or dim != "3d" else bool(min(top[1], bar[1]) > max(top[0], bar[0])),
                "constant_concepts": int(sum(t == 0.0 for t in rec.get("concept_theta", []))),
                "winding": rec.get("winding"), "R": rec.get("R"), "p": rec.get("p")}
    return out


# ----------------------------------------------------------------------------- 7. power v2 uncertainty
def power_rows() -> list[dict]:
    """Ring and arc loop-pass rates of power v2 with exact 95% CIs, interpolated at the real top-3 share."""
    res = config.path("results") / "power"
    p2 = pd.read_csv(res / "power_v2_summary.csv")
    so = {r["id"]: r["top3_explained"] for r in read_json(res / "real_second_order.json")}
    real = {7: so["R5a_llama_weekdays"], 12: so["R5b_llama_months"]}
    rows = []
    for k, top3 in real.items():
        for arr in ("ring", "arc300", "random"):
            t = p2[(p2["k"] == k) & (p2["arrangement"] == arr)].sort_values("top3")
            near = t.iloc[(t["top3"] - top3).abs().argmin()]     # the grid cell the README quoted
            lo, hi = binom_ci(int(round(near["loop"] * POWER_REPS)), POWER_REPS)
            rows.append({"k": k, "arrangement": arr, "real_top3": top3, "nearest_top3": float(near["top3"]),
                         "nearest_loop": float(near["loop"]), "ci_lo": lo, "ci_hi": hi,
                         "interp_loop": float(np.interp(top3, t["top3"], t["loop"])),
                         "loop_min": float(t["loop"].min()), "loop_max": float(t["loop"].max())})
    return rows


def run() -> None:
    m = config.load()["tda"]["mc_draws"]
    out = out_dir("exp7_audit")
    env_record("exp7_audit")
    res = {"colour_baseline": colour_baseline(m)}
    log.info("colour stimulus RGB: top pi %.2f vs null q95 %.2f (p = %.3f); Llama activations %.2f vs %.2f",
             res["colour_baseline"]["rgb"]["top_pi1"], res["colour_baseline"]["rgb"]["null_q95"],
             res["colour_baseline"]["rgb"]["p_loop"], res["colour_baseline"]["llama"]["top_pi1"],
             res["colour_baseline"]["llama"]["null_q95"])
    res["localisation"] = localisation()
    for d, v in res["localisation"].items():
        log.info("%-24s top bar [%.4f, %.4f]; clusters first touch at %.4f -> loop inside one cluster: %s; "
                 "means top pi %.2f", d, *v["top_bar"], v["connect_radius"], v["within_concept_loop"], v["means_top_pi1"])
    res["closure"] = closure_rows()
    res["pca"] = pca_rows()
    res["grok_fourier"] = grok_fourier()
    res["stability"] = {d: matched_stability(d) for d in STABILITY}
    for d, v in res["stability"].items():
        log.info("%-24s stability: %.2f (full-size threshold %.3f) vs %.2f (size-matched %.3f)", d,
                 v["freq_full_threshold"], v["q95_full"], v["freq_matched_threshold"], v["q95_sub"])
    res["posthoc"] = posthoc_checks()
    res["power"] = power_rows()
    write_json(out / "summary.json", res)
    pd.DataFrame(res["closure"]).to_csv(out / "closure_ratio.csv", index=False)
    log.info("wrote %s", out / "summary.json")
