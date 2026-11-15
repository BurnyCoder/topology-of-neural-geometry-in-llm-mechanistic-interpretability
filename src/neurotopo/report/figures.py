"""Figures for README, reports, paper and explorer, drawn from results/ (no hand-typed numbers).

Global context: `run.py report` calls every function here; each reads results files and writes a PNG to
docs/figures/. Axes start at zero for rates/accuracies, error bars are 95% CIs, and colours are consistent
across figures (cyclic concepts warm, ordinal concepts cool, controls grey).
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments.common import read_json

CYCLIC = ["R5a_llama_weekdays", "R5b_llama_months", "R2_grokking_WE", "R5c_llama_days_time"]
ORDINAL = ["R1_gpt2_wpos", "R4_llama_counting", "R4b_pythia_counting", "R6_llama_years", "R8a_llama_temperature",
           "R8b_llama_age"]
COL = {"cyclic": "#d1495b", "colours": "#edae49", "ordinal": "#00798c", "control": "#8d8d8d", "other": "#30638e"}


def group_of(d: str) -> str:
    if d in CYCLIC or d.replace("_means", "") in CYCLIC:
        return "cyclic"
    if d == "R7_llama_colors":
        return "colours"
    if d in ORDINAL:
        return "ordinal"
    if d.startswith("C"):
        return "control"
    return "other"


def short(d: str) -> str:
    """Readable dataset label (drops model prefixes)."""
    return (d.replace("_llama", "").replace("R5a_", "").replace("R5b_", "").replace("R5c_", "").replace("R2_", "")
            .replace("R1_", "").replace("R4_", "").replace("R4b_", "").replace("R6_", "").replace("R7_", "")
            .replace("R8a_", "").replace("R8b_", "").replace("R9_", "").replace("R3_", ""))


def save(fig, name: str) -> None:
    p = config.path("figures") / f"{name}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_pipeline() -> None:
    """Pipeline / architecture diagram of the two methods and the steering test (fixed-size boxes, straight arrows)."""
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(13, 4.4))
    ax.axis("off")
    w, h = 0.2, 0.22
    boxes = {
        "src": (0.0, 0.62, "shape-fitting repo (submodule)\n44 clouds: top-3 PCA points,\nlabels, fitted shapes", "#e0ecf4"),
        "hf": (0.0, 0.12, "Hugging Face inputs\nraw activations, 39k synthetic\nclouds + exact GT params", "#e0ecf4"),
        "A": (0.26, 0.62, "Method A: exact topology\nof the fitted shape\n(b0,b1,b2), chi, genus, rho_A", "#f4f1de"),
        "B": (0.26, 0.12, "Method B: alpha persistent\nhomology + design-matched\nMonte Carlo null", "#f4f1de"),
        "tA": (0.52, 0.62, "hole coordinate theta_A\n(parameter on the fit)", "#f4f1de"),
        "tB": (0.52, 0.12, "hole coordinate theta_B\n(persistent cohomology,\nDREiMac)", "#f4f1de"),
        "T": (0.78, 0.62, "travel around the hole:\nalignment R, permutation p,\nwinding = +-1", "#e8f5e9"),
        "S": (0.78, 0.12, "steering around the loop\n(simulated now, LLM later):\nconcept goes round once?", "#e8f5e9"),
    }
    for k, (x, y, t, c) in boxes.items():
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01", fc=c, ec="#555"))
        ax.text(x + w / 2, y + h / 2, t, fontsize=8.5, ha="center", va="center")
    def arrow(a, b):
        xa, ya = boxes[a][0] + w, boxes[a][1] + h / 2
        xb, yb = boxes[b][0], boxes[b][1] + h / 2
        ax.annotate("", xy=(xb, yb), xytext=(xa, ya), arrowprops=dict(arrowstyle="->", color="#444", lw=1))
    for a, b in [("src", "A"), ("src", "B"), ("hf", "B"), ("hf", "A"), ("A", "tA"), ("B", "tB"), ("tA", "T"),
                 ("tB", "T"), ("tB", "S"), ("tA", "S")]:
        arrow(a, b)
    ax.set_xlim(-0.01, 1.0)
    ax.set_ylim(0.05, 0.9)
    save(fig, "fig_pipeline")


def fig_exp0_helix() -> None:
    """Helix fits: axial-winding alignment R vs closure gap; cyclic concepts vs smooth random-process controls."""
    recs = read_json(config.path("results") / "exp0" / "real_alignment.json")
    rows = [r for r in recs if r["kind"].startswith("axial") and r.get("closure_gap") is not None
            and ("7 bins" in r["variable"] or "bins" not in r["variable"])]
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for r in rows:
        g = group_of(r["id"])
        ax.scatter(r["closure_gap"], r["R"], c=COL[g], s=50, edgecolor="k", lw=0.4, zorder=3)
        if g != "control" and not r["id"].endswith("_means"):
            ax.annotate(short(r["id"]), (r["closure_gap"], r["R"]), fontsize=8, xytext=(6, -10), textcoords="offset points")
    ax.scatter([], [], c=COL["cyclic"], label="cyclic concept (helix fit)")
    ax.scatter([], [], c=COL["control"], label="Gaussian-process control (helix fit)")
    ax.set_xlabel("closure gap (axial distance first-last concept / radius)")
    ax.set_ylabel("axial-winding alignment R")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Method A, helix fits: winding is not specific, closure is", fontsize=10)
    save(fig, "fig_exp0_helix")


def fig_exp0_margin() -> None:
    """Exact topology of every real fit: margin ratio rho_A (log scale), marker by Betti vector."""
    d = pd.read_csv(config.path("results") / "exp0" / "real_topology.csv")
    d = d[np.isfinite(d["rho_A"])].sort_values("rho_A")
    fig, ax = plt.subplots(figsize=(7, 8))
    y = np.arange(len(d))
    for i, (_, r) in enumerate(d.iterrows()):
        mk = "o" if r["b1"] == 0 and r["b2"] == 0 else ("s" if r["b1"] > 0 else "^")
        ax.scatter(r["rho_A"], i, c=COL[group_of(r["id"])], marker=mk, s=40, edgecolor="k", lw=0.4)
    ax.axvline(1, color="k", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{short(i)} ({f})" for i, f in zip(d["id"], d["family"])], fontsize=7)
    ax.set_xlabel("margin ratio rho_A = margin / (2 nu)   (>= 1: fitted topology resolvable)")
    for mk, lab in (("o", "no hole (b1 = b2 = 0)"), ("s", "hole (b1 = 1)"), ("^", "void (b2 = 1)")):
        ax.scatter([], [], marker=mk, c="w", edgecolor="k", label=lab)
    ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Method A: exact topology of the 44 fitted shapes", fontsize=10)
    save(fig, "fig_exp0_margin")


def fig_exp1_estimators() -> None:
    """Exp1: macro exact Betti-vector accuracy (95% cluster-bootstrap CI) of every estimator on resolvable clouds."""
    s = read_json(config.path("results") / "exp1" / "summary.json")
    names = [k for k in s["table"] if "subset" not in k]
    est = [s["table"][k]["macro_exact"] for k in names]
    lo = [s["table"][k]["macro_exact"] - s["table"][k]["ci"][0] for k in names]
    hi = [s["table"][k]["ci"][1] - s["table"][k]["macro_exact"] for k in names]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(range(len(names)), est, xerr=[lo, hi], color=["#30638e" if k.startswith(("P", "S")) else "#bbbbbb" for k in names],
            capsize=3)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("exact (b0, b1, b2) accuracy, macro over 13 families (resolvable clouds, 95% CI)")
    ax.invert_yaxis()
    save(fig, "fig_exp1_estimators")


def fig_exp1_by_rho() -> None:
    """Exp1: accuracy against the margin ratio rho_A (all clouds, including unresolvable ones)."""
    s = read_json(config.path("results") / "exp1" / "summary.json")
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    for name, d in s["accuracy_by_rho"].items():
        ks = list(d.keys())
        ax.plot(range(len(ks)), [d[k] for k in ks], marker="o", label=name)
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(ks, fontsize=7, rotation=20)
    ax.axvline(2.5, color="k", ls="--", lw=0.8)
    ax.set_ylim(0, 1)
    ax.set_xlabel("margin ratio rho_A bin (right of dashed line: resolvable)")
    ax.set_ylabel("exact (b0,b1,b2) accuracy")
    ax.legend(fontsize=7)
    save(fig, "fig_exp1_by_rho")


def fig_real_gallery(ids: list[str], name: str) -> None:
    """3D clouds (PC1-PC2 view, coloured by concept) with their alpha H1/H2 persistence and the MC threshold."""
    from neurotopo.experiments import realdata
    from neurotopo.tda import diagrams
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    fig, axes = plt.subplots(2, len(ids), figsize=(3.1 * len(ids), 6))
    for j, d in enumerate(ids):
        c = realdata.cloud(d)
        y = c["y"]
        try:
            con = source.concepts(d, c["labels"], n_bins=12)
            col = con.index / max(con.index.max(), 1)
        except ValueError:
            col = np.zeros(len(y))
        axes[0, j].scatter(y[:, 0], y[:, 1], c=col, cmap="twilight" if group_of(d) in ("cyclic", "colours") else "viridis",
                           s=8)
        axes[0, j].set_title(f"{short(d)}\n({source.real_results()[d]['family']} fit)", fontsize=8)
        axes[0, j].set_xticks([])
        axes[0, j].set_yticks([])
        dg = realdata.alpha(d)
        for k, mk in ((1, "o"), (2, "^")):
            pi = diagrams.ratios(dg[k])
            if pi.size:
                axes[1, j].scatter(np.full(pi.size, k) + np.random.default_rng(0).uniform(-0.15, 0.15, pi.size), pi, s=8,
                                   marker=mk, c="k", alpha=0.5)
        axes[1, j].hlines([inv.loc[d, "null_q95_pi1"]], 0.7, 1.3, color="r", lw=1.5)
        axes[1, j].hlines([inv.loc[d, "null_q95_pi2"]], 1.7, 2.3, color="r", lw=1.5)
        axes[1, j].set_xticks([1, 2])
        axes[1, j].set_xticklabels(["H1", "H2"])
        axes[1, j].set_yscale("log")
        axes[1, j].set_ylim(1, max(10, float(np.nanmax(np.r_[diagrams.ratios(dg[1]), 2])) * 1.3))
        if j == 0:
            axes[1, j].set_ylabel("persistence ratio pi = death/birth\n(red: null 95th pct of max pi)", fontsize=8)
    save(fig, name)


def fig_exp6sim() -> None:
    """Simulated steering: T (mean traversal R) of loop B, loop A, chord and the random-loop 95th percentile."""
    s = read_json(config.path("results") / "exp6_sim" / "simulated_steering.json")
    ids = [d for d in s if "B_cohomology" in s[d] or "A_fitted_axis_circle" in s[d] or "chord_centroids" in s[d]]
    ids = [d for d in ids if not d.startswith("C1_")] + [d for d in ids if d.startswith("C1_")][:4]
    fig, ax = plt.subplots(figsize=(8, 0.32 * len(ids) + 1.2))
    for i, d in enumerate(ids):
        r = s[d]
        for key, mk, colr in (("B_cohomology", "o", "#d1495b"), ("A_fitted_axis_circle", "s", "#edae49"),
                              ("chord_centroids", "D", "#30638e")):
            if key in r:
                ax.scatter(r[key]["T"], i, marker=mk, c=colr, s=40, edgecolor="k", lw=0.4)
        if "random_null" in r:
            ax.plot([0, r["random_null"]["T_random_q95"]], [i, i], color="#bbbbbb", lw=3, zorder=0)
    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels([f"{short(d)}{' (hole)' if s[d].get('hole_detected_B') else ''}" for d in ids], fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_xlabel("simulated steering: mean traversal R of the decoded concept (1 = goes round in order)")
    for mk, colr, lab in (("o", "#d1495b", "loop B (cohomology)"), ("s", "#edae49", "loop A (fitted axis)"),
                          ("D", "#30638e", "chord through centroids")):
        ax.scatter([], [], marker=mk, c=colr, label=lab)
    ax.plot([], [], color="#bbbbbb", lw=3, label="random loops (0 to 95th pct)")
    ax.legend(fontsize=7, loc="lower right")
    ax.invert_yaxis()
    save(fig, "fig_exp6sim")
