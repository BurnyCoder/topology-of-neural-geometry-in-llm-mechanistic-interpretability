"""Exp3: do semantically cyclic concepts travel around a hole? H1-A/H1-B (co-primary), H2, H3, H4, exploratory.

Global context (reports/preregistration.md, section 6). Method B per dataset:
(a) the most persistent alpha H1 bar is significant under the design-matched MC null;
(b) the alignment of the cohomology coordinate theta_B (DREiMac) with the semantic phases is significant
    (permutation test; Holm over the 6 co-primary tests);
(c) the semantic cycle winds exactly once (|w| = 1);
(d) recomputing theta_B on the top-10 PCs keeps p < 0.05 and |w| = 1 (guards against projection loops).
Method A records come from Exp0 (theta_A on fitted shapes with a hole; a b1 = 0 fit fails H1-A, so its
co-primary p-value is 1). Inspired by manifold steering (Wurgaft et al. 2026, arXiv:2605.05115).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import alignment, realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.stats import tests as st
from neurotopo.tda import circular
from neurotopo.tda.diagrams import ratios

log = logging.getLogger(__name__)
THETA_CACHE: dict = {}                     # theta_B per dataset, saved for Exp6-sim and the explorer
EXPLORATORY = ["R7_llama_colors", "R5a_llama_weekdays_means", "R5b_llama_months_means", "C3_grokking_WE_memorised",
               "C3_gpt2_wpos_init", "C3_llama_counting_init"]


def method_b(dataset_id: str, seed: int) -> dict:
    """Conditions (a)-(d) inputs for one dataset: loop p-value, theta_B records in 3D and in the top-10 PCs."""
    c = realdata.cloud(dataset_id)
    mc = realdata.mc_significance(dataset_id, seed)
    p1 = mc["p"][1]
    p_loop = float(np.nanmin(p1)) if p1.size else 1.0
    cc3 = circular.circular_coordinates(c["y"])
    y10, _ = fit_frame(c["x"], k=config.load()["circular"]["topk_check"])
    cc10 = circular.circular_coordinates(y10)
    rec3 = alignment.records(dataset_id, cc3["theta"], c["labels"], seed) if cc3["theta"] is not None else []
    rec10 = alignment.records(dataset_id, cc10["theta"], c["labels"], seed) if cc10["theta"] is not None else []
    THETA_CACHE[dataset_id] = cc3["theta"]
    d1 = realdata.alpha(dataset_id)[1]
    pis = ratios(d1)
    top = d1[int(np.nanargmax(pis))] if pis.size and np.isfinite(pis).any() else None   # most persistent alpha bar
    overlap = None
    if top is not None and cc3["bar"] is not None:
        overlap = bool(min(top[1], cc3["bar"][1]) > max(top[0], cc3["bar"][0]))  # intervals intersect (prereg 4.6)
    return {"id": dataset_id, "p_loop": p_loop, "loop": p_loop < config.load()["tda"]["alpha_level"],
            "theta3_error": cc3["error"], "theta10_error": cc10["error"], "rips_bar3": cc3["bar"],
            "alpha_top_bar": None if top is None else top.tolist(), "rips_alpha_overlap": overlap,
            "coverage3": cc3.get("uncovered"), "coverage10": cc10.get("uncovered"),
            "diagnostics": {k: {"n_landmarks": cc["n_landmarks"], "candidate_radius_interval": cc.get("candidate_bar"),
                                "cover_radius": cc.get("cover_radius"), "uncovered": cc.get("uncovered")}
                            for k,cc in (("3d",cc3), ("top10",cc10))},
            "records3": rec3, "records10": rec10}


VARS = {None: None, "day": "day of week", "time": "time of day", "7 bins": "value in 7 bins",
        "12 bins": "value in 12 bins"}


def _first(recs: list[dict], variable: str | None = None) -> dict | None:
    """The record of a variable: the dataset's first (primary) record for None, otherwise the record whose
    variable name equals the full name (exact match, so "day" cannot match "time of day"; audit fix, D6)."""
    full = VARS.get(variable, variable)
    for r in recs:
        if full is None or r["variable"] == full:
            return r
    return None


def b_pass(mb: dict, var: str | None, p_adj: float | None, alpha: float = 0.05) -> dict:
    """Evaluate H1-B conditions for one variable; p_adj replaces the raw alignment p in (b) when given."""
    r3, r10 = _first(mb["records3"], var), _first(mb["records10"], var)
    pb = (p_adj if p_adj is not None else r3["p"]) if r3 else 1.0
    cond = {"a_loop": bool(mb["loop"]), "b_align": bool(r3 is not None and pb < alpha),
            "c_wind1": bool(r3 is not None and abs(r3["winding"]) == 1),
            "d_top10": bool(r10 is not None and r10["p"] < alpha and abs(r10["winding"]) == 1)}
    cond["pass"] = all(cond.values())
    return cond


def a_records(exp0: list[dict], dataset_id: str) -> list[dict]:
    return [r for r in exp0 if r["id"] == dataset_id]


def a_pass(topo: pd.Series, recs: list[dict], var: str | None, p_adj: float | None, alpha: float = 0.05) -> dict:
    """H1-A: exact hole with rho_A >= 1, and theta_A alignment significant with |w| = 1 (any torus angle)."""
    hole = bool(topo["b1"] >= 1 and topo["rho_A"] >= 1)
    holes = [r for r in recs if r["kind"] == "hole" and (var is None or r["variable"] == VARS.get(var, var))]
    ok = any((p_adj if p_adj is not None else r["p"]) < alpha and abs(r["winding"]) == 1 for r in holes)
    return {"hole_resolvable": hole, "traversal": bool(ok), "pass": bool(hole and ok)}


def a_pvalue(topo: pd.Series, recs: list[dict], var: str | None) -> float:
    """Co-primary H1-A p-value: smallest theta_A alignment p over hole coordinates; 1 if the fit has no hole."""
    holes = [r for r in recs if r["kind"] == "hole" and (var is None or r["variable"] == VARS.get(var, var))]
    if topo["b1"] < 1 or not holes:
        return 1.0
    return float(min(r["p"] for r in holes))


def run() -> None:
    cfg = config.load()
    out = out_dir("exp3")
    env_record("exp3")
    seed = cfg["seed"]
    g = cfg["groups"]
    topo = pd.read_csv(config.path("results") / "exp0" / "real_topology.csv").set_index("id")
    exp0 = read_json(config.path("results") / "exp0" / "real_alignment.json")
    ids = g["cyclic_primary"] + g["cyclic_secondary"] + g["ordinal"] + g["init_controls"] + \
        [f"C1_{k}_{i}" for k in ("gp", "walk") for i in range(10)] + EXPLORATORY
    mb = {}
    for did in ids:
        mb[did] = method_b(did, seed)
        r = _first(mb[did]["records3"])
        log.info("%-28s loop p=%.4f | theta_B: %s", did, mb[did]["p_loop"],
                 "none" if r is None else f"R={r['R']:.3f} p={r['p']:.2g} w={r['winding']}")
    write_json(out / "method_b.json", mb)
    np.savez_compressed(out / "theta_B.npz", **{k: v for k, v in THETA_CACHE.items() if v is not None})

    # Co-primary family: Holm over 6 p-values (3 datasets x Methods A, B).
    prim = g["cyclic_primary"]
    pa = [a_pvalue(topo.loc[d], a_records(exp0, d), None) for d in prim]
    pb = [(_first(mb[d]["records3"]) or {"p": 1.0})["p"] for d in prim]
    adj = st.holm(pa + pb)
    h1 = {}
    for i, d in enumerate(prim):
        h1[d] = {"A": {**a_pass(topo.loc[d], a_records(exp0, d), None, adj[i]), "p_raw": pa[i], "p_holm": adj[i]},
                 "B": {**b_pass(mb[d], None, adj[3 + i]), "p_raw": pb[i], "p_holm": adj[3 + i]}}
    verdict = {m: sum(h1[d][m]["pass"] for d in prim) for m in ("A", "B")}

    # H2: ordinal sets (7 and 12 bins), init controls and C1 controls; unadjusted alpha (conservative).
    h2 = {}
    for d in g["ordinal"] + g["init_controls"] + [f"C1_{k}_{i}" for k in ("gp", "walk") for i in range(10)]:
        recA = a_records(exp0, d)
        h2[d] = {}
        for var in (["7 bins", "12 bins"] if d in g["ordinal"] or d.startswith("C1") else [None]):
            h2[d][var or "concept"] = {"A": a_pass(topo.loc[d], recA, var, None)["pass"],
                                       "B": b_pass(mb[d], var, None)["pass"]}
    passes = lambda d, m: any(v[m] for v in h2[d].values())
    h2_summary = {m: {"ordinal_pass": sum(passes(d, m) for d in g["ordinal"]),
                      "init_pass": sum(passes(d, m) for d in g["init_controls"]),
                      "c1_pass": sum(passes(d, m) for d in h2 if d.startswith("C1")),
                      "falsified": sum(passes(d, m) for d in g["ordinal"]) >= 2 or
                                   any(passes(d, m) for d in g["init_controls"])} for m in ("A", "B")}
    for m in ("A", "B"):
        k = h2_summary[m]["c1_pass"]
        h2_summary[m]["c1_fpr_ci"] = st.binom_ci(k, 20)

    # H3: R5c day phase (unadjusted).
    d = "R5c_llama_days_time"
    h3 = {"A": a_pass(topo.loc[d], a_records(exp0, d), "day", None), "B": b_pass(mb[d], "day", None)}

    # H4: balanced accuracy of three criteria for cyclic {R5a, R5b, R2, R5c} vs the 6 ordinal sets.
    cyc = prim + g["cyclic_secondary"]
    crit = {"hole_only_A": {x: bool(topo.loc[x, "b1"] >= 1 and topo.loc[x, "rho_A"] >= 1) for x in cyc + g["ordinal"]},
            "conj_A": {**{x: h1[x]["A"]["pass"] for x in prim}, d: h3["A"]["pass"],
                       **{x: passes(x, "A") for x in g["ordinal"]}},
            "conj_B": {**{x: h1[x]["B"]["pass"] for x in prim}, d: h3["B"]["pass"],
                       **{x: passes(x, "B") for x in g["ordinal"]}}}
    bal = {k: 0.5 * (np.mean([v[x] for x in cyc]) + np.mean([not v[x] for x in g["ordinal"]])) for k, v in crit.items()}
    def mcn(a, b):
        truth = {x: x in cyc for x in cyc + g["ordinal"]}
        ca = [crit[a][x] == truth[x] for x in truth]
        cb = [crit[b][x] == truth[x] for x in truth]
        return st.mcnemar_exact(sum(i and not j for i, j in zip(ca, cb)), sum(j and not i for i, j in zip(ca, cb)))
    h4 = {"balanced_accuracy": bal, "criteria": crit,
          "mcnemar": {f"{a} vs {b}": mcn(a, b) for a, b in [("hole_only_A", "conj_A"), ("hole_only_A", "conj_B"),
                                                           ("conj_A", "conj_B")]}}

    # Exploratory (BH within the list): every remaining alignment record under both methods.
    expl = []
    for d2 in EXPLORATORY + ["R6_llama_years", "R8a_llama_temperature", "R8b_llama_age", "R5c_llama_days_time"]:
        for r in mb[d2]["records3"]:
            if d2 == "R5c_llama_days_time" and "time" not in r["variable"]:
                continue
            if d2 in g["ordinal"] and "mod" not in r["variable"]:
                continue
            expl.append({"id": d2, "method": "B", "variable": r["variable"], "R": r["R"], "p": r["p"],
                         "winding": r["winding"], "loop": mb[d2]["loop"]})
        for r in a_records(exp0, d2):
            if (d2 in g["ordinal"] and "mod" not in r["variable"]) or (d2 == "R5c_llama_days_time" and "time" not in r["variable"]):
                continue
            expl.append({"id": d2, "method": "A", "variable": r["variable"], "kind": r["kind"], "R": r["R"],
                         "p": r["p"], "winding": r["winding"]})
    q = st.bh([e["p"] for e in expl])
    for e, qq in zip(expl, q):
        e["q_bh"] = qq
    write_json(out / "summary.json", {"H1": h1, "H1_verdict_passes_of_3": verdict, "H2": h2, "H2_summary": h2_summary,
                                      "H3": h3, "H4": h4, "exploratory": expl})
    log.info("H1 passes of 3: %s; H2 summary: %s", verdict, h2_summary)
