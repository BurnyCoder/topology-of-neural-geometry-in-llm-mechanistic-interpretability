"""`run.py report`: regenerate every table, figure and number in README, reports and paper from results/.

Global context: no number in the documentation is typed by hand. This phase reads results/<exp>/*.json|csv,
writes markdown fragments to reports/generated/, replaces the text between <!-- BEGIN:x --> / <!-- END:x -->
markers in README.md and reports/*.md, writes LaTeX macros/tables to paper/generated/, and draws all figures.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.experiments.common import read_json
from neurotopo.report import figures, numbers, tables
from neurotopo.report.science import ordered_estimators

log = logging.getLogger(__name__)
R = None


def res(*parts) -> Path:
    return config.path("results").joinpath(*parts)


def have(*parts) -> bool:
    return res(*parts).exists()


def replace_block(path: Path, key: str, text: str) -> None:
    """Replace the content between <!-- BEGIN:key --> and <!-- END:key --> in a markdown file."""
    if not path.exists():
        return
    s = path.read_text(encoding="utf-8")
    pat = re.compile(rf"(<!-- BEGIN:{key} -->)(.*?)(<!-- END:{key} -->)", re.S)
    if not pat.search(s):
        return
    s = pat.sub(lambda m: m.group(1) + "\n" + text.strip() + "\n" + m.group(3), s)
    path.write_text(s, encoding="utf-8", newline=chr(10))


# ----------------------------------------------------------------------------- tables
def exp0_table() -> str:
    d = pd.read_csv(res("exp0", "real_topology.csv"))
    d = d[["id", "family", "b0", "b1", "b2", "chi", "genus", "homotopy", "rho_A", "resolvable"]]
    return tables.md_table(d, 2)


def exp0_alignment_table() -> str:
    recs = read_json(res("exp0", "real_alignment.json"))
    rows = [{"id": r["id"], "coordinate": r["coordinate"], "kind": r["kind"], "variable": r["variable"], "R": r["R"],
             "p": r["p"], "winding": r["winding"], "closure gap": r.get("closure_gap")} for r in recs]
    return tables.md_table(pd.DataFrame(rows), 3)


def exp0_family_homotopy_table() -> str:
    """Family x registered catalog Betti vector on the 39,000 synthetic test clouds (all / resolvable): which
    geometric families are topologically equivalent (plan, Exp1)."""
    d = pd.read_csv(res("exp0", "synth_test_topology.csv.gz"), usecols=["family_name", "b0", "b1", "b2", "resolvable"])
    d["Betti vector"] = ["(" + ", ".join(map(str, v)) + ")" if v[0] <= 1 else "(k, 0, 0), k >= 2"
                         for v in d[["b0", "b1", "b2"]].itertuples(index=False)]
    t = pd.crosstab(d["family_name"], d["Betti vector"])
    r = pd.crosstab(d.loc[d["resolvable"], "family_name"], d.loc[d["resolvable"], "Betti vector"])
    out = t.astype(str) + " (" + r.reindex_like(t).fillna(0).astype(int).astype(str) + ")"
    head = "Clouds per family and catalog Betti target (in brackets: resolvable, rho_A >= 1)."
    return head + "\n\n" + tables.md_table(out.reset_index().rename(columns={"family_name": "family"}), 0)


def role_table() -> str:
    """Real data by role: test sets (cyclic concepts) vs negative controls (ordinal concepts, random-init networks,
    random processes). Per group, how many sets have: a top-3 loop under the design-matched MC null (Exp2); a
    resolvable fitted hole that the concept goes around (Method A); a loop that the concept goes around in the
    preregistered theta_B (Method B, 3D); the same plus the preregistered top-10-PC check (full H1-B conjunction);
    a single traversal in 3D post hoc (DREiMac standard_range=False, D5). Definitions: report/verdicts.py."""
    from neurotopo.report import verdicts as v
    cfg = config.load()
    c1 = sorted(d for d in pd.read_csv(res("exp2", "invariants.csv"))["id"] if d.startswith("C1_"))
    groups = [("test: cyclic, primary (H1)", cfg["groups"]["cyclic_primary"]),
              ("test: cyclic, secondary (H3)", cfg["groups"]["cyclic_secondary"]),
              ("test: cyclic, exploratory", ["R7_llama_colors"]),
              ("negative control: ordinal concepts (H2)", cfg["groups"]["ordinal"]),
              ("control: random-init networks (H2)", cfg["groups"]["init_controls"]),
              ("control: random walks / Gaussian processes (H2)", c1)]
    rows = []
    for role, ids in groups:
        cnt = lambda f: f"{sum(bool(f(d)) for d in ids)}/{len(ids)}"
        rows.append({"role": role, "sets": ", ".join(figures.short(d) for d in ids) if len(ids) < 7 else f"{len(ids)} sets",
                     "loop in top-3 PCs (MC null, p < 0.05)": cnt(v.loop),
                     "A: resolvable fitted hole, goes around": cnt(v.method_a),
                     "B: loop, goes around (θ_B, 3D)": cnt(v.method_b),
                     "B + top-10 check (full H1-B rule)": cnt(v.method_b10),
                     "goes around once, post hoc (3D)": cnt(v.posthoc)})
    return tables.md_table(pd.DataFrame(rows), 0)


def exp1_table() -> str:
    s = read_json(res("exp1", "summary.json"))
    rows = []
    for name in ordered_estimators(s["table"]):
        value = s["table"][name]
        rows.append({"estimator": name, "macro exact accuracy": value["macro_exact"],
                     "95% CI": f"[{value['ci'][0]:.3f}, {value['ci'][1]:.3f}]", "n clouds": value["n"]})
    diffs = [{"comparison": k, "difference": v["estimate"], "95% CI": f"[{v['ci'][0]:.3f}, {v['ci'][1]:.3f}]"}
             for k, v in s["paired_differences"].items()]
    fpr = pd.DataFrame(s["fpr_contractible"]).T.rename(columns=lambda c: f"N-bin {c}")
    fpr.insert(0, "estimator", fpr.index)
    cal = pd.DataFrame(s["calibration_blobs"]).T
    cal.insert(0, "N-bin", cal.index)
    pf = pd.DataFrame({k: v["per_family"] for k, v in s["table"].items() if "per_family" in v})
    pf.insert(0, "family", pf.index)
    return "\n\n".join([tables.md_table(pd.DataFrame(rows)), "Paired differences (primary minus comparator):",
                        tables.md_table(pd.DataFrame(diffs)),
                        "False-positive rate (b1 >= 1 or b2 >= 1) on resolvable contractible clouds, by N-bin:",
                        tables.md_table(fpr.reset_index(drop=True)),
                        "Universal-null calibration on blobs (FWER = fraction with any significant alpha H1 bar):",
                        tables.md_table(cal.reset_index(drop=True)),
                        "Per-family exact accuracy (resolvable clouds):", tables.md_table(pf.reset_index(drop=True)),
                        f"Resolvable fraction of test clouds: {tables.fmt(s['resolvable_fraction'])}."])


def exp2_table() -> str:
    d = pd.read_csv(res("exp2", "invariants.csv"))
    cols = ["id", "N", "design", "top_pi1", "null_q95_pi1", "p_top_loop", "top_pi2", "null_q95_pi2", "p_top_void",
            "b0_rc", "b1_rc", "b2_rc", "chi_rc", "genus_rc", "betti_label_rc", "b1_alpha_univ", "b1_rips_univ",
            "loop_freq", "family", "A_b1", "A_b2"]
    return tables.md_table(d[[c for c in cols if c in d.columns]], 3)


def exp3_tables() -> str:
    s = read_json(res("exp3", "summary.json"))
    rows = []
    for d, v in s["H1"].items():
        for m in ("A", "B"):
            row = {"dataset": d, "method": m, "p raw": v[m]["p_raw"], "p Holm": v[m]["p_holm"], "pass": v[m]["pass"]}
            row.update({k: v[m][k] for k in v[m] if k not in ("p_raw", "p_holm", "pass")})
            rows.append(row)
    h2 = s["H2_summary"]
    h2rows = [{"method": m, "ordinal sets passing (of 6)": h2[m]["ordinal_pass"], "init controls passing (of 3)": h2[m]["init_pass"],
               "C1 controls passing (of 20)": h2[m]["c1_pass"], "C1 rate 95% CI": f"[{h2[m]['c1_fpr_ci'][0]:.2f}, {h2[m]['c1_fpr_ci'][1]:.2f}]",
               "falsified": h2[m]["falsified"]} for m in ("A", "B")]
    h4 = s["H4"]["balanced_accuracy"]
    expl = pd.DataFrame(s["exploratory"])
    keep = [c for c in ("id", "method", "variable", "R", "p", "q_bh", "winding", "loop", "kind") if c in expl.columns]
    return "\n\n".join([
        "H1 (co-primary): " + ", ".join(f"Method {m}: {n}/3 datasets pass" for m, n in s["H1_verdict_passes_of_3"].items()),
        tables.md_table(pd.DataFrame(rows)), "H2 (specificity):", tables.md_table(pd.DataFrame(h2rows)),
        "H3 (R5c day phase): " + ", ".join(f"Method {m}: {'pass' if s['H3'][m]['pass'] else 'fail'}" for m in ("A", "B")),
        "H4 balanced accuracy (cyclic vs ordinal): " + ", ".join(f"{k} {tables.fmt(v)}" for k, v in h4.items()) +
        "; exact McNemar: " + ", ".join(f"{k} p = {tables.fmt(v)}" for k, v in s["H4"]["mcnemar"].items()),
        "Exploratory alignment records (BH q-values):", tables.md_table(expl[keep])])


def exp6sim_table() -> str:
    s = read_json(res("exp6_sim", "simulated_steering.json"))
    rows = []
    for d, r in s.items():
        row = {"dataset": d, "hole (B)": r.get("hole_detected_B")}
        for key, lab in (("B_cohomology", "B"), ("A_fitted_axis_circle", "A"), ("chord_centroids", "chord")):
            if key in r:
                row[f"T {lab}"] = r[key]["T"]
                row[f"wind1 {lab}"] = r[key]["frac_wind1"]
                row[f"on-manifold {lab}"] = r[key]["vocab_mass"]
        row["random q95"] = r.get("random_null", {}).get("T_random_q95")
        row["p (B vs random)"] = r.get("random_null", {}).get("p")
        row["H6-sim pass"] = r.get("H6_sim_pass")
        rows.append(row)
    summ = read_json(res("exp6_sim", "summary.json"))
    return (f"Verdict (cyclic datasets with a detected hole): {summ['verdict']}; cyclic with hole: "
            f"{', '.join(summ['cyclic_with_hole']) or 'none'}; passing: {', '.join(summ['cyclic_with_hole_pass']) or 'none'}; "
            f"non-cyclic with hole passing: {', '.join(summ['noncyclic_with_hole_pass']) or 'none'}.\n\n"
            + tables.md_table(pd.DataFrame(rows), 3))


def audit_tables() -> str:
    """Exp7 audit (post hoc, D8): where the top loop of each cluster design lives, the preregistered closure
    ratio of every concept set, and subsample stability against full-size and size-matched thresholds."""
    from neurotopo.report.figures import short
    a = read_json(res("exp7_audit", "summary.json"))
    loc = pd.DataFrame([{"dataset": short(d), "top bar birth": v["top_bar"][0], "top bar death": v["top_bar"][1],
                         "clusters first touch (radius)": v["connect_radius"], "mean within-concept radius": v["within_radius"],
                         "loop inside one cluster": v["within_concept_loop"], "top pi of concept means alone": v["means_top_pi1"],
                         "last->first step / median step": v["last_first_step_over_median"]}
                        for d, v in a["localisation"].items()])
    cl = pd.DataFrame(a["closure"])
    cl["id"] = cl["id"].map(short)
    st = pd.DataFrame([{"dataset": short(d), "null q95 (full N)": v["q95_full"], "loop kept (full-N threshold)": v["freq_full_threshold"],
                        "null q95 (80% N)": v["q95_sub"], "loop kept (size-matched threshold)": v["freq_matched_threshold"]}
                       for d, v in a["stability"].items()])
    pw = pd.DataFrame(a["power"]).rename(columns={"nearest_loop": "loop pass (nearest cell)", "ci_lo": "95% CI low",
                                                  "ci_hi": "95% CI high", "interp_loop": "loop pass (interpolated)"})
    return "\n\n".join(["Where the most persistent loop lives (normalised top-3 cloud, radius units):", tables.md_table(loc, 3),
                        "Subsample stability (200 subsamples of 80%):", tables.md_table(st, 3),
                        "Corrected power simulation (power2), loop condition (a) with exact 95% CIs (40 replicates per cell):",
                        tables.md_table(pw, 3),
                        "Preregistered closure ratio (section 5; full activation space, cosine): d(last, first) / median d(c, c+1):",
                        tables.md_table(cl, 3)])


def audit3_tables() -> str:
    """Exp8 audit (post hoc, D9): hole sensitivity and false-loop rate of the synthetic estimators (overall and per
    family), the cluster-centre null on hole-free arrangements of concept centres, centre loops in other projections,
    and the dense-check tori."""
    from neurotopo.report.figures import short
    a = read_json(res("exp8_audit3", "summary.json"))
    sy = a["synthetic"]
    est = pd.DataFrame([{"estimator": k.split("|")[0], "clouds": k.split("|")[1],
                         "hole sensitivity": v["sensitivity"]["rate"], "sens. 95% CI": _ci(v["sensitivity"]["ci"]),
                         "n (true b1 >= 1)": v["sensitivity"]["n"], "false-loop rate": v["false_loop"]["rate"],
                         "FPR 95% CI": _ci(v["false_loop"]["ci"]), "n (true b1 = 0)": v["false_loop"]["n"]}
                        for k, v in sy.items() if "|" in k])
    fam = pd.read_csv(res("exp8_audit3", "synthetic_by_family.csv"))
    piv = fam.pivot_table(index=["family", "true_b1"], columns="estimator", values="loop_rate").reset_index()
    piv = piv.merge(fam[fam["estimator"] == "MC"][["family", "true_b1", "n"]], on=["family", "true_b1"])
    cl = []
    for k, v in a["cluster"].items():
        for arr, r in v["arrangements"].items():
            cl.append({"design": f"{k[1:]} clusters ({short(v['real_id'])}-like)", "arrangement": arr,
                       "loop pass": r["pass"], "95% CI": _ci(r["ci"]), "max over cells": r["pass_max_over_cells"],
                       "median top pi": r["median_pi1"], f"share with pi >= real": r["frac_pi_ge_real"],
                       "verdict (cap, grid)": v["verdict"]})
    cen = pd.DataFrame([{"dataset": short(d), "cloud PC1-PC2 (alpha)": v["pc12_alpha_pi"], "cloud top-3 (alpha)": v["pc123_alpha_pi"],
                         **{f"own top-{k} (Rips)": v[f"own_top{k}_rips_pi"] for k in range(2, 7)}}
                        for d, v in a["centres"].items()])
    tor = pd.DataFrame(a["tori"])
    return "\n\n".join([
        "Loop detection on synthetic clouds of known topology (resolvable clouds; >= 1 significant H1 bar; "
        "cluster-bootstrap 95% CIs over generator chunks):", tables.md_table(est, 3),
        "Fraction of clouds with >= 1 significant H1 bar, per family (resolvable clouds of the 3,120-cloud subset; "
        "true_b1 = 0 rows are false loops):", tables.md_table(piv, 3),
        "Cluster-centre null on concept centres in five arrangements (cell nearest the real top-3 share; 40 replicates; "
        "exact 95% CIs):", tables.md_table(pd.DataFrame(cl), 3),
        "Largest H1 pi of the concept centres in other projections:", tables.md_table(cen, 3),
        "Dense-check tori without a counted void:", tables.md_table(tor, 3)])


def _ci(ci) -> str:
    return "-" if ci[0] is None else f"[{tables.fmt(ci[0], 3)}, {tables.fmt(ci[1], 3)}]"


def coords_table() -> str:
    q = pd.read_csv(res("coords", "point_coordinates.csv"))
    cols = [c for c in ("id", "family", "coordinate", "variable", "statistic", "n", "R", "p", "winding", "rho", "NMI", "ARI")
            if c in q.columns]
    return tables.md_table(q[cols], 3)


def voids_table() -> str:
    """The interesting voids (results/voids/summary.json, run.py voids; post hoc, D10), in the gallery's order."""
    rows = pd.DataFrame(read_json(res("voids", "summary.json"))["interesting"])
    rows["shell corners"] = [f"{c} of {n} points" for c, n in zip(rows["corners"], rows["N"])]
    rows["concepts on shell"] = [f"{s} of {n}" for s, n in zip(rows["shell_concepts"], rows["n_concepts"])]
    out = rows.rename(columns={"k": "void # (by pi)", "pi": "pi", "empty": "empty middle (death - birth)",
                               "extent": "span of cloud"})
    return tables.md_table(out[["id", "void # (by pi)", "reasons", "birth", "death", "pi", "p",
                                "empty middle (death - birth)", "faces", "shell corners", "span of cloud",
                                "concepts on shell"]], 3)


def loops_table() -> str:
    """The interesting loops (results/loops/summary.json, run.py loops; post hoc, D11), in the gallery's order."""
    rows = pd.DataFrame(read_json(res("loops", "summary.json"))["interesting"])
    rows["concepts on cycle"] = [f"{s} of {n}" for s, n in zip(rows["loop_concepts"], rows["n_concepts"])]
    rows["concept winding"] = [f"{w:+d}" if c else "-" for w, c in zip(rows["winding"], rows["cyclic"])]
    out = rows.rename(columns={"k": "loop # (by pi)", "size": "size (death - birth)", "length": "cycle points",
                               "extent": "span of cloud"})
    return tables.md_table(out[["id", "loop # (by pi)", "reasons", "birth", "death", "pi", "p", "size (death - birth)",
                                "cycle points", "span of cloud", "concepts on cycle", "concept winding"]], 3)


# ----------------------------------------------------------------------------- orchestration
SECTIONS = [("exp0_topology", exp0_table, ("exp0", "real_topology.csv")),
            ("exp0_alignment", exp0_alignment_table, ("exp0", "real_alignment.json")),
            ("exp0_family_homotopy", exp0_family_homotopy_table, ("exp0", "synth_test_topology.csv.gz")),
            ("exp1", exp1_table, ("exp1", "summary.json")),
            ("readme_roles", role_table, ("exp3", "method_b.json")),
            ("exp2", exp2_table, ("exp2", "invariants.csv")),
            ("exp3", exp3_tables, ("exp3", "summary.json")),
            ("coords", coords_table, ("coords", "point_coordinates.csv")),
            ("audit", audit_tables, ("exp7_audit", "summary.json")),
            ("audit3", audit3_tables, ("exp8_audit3", "summary.json")),
            ("voids", voids_table, ("voids", "summary.json")),
            ("loops", loops_table, ("loops", "summary.json")),
            ("exp6sim", exp6sim_table, ("exp6_sim", "summary.json"))]


def render_templates(nums: dict) -> None:
    """README.template.md -> README.md, reports/templates/*.md -> reports/*.md and docs/templates/*.md -> docs/*.md
    with {{key}} placeholders filled; paper/generated/numbers.tex gets one LaTeX macro per number."""
    root = config.ROOT
    pairs = [(root / "README.template.md", root / "README.md")]
    for folder in ("reports", "docs"):
        pairs += [(t, root / folder / t.name) for t in sorted((root / folder / "templates").glob("*.md"))]
    # Reviews with generated numbers (reports/templates/reviews/*.md -> reports/reviews/*.md; independent audit, D14).
    pairs += [(t, root / "reports" / "reviews" / t.name) for t in sorted((root / "reports" / "templates" / "reviews").glob("*.md"))]
    pairs += [(root / "paper" / "main.template.tex", root / "paper" / "main.tex")]
    for src, dst in pairs:
        if src.exists():
            dst.write_text(numbers.render(src.read_text(encoding="utf-8"), nums, latex=src.suffix == ".tex"),
                           encoding="utf-8", newline=chr(10))
    gen = root / "paper" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "numbers.tex").write_text(numbers.latex_macros(nums) + "\n", encoding="utf-8", newline=chr(10))


def render_documents() -> None:
    """Rebuild the study text, evidence tables and audit figure from completed results."""
    nums = numbers.collect()
    render_templates(nums)
    tables.write_generated("prereg_addendum_A1", tables.addendum())
    for key, fn, need in SECTIONS:
        if have(*need):
            txt = fn()
            tables.write_generated(key, txt)
            for f in [config.ROOT / "README.md", *sorted((config.ROOT / "reports").glob("*.md"))]:
                replace_block(f, key, txt)
            log.info("generated %s", key)
    if have("science", "summary.json"):
        from neurotopo.report import science
        science.dossier()
        science.figure()


def run() -> None:
    render_documents()
    figures.fig_pipeline()
    if have("exp0", "real_alignment.json"):
        figures.fig_exp0_helix()
        figures.fig_exp0_margin()
    if have("exp1", "summary.json"):
        figures.fig_exp1_estimators()
        figures.fig_exp1_by_rho()
    if have("exp1", "outliers.json"):
        figures.fig_exp1_outliers()
    if have("power", "power_v2_summary.csv"):
        figures.fig_power()
    if have("exp3", "method_b.json") and have("exp3", "posthoc_relaxed_range.json"):
        figures.fig_traversal()
    if have("exp4", "summary.json"):
        figures.fig_exp4()
    if have("exp5", "topk_null.csv"):
        figures.fig_top10()
    if have("exp2", "invariants.csv"):
        figures.fig_real_gallery(["R5a_llama_weekdays", "R5b_llama_months", "R2_grokking_WE", "R7_llama_colors",
                                  "R6_llama_years", "R1_gpt2_wpos", "C3_llama_weekdays_init", "C1_walk_0"], "fig_real_gallery")
        figures.fig_null_tests()
        figures.anim_clouds()
        figures.fig_detected_voids()
        if have("loops", "summary.json") and have("voids", "summary.json"):
            figures.fig_highlights()
            figures.fig_growing_balls()
            figures.anim_highlights_3d()
            figures.anim_highlights()
        if have("loops", "summary.json"):
            figures.fig_loop_gallery()
        if have("voids", "summary.json"):
            figures.fig_void_gallery()
        figures.fig_void_life()
        if have("exp3", "method_b.json") and have("exp3", "posthoc_relaxed_range.json"):
            figures.fig_examples()
            figures.anim_examples()
            figures.fig_detected_loops()
    if have("exp6_sim", "simulated_steering.json"):
        figures.fig_exp6sim()
    if have("toy", "summary.json"):
        figures.fig_toy()
