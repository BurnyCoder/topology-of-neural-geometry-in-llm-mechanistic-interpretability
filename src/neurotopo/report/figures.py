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
    k = read_json(config.path("results") / "exp3" / "method_b.json")["R2_grokking_WE"]["records3"][0]["k"]
    sets = [("R7_llama_colors", "colours (hue)"), ("R2_grokking_WE", f"residues mod 113 (k = {k})"),
            ("R5b_llama_months", "months"), ("R5a_llama_weekdays", "weekdays")]
    fig = plt.figure(figsize=(12, 3.6))
    axes = []
    for j, (d, title) in enumerate(sets):
        c = realdata.cloud(d)
        if d == "R2_grokking_WE":
            pos = (k * np.array([int(s) for s in c["labels"]])) % 113 / 113
        else:
            con = source.concepts(d, c["labels"])
            pos = con.index / len(con.phase)
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


EXAMPLES = [("R7_llama_colors", "Colours"), ("R2_grokking_WE", "Residues mod 113\n(toy network)"),
            ("R5b_llama_months", "Months"), ("R5a_llama_weekdays", "Weekdays"),
            ("R5c_llama_days_time", "Days + times of day"), ("R6_llama_years", "Years (control)")]


def fig_examples() -> None:
    """Plain-language positive and negative examples. Top: each cloud (PC1-PC2), coloured by position in its cycle
    (years: by value), titled with two verdicts read from results (report/verdicts.py): is there a ring (top-3
    loop beyond the Monte Carlo null), and does the concept go around it once (preregistered theta_B or theta_A;
    otherwise post hoc only; otherwise no). Bottom: ring strength / chance level = observed top H1 persistence
    ratio / the null's 95th percentile, so a bar above 1 is a significant ring (p < 0.05)."""
    from neurotopo.experiments import realdata
    from neurotopo.report import verdicts as v
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    k = read_json(config.path("results") / "exp3" / "method_b.json")["R2_grokking_WE"]["records3"][0]["k"]
    fig = plt.figure(figsize=(15, 5.8))
    gs = fig.add_gridspec(2, len(EXAMPLES), height_ratios=[1.25, 1], hspace=0.38)
    ratios, cols = [], []
    for j, (d, name) in enumerate(EXAMPLES):
        c = realdata.cloud(d)
        if d == "R2_grokking_WE":
            pos = (k * np.array([int(s) for s in c["labels"]])) % 113 / 113
        else:
            con = source.concepts(d, c["labels"], n_bins=12)
            pos = con.index / len(con.phase)
        ax = fig.add_subplot(gs[0, j])
        ax.scatter(c["y"][:, 0], c["y"][:, 1], c=pos, cmap="viridis" if d == "R6_llama_years" else "twilight",
                   s=5 if len(pos) > 200 else 12)
        ax.set_xticks([])
        ax.set_yticks([])
        ring = v.loop(d)
        goes = "yes" if (v.method_b(d) or v.method_a(d)) else ("only post hoc" if v.posthoc(d) else "no")
        control = d == "R6_llama_years"                     # an ordinal concept: no ring is the expected outcome
        ok = (ring and goes == "yes") or (control and not ring)
        verdict = f"ring: {'yes' if ring else 'no'}" + (" (as expected)" if control and not ring else "")
        ax.set_title(f"{name}\n{verdict}\ngoes around once: {goes}", fontsize=8.5,
                     color="#1b7837" if ok else ("#b35806" if ring else "#333333"))
        ratios.append(float(inv.loc[d, "top_pi1"] / inv.loc[d, "null_q95_pi1"]))
        cols.append("#1b7837" if ring else "#bbbbbb")
    ax = fig.add_subplot(gs[1, :])
    ax.bar(range(len(EXAMPLES)), ratios, color=cols, width=0.5)
    ax.axhline(1, color="k", ls="--", lw=0.9)
    ax.text(len(EXAMPLES) - 1.5, 1.03, "chance level", ha="center", va="bottom", fontsize=8)   # in the gap between bars
    ax.set_xticks(range(len(EXAMPLES)))
    ax.set_xticklabels([n.replace("\n", " ") for _, n in EXAMPLES], fontsize=8)
    ax.set_xlim(-0.5, len(EXAMPLES) - 0.5)
    ax.set_ylim(0, max(ratios) * 1.15)
    ax.set_ylabel("ring strength / chance level\n(above 1 = real ring)", fontsize=8)
    for i, r in enumerate(ratios):
        ax.text(i, r + 0.03, f"{r:.2f}", ha="center", va="bottom", fontsize=8)
    save(fig, "fig_examples")
