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
        "S": (0.78, 0.12, "steering around the loop\n(postponed):\nconcept goes round once?", "#e8f5e9"),
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
    ax.set_title("Method A, helix fits: winding is not specific;\nonly months close more tightly than every control",
                 fontsize=10)
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


def _concept_ring(ax, th: np.ndarray, title: str, first: str) -> None:
    """Concept circular means on the unit circle (x = cos, y = sin), coloured by semantic position (cyclic
    colour map) and joined by chords in semantic order. One clean polygon = the cycle goes round once in order."""
    th = np.asarray(th, dtype=np.float64)
    ok = np.flatnonzero(np.isfinite(th))
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), color="#dddddd", lw=0.8, zorder=0)
    loop = np.r_[ok, ok[:1]]
    ax.plot(np.cos(th[loop]), np.sin(th[loop]), color="#777777", lw=0.7, zorder=1)
    ax.scatter(np.cos(th[ok]), np.sin(th[ok]), c=plt.cm.twilight(ok / th.size), s=30 if th.size < 40 else 9,
               edgecolor="k", lw=0.3, zorder=2)
    x0, y0 = np.cos(th[ok[0]]), np.sin(th[ok[0]])
    ax.annotate(first, (x0, y0), xytext=(1.3 * x0, 1.3 * y0), fontsize=7, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color="#555555", lw=0.5))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)


def fig_traversal() -> None:
    """Travel around the hole: per-concept mean hole angle for the cyclic sets with a coordinate (theta_B from
    persistent cohomology, theta_A from the fitted shape) and, for contrast, the weekday helix fit and a
    Gaussian-process control fitted as a helix (its azimuth also winds: axial winding is not specific)."""
    from neurotopo.stats import circular as cs
    res = config.path("results")
    mb = read_json(res / "exp3" / "method_b.json")
    ph = read_json(res / "exp3" / "posthoc_relaxed_range.json")
    a0 = read_json(res / "exp0" / "real_alignment.json")

    def pick(d, var):
        return next(r for r in a0 if r["id"] == d and r["variable"] == var)

    col = mb["R7_llama_colors"]["records3"][0]
    grok = mb["R2_grokking_WE"]["records3"][0]
    tb = np.load(res / "exp3" / "theta_B.npz")["R2_grokking_WE"]
    labels = np.array([int(s) for s in source.load_viz("R2_grokking_WE")["labels"]])
    grok_th = cs.concept_means(tb, (grok["k"] * labels) % 113, 113)      # residues ordered around the k-circle
    mon = ph["R5b_llama_months"]["3d"]["records"][0]
    cone, wk, gp = pick("R7_llama_colors", "hue"), pick("R5a_llama_weekdays", "day of week"), pick("C1_gp_3", "value in 7 bins")
    panels = [
        (col["concept_theta"], f"colours, theta_B (prereg.)\nR = {col['R']:.2f}, winding {col['winding']}", "hue 0"),
        (cone["concept_theta"], f"colours, theta_A (fitted cone)\nR = {cone['R']:.2f}, winding {cone['winding']}", "hue 0"),
        (grok_th, f"residues mod 113, theta_B, k = {grok['k']}\nR = {grok['R']:.2f}, winding {grok['winding']}", "r = 0"),
        (mon["concept_theta"], f"months, theta_B (post hoc)\nR = {mon['R']:.2f}, winding {mon['winding']}", "Jan"),
        (wk["concept_theta"], f"weekdays, helix azimuth\nR = {wk['R']:.2f}, winding {wk['winding']}", "Mon"),
        (gp["concept_theta"], f"control (Gaussian process),\nhelix azimuth R = {gp['R']:.2f}, winding {gp['winding']}", "bin 1"),
    ]
    fig, axes = plt.subplots(1, len(panels), figsize=(2.4 * len(panels), 2.9))
    for ax, (th, title, first) in zip(axes, panels):
        _concept_ring(ax, th, title, first)
    save(fig, "fig_traversal")


def fig_null_tests() -> None:
    """Loop test per dataset: Monte Carlo null distribution of the maximum H1 persistence ratio (999 draws,
    design-matched) with the observed top ratio (solid line) and the null's 95th percentile (dashed)."""
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    ids = ["R7_llama_colors", "R2_grokking_WE", "R5b_llama_months", "R5c_llama_days_time", "R5a_llama_weekdays",
           "R6_llama_years", "R4_llama_counting", "R1_gpt2_wpos", "C3_llama_weekdays_init", "C1_gp_0"]
    fig, axes = plt.subplots(2, 5, figsize=(14, 5.2))
    for ax, d in zip(axes.ravel(), ids):
        nm = np.load(config.path("results") / "nulls" / f"{d}_seed0.npy")[:, 0]
        obs = float(inv.loc[d, "top_pi1"])
        hi = max(float(np.nanmax(nm)), obs) * 1.05
        ax.hist(nm, bins=np.linspace(1, hi, 40), color="#bbbbbb")
        ax.axvline(inv.loc[d, "null_q95_pi1"], color="k", ls="--", lw=0.8)
        ax.axvline(obs, color=COL[group_of(d)], lw=2)
        ax.set_title(f"{short(d)}: p = {inv.loc[d, 'p_top_loop']:.3f}", fontsize=8)
        ax.set_xlim(0.97, hi)                                 # observed pi can be ~1 (no real loop)
        ax.tick_params(labelsize=7)
    for ax in axes[1]:
        ax.set_xlabel("max H1 persistence ratio pi", fontsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("null draws", fontsize=8)
    fig.tight_layout()
    save(fig, "fig_null_tests")


def fig_top10() -> None:
    """Top-10-PC loop test (post hoc, D6): observed max Rips H1 ratio vs the matched null's 95th percentile."""
    t = pd.read_csv(config.path("results") / "exp5" / "topk_null.csv")
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    for i, r in enumerate(t.itertuples()):
        c = COL[group_of(r.id)]
        ax.plot([r.null_q95, r.rips_pi1], [i, i], color="#cccccc", lw=2, zorder=0)
        ax.scatter(r.null_q95, i, marker="|", c="k", s=120, zorder=1)
        ax.scatter(r.rips_pi1, i, c=c if r.p_loop < 0.05 else "w", edgecolor=c, s=45, lw=1.2, zorder=2)
    ax.set_yticks(range(len(t)))
    ax.set_yticklabels([short(d) for d in t["id"]], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("max Rips H1 persistence ratio in the top-10 PCs (|: null 95th percentile)")
    ax.scatter([], [], c="k", label="p < 0.05 (filled)")
    ax.scatter([], [], c="w", edgecolor="k", label="p >= 0.05 (open)")
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("Top-10 PCs: loops are not specific to cyclic concepts", fontsize=10)
    save(fig, "fig_top10")


def fig_power() -> None:
    """Corrected power simulation (post hoc, v2): pass rate of the loop test and of the full preregistered
    conjunction for rings, open 300-degree arcs and random placements of 7 or 12 clusters vs top-3 variance."""
    s = pd.read_csv(config.path("results") / "power" / "power_v2_summary.csv")
    real = {r["id"]: r["top3_explained"] for r in read_json(config.path("results") / "power" / "real_second_order.json")}
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, (k, d) in zip(axes, ((7, "R5a_llama_weekdays"), (12, "R5b_llama_months"))):
        for arr, c in (("ring", COL["cyclic"]), ("arc300", COL["ordinal"]), ("random", COL["control"])):
            q = s[(s["k"] == k) & (s["arrangement"] == arr)].sort_values("top3")
            ax.plot(q["top3"], q["loop"], marker="o", color=c, label=f"{arr}: loop test")
            if arr == "ring":
                ax.plot(q["top3"], q["all"], marker="s", ls="--", color=c, label="ring: full conjunction")
        ax.axvline(real[d], color="k", ls=":", lw=1)
        ax.text(real[d], 1.03, f" real {short(d)}", fontsize=7)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("top-3 explained variance of the simulated cloud")
        ax.set_title(f"{k} clusters of {k} points in R^4096", fontsize=9)
    axes[0].set_ylabel("fraction of replicates passing")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, fontsize=7, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.08))
    save(fig, "fig_power")


def fig_exp4() -> None:
    """Exp4: MDS map of bottleneck distances on significant bars (clouds and ideal templates) and the
    average-linkage dendrogram."""
    from scipy.cluster.hierarchy import dendrogram
    s = read_json(config.path("results") / "exp4" / "summary.json")
    names, mds = s["names"], np.asarray(s["mds"])
    tmpl = {i for i, k in enumerate(s["kinds"]) if k == "template"}
    # Clouds without significant bars all have distance 0 to each other and to the line/helix/blob templates,
    # so they share one MDS point: draw it once with a group label instead of overlapping labels.
    empty = np.flatnonzero(np.linalg.norm(mds - mds[names.index("template: line")], axis=1) < 1e-6)
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1, 1.4]})
    for i, d in enumerate(names):
        if i in empty:
            continue
        if i in tmpl:
            a.scatter(*mds[i], marker="*", s=120, c="k")
            a.annotate(d.replace("template: ", ""), mds[i], fontsize=7, xytext=(5, 3), textcoords="offset points")
        else:
            a.scatter(*mds[i], c=COL[group_of(d)], s=30, edgecolor="k", lw=0.3)
            if group_of(d) in ("cyclic", "colours", "ordinal") or d == "C3_llama_counting_init":
                a.annotate(short(d), mds[i], fontsize=6, xytext=(3, -8), textcoords="offset points")
    n_cl = sum(i not in tmpl for i in empty)
    a.scatter(*mds[empty[0]], marker="X", s=90, c="#555555")
    a.annotate(f"no significant bars:\n{n_cl} clouds + line, helix,\nblob templates", mds[empty[0]], fontsize=6,
               xytext=(-120, 25), textcoords="offset points", arrowprops=dict(arrowstyle="-", color="#555555", lw=0.5))
    for g in ("cyclic", "colours", "ordinal", "control", "other"):
        a.scatter([], [], c=COL[g], label=g)
    a.scatter([], [], marker="*", c="k", label="ideal template")
    a.legend(fontsize=7)
    a.set_title("MDS of bottleneck distances (significant bars)", fontsize=9)
    a.set_xlabel("MDS 1")
    a.set_ylabel("MDS 2")
    dendrogram(np.asarray(s["linkage"]), labels=[f"*{d}" if i in tmpl else short(d) for i, d in enumerate(names)],
               ax=b, leaf_font_size=6, color_threshold=0, above_threshold_color="#555555")
    b.set_ylabel("bottleneck distance (average linkage)")
    b.set_title("Dendrogram (* = ideal template)", fontsize=9)
    save(fig, "fig_exp4")


def fig_exp1_outliers() -> None:
    """Exp1 (D7): false-positive rate on resolvable contractible clouds with and without detected outliers,
    per estimator, with 95% cluster-bootstrap CIs and the preregistered 10% DTM threshold."""
    s = read_json(config.path("results") / "exp1" / "outliers.json")
    names = [k for k in s["fpr"] if k != "Bc_majority"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for j, (lab, c) in enumerate((("clean", "#bbbbbb"), ("outlier", "#d1495b"))):
        est = np.array([s["fpr"][n][lab]["fpr"] for n in names])
        ci = np.array([s["fpr"][n][lab]["ci"] for n in names])
        ax.barh(np.arange(len(names)) + (j - 0.5) * 0.38, est, height=0.38, color=c,
                xerr=[est - ci[:, 0], ci[:, 1] - est], capsize=2, label=f"{lab} clouds")
    ax.axvline(s["threshold"], color="k", ls="--", lw=0.8)
    ax.text(s["threshold"], -0.6, " DTM threshold (prereg.)", fontsize=7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(0.15, max(s["fpr"][n]["outlier"]["ci"][1] for n in names) * 1.1))
    ax.set_xlabel("false-positive rate (any H1/H2 on a contractible shape), 95% CI")
    ax.legend(fontsize=7, loc="lower right")
    save(fig, "fig_exp1_outliers")


def anim_clouds() -> None:
    """Rotating 3D views (animated GIF) of four clouds in their top-3 PCs, coloured by semantic position:
    colours (hue, a robust loop), residues mod 113 (ordered by k r mod 113, k from theta_B), months, weekdays.
    matplotlib.animation.FuncAnimation + PillowWriter (https://matplotlib.org/stable/api/animation_api.html)."""
    from matplotlib.animation import FuncAnimation, PillowWriter
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import concept_positions, grok_k
    sets = [("R7_llama_colors", "colours (hue)"), ("R2_grokking_WE", f"residues mod 113 (k = {grok_k()})"),
            ("R5b_llama_months", "months"), ("R5a_llama_weekdays", "weekdays")]
    fig = plt.figure(figsize=(12, 3.6))
    axes = []
    for j, (d, title) in enumerate(sets):
        c = realdata.cloud(d)
        pos = concept_positions(d, c["labels"])
        ax = fig.add_subplot(1, len(sets), j + 1, projection="3d")
        ax.scatter(*c["y"].T, c=pos, cmap="twilight", s=6 if len(pos) > 200 else 14, depthshade=False)
        ax.set_title(title, fontsize=9)
        ax.set_axis_off()
        axes.append(ax)
    fig.suptitle("Top-3 PCA clouds, coloured by position in the semantic cycle (cyclic colour map)", fontsize=9)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.88, wspace=0)

    def turn(i):
        for ax in axes:
            ax.view_init(elev=20, azim=i * 10)
        return axes

    FuncAnimation(fig, turn, frames=36).save(config.path("figures") / "anim_clouds.gif", writer=PillowWriter(fps=10), dpi=80)
    plt.close(fig)


def fig_examples() -> None:
    """Plain-language positive and negative examples. Top: each cloud (PC1-PC2), coloured by position in its cycle
    (years: by value), titled with the two verdicts of report/examples.headline (is there a ring; does the concept
    go around it once). Bottom: observed top H1 persistence ratio / the null's 95th percentile, so a bar above 1 is
    a significant loop (p < 0.05)."""
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import EXAMPLES, concept_positions, headline
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    fig = plt.figure(figsize=(15, 5.8))
    gs = fig.add_gridspec(2, len(EXAMPLES), height_ratios=[1.25, 1], hspace=0.38)
    ratios, cols = [], []
    for j, (d, name) in enumerate(EXAMPLES):
        c = realdata.cloud(d)
        pos = concept_positions(d, c["labels"])
        ax = fig.add_subplot(gs[0, j])
        ax.scatter(c["y"][:, 0], c["y"][:, 1], c=pos, cmap="viridis" if d == "R6_llama_years" else "twilight",
                   s=5 if len(pos) > 200 else 12)
        ax.set_xticks([])
        ax.set_yticks([])
        h = headline(d)
        ax.set_title(f"{name}\n{h['verdict']}\ngoes around once: {h['goes']}", fontsize=8.5, color=h["colour"])
        ratios.append(float(inv.loc[d, "top_pi1"] / inv.loc[d, "null_q95_pi1"]))
        cols.append("#1b7837" if h["ring"] else "#bbbbbb")
    ax = fig.add_subplot(gs[1, :])
    ax.bar(range(len(EXAMPLES)), ratios, color=cols, width=0.5)
    ax.axhline(1, color="k", ls="--", lw=0.9, label="null 95th percentile")
    ax.legend(loc="upper right", fontsize=8, frameon=False)        # empty corner: no clash with bar labels
    ax.set_xticks(range(len(EXAMPLES)))
    ax.set_xticklabels([n.replace("\n", " ") for _, n in EXAMPLES], fontsize=8)
    ax.set_xlim(-0.5, len(EXAMPLES) - 0.5)
    ax.set_ylim(0, max(ratios) * 1.15)
    ax.set_ylabel("top loop persistence / Gaussian null's\n95th pct. (above 1 = significant loop)", fontsize=8)
    for i, r in enumerate(ratios):
        inside_bar = 0.8 < r < 0.97                                 # label just below the dashed line: put it in the bar
        ax.text(i, r - 0.03 if inside_bar else r + 0.03, f"{r:.2f}", ha="center", va="top" if inside_bar else "bottom",
                fontsize=8)
    save(fig, "fig_examples")


def fig_toy() -> None:
    """Worked example (docs/worked_example.md): the 7-concept toy cloud from experiments/toy_example.py.
    Top: discs of radius r around every point at three radii (a tiny loop inside one concept; 7 separate blobs;
    the ring through all concepts). Bottom: the H1 persistence diagram with the null's 95th-percentile line
    d = q95 * b, the null distribution of the max persistence ratio, and the concepts' mean theta_B angles."""
    from matplotlib.patches import Circle
    s = read_json(config.path("results") / "toy" / "summary.json")
    num, dat = s["numbers"], s["data"]
    y, con, n = np.array(dat["points"]), np.array(dat["concept"]), num["n"]
    col = plt.get_cmap("tab10")(np.arange(n))                 # categorical: twilight's ends are near white
    fig, ax = plt.subplots(2, 3, figsize=(13, 8.6))
    radii = [(num["tiny_b"] + num["tiny_d"]) / 2, (num["tiny_d"] + num["big_b"]) / 2, (2 * num["big_b"] + num["big_d"]) / 3]
    titles = [f"(a) r = {radii[0]:.3f}: a tiny loop inside one\nconcept (zoom on {dat['names'][0]}; \u03c0 = {num['tiny_pi']:.2f})",
              f"(b) r = {radii[1]:.2f}: 7 separate blobs,\nno loop",
              f"(c) r = {radii[2]:.2f}: the ring through all\nconcepts (born {num['big_b']:.3f}, dies {num['big_d']:.3f})"]
    for j, r in enumerate(radii):
        a = ax[0, j]
        for (px, py), c in zip(y, con):
            a.add_patch(Circle((px, py), r, color=col[c], alpha=0.16, lw=0))
        a.scatter(y[:, 0], y[:, 1], c=col[con], s=10 if j else 40, zorder=3, edgecolors="k", linewidths=0.3)
        if j == 0:                                             # zoom on concept 0's triangle
            cx, cy = y[con == 0].mean(0)
            a.set_xlim(cx - 0.12, cx + 0.12)
            a.set_ylim(cy - 0.12, cy + 0.12)
        else:
            a.set_xlim(-1.35, 1.35)
            a.set_ylim(-1.35, 1.35)
        a.set_aspect("equal")
        a.set_xticks([])
        a.set_yticks([])
        a.set_title(titles[j], fontsize=9.5)
    a = ax[1, 0]                                              # persistence diagram
    h1 = np.array(dat["h1"])
    top = 1.08 * h1[:, 1].max()
    a.plot([0, top], [0, top], color="#999", lw=0.8, label="diagonal (\u03c0 = 1)")
    a.plot([0, top / num["null_q95"]], [0, top], color="#d1495b", ls="--", lw=0.9,
           label=f"null 95th pct. (\u03c0 = {num['null_q95']:.2f})")
    a.scatter(h1[:, 0], h1[:, 1], color="k", s=18, zorder=3)
    a.annotate(f"{num['n_tiny']} tiny loops, \u03c0 = {num['tiny_pi']:.2f}", (num["tiny_b"], num["tiny_d"]),
               xytext=(0.12, 0.05), fontsize=8.5, arrowprops={"arrowstyle": "-", "lw": 0.6})
    a.annotate(f"ring, \u03c0 = {num['big_pi']:.2f}", (num["big_b"], num["big_d"]), xytext=(num["big_b"] + 0.06, num["big_d"] - 0.08),
               fontsize=8.5)
    a.set_xlim(0, top)
    a.set_ylim(0, top)
    a.set_aspect("equal")
    a.set_xlabel("birth radius b")
    a.set_ylabel("death radius d")
    a.legend(fontsize=8, loc="lower right", frameon=False)
    a.set_title("(d) H1 persistence diagram (alpha complex)", fontsize=9.5)
    a = ax[1, 1]                                              # null distribution of the max persistence ratio
    nm = np.array(dat["null_max"])
    a.hist(nm, bins=np.linspace(1.0, max(nm.max(), num["big_pi"]) + 0.1, 40), color="#bbbbbb")
    a.axvline(num["null_q95"], color="#d1495b", ls="--", lw=0.9, label=f"95th percentile {num['null_q95']:.2f}")
    a.axvline(num["big_pi"], color="k", lw=1.2, label=f"toy cloud {num['big_pi']:.2f} (p = {num['null_p']:.3f})")
    a.set_xlabel("largest H1 \u03c0 in a null cloud")
    a.set_ylabel(f"null clouds (of {num['null_m']})")
    a.legend(fontsize=8, frameon=False)
    a.set_title("(e) cluster-centre Monte Carlo null", fontsize=9.5)
    a = ax[1, 2]                                              # traversal: concept mean angles of theta_B
    tc = np.array(dat["concept_theta"])
    a.add_patch(Circle((0, 0), 1, fill=False, color="#999", lw=0.8))
    xy = np.c_[np.cos(tc), np.sin(tc)]
    a.plot(*np.r_[xy, xy[:1]].T, color="#555", lw=0.8)
    a.scatter(xy[:, 0], xy[:, 1], c=col, s=60, zorder=3, edgecolors="k", linewidths=0.4)
    for c in range(n):
        a.text(1.2 * xy[c, 0], 1.2 * xy[c, 1], dat["names"][c], ha="center", va="center", fontsize=8.5)
    a.set_xlim(-1.45, 1.45)
    a.set_ylim(-1.45, 1.45)
    a.set_aspect("equal")
    a.axis("off")
    a.set_title(f"(f) concept means of \u03b8_B: R = {num['R']:.3f}, p = {num['p_align']:.4f},\nwinding {num['w']}",
                fontsize=9.5)
    fig.tight_layout()
    save(fig, "fig_toy")


def anim_examples() -> None:
    """How the six example results were made (animated GIF near the top of the README). For each example cloud:
    top, the edges of its alpha complex present at radius r, in 3D, with one representative cycle of every loop
    alive at r drawn in that loop's own colour; bottom, its loop persistence diagram (log axes), each loop a dot in
    the same colour (solid while alive, faded otherwise), the most persistent loop ringed, the null's 95th-percentile
    line d = q95 * b (dashed) and the connect radius (dotted). r sweeps one logarithmic range for all clouds (each
    has RMS radius 1).
    Data from report/examples.py; matplotlib FuncAnimation + PillowWriter, Line3DCollection for the edges
    (https://matplotlib.org/stable/api/animation_api.html)."""
    from matplotlib.animation import FuncAnimation, PillowWriter
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from neurotopo.report.examples import EXAMPLES, example
    ex = [example(d) for d, _ in EXAMPLES]
    rmin, rmax = 0.004, 1.2
    radii = np.r_[rmin * (rmax / rmin) ** np.linspace(0, 1, 64), np.full(12, rmax)]     # sweep, then hold
    fig = plt.figure(figsize=(15, 6.6))
    gs = fig.add_gridspec(2, len(ex), height_ratios=[1.25, 1], hspace=0.22, wspace=0.18, top=0.88, bottom=0.12)
    panels = []
    for j, e in enumerate(ex):
        y, h1 = e["points"], e["h1"]
        a3 = fig.add_subplot(gs[0, j], projection="3d")
        a3.scatter(*y.T, c=e["pos"], cmap="twilight" if e["cyclic"] else "viridis", vmin=0, vmax=1,
                   s=2 if len(y) > 300 else 7, depthshade=False)
        lc = Line3DCollection(np.zeros((1, 2, 3)), colors="#777", linewidths=0.3, alpha=0.45)
        a3.add_collection3d(lc)
        ll = Line3DCollection(np.zeros((1, 2, 3)), linewidths=2.0, zorder=5)       # alive loops, own colours
        a3.add_collection3d(ll)
        a3.computed_zorder = False                                               # draw loops on top of points and edges
        rings = [np.r_[c, c[:1]] for c in e["cycles"]]                           # closed cycles of vertex indices
        loop_seg = [np.stack([y[g[:-1]], y[g[1:]]], 1) for g in rings]
        rgba = matplotlib.colors.to_rgba_array(e["loop_colour"]) if len(h1) else np.zeros((0, 4))
        lim = float(np.abs(y).max())
        a3.set_xlim(-lim, lim)
        a3.set_ylim(-lim, lim)
        a3.set_zlim(-lim, lim)
        a3.set_box_aspect((1, 1, 1), zoom=1.6)                     # fill the panel (matplotlib >= 3.6)
        a3.set_axis_off()
        a3.set_title(f"{e['name']}\n{e['verdict']}", fontsize=8, color=e["colour"])
        ap = fig.add_subplot(gs[1, j])
        ap.loglog([rmin, rmax], [rmin, rmax], color="#999", lw=0.8)
        ap.loglog([rmin, rmax / e["q95"]], [rmin * e["q95"], rmax], color="#d1495b", ls="--", lw=0.9)
        if e["connect_r"]:
            ap.axhline(e["connect_r"], color="#555", ls=":", lw=0.9)
        dots = ap.scatter(h1[:, 0], h1[:, 1], s=6, c=rgba, edgecolors="none", zorder=3)
        top = h1[e["top"]]
        ap.scatter([top[0]], [top[1]], s=70, facecolors="none", edgecolors="k", linewidths=1.1, zorder=4)
        cross, = ap.plot([], [], color="k", lw=0.6, alpha=0.6)             # current r (solid; dotted = connect radius)
        ap.text(0.04, 0.96, f"top loop: \u03c0 / q95 = {e['ratio']:.2f}", transform=ap.transAxes, fontsize=7.5, va="top")
        ap.set_xlim(rmin, rmax)
        ap.set_ylim(rmin, rmax)
        ap.set_aspect("equal")
        ap.tick_params(labelsize=7)
        ap.set_xlabel("birth radius", fontsize=7.5)
        if j == 0:
            ap.set_ylabel("death radius", fontsize=7.5)
        panels.append((a3, lc, ll, y[e["edges"]], loop_seg, rgba, e, dots, cross, ap.set_title("", fontsize=8)))
    sup = fig.suptitle("", fontsize=11)
    fig.text(0.5, 0.012, "Top: edges of the alpha complex at radius r (3D). Each loop has its own colour: while alive at r, one cycle of it "
             "is drawn in 3D and its dot below is solid (faded: not alive).\nBottom: each loop as (birth, death); ringed = most "
             "persistent, black lines = current r. Above the dashed line: beats the null's 95th percentile. "
             "Below the dotted line: dies before two concepts' clusters touch (a loop inside one cluster).", ha="center", fontsize=8)

    def frame(i):
        r = radii[i]
        for a3, lc, ll, seg, loop_seg, rgba, e, dots, cross, title in panels:
            n = int(np.searchsorted(e["edge_r"], r, side="right"))          # edges are sorted by entry radius
            lc.set_segments(seg[:n] if n else np.zeros((1, 2, 3)))
            a3.view_init(elev=18, azim=35 + 1.5 * i)
            alive = (e["h1"][:, 0] <= r) & (r < e["h1"][:, 1])
            on = np.flatnonzero(alive)
            if on.size:                                                    # one cycle per alive loop, in its colour
                ll.set_segments(np.concatenate([loop_seg[k] for k in on]))
                ll.set_color(np.concatenate([np.repeat(rgba[k:k + 1], len(loop_seg[k]), 0) for k in on]))
            else:
                ll.set_segments(np.zeros((1, 2, 3)))
                ll.set_color([(0, 0, 0, 0)])
            face = rgba.copy()
            face[:, 3] = np.where(alive, 1.0, 0.15)                        # solid while alive, faded otherwise
            dots.set_facecolor(face)
            dots.set_sizes(np.where(alive, 18, 6))
            cross.set_data([r, r, np.nan, rmin, r], [r, rmax, np.nan, r, r])
            title.set_text(f"loops alive at r: {int(alive.sum())}")
        sup.set_text(f"How the example results were made: balls of radius r = {r:.3f} around every point "
                     "(all clouds have RMS radius 1)")
        return []

    FuncAnimation(fig, frame, frames=len(radii)).save(config.path("figures") / "anim_examples.gif",
                                                      writer=PillowWriter(fps=8), dpi=68)
    plt.close(fig)


def fig_detected_loops() -> None:
    """The detected circles (README, near the top). For each example cloud, top: the cloud in its top-3 PCA
    coordinates with one closed path of edges carrying its most persistent loop (diagrams.alpha_h1_cycles) drawn
    in red, viewed face-on (camera along the normal of the path's best-fit plane, from an SVD of its vertices);
    a loop smaller than a tenth of the cloud is also circled so it can be found. Bottom: the persistence diagram
    (log axes) with that loop's dot, the null's 95th-percentile line and the connect radius. Data: report/examples.py."""
    from neurotopo.report.examples import EXAMPLES, example
    ex = [example(d) for d, _ in EXAMPLES]
    rmin, rmax, red = 0.004, 1.2, "#d62728"
    fig = plt.figure(figsize=(15, 6.2))
    gs = fig.add_gridspec(2, len(ex), height_ratios=[1.35, 1], hspace=0.16, wspace=0.18, top=0.88, bottom=0.12)
    for j, e in enumerate(ex):
        y, h1 = e["points"], e["h1"]
        ring = y[np.r_[e["cycles"][0], e["cycles"][0][:1]]]              # the most persistent loop, closed
        normal = np.linalg.svd(ring - ring.mean(0))[2][-1]              # normal of the ring's best-fit plane
        a3 = fig.add_subplot(gs[0, j], projection="3d")
        a3.computed_zorder = False                                     # draw the ring on top of the points
        a3.scatter(*y.T, c=e["pos"], cmap="twilight" if e["cyclic"] else "viridis", vmin=0, vmax=1,
                   s=2 if len(y) > 300 else 6, alpha=0.45, depthshade=False, zorder=1)
        a3.plot(*ring.T, color="white", lw=5.5, zorder=2)              # halo, so the ring stands out
        a3.plot(*ring.T, color=red, lw=2.6, zorder=3)
        if np.ptp(ring, axis=0).max() < 0.1 * np.ptp(y, axis=0).max():  # tiny loop: circle it
            a3.scatter(*ring.mean(0), s=700, facecolors="none", edgecolors=red, linewidths=1.4, zorder=4)
        lim = float(np.abs(y).max())
        a3.set_xlim(-lim, lim)
        a3.set_ylim(-lim, lim)
        a3.set_zlim(-lim, lim)
        a3.set_box_aspect((1, 1, 1), zoom=1.65)
        a3.view_init(elev=float(np.degrees(np.arcsin(np.clip(normal[2], -1, 1)))),
                     azim=float(np.degrees(np.arctan2(normal[1], normal[0]))))
        a3.set_axis_off()
        a3.set_title(f"{e['name']}\n{e['verdict']}", fontsize=8, color=e["colour"])
        ap = fig.add_subplot(gs[1, j])
        ap.loglog([rmin, rmax], [rmin, rmax], color="#999", lw=0.8)
        ap.loglog([rmin, rmax / e["q95"]], [rmin * e["q95"], rmax], color="#555", ls="--", lw=0.9)
        if e["connect_r"]:
            ap.axhline(e["connect_r"], color="#555", ls=":", lw=0.9)
        ap.scatter(h1[:, 0], h1[:, 1], s=5, color="#aaaaaa", alpha=0.5, edgecolors="none")
        ap.scatter([h1[0, 0]], [h1[0, 1]], s=70, color=red, edgecolors="k", linewidths=0.8, zorder=4)
        ap.text(0.04, 0.96, f"\u03c0 / q95 = {e['ratio']:.2f}", transform=ap.transAxes, fontsize=8, va="top")
        ap.set_xlim(rmin, rmax)
        ap.set_ylim(rmin, rmax)
        ap.set_aspect("equal")
        ap.tick_params(labelsize=7)
        ap.set_xlabel("birth radius", fontsize=7.5)
        if j == 0:
            ap.set_ylabel("death radius", fontsize=7.5)
        ap.set_title(f"born {h1[0, 0]:.3f}, dies {h1[0, 1]:.3f}", fontsize=8)
    fig.suptitle("The detected circles: each cloud's most persistent loop, drawn in red as a closed path of edges "
                 "(viewed face-on) and as its red dot in the persistence diagram", fontsize=11)
    fig.text(0.5, 0.015, "Above the dashed line: beats the null's 95th percentile. Below the dotted line: dies before two "
             "concepts' clusters touch (a small loop inside one cluster). Small loops are circled.", ha="center", fontsize=8)
    save(fig, "fig_detected_loops")
