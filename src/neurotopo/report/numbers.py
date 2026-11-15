"""Every number quoted in README, reports and paper, computed from results/ into one flat dictionary.

Global context: documentation templates (README.template.md, reports/templates/*.md, paper macros) contain
placeholders {{key}} that `render` replaces with values from `collect()`, so prose never contains hand-typed
numbers and one command (`run.py report`) regenerates all of them. Keys are dotted names, e.g.
"exp1.P.acc" or "exp2.R7_llama_colors.p_loop".
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.experiments.common import read_json
from neurotopo.report.tables import fmt

SHORT = {"R5a_llama_weekdays": "weekdays", "R5b_llama_months": "months", "R2_grokking_WE": "grok",
         "R5c_llama_days_time": "daystime", "R7_llama_colors": "colors", "R6_llama_years": "years",
         "R1_gpt2_wpos": "wpos", "R4_llama_counting": "counting", "R4b_pythia_counting": "pythia",
         "R8a_llama_temperature": "temperature", "R8b_llama_age": "age", "R5b_llama_months_means": "monthsmeans",
         "R5a_llama_weekdays_means": "weekdaysmeans", "C3_grokking_WE_init": "grokinit",
         "C3_llama_weekdays_init": "weekdaysinit", "C3_llama_months_init": "monthsinit", "C3_tms_dense": "tmsdense",
         "R9_llama_truth_cities": "truth", "C3_gpt2_wpos_init": "wposinit"}


def _res(*p):
    return config.path("results").joinpath(*p)


def collect() -> dict:
    n = {}
    # Exp0: Method A on real fits and synthetic GT.
    if _res("exp0", "real_topology.csv").exists():
        t = pd.read_csv(_res("exp0", "real_topology.csv")).set_index("id")
        n["exp0.n_hole_fits"] = int((t["b1"] >= 1).sum())
        n["exp0.n_void_fits"] = int((t["b2"] >= 1).sum())
        n["exp0.n_resolvable"] = int(t["resolvable"].sum())
        n["exp0.families"] = ", ".join(f"{f} {c}" for f, c in t["family"].value_counts().items())
        for d, s in SHORT.items():
            if d in t.index:
                n[f"exp0.{s}.family"] = t.loc[d, "family"]
                n[f"exp0.{s}.rho"] = float(t.loc[d, "rho_A"])
        dc = read_json(_res("exp0", "summary.json"))
        n["exp0.dense_agree"] = dc["dense_check_agreement_all"]
        n["exp0.dense_agree_resolved"] = dc["dense_check_agreement_margin_ge_4_spacings"]
        n["exp0.dense_n"] = dc["dense_check_n"]
        recs = read_json(_res("exp0", "real_alignment.json"))
        for r in recs:
            s = SHORT.get(r["id"])
            if s and ("bins" not in r["variable"] or "7 bins" in r["variable"]) and "mod" not in r["variable"]:
                key = f"exp0.{s}.{r['coordinate']}"
                n[key + ".R"], n[key + ".p"], n[key + ".w"] = r["R"], r["p"], r["winding"]
                if r.get("closure_gap") is not None:
                    n[key + ".gap"] = r["closure_gap"]
        gp = [r for r in recs if r["id"].startswith("C1_gp") and "7 bins" in r["variable"]]
        n["exp0.gp_helix_n"] = len(gp)
        n["exp0.gp_wind1"] = sum(abs(r["winding"]) == 1 for r in gp)
        n["exp0.gp_R_min"] = min(r["R"] for r in gp) if gp else float("nan")
        n["exp0.gp_R_max"] = max(r["R"] for r in gp) if gp else float("nan")
        n["exp0.gp_gap_min"] = min(r["closure_gap"] for r in gp) if gp else float("nan")
        n["exp0.gp_gap_max"] = max(r["closure_gap"] for r in gp) if gp else float("nan")
        st = pd.read_csv(_res("exp0", "synth_test_topology.csv.gz"))
        n["exp0.synth_resolvable"] = float(st["resolvable"].mean())
    # Coordinates on fitted shapes.
    if _res("coords", "point_coordinates.json").exists():
        for q in read_json(_res("coords", "point_coordinates.json")):
            s = SHORT.get(q["id"])
            if not s:
                continue
            key = f"coords.{s}.{q['coordinate'].replace(' ', '_')}.{q['variable'].replace(' ', '_')}"
            for k in ("rho", "p", "R", "winding", "NMI", "ARI"):
                if k in q:
                    n[f"{key}.{k}"] = q[k]
            if "post_hoc_axial_harmonic_r2" in q:
                for h, v in q["post_hoc_axial_harmonic_r2"].items():
                    n[f"coords.{s}.harmonic.{h}"] = v
    # Power and tuning.
    if _res("power", "val_tuning.json").exists():
        t = read_json(_res("power", "val_tuning.json"))
        n["power.b0_tau"], n["power.b0_minfrac"], n["power.b0_acc"] = t["b0_tau"], t["b0_minfrac"], t["b0_val_accuracy"]
        n["power.pi0_1"], n["power.pi0_2"] = t["pi0_1"], t["pi0_2"]
        ps = pd.read_csv(_res("power", "power_summary.csv"))
        n["power.ring_all_min"] = float(ps[ps["arrangement"] == "ring"]["all"].min())
        n["power.random_all_max"] = float(ps[ps["arrangement"] == "random"]["all"].max())
        n["power.random_loop_max"] = float(ps[ps["arrangement"] == "random"]["loop"].max())
        n["power.arc_all_max"] = float(ps[ps["arrangement"] == "arc300"]["all"].max())
        if _res("power", "power_v2_summary.csv").exists():
            p2 = pd.read_csv(_res("power", "power_v2_summary.csv"))
            names = {7: "weekdays", 12: "months", 113: "grok"}
            real_top3 = {"weekdays": 0.0, "months": 0.0, "grok": 0.0}
            so = {r["id"]: r for r in read_json(_res("power", "real_second_order.json"))}
            real_top3 = {"weekdays": so["R5a_llama_weekdays"]["top3_explained"], "months": so["R5b_llama_months"]["top3_explained"],
                         "grok": so["R2_grokking_WE"]["top3_explained"]}
            for k, nm in names.items():
                ring = p2[(p2["k"] == k) & (p2["arrangement"] == "ring")]
                rnd = p2[(p2["k"] == k) & (p2["arrangement"] == "random")]
                j = (ring["top3"] - real_top3[nm]).abs().idxmin()       # cell closest to the real top-3 variance
                n[f"power2.{nm}.top3"], n[f"power2.{nm}.loop"], n[f"power2.{nm}.all"] = (
                    float(ring.loc[j, "top3"]), float(ring.loc[j, "loop"]), float(ring.loc[j, "all"]))
                n[f"power2.{nm}.real_top3"] = real_top3[nm]
                n[f"power2.{nm}.random_loop_max"] = float(rnd["loop"].max())
                n[f"power2.{nm}.ring_all_min"], n[f"power2.{nm}.ring_all_max"] = float(ring["all"].min()), float(ring["all"].max())
    # Exp1.
    if _res("exp1", "summary.json").exists():
        s = read_json(_res("exp1", "summary.json"))
        ab = {"P_alpha_universal": "P", "S_rips_universal": "S", "Ba_fixed_pi": "Ba", "Bb_family_implied": "Bb",
              "Bc_majority": "Bc", "MC_gaussian3d (subset)": "MC"}
        for k, a in ab.items():
            if k in s["table"]:
                v = s["table"][k]
                n[f"exp1.{a}.acc"], n[f"exp1.{a}.lo"], n[f"exp1.{a}.hi"] = v["macro_exact"], v["ci"][0], v["ci"][1]
                for fam, acc in v.get("per_family", {}).items():
                    n[f"exp1.{a}.{fam}"] = acc
        n["exp1.n"] = s["table"]["P_alpha_universal"]["n"]
        for k, v in s["paired_differences"].items():
            a = ab[k.replace("P - ", "")]
            n[f"exp1.diff.{a}"], n[f"exp1.diff.{a}.lo"], n[f"exp1.diff.{a}.hi"] = v["estimate"], v["ci"][0], v["ci"][1]
        n["exp1.P.fpr_max"] = max(s["fpr_contractible"]["P_alpha_universal"].values())
        n["exp1.P.fpr_min"] = min(s["fpr_contractible"]["P_alpha_universal"].values())
        n["exp1.resolvable"] = s["resolvable_fraction"]
        if "well_resolved" in s:
            w = s["well_resolved"]
            n["exp1.well.n"] = w["n"]
            triv = sum(v for f, v in w["family_counts"].items() if f in ("blob", "disc", "paraboloid"))
            n["exp1.well.trivial_frac"] = triv / w["n"]
            for k, a in ab.items():
                if k in w:
                    n[f"exp1.well.{a}.acc"], n[f"exp1.well.{a}.lo"], n[f"exp1.well.{a}.hi"] = w[k]["macro_exact"], *w[k]["ci"]
                    for fam, acc in w[k]["per_family"].items():
                        n[f"exp1.well.{a}.{fam}"] = acc
            for other, a in (("Bb_family_implied", "Bb"), ("Ba_fixed_pi", "Ba"), ("Bc_majority", "Bc")):
                v = w[f"P - {other}"]
                n[f"exp1.well.diff.{a}"], n[f"exp1.well.diff.{a}.lo"], n[f"exp1.well.diff.{a}.hi"] = v["estimate"], *v["ci"]
        last = list(s["accuracy_by_rho"]["P_alpha_universal"].keys())[-1]
        for a in ("P_alpha_universal", "S_rips_universal", "Ba_fixed_pi", "Bb_family_implied"):
            n[f"exp1.rho4.{ab[a]}"] = s["accuracy_by_rho"][a][last]
    # Exp2.
    if _res("exp2", "invariants.csv").exists():
        d = pd.read_csv(_res("exp2", "invariants.csv")).set_index("id")
        for i, s in SHORT.items():
            if i in d.index:
                for c in ("top_pi1", "null_q95_pi1", "p_top_loop", "top_pi2", "null_q95_pi2", "p_top_void", "loop_freq"):
                    n[f"exp2.{s}.{c}"] = float(d.loc[i, c])
                n[f"exp2.{s}.homotopy"] = d.loc[i, "homotopy_rc"]
        sm = read_json(_res("exp2", "summary.json"))
        n["exp2.agree"] = sm["agree_b1b2_A_vs_B"]
        n["exp2.n_loop"], n["exp2.n_void"] = sm["n_with_loop_mc"], sm["n_with_void_mc"]
        if "n_loop_q05" in sm:
            n["exp2.n_loop_q05"] = sm["n_loop_q05"]
            n["exp2.loops_q05"] = ", ".join(sm["loops_q05"])
            for i, sh in SHORT.items():
                if i in d.index and "q_top_loop" in d.columns:
                    n[f"exp2.{sh}.q_loop"] = float(d.loc[i, "q_top_loop"])
        c1 = d[d.index.str.startswith("C1_")]
        n["exp2.c1_loops"] = int((c1["p_top_loop"] < 0.05).sum())
        n["exp2.c1_pi_max"] = float(c1["top_pi1"].max())
        ordinal = ["R1_gpt2_wpos", "R4_llama_counting", "R4b_pythia_counting", "R6_llama_years", "R8a_llama_temperature",
                   "R8b_llama_age"]
        n["exp2.ordinal_loops"] = int((d.loc[ordinal, "p_top_loop"] < 0.05).sum())
    # Exp3.
    if _res("exp3", "summary.json").exists():
        s = read_json(_res("exp3", "summary.json"))
        n["exp3.H1A"], n["exp3.H1B"] = s["H1_verdict_passes_of_3"]["A"], s["H1_verdict_passes_of_3"]["B"]
        for d, v in s["H1"].items():
            sh = SHORT[d]
            for m in ("A", "B"):
                n[f"exp3.{sh}.{m}.p"], n[f"exp3.{sh}.{m}.holm"] = v[m]["p_raw"], v[m]["p_holm"]
                n[f"exp3.{sh}.{m}.pass"] = "pass" if v[m]["pass"] else "fail"
                for c in ("a_loop", "b_align", "c_wind1", "d_top10", "hole_resolvable", "traversal"):
                    if c in v[m]:
                        n[f"exp3.{sh}.{m}.{c}"] = "yes" if v[m][c] else "no"
        for m in ("A", "B"):
            h = s["H2_summary"][m]
            n[f"exp3.H2.{m}.ordinal"], n[f"exp3.H2.{m}.init"], n[f"exp3.H2.{m}.c1"] = h["ordinal_pass"], h["init_pass"], h["c1_pass"]
            n[f"exp3.H2.{m}.falsified"] = "falsified" if h["falsified"] else "not falsified"
            n[f"exp3.H3.{m}"] = "pass" if s["H3"][m]["pass"] else "fail"
        for k, v in s["H4"]["balanced_accuracy"].items():
            n[f"exp3.H4.{k}"] = v
        mb = read_json(_res("exp3", "method_b.json"))
        for d, v in mb.items():
            sh = SHORT.get(d)
            if sh and v["records3"]:
                r = v["records3"][0]
                n[f"exp3.{sh}.thetaB.R"], n[f"exp3.{sh}.thetaB.p"], n[f"exp3.{sh}.thetaB.w"] = r["R"], r["p"], r["winding"]
                if "k" in r:
                    n[f"exp3.{sh}.thetaB.k"] = r["k"]
            if sh:
                n[f"exp3.{sh}.thetaB"] = "none (no usable class)" if v["theta3_error"] else "computed"
                if v.get("rips_alpha_overlap") is not None:
                    n[f"exp3.{sh}.overlap"] = "yes" if v["rips_alpha_overlap"] else "no"
    # Exp3 post hoc (relaxed DREiMac range).
    if _res("exp3", "posthoc_relaxed_range.json").exists():
        ph = read_json(_res("exp3", "posthoc_relaxed_range.json"))
        for d, v in ph.items():
            sh = SHORT.get(d)
            if not sh:
                continue
            for dim in ("3d", "top10"):
                recs = v[dim]["records"]
                if recs:
                    r = recs[0]
                    n[f"exp3ph.{sh}.{dim}.R"], n[f"exp3ph.{sh}.{dim}.p"], n[f"exp3ph.{sh}.{dim}.w"] = r["R"], r["p"], r["winding"]
        non = [d for d in ph if d.startswith("C1_") or d in ("R1_gpt2_wpos", "R4_llama_counting", "R4b_pythia_counting",
                                                             "R6_llama_years", "R8a_llama_temperature", "R8b_llama_age")]
        hits = sorted({d for d in non for dim in ("3d", "top10") for r in ph[d][dim]["records"]
                       if abs(r["winding"]) == 1 and "mod" not in r["variable"]})
        n["exp3ph.noncyclic_wind1"] = len(hits)
        n["exp3ph.noncyclic_wind1_ids"] = ", ".join(hits) if hits else "none"
        inits = sorted({d for d in ph if d.startswith("C3_") for dim in ("3d", "top10") for r in ph[d][dim]["records"]
                        if abs(r["winding"]) == 1})
        n["exp3ph.init_wind1_ids"] = ", ".join(inits) if inits else "none"
    # Clean-room replication (scripts/compare_results.py output).
    if _res("replication.json").exists():
        r = read_json(_res("replication.json"))
        n["replication.files"], n["replication.identical"], n["replication.date"] = r["files"], r["identical"], r["date"]
    # Exp4 / Exp5.
    if _res("exp4", "summary.json").exists():
        s4 = read_json(_res("exp4", "summary.json"))
        n["exp4.cohesion_p"] = s4["cyclic_cohesion"]["p_exact"]
    if _res("exp5", "summary.json").exists():
        s5 = read_json(_res("exp5", "summary.json"))
        for r in s5["offset_removed"]:
            n[f"exp5.offset.{SHORT[r['id']]}.p_loop"] = r["p_loop"]
        for r in s5["seeds"]:
            n[f"exp5.seed{r['seed']}.{SHORT[r['id']]}.p_loop"] = r["p_loop"]
        for k, v in s5["nu_variant_resolvable_counts"].items():
            n[f"exp5.resolvable.{k}"] = v
        if _res("exp5", "topk_null.csv").exists():
            tk = pd.read_csv(_res("exp5", "topk_null.csv")).set_index("id")
            for d in tk.index:
                sh = SHORT.get(d)
                if sh:
                    n[f"exp5.top10.{sh}.pi"], n[f"exp5.top10.{sh}.q95"], n[f"exp5.top10.{sh}.p"] = (
                        float(tk.loc[d, "rips_pi1"]), float(tk.loc[d, "null_q95"]), float(tk.loc[d, "p_loop"]))
            n["exp5.top10.n_sig"] = int((tk["p_loop"] < 0.05).sum())
            n["exp5.top10.sig_ids"] = ", ".join(tk.index[tk["p_loop"] < 0.05])
        pr = pd.read_csv(_res("exp5", "projection.csv")).set_index("id")
        for d in pr.index:
            sh = SHORT.get(d)
            if sh:
                for c in ("rips3_pi1", "rips5_pi1", "rips10_pi1", "ripsD_cos_pi1"):
                    n[f"exp5.{sh}.{c}"] = float(pr.loc[d, c])
    return n


def render(text: str, nums: dict, latex: bool = False) -> str:
    """Replace {{key}} or {{key:digits}} with formatted values; unknown keys are left visible as ??key??.
    latex=True escapes underscores (dataset ids) so values are valid LaTeX text."""
    def sub(m):
        key, _, nd = m.group(1).partition(":")
        if key not in nums:
            return f"??{key}??"
        v = nums[key]
        out = fmt(v, int(nd)) if nd else fmt(v, 3)
        return out.replace("_", r"\_") if latex else out
    return re.sub(r"\{\{([^}]+)\}\}", sub, text)


def latex_macros(nums: dict) -> str:
    """\\newcommand macros for the paper (letters only in names: dots/digits mapped to words)."""
    out = []
    digits = {str(i): w for i, w in enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])}
    for k, v in nums.items():
        name = "".join(digits.get(ch, ch) for ch in re.sub(r"[^A-Za-z0-9]", "", k.title()))
        val = fmt(v, 3) if not isinstance(v, str) else v
        out.append(f"\\newcommand{{\\N{name}}}{{{val.replace('_', ' ')}}}")
    return "\n".join(out)
