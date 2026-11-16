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


ESTSHORT = {"MC": "mc"}            # exp8 per-family rows: estimator label -> number-key prefix (P, S, Ba stay)


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
            n["exp1.well.n_torus"] = int(w["family_counts"].get("torus", 0))   # tori never reach rho_A >= 4 (D8)
            n["exp1.well.n_families"] = len(w["family_counts"])
            for k, a in ab.items():
                if k in w:
                    n[f"exp1.well.{a}.acc"], n[f"exp1.well.{a}.lo"], n[f"exp1.well.{a}.hi"] = w[k]["macro_exact"], *w[k]["ci"]
                    for fam, acc in w[k]["per_family"].items():
                        n[f"exp1.well.{a}.{fam}"] = acc
            for other, a in (("Bb_family_implied", "Bb"), ("Ba_fixed_pi", "Ba"), ("Bc_majority", "Bc")):
                v = w[f"P - {other}"]
                n[f"exp1.well.diff.{a}"], n[f"exp1.well.diff.{a}.lo"], n[f"exp1.well.diff.{a}.hi"] = v["estimate"], *v["ci"]
        if _res("exp1", "outliers.json").exists():                 # D7: outlier FPR and the DTM conditional
            o = read_json(_res("exp1", "outliers.json"))
            n["exp1.out.factor"], n["exp1.out.thr"], n["exp1.out.flagged"] = o["far_factor"], o["threshold"], o["flagged_fraction"]
            n["exp1.out.dtm"] = "required" if o["dtm_required"] else "not required"
            n["exp1.out.gen.prob"], n["exp1.out.gen.fracmax"] = o["generator"]["outlier_prob"], o["generator"]["outlier_frac_max"]
            for k, a in ab.items():
                if k in o["fpr"]:
                    for lab in ("outlier", "clean"):
                        v = o["fpr"][k][lab]
                        n[f"exp1.out.{a}.{lab}"], n[f"exp1.out.{a}.{lab}.lo"], n[f"exp1.out.{a}.{lab}.hi"] = v["fpr"], *v["ci"]
                        n[f"exp1.out.{a}.{lab}.n"] = v["n"]
                    n[f"exp1.out.{a}.fisher"] = o["fpr"][k]["fisher_p_outlier_gt_clean"]
            for b, v in o["proxy_by_n_bin"].items():
                n[f"exp1.out.bin{b}.flagged"], n[f"exp1.out.bin{b}.expected"] = v["flagged"], v["expected_with_outliers"]
                n[f"exp1.out.bin{b}.range"] = f"{v['n_min']}–{v['n_max']}"
            fs = sorted(o["sensitivity"], key=float)
            n["exp1.out.sens.factors"] = " and ".join(f"{float(f):g}" for f in fs)
            n["exp1.out.sens.P.min"] = min([o["sensitivity"][f]["P_alpha_universal"] for f in fs] + [o["P_outlier_fpr"]])
            n["exp1.out.sens.P.max"] = max([o["sensitivity"][f]["P_alpha_universal"] for f in fs] + [o["P_outlier_fpr"]])
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
                n[f"exp2.{s}.b0"], n[f"exp2.{s}.b0_rc"] = int(d.loc[i, "b0"]), int(d.loc[i, "b0_rc"])
                n[f"exp2.{s}.ratio"] = float(d.loc[i, "top_pi1"] / d.loc[i, "null_q95_pi1"])   # ring strength / chance
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
        # Open-curve controls (ordinal sets and random processes) vs their Gaussian-null thresholds (audit, D8).
        op = d.loc[ordinal + list(c1.index)]
        n["exp2.open.pi_min"], n["exp2.open.pi_max"] = float(op["top_pi1"].min()), float(op["top_pi1"].max())
        n["exp2.open.q95_min"], n["exp2.open.q95_max"] = float(op["null_q95_pi1"].min()), float(op["null_q95_pi1"].max())
        n["exp2.open.p_min"] = float(op["p_top_loop"].min())
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
            n["exp5.top10.n"] = len(tk)
            n["exp5.top10.sig_ids"] = ", ".join(tk.index[tk["p_loop"] < 0.05])
            if _res("exp2", "invariants.csv").exists():             # same sets, 3D loop test (Exp2), for the ablation table
                inv = pd.read_csv(_res("exp2", "invariants.csv")).set_index("id")
                n["exp5.top3.n_sig"] = int((inv.loc[tk.index, "p_top_loop"] < 0.05).sum())
        pr = pd.read_csv(_res("exp5", "projection.csv")).set_index("id")
        for d in pr.index:
            sh = SHORT.get(d)
            if sh:
                for c in ("alpha3_pi1", "rips3_pi1", "rips5_pi1", "rips10_pi1", "ripsD_cos_pi1"):
                    n[f"exp5.{sh}.{c}"] = float(pr.loc[d, c])
    # Exp7 audit (post hoc, D8): stimulus baseline, loop localisation, closure ratio, PCA, stability, power CIs.
    if _res("exp7_audit", "summary.json").exists():
        a = read_json(_res("exp7_audit", "summary.json"))
        rgb, lla = a["colour_baseline"]["rgb"], a["colour_baseline"]["llama"]
        n["audit.rgb.pi"], n["audit.rgb.q95"], n["audit.rgb.p"] = rgb["top_pi1"], rgb["null_q95"], rgb["p_loop"]
        n["audit.rgb.ratio"], n["audit.rgb.freq"] = rgb["top_pi1"] / rgb["null_q95"], rgb["loop_freq"]
        n["audit.rgb.means_pi"], n["audit.rgb.means_R"], n["audit.rgb.means_w"] = (
            rgb["means_top_pi1"], rgb["means_pc12_R"], rgb["means_pc12_winding"])
        n["audit.rgb.m"] = rgb["m"]
        for name in ("prereg", "relaxed"):
            t = rgb["traversal"][name]
            n[f"audit.rgb.thetaB.{name}"] = "no coordinate" if t["record"] is None else \
                f"R = {fmt(t['record']['R'], 2)}, winding {t['record']['winding']}"
        n["audit.llama_over_rgb"] = lla["top_pi1"] / rgb["top_pi1"]
        for d, v in a["localisation"].items():
            sh = SHORT[d]
            n[f"audit.loc.{sh}.birth"], n[f"audit.loc.{sh}.death"] = v["top_bar"]
            n[f"audit.loc.{sh}.connect"], n[f"audit.loc.{sh}.within"] = v["connect_radius"], v["within_radius"]
            n[f"audit.loc.{sh}.inside"] = "yes" if v["within_concept_loop"] else "no"
            n[f"audit.loc.{sh}.means_pi"], n[f"audit.loc.{sh}.lastfirst"] = v["means_top_pi1"], v["last_first_step_over_median"]
        cl = pd.DataFrame(a["closure"])
        for d in cl["id"].unique():
            sh = SHORT.get(d)
            r = cl[(cl["id"] == d) & ~cl["variable"].str.contains("12 bins")]
            if sh and len(r):
                n[f"audit.closure.{sh}"] = float(r["closure_ratio"].iloc[0])
        for grp, mask in (("ordinal", cl["id"].isin(["R1_gpt2_wpos", "R4_llama_counting", "R4b_pythia_counting",
                                                        "R6_llama_years", "R8a_llama_temperature", "R8b_llama_age"])),
                          ("c1", cl["id"].str.startswith("C1_"))):
            r = cl[mask & cl["variable"].str.contains("7 bins")]["closure_ratio"]
            n[f"audit.closure.{grp}.min"], n[f"audit.closure.{grp}.max"] = float(r.min()), float(r.max())
        for r in a["pca"]:
            sh = SHORT[r["id"]]
            n[f"audit.pca.{sh}.gap34"] = r["gap34"]
            for i in range(1, 7):
                n[f"audit.pca.{sh}.l{i}"] = r[f"l{i}"]
        gf = a["grok_fourier"]
        n["audit.grok.freqs"] = ", ".join(str(k) for k in gf["top_frequencies"][:5])
        n["audit.grok.share_min"], n["audit.grok.share_max"] = min(gf["shares"][:5]), max(gf["shares"][:5])
        n["audit.grok.share_sum"] = sum(gf["shares"][:5])
        for d, v in a["stability"].items():
            sh = SHORT[d]
            n[f"audit.stab.{sh}.full"], n[f"audit.stab.{sh}.matched"] = v["freq_full_threshold"], v["freq_matched_threshold"]
            n[f"audit.stab.{sh}.q95_full"], n[f"audit.stab.{sh}.q95_sub"] = v["q95_full"], v["q95_sub"]
        for key, v in a["posthoc"].items():
            d, dim = key.split("|")
            sh = SHORT[d]
            if v["overlap"] is not None:
                n[f"audit.ph.{sh}.{dim}.overlap"] = "yes" if v["overlap"] else "no"
            if v["rips_bar"] is not None:
                n[f"audit.ph.{sh}.{dim}.bar"] = f"[{fmt(v['rips_bar'][0], 2)}, {fmt(v['rips_bar'][1], 2)}]"
            n[f"audit.ph.{sh}.{dim}.constant"] = v["constant_concepts"]
        for r in a["power"]:
            key = f"audit.power.k{r['k']}.{r['arrangement']}"
            for c in ("nearest_loop", "ci_lo", "ci_hi", "interp_loop", "loop_min", "loop_max", "nearest_top3", "real_top3"):
                n[f"{key}.{c}"] = r[c]
            n[f"{key}.nearest_count"] = int(round(40 * r["nearest_loop"]))   # replicates passing (exp7_audit.POWER_REPS)
    # Exp8 audit (post hoc, D9): specificity of the loop test's Gaussian nulls to holes.
    if _res("exp8_audit3", "summary.json").exists():
        a3 = read_json(_res("exp8_audit3", "summary.json"))
        sy = a3["synthetic"]
        for key, est in (("MC|subset", "mc"), ("P|all", "P"), ("S|all", "S"), ("Ba|all", "Ba"), ("P|subset", "Psub")):
            v = sy[key]
            n[f"audit3.{est}.sens"], n[f"audit3.{est}.fpr"] = v["sensitivity"]["rate"], v["false_loop"]["rate"]
            n[f"audit3.{est}.sens_lo"], n[f"audit3.{est}.sens_hi"] = v["sensitivity"]["ci"]
            n[f"audit3.{est}.fpr_lo"], n[f"audit3.{est}.fpr_hi"] = v["false_loop"]["ci"]
            n[f"audit3.{est}.n_hole"], n[f"audit3.{est}.n_free"] = v["sensitivity"]["n"], v["false_loop"]["n"]
            for b, r in v["false_loop_by_n_bin"].items():
                n[f"audit3.{est}.fpr_bin{b}"] = r
        fam = pd.read_csv(_res("exp8_audit3", "synthetic_by_family.csv"))
        for r in fam.itertuples():                                     # key suffix _b<true b1>: arcs/cones are mixed
            n[f"audit3.{ESTSHORT.get(r.estimator, r.estimator)}.fam.{r.family}_b{r.true_b1}"] = float(r.loop_rate)
        n["audit3.mc.flag_pi_q10"], n["audit3.mc.flag_pi_q50"], n["audit3.mc.flag_pi_q90"] = sy["MC_flagged_hole_free_pi1_q10_50_90"]
        n["audit3.mc.det_pi_q10"], n["audit3.mc.det_pi_q50"], n["audit3.mc.det_pi_q90"] = sy["MC_detected_holes_pi1_q10_50_90"]
        for lab in ("outlier", "clean"):
            v = sy["MC_false_loop_by_outlier_flag"][lab]
            n[f"audit3.mc.fpr_{lab}"], n[f"audit3.mc.fpr_{lab}_n"] = v["rate"], v["n"]
            n[f"audit3.mc.fpr_{lab}_lo"], n[f"audit3.mc.fpr_{lab}_hi"] = v["ci"]
        eq = a3["sampler_equivalence"]
        n["audit3.eq.median_rel"], n["audit3.eq.max_rel"] = eq["median_abs_rel_diff_q95"], eq["max_abs_rel_diff_q95"]
        n["audit3.eq.ks_frac"], n["audit3.eq.n"] = eq["frac_ks_p_below_005"], len(eq["clouds"])
        for k, v in a3["cluster"].items():
            n[f"audit3.{k}.verdict"], n[f"audit3.{k}.fs"] = v["verdict"], v["fs_nearest"]
            n[f"audit3.{k}.sim_top3"], n[f"audit3.{k}.real_top3"], n[f"audit3.{k}.real_pi"] = (
                v["sim_top3_nearest"], v["real_top3"], v["real_top_pi1"])
            for arr, r in v["arrangements"].items():
                p = f"audit3.{k}.{arr}"
                n[f"{p}.pass"], n[f"{p}.n_pass"], n[f"{p}.n"] = r["pass"], r["n_pass"], r["n"]
                n[f"{p}.ci_lo"], n[f"{p}.ci_hi"] = r["ci"]
                n[f"{p}.pass_max"], n[f"{p}.frac_pi_ge_real"] = r["pass_max_over_cells"], r["frac_pi_ge_real"]
                n[f"{p}.median_pi"], n[f"{p}.median_means_pi"] = r["median_pi1"], r["median_means_pi1"]
                n[f"{p}.n_pi_ge_real_all"], n[f"{p}.n_all"] = r["n_pi_ge_real_all_cells"], r["n_all_cells"]
            n[f"audit3.{k}.holefree_pi_ge_real_all"] = sum(v["arrangements"][a]["n_pi_ge_real_all_cells"] for a in ("cap", "grid"))
            n[f"audit3.{k}.holefree_n_all"] = sum(v["arrangements"][a]["n_all_cells"] for a in ("cap", "grid"))
            n[f"audit3.{k}.holefree_pass_max"] = max(v["arrangements"][a]["pass_max_over_cells"] for a in ("cap", "grid"))
        for d, v in a3["centres"].items():
            sh = SHORT[d]
            n[f"audit3.cen.{sh}.pc12"], n[f"audit3.cen.{sh}.pc123"] = v["pc12_alpha_pi"], v["pc123_alpha_pi"]
            n[f"audit3.cen.{sh}.pc12_last"] = v["pc12_last_step_over_median"]
            for k in range(2, 7):
                n[f"audit3.cen.{sh}.own{k}"] = v[f"own_top{k}_rips_pi"]
            n[f"audit3.cen.{sh}.own36_max"] = max(v[f"own_top{k}_rips_pi"] for k in range(3, 7))
        tori = a3["tori"]
        n["audit3.tori.n"] = len(tori)
        n["audit3.tori.n_above_cut"] = sum(t["born_above_cut"] for t in tori)
        n["audit3.tori.terms"] = ", ".join(sorted({t["margin_term"] for t in tori}))
        if tori:
            n["audit3.tori.pi_min"], n["audit3.tori.pi_max"] = min(t["void_pi"] for t in tori), max(t["void_pi"] for t in tori)
            n["audit3.tori.birth_over_cut_min"] = min(t["void_birth"] / t["cut"] for t in tori)
            n["audit3.tori.birth_over_cut_max"] = max(t["void_birth"] / t["cut"] for t in tori)
    # Worked example (experiments/toy_example.py): every number of docs/worked_example.md, keys "toy.<name>".
    if _res("toy", "summary.json").exists():
        n.update({f"toy.{k}": v for k, v in read_json(_res("toy", "summary.json"))["numbers"].items()})
    # Percent versions of fractions quoted in the README's plain-language section.
    for k in [k for k in list(n) if k.endswith(".loop_freq")] + ["power2.weekdays.loop", "exp1.P.acc", "exp1.Bb.acc",
                                                                 "exp1.well.Ba.acc", "exp1.well.Bb.acc",
                                                                 "audit.power.k7.ring.interp_loop", "audit.power.k7.ring.ci_lo",
                                                                 "audit.power.k7.ring.ci_hi", "audit.stab.grok.matched",
                                                                 "audit.rgb.freq", "exp1.well.trivial_frac"] + \
            [k for k in list(n) if k.startswith("audit3.") and (".fam." in k or k.split(".")[-1] in
                                                               ("sens", "fpr", "fpr_lo", "fpr_hi", "pass", "ci_hi", "ci_lo",
                                                                "fpr_bin0", "fpr_bin3", "fpr_outlier", "fpr_clean"))]:
        if isinstance(n.get(k), float):
            n[k + "_pct"] = int(np.floor(100 * n[k] + 0.5))         # half-up, consistent with the 2-digit text
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
