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
from neurotopo.report.science import ordered_estimators
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
        "A": (0.26, 0.62, "Method A: catalog topology\nof the reported fit\n(b0,b1,b2), chi, genus, rho_A", "#f4f1de"),
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
    """Fitted catalog topology for every real cloud: margin ratio rho_A (log scale), marker by Betti vector."""
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
    ax.set_title("Method A: topology of the 44 catalog fits", fontsize=10)
    save(fig, "fig_exp0_margin")


def fig_exp1_estimators() -> None:
    """Exp1: macro exact Betti-vector accuracy (95% cluster-bootstrap CI) of every estimator on resolvable clouds."""
    s = read_json(config.path("results") / "exp1" / "summary.json")
    names = [k for k in ordered_estimators(s["table"]) if "subset" not in k]
    est = [s["table"][k]["macro_exact"] for k in names]
    lo = [s["table"][k]["macro_exact"] - s["table"][k]["ci"][0] for k in names]
    hi = [s["table"][k]["ci"][1] - s["table"][k]["macro_exact"] for k in names]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(range(len(names)), est, xerr=[lo, hi], color=["#30638e" if k.startswith(("P", "S")) else "#bbbbbb" for k in names],
            capsize=3)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Catalog accuracy, equal family weights (polytope: components only, 95% CI)")
    ax.invert_yaxis()
    save(fig, "fig_exp1_estimators")


def fig_exp1_by_rho() -> None:
    """Exp1: accuracy against the margin ratio rho_A (all clouds, including unresolvable ones)."""
    s = read_json(config.path("results") / "exp1" / "summary.json")
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    for name in ordered_estimators(s["accuracy_by_rho"]):
        d = s["accuracy_by_rho"][name]
        ks = list(d.keys())
        ax.plot(range(len(ks)), [d[k] for k in ks], marker="o", label=name)
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(ks, fontsize=7, rotation=20)
    ax.axvline(2.5, color="k", ls="--", lw=0.8)
    ax.set_ylim(0, 1)
    ax.set_xlabel("margin ratio rho_A bin (right of dashed line: resolvable)")
    ax.set_ylabel("Catalog target accuracy")
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
    go around it once). Bottom: observed top H1 persistence ratio / the null's 95th percentile, a descriptive reference line. The decision uses the Monte Carlo rank."""
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
    ax.set_ylabel("top loop ratio / fitted null's\n95th percentile", fontsize=8)
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


def _loop_3d(a3, y: np.ndarray, cycle, rgb: np.ndarray | None = None) -> None:
    """Draw one loop's representative cycle (diagrams.alpha_h1_cycles) in red with a white halo over the cloud's
    points (rgb per point, or grey), viewed face-on: camera along the normal of the cycle's best-fit plane (SVD of its
    vertices). A loop smaller than a tenth of the cloud is circled. Clouds of at most 20 points (concept centres, toy
    models) get large points and a box that fits their largest radius, so no corner is clipped. Shared by
    fig_detected_loops and fig_loop_gallery."""
    ring = y[np.r_[cycle, cycle[:1]]]                                  # the cycle, closed
    normal = np.linalg.svd(ring - ring.mean(0))[2][-1]                 # normal of its best-fit plane
    few = len(y) <= 20
    a3.computed_zorder = False                                         # draw the ring on top of the points
    a3.scatter(*y.T, color=rgb if rgb is not None else "#555555", s=40 if few else 2 if len(y) > 300 else 6,
               alpha=0.9 if few else 0.45, depthshade=False, zorder=1 if not few else 4)
    a3.plot(*ring.T, color="white", lw=5.5, zorder=2)                  # halo, so the ring stands out
    a3.plot(*ring.T, color=RED, lw=2.6, zorder=3)
    if np.ptp(ring, axis=0).max() < 0.1 * np.ptp(y, axis=0).max():     # tiny loop: circle it
        a3.scatter(*ring.mean(0), s=700, facecolors="none", edgecolors=RED, linewidths=1.4, zorder=4)
    lim = float(np.linalg.norm(y, axis=1).max() if few else np.abs(y).max())
    a3.set_xlim(-lim, lim)
    a3.set_ylim(-lim, lim)
    a3.set_zlim(-lim, lim)
    a3.set_box_aspect((1, 1, 1), zoom=1.3 if few else 1.65)
    a3.view_init(elev=float(np.degrees(np.arcsin(np.clip(normal[2], -1, 1)))),
                 azim=float(np.degrees(np.arctan2(normal[1], normal[0]))))
    a3.set_axis_off()


def _point_rgb(d: str, labels: list[str]) -> np.ndarray | None:
    """(N, 3) colours for a cloud's points: the colours cloud in its prompts' own RGB; other concept clouds by
    position in their cycle (examples.concept_positions; twilight if the concept is cyclic, viridis otherwise); None
    (grey) for the toy models, whose concept bins carry no meaning, and for clouds without concepts."""
    from neurotopo.report.examples import concept_positions, stimulus_rgb
    rgb = stimulus_rgb(d, labels)
    if rgb is not None or "tms" in d:
        return rgb
    try:
        cmap = "twilight" if source.concepts(d, labels).cyclic else "viridis"
        return plt.get_cmap(cmap)(concept_positions(d, labels))[:, :3]
    except ValueError:
        return None


def fig_detected_loops() -> None:
    """The detected circular loops (README, near the top). For each example cloud, top: the cloud in its top-3 PCA
    coordinates with one closed path of edges carrying its most persistent loop (diagrams.alpha_h1_cycles) drawn
    in red, viewed face-on (camera along the normal of the path's best-fit plane, from an SVD of its vertices);
    a loop smaller than a tenth of the cloud is also circled so it can be found. Bottom: the persistence diagram
    (log axes) with that loop's dot, the null's 95th-percentile line and the connect radius. Data: report/examples.py."""
    from neurotopo.report.examples import EXAMPLES, example
    ex = [example(d) for d, _ in EXAMPLES]
    rmin, rmax = 0.004, 1.2
    fig = plt.figure(figsize=(15, 6.2))
    gs = fig.add_gridspec(2, len(ex), height_ratios=[1.35, 1], hspace=0.16, wspace=0.18, top=0.88, bottom=0.12)
    for j, e in enumerate(ex):
        y, h1 = e["points"], e["h1"]
        a3 = fig.add_subplot(gs[0, j], projection="3d")
        _loop_3d(a3, y, e["cycles"][0], plt.get_cmap("twilight" if e["cyclic"] else "viridis")(e["pos"])[:, :3])
        a3.set_title(f"{e['name']}\n{e['verdict']}", fontsize=8, color=e["colour"])
        ap = fig.add_subplot(gs[1, j])
        ap.loglog([rmin, rmax], [rmin, rmax], color="#999", lw=0.8)
        ap.loglog([rmin, rmax / e["q95"]], [rmin * e["q95"], rmax], color="#555", ls="--", lw=0.9)
        if e["connect_r"]:
            ap.axhline(e["connect_r"], color="#555", ls=":", lw=0.9)
        ap.scatter(h1[:, 0], h1[:, 1], s=5, color="#aaaaaa", alpha=0.5, edgecolors="none")
        ap.scatter([h1[0, 0]], [h1[0, 1]], s=70, color=RED, edgecolors="k", linewidths=0.8, zorder=4)
        ap.text(0.04, 0.96, f"\u03c0 / q95 = {e['ratio']:.2f}", transform=ap.transAxes, fontsize=8, va="top")
        ap.set_xlim(rmin, rmax)
        ap.set_ylim(rmin, rmax)
        ap.set_aspect("equal")
        ap.tick_params(labelsize=7)
        ap.set_xlabel("birth radius", fontsize=7.5)
        if j == 0:
            ap.set_ylabel("death radius", fontsize=7.5)
        ap.set_title(f"born {h1[0, 0]:.3f}, dies {h1[0, 1]:.3f}", fontsize=8)
    fig.suptitle("The detected circular loops: each cloud's most persistent loop, drawn in red as a closed path of edges "
                 "(viewed face-on) and as its red dot in the persistence diagram", fontsize=11)
    fig.text(0.5, 0.015, "Above the dashed line: beats the null's 95th percentile. Below the dotted line: dies before two "
             "concepts' clusters touch (a small loop inside one cluster). Small loops are circled.", ha="center", fontsize=8)
    save(fig, "fig_detected_loops")


# The README's void figure: the three clouds whose top void survives Benjamini-Hochberg (toy models of superposition,
# Elhage et al. 2022, https://transformer-circuits.pub/2022/toy_model/index.html; the strongest first), the colours
# cloud's largest void (found by browsing the explorer: the largest empty middle outside the toy models) and two GPT-2
# position controls. pick: "top" = the most persistent void, "largest" = examples.largest_void.
VOID_EXAMPLES = [("R3_tms_n20", "toy model, 20 features", "top"), ("R3_tms_n8", "toy model, 8 features", "top"),
                 ("R3_tms_n6", "toy model, 6 features", "top"), ("R7_llama_colors", "colours (Llama)", "largest"),
                 ("C3_gpt2_wpos_init", "GPT-2 positions, random init", "top"),
                 ("R1_gpt2_wpos", "GPT-2 positions, trained", "top")]
RED, BLUE = "#d62728", "#4393c3"                 # void shells red, as the detected loops; blue = the void's empty middle
RING_FACE_ON = {"R7_llama_colors"}               # clouds whose void is shown inside their hue ring, seen face-on
_U, _V = np.meshgrid(np.linspace(0, 2 * np.pi, 28), np.linspace(0, np.pi, 14))
BALL = np.stack([np.cos(_U) * np.sin(_V), np.sin(_U) * np.sin(_V), np.cos(_V)])   # unit sphere for plot_surface, (3, 14, 28)


def _void_3d(a3, d: str, y: np.ndarray, labels: list[str], rp: dict, k: int, ring: bool = False,
             concept_colours: bool = False) -> None:
    """Draw void k of examples.replay data rp in the 3D axes a3 (shared by fig_detected_voids and fig_void_gallery):
    the points (the colours cloud in its prompts' RGB; with concept_colours, other concept clouds by position in their
    cycle, twilight if cyclic, viridis otherwise; grey for the toy models and otherwise), the void's empty middle as a
    blue ball (radius death - birth around its centre: still uncovered when the void closes), its shell as red edges
    with a white halo over faint red faces, and with ring the most persistent loop as a dark line seen face-on (view
    along the normal of its best-fit plane; the farthest 2% of points are then left out so the ring fills the panel).
    A void smaller than a quarter of the cloud is circled; points are faded in dense clouds (> 300 points)."""
    from itertools import combinations
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
    from neurotopo.report.examples import stimulus_rgb
    h2, shell, centre = rp["h2"], rp["shells"][k], rp["void_centres"][k]
    rgb = _point_rgb(d, labels) if concept_colours else stimulus_rgb(d, labels)
    dense, corners = len(y) > 300, y[np.unique(shell)]
    edges = np.array(sorted({tuple(sorted(e)) for t in shell.tolist() for e in combinations(t, 2)}))
    r = np.linalg.norm(y, axis=1)                                        # largest radius: no corner is clipped
    lim = float(np.percentile(r, 98) if ring else r.max())
    keep = r <= lim
    a3.computed_zorder = False                                           # draw in call order: points, ball, shell
    a3.scatter(*y[keep].T, color=rgb[keep] if rgb is not None else "#333333",
               s=(2 if dense else 14) if rgb is None else (5 if dense else 16),
               alpha=(0.15 if dense else 0.6) if rgb is None else (0.5 if dense else 0.85), depthshade=False, zorder=1)
    a3.plot_surface(*(centre[:, None, None] + (h2[k, 1] - h2[k, 0]) * BALL), color=BLUE, alpha=0.9, shade=False,
                    linewidth=0, zorder=2)                               # the empty middle, radius death - birth
    a3.add_collection3d(Poly3DCollection(y[shell], facecolors=RED, edgecolors="none", alpha=0.1, zorder=3))
    a3.add_collection3d(Line3DCollection(y[edges], colors="white", linewidths=3.0, zorder=4))   # halo
    a3.add_collection3d(Line3DCollection(y[edges], colors=RED, linewidths=1.3, zorder=5))
    if ring:                                                             # the most persistent loop around the void
        loop = y[np.r_[rp["cycles"][0], rp["cycles"][0][:1]]]
        a3.plot(*loop.T, color="#222222", lw=1.6, zorder=6)
        normal = np.linalg.svd(loop - loop.mean(0))[2][-1]
        a3.view_init(elev=float(np.degrees(np.arcsin(np.clip(normal[2], -1, 1)))),
                     azim=float(np.degrees(np.arctan2(normal[1], normal[0]))))
    if np.ptp(corners, axis=0).max() < 0.25 * np.ptp(y, axis=0).max():  # small void: circle it
        a3.scatter(*corners.mean(0), s=900, facecolors="none", edgecolors=RED, linewidths=1.4, zorder=7)
    a3.set_xlim(-lim, lim)
    a3.set_ylim(-lim, lim)
    a3.set_zlim(-lim, lim)
    a3.set_box_aspect((1, 1, 1), zoom=1.4)
    a3.set_axis_off()


def fig_detected_voids() -> None:
    """The detected voids (README, right after the detected circular loops, in the same style). For each cloud of
    VOID_EXAMPLES, top: the cloud in its top-3 PCA coordinates (the colours cloud painted in its prompts' own colours,
    with its most persistent loop, the hue ring, as a dark line, seen face-on, and its farthest 2% of points left out so
    the ring fills the panel; its title gives that void's own p, without BH) with one void drawn explicitly (pick): the shell
    (diagrams.alpha_h2_voids, via examples.replay), a closed surface of triangles, as red edges with a white halo over
    faint red faces, and inside it the void's empty middle as a blue ball: centred on the circumcentre of the
    tetrahedron that fills the void, radius death - birth, the part of the void the balls of the birth radius do not
    cover (no point is closer to the centre than the death radius). A void smaller than a quarter of the cloud is
    circled, and points are faded in dense clouds. Bottom: the void (H2) persistence diagram on linear axes zoomed to
    the cloud's voids (void ratios are small, 1-1.5, so a fixed range would squeeze every void onto the diagonal),
    with that void's red triangle and the null's 95th-percentile line. Title colour: green if the void survives
    Benjamini-Hochberg over the 44 void tests, orange if only p < 0.05, black otherwise. Numbers:
    results/exp2/invariants.csv. mplot3d: Poly3DCollection, Line3DCollection, plot_surface
    (https://matplotlib.org/stable/api/toolkits/mplot3d.html)."""
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import largest_void, replay
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    fig = plt.figure(figsize=(16.5, 6.8))
    gs = fig.add_gridspec(2, len(VOID_EXAMPLES), height_ratios=[1.35, 1], hspace=0.2, wspace=0.22, top=0.86, bottom=0.13)
    for j, (d, label, pick) in enumerate(VOID_EXAMPLES):
        c, row = realdata.cloud(d), inv.loc[d]
        y = c["y"]
        if pick == "largest":                                            # a chosen void: its own p, no BH (not a test)
            lv = largest_void(d)
            rp, k = lv["rp"], lv["k"]
            verdict = f"largest void (#{lv['rank']} by π): p = {lv['p']:.3f}"
            colour = "#e08214" if lv["p"] < 0.05 else "#222222"
        else:                                                            # voids sorted by pi: index 0 is the top void
            rp, k = replay(y), 0
            p, q = float(row["p_top_void"]), float(row["q_top_void"])
            verdict, colour = ((f"void: yes (q = {q:.3f})", "#1b7837") if q < 0.05 else
                               (f"p = {p:.3f}, but q = {q:.2f} after BH", "#e08214") if p < 0.05 else
                               (f"void: no (p = {p:.2f})", "#222222"))
        h2, shell = rp["h2"], rp["shells"][k]
        a3 = fig.add_subplot(gs[0, j], projection="3d")
        _void_3d(a3, d, y, c["labels"], rp, k, ring=d in RING_FACE_ON)
        a3.set_title(f"{label}\n{verdict}", fontsize=8.5, color=colour)
        ap = fig.add_subplot(gs[1, j])
        lo, hi = 0.8 * h2[:, 0].min(), 1.1 * h2[:, 1].max()               # zoom to this cloud's voids (narrow: linear axes)
        q95 = float(row["null_q95_pi2"])
        ap.plot([lo, hi], [lo, hi], color="#999", lw=0.8)
        ap.plot([lo, hi / q95], [lo * q95, hi], color="#555", ls="--", lw=0.9)
        ap.scatter(h2[:, 0], h2[:, 1], s=5, marker="^", color="#aaaaaa", alpha=0.5, edgecolors="none")
        ap.scatter([h2[k, 0]], [h2[k, 1]], s=80, marker="^", color=RED, edgecolors="k", linewidths=0.8, zorder=4)
        kept = int(np.floor(100 * row["void_freq"] + 0.5))             # half-up, as numbers.py rounds the README's %
        note = f"void #{k + 1} of {len(h2)} by π" if pick == "largest" else f"kept in {kept}% of subsamples"
        ap.text(0.96, 0.04, f"π / q95 = {h2[k, 1] / h2[k, 0] / q95:.2f}\n{note}",
                transform=ap.transAxes, fontsize=7.5, va="bottom", ha="right")   # below the diagonal: always empty
        ap.set_xlim(lo, hi)
        ap.set_ylim(lo, hi)
        ap.set_aspect("equal")
        ap.tick_params(labelsize=7)
        ap.set_xlabel("birth radius", fontsize=7.5)
        if j == 0:
            ap.set_ylabel("death radius", fontsize=7.5)
        ap.set_title(f"{len(shell)} faces; born {h2[k, 0]:.3f}, dies {h2[k, 1]:.3f}", fontsize=8)
    fig.suptitle("The detected voids: each cloud's most persistent void (colours: its largest), drawn as its shell (red, "
                 "a closed surface of "
                 "triangles) around its empty middle (blue)\nand as its red triangle in the void persistence diagram",
                 fontsize=11)
    fig.text(0.5, 0.015, "Blue ball: radius death - birth around the void's centre, still empty when the void closes. "
             "Above the dashed line: beats the null's 95th percentile (p < 0.05).\nq: Benjamini-Hochberg over the 44 "
             "void tests. Subsamples: 200 random 80% subsamples. Diagram axes are zoomed per cloud. Small voids are "
             "circled.", ha="center", fontsize=8)
    save(fig, "fig_detected_voids")


def fig_void_gallery() -> None:
    """Every interesting void (results/voids/summary.json from `run.py voids`: significant, large, or shape and
    meaning; post hoc rules, deviation D10), drawn as in fig_detected_voids with points coloured by concept (colours:
    RGB), five per row. Title: the cloud and the void's rank by pi, the rules that picked it, then pi, p (against the
    cloud's null), the empty middle (death - birth), and the shell's corners (features for the toy models, concepts
    otherwise). Title colour: green if it is a cloud's most persistent void surviving BH over Exp2's 44 void tests,
    orange if only p < 0.05, black otherwise."""
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import replay
    rows = read_json(config.path("results") / "voids" / "summary.json")["interesting"]
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    ncol = 5
    nrow = -(-len(rows) // ncol)                                         # ceiling division
    fig = plt.figure(figsize=(3.4 * ncol, 3.9 * nrow + 0.8))
    for j, r in enumerate(rows):
        d, k = r["id"], int(r["k"]) - 1                                  # k: rank by pi, 1 = most persistent
        c = realdata.cloud(d)
        rp = replay(c["y"])                                              # same order as void_search (stable sort by pi)
        assert np.isclose(rp["h2"][k, 1] / rp["h2"][k, 0], r["pi"]), (d, r["k"])
        a3 = fig.add_subplot(nrow, ncol, j + 1, projection="3d")
        _void_3d(a3, d, c["y"], c["labels"], rp, k, ring=d in RING_FACE_ON, concept_colours=True)
        colour = ("#1b7837" if r["k"] == 1 and inv.loc[d, "q_top_void"] < 0.05 else
                  "#e08214" if r["p"] < 0.05 else "#222222")
        what = (f"{r['corners']} of {r['N']} features on the shell" if "tms" in d else
                f"{r['shell_concepts']} of {r['n_concepts']} concepts on the shell")
        name = short(d).replace("C3_", "").replace("C1_", "").replace("colors", "colours")   # readable cloud name
        a3.set_title(f"{name}, void #{r['k']} ({r['reasons']})\nπ = {r['pi']:.3f}, p = {r['p']:.3f}, empty "
                     f"middle {r['empty']:.3f}\n{what}", fontsize=8, color=colour)
    fig.suptitle("Every interesting void of the 44 clouds (picked by rule: significant, large, or shape and meaning; post "
                 "hoc), drawn as a red shell around its empty middle (blue)", fontsize=11, y=0.995)
    fig.text(0.5, 0.005, "Green: a cloud's most persistent void surviving Benjamini-Hochberg over the 44 void tests. "
             "Orange: p < 0.05 only. Black: not significant. p: against the cloud's design-matched null of the largest "
             "void π.", ha="center", fontsize=8)
    save(fig, "fig_void_gallery")


HIGHLIGHT_NAMES = {"R7_llama_colors": "colours (Llama)", "R2_grokking_WE": "residues mod 113 (grokked network)",
                   "R5b_llama_months": "months (Llama)", "R5b_llama_months_means": "the 12 month centres (Llama)",
                   "R3_tms_n20": "toy model, 20 features", "R3_tms_n8": "toy model, 8 features",
                   "R3_tms_n6": "toy model, 6 features"}
CONCEPT_NOUN = {"R7_llama_colors": "hues", "R2_grokking_WE": "residues", "R5b_llama_months": "months",
                "R5b_llama_months_means": "months"}


def fig_highlights() -> None:
    """The README's first figure: the strongest loops and voids by rule (examples.highlights). Top row: a cloud's most
    persistent loop surviving Benjamini-Hochberg over Exp2's 44 loop tests (post hoc, D6) whose concepts wind once
    along its drawn cycle (a post hoc check, D11), drawn as in fig_detected_loops (red cycle face-on, points coloured
    by concept, colours in their RGB). Each title carries the cloud's original verdict (examples.headline: "ring"
    only where the concept goes around the loop in the preregistered analysis, D9; colours' ring inherited from the
    stimuli, D8) in its colour, so the figure says no more than the results. Bottom row: the voids surviving the same
    correction over the 44 void tests (exploratory toy models), drawn as in fig_detected_voids (red shell around a
    blue empty middle). Titles give pi, the BH q and the concepts or features on the cycle or shell."""
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import headline, highlights, replay
    loops, voids = highlights()
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    fig = plt.figure(figsize=(15, 8.8))
    gs = fig.add_gridspec(2, 2 * max(len(loops), len(voids)), hspace=0.42, wspace=0.1, top=0.82, bottom=0.02)
    for row, rows in ((0, loops), (1, voids)):
        off = max(len(loops), len(voids)) - len(rows)                    # centre a shorter row
        for j, r in enumerate(rows):
            d, c = r["id"], realdata.cloud(r["id"])
            a3 = fig.add_subplot(gs[row, off + 2 * j: off + 2 * j + 2], projection="3d")
            if row == 0:                                                 # the original verdict, word for word
                _loop_3d(a3, c["y"], np.array(r["cycle"]), _point_rgb(d, c["labels"]))
                h = headline(d)
                what = (f"{r['loop_concepts']} of {r['n_concepts']} {CONCEPT_NOUN.get(d, 'concepts')} on it\n"
                        f"{h['verdict'].replace(chr(10), ' ')}")
                q, colour = inv.loc[d, "q_top_loop"], h["colour"]
            else:
                _void_3d(a3, d, c["y"], c["labels"], replay(c["y"]), 0)
                what = f"{r['corners']} of {r['N']} features on its shell\nexploratory set"
                q, colour = inv.loc[d, "q_top_void"], "#222222"                  # neutral: green means "ring" above
            a3.set_title(f"{HIGHLIGHT_NAMES.get(d, short(d))}\nπ = {r['pi']:.2f}, q = {q:.3f}\n{what}",
                         fontsize=9, color=colour)
    for row, head in ((0, "Loops through the concepts (the concepts wind once along the drawn cycle, a post hoc check)"),
                      (1, "Voids: an empty middle walled in by a closed surface")):
        top = gs[row, :].get_position(fig).y1                           # row headers sit above the panel titles
        fig.text(0.5, top + 0.1, head, ha="center", fontsize=10.5, weight="bold")
    fig.suptitle("The strongest loops and voids: each survives Benjamini-Hochberg over 44 tests (q < 0.05, post hoc)\n"
                 "Loop titles give each cloud's original verdict (green: ring; orange: partial), as in the example figure",
                 fontsize=11.5, y=0.995)
    save(fig, "fig_highlights")


HL_RADII = np.r_[0.04 * (1.15 / 0.04) ** np.linspace(0, 1, 72), np.full(10, 1.15)]   # the animations' r: sweep, hold


def _highlight_items() -> list[dict]:
    """The panels of fig_highlights' animations (examples.highlights): for each loop or void, the cloud's points and
    colours, its bar, the loop's closed cycle or the void's shell and centre, and the slice plane through the cycle's
    mean or the void's centre (rows of `plane`: two in-plane axes, then the normal; from an SVD of the cycle or of the
    shell's corners)."""
    from neurotopo.experiments import realdata
    from neurotopo.report.examples import highlights, replay
    loops, voids = highlights()
    items = []
    for row, rows in ((0, loops), (1, voids)):
        for r in rows:
            c = realdata.cloud(r["id"])
            y = c["y"]
            it = {"id": r["id"], "row": row, "n_row": len(rows), "y": y, "colour": _point_rgb(r["id"], c["labels"]),
                  "bar": (r["birth"], r["death"])}
            if row == 0:
                cyc = np.array(r["cycle"])
                ring = y[np.r_[cyc, cyc[:1]]]
                it.update(cycle=ring, origin=ring.mean(0), plane=np.linalg.svd(ring - ring.mean(0))[2])
            else:
                rp = replay(y)
                corners = y[np.unique(rp["shells"][0])]
                it.update(shell=rp["shells"][0], origin=rp["void_centres"][0],
                          plane=np.linalg.svd(corners - corners.mean(0))[2])
            items.append(it)
    return items


def _highlight_axes(fig, items: list[dict], top: float, **kw) -> list:
    """One axes per item on the highlights grid: loops in the top row, voids centred in the bottom row."""
    ncol = max(it["n_row"] for it in items)
    gs = fig.add_gridspec(2, 2 * ncol, hspace=0.38, wspace=0.12, top=top, bottom=0.03)
    seen = {0: 0, 1: 0}
    out = []
    for it in items:
        j, off = seen[it["row"]], ncol - it["n_row"]                     # centre a shorter row
        seen[it["row"]] += 1
        out.append(fig.add_subplot(gs[it["row"], off + 2 * j: off + 2 * j + 2], **kw))
    return out


def _status(it: dict, r: float) -> tuple[str, bool]:
    """The status line of a loop or void at radius r, from its bar, and whether it is alive."""
    b, d = it["bar"]
    alive = b <= r < d
    state = "not born yet" if r < b else "alive" if alive else "filled"
    return f"{'loop' if it['row'] == 0 else 'void'} born {b:.3f}, filled {d:.3f}: {state}", alive


def _slice_prepare(items: list[dict]) -> float:
    """Slice coordinates of each item's points (p2), their distances h from the slice and the loop's cycle in the
    slice (ring2); returns one axis limit for all panels (1.05 x the largest 98th-percentile radius in the slice)."""
    for it in items:
        rel = it["y"] - it["origin"]
        it["p2"], it["h"] = rel @ it["plane"][:2].T, np.abs(rel @ it["plane"][2])
        it["ring2"] = (it["cycle"] - it["origin"]) @ it["plane"][:2].T if it["row"] == 0 else None
    return 1.05 * max(float(np.percentile(np.linalg.norm(it["p2"], axis=1), 98)) for it in items)


def _slice_axes(ax, it: dict, lim: float) -> None:
    """Set up a slice panel: equal axes of half-width lim, the points, and a status line under it."""
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.scatter(*it["p2"].T, s=3 if len(it["y"]) > 300 else 14,
               color=it["colour"] if it["colour"] is not None else "#333333", zorder=3)
    it.update(ax=ax, artists=[], text=ax.text(0.5, -0.04, "", transform=ax.transAxes, ha="center", va="top",
                                              fontsize=8.5))


def _slice_draw(it: dict, r: float) -> None:
    """Draw an item's slice at radius r (replacing the previous radius): each ball at distance h from the slice as a
    disc of radius sqrt(r^2 - h^2), the loop's cycle (bold while alive) or the void's empty middle (blue, radius
    death - r, while alive), and the status line from the bar."""
    from matplotlib.collections import EllipseCollection
    ax = it["ax"]
    for a in it["artists"]:
        a.remove()
    rad = np.sqrt(np.clip(r ** 2 - it["h"] ** 2, 0, None))               # the slice of each ball
    on = rad > 0
    discs = EllipseCollection(2 * rad[on], 2 * rad[on], np.zeros(on.sum()), units="xy", offsets=it["p2"][on],
                              offset_transform=ax.transData, edgecolors="none", alpha=0.22, zorder=1,
                              facecolors=it["colour"][on] if it["colour"] is not None else "#888888")
    it["artists"] = [ax.add_collection(discs)]
    text, alive = _status(it, r)
    if it["row"] == 0:                                                   # the loop's cycle: bold while alive
        it["artists"] += ax.plot(*it["ring2"].T, color=RED, lw=2.6 if alive else 0.8, ls="-" if alive else "--",
                                 zorder=4)
    elif alive:                                                          # the void's empty middle, radius death - r
        it["artists"].append(ax.add_patch(plt.Circle((0, 0), it["bar"][1] - r, color=BLUE, alpha=0.9, zorder=4)))
    it["text"].set_text(text)
    it["text"].set_color("#1b7837" if alive else "#222222")


def fig_growing_balls() -> None:
    """Static print version of anim_highlights for the paper: for each highlighted loop and void (examples.highlights),
    four radii relative to its own bar (before it is born, just after, shortly before it is filled, after), drawn as
    exact slices of the union of balls (_slice_draw) on one scale. Loop titles carry the original verdicts."""
    from neurotopo.report.examples import headline
    items = _highlight_items()
    lim = _slice_prepare(items)
    fig, axes = plt.subplots(len(items), 4, figsize=(9.6, 2.45 * len(items)))
    for it, row in zip(items, axes):
        b, d = it["bar"]
        verdict = headline(it["id"])["verdict"].replace("\n", " ") if it["row"] == 0 else "void (exploratory set)"
        for j, (ax, r) in enumerate(zip(row, [0.6 * b, b + 0.2 * (d - b), b + 0.8 * (d - b), 1.1 * d])):
            _slice_axes(ax, it, lim)
            _slice_draw(it, r)
            it["text"].set_text(_status(it, r)[0].split(": ")[-1])      # the state only; the bar is in the row label
            ax.set_title(f"r = {r:.3f}", fontsize=8)
            if j == 0:
                ax.text(-0.12, 0.5, f"{HIGHLIGHT_NAMES.get(it['id'], short(it['id']))}\n{verdict}\nborn {b:.3f}, "
                        f"filled {d:.3f}", rotation=90, transform=ax.transAxes, ha="right", va="center", fontsize=7)
    fig.suptitle("Growing balls, in slices: each ball at distance h from the slice is a disc of radius "
                 "√(r² - h²); loops bold while alive, voids' empty middle in blue", fontsize=10)
    fig.tight_layout(rect=(0.05, 0, 1, 0.98))
    save(fig, "fig_growing_balls")


def anim_highlights() -> None:
    """Animated variant of fig_highlights in slices (README, under the 3D animation): balls of radius r grow around
    every point, r the same for all clouds (each has RMS radius 1), and the holes of their union are the holes measured
    (the alpha complex has the persistence of the union of balls, nerve theorem). Each panel is a slice: the best-fit
    plane of the loop's red cycle (loops, top) or the plane of the void shell's two main directions through the void's
    centre (voids, bottom). A ball at distance h from the slice cuts it in a disc of radius sqrt(r^2 - h^2), so the
    picture is the exact cross-section of the union of balls; a disc appears only once r reaches h and then grows
    faster than r (d/dr sqrt(r^2 - h^2) = r / sqrt(r^2 - h^2)). All panels share one scale. The cycle is bold while the
    loop is alive; the blue disc of radius death - r around the void's centre is the part of the void no ball reaches
    yet. A slice can show a region as open or enclosed differently from 3D, so the status line comes from the bar.
    matplotlib FuncAnimation + PillowWriter, EllipseCollection with data units for the discs
    (https://matplotlib.org/stable/api/animation_api.html, https://matplotlib.org/stable/api/collections_api.html)."""
    from matplotlib.animation import FuncAnimation, PillowWriter
    items = _highlight_items()
    lim = _slice_prepare(items)
    fig = plt.figure(figsize=(15, 8.4))
    axes = _highlight_axes(fig, items, top=0.83)
    for it, ax in zip(items, axes):
        _slice_axes(ax, it, lim)
        ax.set_title(f"{HIGHLIGHT_NAMES.get(it['id'], short(it['id']))}\n" +
                     ("a slice through the loop's plane" if it["row"] == 0 else "a slice through the void's centre"),
                     fontsize=9)
    head = fig.suptitle("", fontsize=12, y=0.985)
    fig.text(0.5, 0.935, "Each ball cut by the slice is a disc of radius √(r² - h²), h = the point's "
             "distance from the slice: a disc appears once r reaches h, then grows faster than r.", ha="center",
             fontsize=10)
    fig.text(0.5, 0.905, "Loops: the red loop is bold while it is alive. Voids: blue is the part of the void no ball "
             "reaches yet (radius death - r). One scale for all panels.", ha="center", fontsize=10)

    def frame(i):
        r = HL_RADII[i]
        head.set_text(f"Balls of radius r = {r:.3f} grow around every point (the same r for all clouds, RMS radius 1)")
        for it in items:
            _slice_draw(it, r)
        return []

    FuncAnimation(fig, frame, frames=len(HL_RADII)).save(config.path("figures") / "anim_highlights.gif",
                                                         writer=PillowWriter(fps=8), dpi=62)
    plt.close(fig)


def _points_per_unit(fig, a3) -> float:
    """Typographic points per data unit across the screen in a 3D axes with an orthographic projection, equal limits
    and a cubic box: the projected length of a unit vector perpendicular to the viewing direction (proj3d), so a ball
    of radius r is drawn as a scatter marker of diameter 2 r times this (marker size s = diameter^2 in points^2)."""
    from mpl_toolkits.mplot3d import proj3d
    fig.canvas.draw()
    e, a = np.radians(a3.elev), np.radians(a3.azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    u = np.cross(view, [0.0, 0.0, 1.0])
    u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-6 else np.array([1.0, 0.0, 0.0])
    px = a3.transData.transform([proj3d.proj_transform(*p, a3.get_proj())[:2] for p in (np.zeros(3), u)])
    return float(np.linalg.norm(px[1] - px[0]) * 72 / fig.dpi)


def anim_highlights_3d() -> None:
    """Animated variant of fig_highlights in 3D (README, under the highlights): the balls of radius r themselves,
    growing around every point, with one r and one scale for all clouds (RMS radius 1). Orthographic projection, in
    which a ball's outline is exactly a disc of radius r: each ball is a translucent scatter marker of that diameter
    (_points_per_unit), coloured as its point. The camera starts face-on to the loop's cycle or the void shell's two
    main directions and turns slowly. Loops: the red cycle, bold while the loop is alive. Voids: the shell's red edges
    and, while the void is alive, its empty middle (blue ball of radius death - r), drawn over the balls (x-ray) since
    the balls hide it. From outside, balls in front can hide a hole that is still open, so the status line (not born /
    alive / filled) comes from the bar."""
    from itertools import combinations
    from matplotlib.animation import FuncAnimation, PillowWriter
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    items = _highlight_items()
    lim = max(float(np.percentile(np.linalg.norm(it["y"], axis=1), 98)) for it in items)   # one scale for all panels
    fig = plt.figure(figsize=(15, 8.6))
    axes = _highlight_axes(fig, items, top=0.84, projection="3d")
    for it, a3 in zip(items, axes):
        y, n = it["y"], it["plane"][2]
        a3.set_proj_type("ortho")
        a3.computed_zorder = False                                       # draw in call order: balls, cycle, middle
        for set_lim in (a3.set_xlim, a3.set_ylim, a3.set_zlim):
            set_lim(-lim, lim)
        a3.set_box_aspect((1, 1, 1), zoom=1.3)
        a3.set_axis_off()
        elev, azim = float(np.degrees(np.arcsin(np.clip(n[2], -1, 1)))), float(np.degrees(np.arctan2(n[1], n[0])))
        a3.view_init(elev=elev, azim=azim)
        col = it["colour"] if it["colour"] is not None else np.tile([0.45, 0.45, 0.45], (len(y), 1))
        balls = a3.scatter(*y.T, s=0, c=col, alpha=0.18 if len(y) > 100 else 0.3, edgecolors="none",
                           depthshade=False, zorder=1)
        a3.scatter(*y.T, s=2 if len(y) > 300 else 10, c=col, depthshade=False, zorder=2)
        if it["row"] == 0:
            line, = a3.plot(*it["cycle"].T, color=RED, lw=0.8, zorder=3)
            middle = None
        else:
            edges = np.array(sorted({tuple(sorted(e)) for t in it["shell"].tolist() for e in combinations(t, 2)}))
            line = a3.add_collection3d(Line3DCollection(y[edges], colors=RED, linewidths=0.6, zorder=3))
            middle = a3.scatter(*it["origin"], s=0, color=BLUE, alpha=0.95, depthshade=False, zorder=4)
        a3.set_title(HIGHLIGHT_NAMES.get(it["id"], short(it["id"])), fontsize=9)
        it.update(ax=a3, balls=balls, line=line, middle=middle, elev=elev, azim=azim,
                  k=_points_per_unit(fig, a3), text=a3.text2D(0.5, -0.02, "", transform=a3.transAxes, ha="center",
                                                               va="top", fontsize=8.5))
    head = fig.suptitle("", fontsize=12, y=0.985)
    fig.text(0.5, 0.935, "The balls themselves, in 3D (one scale for all clouds; the camera turns slowly). Loops: the "
             "red loop is bold while it is alive.", ha="center", fontsize=10)
    fig.text(0.5, 0.905, "Voids: the red shell, and in blue the part of the void no ball reaches yet (radius death - r), "
             "drawn through the balls that hide it.", ha="center", fontsize=10)

    def frame(i):
        r = HL_RADII[i]
        head.set_text(f"Balls of radius r = {r:.3f} grow around every point (the same r for all clouds, RMS radius 1)")
        for it in items:
            it["ax"].view_init(elev=it["elev"], azim=it["azim"] + 60 * i / (len(HL_RADII) - 1))
            it["balls"].set_sizes(np.full(len(it["y"]), (2 * r * it["k"]) ** 2))   # marker diameter 2 r in data units
            text, alive = _status(it, r)
            it["line"].set_linewidth((2.6 if it["row"] == 0 else 1.4) if alive else (0.8 if it["row"] == 0 else 0.4))
            if it["middle"] is not None:
                it["middle"].set_sizes([(2 * (it["bar"][1] - r) * it["k"]) ** 2 if alive else 0])
            it["text"].set_text(text)
            it["text"].set_color("#1b7837" if alive else "#222222")
        return []

    FuncAnimation(fig, frame, frames=len(HL_RADII)).save(config.path("figures") / "anim_highlights_3d.gif",
                                                         writer=PillowWriter(fps=8), dpi=62)
    plt.close(fig)


def fig_loop_gallery() -> None:
    """Every interesting loop (results/loops/summary.json from `run.py loops`: significant, large, or goes around once;
    post hoc rules, deviation D11), drawn as in fig_detected_loops (red cycle, face-on), points coloured by concept
    (colours: RGB), five per row. Title: the cloud and the loop's rank by pi, the rules that picked it, then pi, p
    (against the cloud's null), size (death - birth), and the concepts on the cycle with their winding number for
    cyclic concepts. Title colour: green if it is a cloud's most persistent loop surviving BH over Exp2's 44 loop
    tests, orange if only p < 0.05, black otherwise."""
    from neurotopo.experiments import realdata
    rows = read_json(config.path("results") / "loops" / "summary.json")["interesting"]
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    ncol = 5
    nrow = -(-len(rows) // ncol)                                         # ceiling division
    fig = plt.figure(figsize=(3.4 * ncol, 3.9 * nrow + 0.8))
    for j, r in enumerate(rows):
        d, c = r["id"], realdata.cloud(r["id"])
        a3 = fig.add_subplot(nrow, ncol, j + 1, projection="3d")
        _loop_3d(a3, c["y"], np.array(r["cycle"]), _point_rgb(d, c["labels"]))
        colour = ("#1b7837" if r["k"] == 1 and inv.loc[d, "q_top_loop"] < 0.05 else
                  "#e08214" if r["p"] < 0.05 else "#222222")
        name = short(d).replace("C3_", "").replace("C1_", "").replace("colors", "colours")   # readable cloud name
        what = (f"{r['length']} points; concept winding {r['winding']:+d}" if r["cyclic"] else
                f"{r['length']} points on the cycle")
        a3.set_title(f"{name}, loop #{r['k']}\n{r['reasons']}\nπ = {r['pi']:.3f}, p = {r['p']:.3f}, size "
                     f"{r['size']:.3f}\n{what}", fontsize=7.5, color=colour)
    fig.suptitle("Every interesting loop of the 44 clouds (picked by rule: significant, large, or the concepts go "
                 "around it once; post hoc), drawn as a red cycle seen face-on", fontsize=11, y=0.995)
    fig.text(0.5, 0.005, "Green: a cloud's most persistent loop surviving Benjamini-Hochberg over the 44 loop tests. "
             "Orange: p < 0.05 only. Points coloured by concept (colours: in their own colour). Small loops are circled.",
             ha="center", fontsize=8)
    save(fig, "fig_loop_gallery")


def fig_void_life(d: str = "R3_tms_n6") -> None:
    """How a void is born and filled, step by step, on the toy model with 6 features (examples.void_life). Four 3D
    panels show the alpha complex at four radii: edges (dark grey), triangles (faint red), tetrahedra (grey), and,
    while the void is alive, the ball of radius death - r around its centre that no ball of radius r reaches yet
    (blue). Right: the loop (H1, dots) and void (H2, triangle) persistence diagram with the four radii marked and the
    void null's 95th-percentile line."""
    from itertools import combinations
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
    from neurotopo.report.examples import void_life
    life = void_life(d)
    y, cx = life["y"], life["complex"]
    q95 = float(pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id").loc[d, "null_q95_pi2"])
    names = ["loops, no void yet", "the void has just closed", "the void is shrinking", "the void is filled"]
    fig = plt.figure(figsize=(16, 4.6))
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 1, 1.05], wspace=0.12, top=0.78, bottom=0.12)
    lim = float(np.linalg.norm(y, axis=1).max())
    for j, s in enumerate(life["stages"]):
        here = [np.array(sx) for sx, x in cx if x <= s["r"]]
        edges, tris, tets = ([sx for sx in here if len(sx) == m] for m in (2, 3, 4))
        a3 = fig.add_subplot(gs[0, j], projection="3d")
        a3.computed_zorder = False                                       # draw in call order
        a3.scatter(*y.T, color="#222222", s=30, depthshade=False, zorder=1)
        if s["pocket"] > 0:                                              # the part of the void no ball reaches yet
            a3.plot_surface(*(life["centre"][:, None, None] + s["pocket"] * BALL), color=BLUE, alpha=0.9, shade=False,
                            linewidth=0, zorder=2)
        if tets:                                                         # filled: the tetrahedra's faces in grey
            a3.add_collection3d(Poly3DCollection([y[list(f)] for t in tets for f in combinations(t, 3)],
                                                 facecolors="#888888", edgecolors="none", alpha=0.3, zorder=3))
        if tris:
            a3.add_collection3d(Poly3DCollection(y[np.array(tris)], facecolors=RED, edgecolors="none", alpha=0.15,
                                                 zorder=4))
        if edges:
            a3.add_collection3d(Line3DCollection(y[np.array(edges)], colors="#444444", linewidths=1.4, zorder=5))
        a3.set_xlim(-lim, lim)
        a3.set_ylim(-lim, lim)
        a3.set_zlim(-lim, lim)
        a3.set_box_aspect((1, 1, 1), zoom=1.25)
        a3.set_axis_off()
        a3.set_title(f"({j + 1}) r = {s['r']:.3f}: {names[j]}\n{s['edges']} edges, {s['triangles']} triangles, "
                     f"{s['tetrahedra']} tetrahedra\n{s['loops']} loops, {s['voids']} void{'' if s['voids'] == 1 else 's'}" +
                     (f"; empty ball radius {s['pocket']:.3f}" if s["pocket"] > 0 else ""), fontsize=8.5)
    ap = fig.add_subplot(gs[0, 4])
    lo, hi = 0.65, 1.1
    ap.plot([lo, hi], [lo, hi], color="#999", lw=0.8)
    ap.plot([lo, hi / q95], [lo * q95, hi], color="#555", ls="--", lw=0.9)
    ap.scatter(*life["h1"].T, s=22, color="#444444", label="loops (H1)", zorder=3)
    ap.text(*(life["h1"].mean(0) + [0.012, 0]), f"{len(life['h1'])} loops, on top\nof each other", fontsize=7.5,
            va="center")                                                 # they are born and die at nearly the same radii
    ap.scatter(*life["h2"].T, s=80, marker="^", color=RED, edgecolors="k", linewidths=0.8, label="voids (H2)", zorder=4)
    for j, s in enumerate(life["stages"]):
        ap.axvline(s["r"], color="#888", ls=":", lw=0.9)
        ap.text(s["r"], hi, f" {j + 1}", fontsize=8, va="top")
    ap.set_xlim(lo, hi)
    ap.set_ylim(lo, hi)
    ap.set_aspect("equal")
    ap.tick_params(labelsize=7)
    ap.set_xlabel("birth radius", fontsize=8)
    ap.set_ylabel("death radius", fontsize=8)
    ap.legend(fontsize=7.5, loc="lower right")
    ap.set_title("persistence diagram (dotted: the four radii)", fontsize=8.5)
    fig.suptitle("The life of a void: the toy model with 6 features. Its edges make loops, its 8 faces close the loops "
                 "into one void, and the tetrahedra inside fill it", fontsize=11)
    save(fig, "fig_void_life")
