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
    path.write_text(s, encoding="utf-8")


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


def exp1_table() -> str:
    s = read_json(res("exp1", "summary.json"))
    rows = [{"estimator": k, "macro exact accuracy": v["macro_exact"], "95% CI": f"[{v['ci'][0]:.3f}, {v['ci'][1]:.3f}]",
             "n clouds": v["n"]} for k, v in s["table"].items()]
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
            "b0_rc", "b1_rc", "b2_rc", "chi_rc", "genus_rc", "homotopy_rc", "b1_alpha_univ", "b1_rips_univ",
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


def coords_table() -> str:
    q = pd.read_csv(res("coords", "point_coordinates.csv"))
    cols = [c for c in ("id", "family", "coordinate", "variable", "statistic", "n", "R", "p", "winding", "rho", "NMI", "ARI")
            if c in q.columns]
    return tables.md_table(q[cols], 3)


# ----------------------------------------------------------------------------- orchestration
SECTIONS = [("exp0_topology", exp0_table, ("exp0", "real_topology.csv")),
            ("exp0_alignment", exp0_alignment_table, ("exp0", "real_alignment.json")),
            ("exp1", exp1_table, ("exp1", "summary.json")),
            ("exp2", exp2_table, ("exp2", "invariants.csv")),
            ("exp3", exp3_tables, ("exp3", "summary.json")),
            ("coords", coords_table, ("coords", "point_coordinates.csv")),
            ("exp6sim", exp6sim_table, ("exp6_sim", "summary.json"))]


def render_templates(nums: dict) -> None:
    """README.template.md -> README.md and reports/templates/*.md -> reports/*.md with {{key}} placeholders filled;
    paper/generated/numbers.tex gets one LaTeX macro per number."""
    root = config.ROOT
    pairs = [(root / "README.template.md", root / "README.md")]
    pairs += [(t, root / "reports" / t.name) for t in sorted((root / "reports" / "templates").glob("*.md"))]
    pairs += [(root / "paper" / "main.template.tex", root / "paper" / "main.tex")]
    for src, dst in pairs:
        if src.exists():
            dst.write_text(numbers.render(src.read_text(encoding="utf-8"), nums, latex=src.suffix == ".tex"),
                           encoding="utf-8")
    gen = root / "paper" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "numbers.tex").write_text(numbers.latex_macros(nums) + "\n", encoding="utf-8")


def run() -> None:
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
    figures.fig_pipeline()
    if have("exp0", "real_alignment.json"):
        figures.fig_exp0_helix()
        figures.fig_exp0_margin()
    if have("exp1", "summary.json"):
        figures.fig_exp1_estimators()
        figures.fig_exp1_by_rho()
    if have("exp2", "invariants.csv"):
        figures.fig_real_gallery(["R5a_llama_weekdays", "R5b_llama_months", "R2_grokking_WE", "R7_llama_colors",
                                  "R6_llama_years", "R1_gpt2_wpos", "C3_llama_weekdays_init", "C1_walk_0"], "fig_real_gallery")
    if have("exp6_sim", "simulated_steering.json"):
        figures.fig_exp6sim()
