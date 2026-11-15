"""Exp5: robustness of the real-data conclusions (exploratory; reports/preregistration.md, section 7).

Global context: the cyclic-concept conclusions could depend on analysis choices. Checks:
- complex: alpha vs Rips (3D) top-H1 persistence and universal-null counts;
- projection: Rips H1 on the top-k PCs (k = 3, 5, 10) and on full-D cosine distances (loops that exist only
  in a 3D projection would vanish; Antognini & Sohl-Dickstein 2018, arXiv:1806.08805);
- nuisance factor: removing the per-offset means of weekdays/months (the "k days from" offset word precedes
  the concept token), then re-running Method B conditions (a)-(c);
- Monte Carlo seeds 1 and 2 for the loop p-values and theta_B alignment of the primary datasets;
- the noise-scale definition of Method A (median term only; coverage term doubled).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.analytic.topology import shape_topology
from neurotopo.data import source
from neurotopo.experiments import alignment, realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.experiments.exp0_analytic import shape_noise
from neurotopo.geometry.pca import fit_frame
from neurotopo.tda import circular, diagrams, nulls
from neurotopo.tda.ground_truth import margin_ratio

log = logging.getLogger(__name__)
KEY = ["R5a_llama_weekdays", "R5b_llama_months", "R2_grokking_WE", "R5c_llama_days_time", "R1_gpt2_wpos",
       "R4_llama_counting", "R4b_pythia_counting", "R6_llama_years", "R8a_llama_temperature", "R8b_llama_age",
       "R7_llama_colors", "C3_llama_weekdays_init", "C3_llama_months_init", "C3_grokking_WE_init"]


def projection_row(dataset_id: str) -> dict:
    """Top H1 pi (radius units) and Rips universal-null counts in 3D (alpha and Rips), top-5, top-10, full-D cosine."""
    c = realdata.cloud(dataset_id)
    out = {"id": dataset_id}
    da = realdata.alpha(dataset_id)
    out["alpha3_pi1"] = diagrams.max_ratio(da[1])
    out["alpha3_b1_univ"] = int(nulls.universal_significant(da[1], A=0.5).sum())
    for k in (3, 5, 10):
        y, _ = fit_frame(c["x"], k=k)
        dr = diagrams.rips_diagrams(y, maxdim=1)
        out[f"rips{k}_pi1"] = diagrams.max_ratio(dr[1])
        out[f"rips{k}_b1_univ"] = int(nulls.universal_significant(dr[1], A=1.0).sum())
    from scipy.spatial.distance import pdist, squareform
    dm = squareform(pdist(c["x"], metric="cosine"))
    dr = diagrams.rips_diagrams(dm, maxdim=1, distance_matrix=True)
    out["ripsD_cos_pi1"] = diagrams.max_ratio(dr[1])
    out["ripsD_cos_b1_univ"] = int(nulls.universal_significant(dr[1], A=1.0).sum())
    return out


def topk_null_row(dataset_id: str, seed: int, k: int = 10, m: int = 199) -> dict:
    """Top-k loop test with a design-matched MC null (audit, D6): observed max Rips H1 pi of the RMS-normalised
    top-k cloud vs the same statistic on m null draws pushed through the same top-k projection."""
    c = realdata.cloud(dataset_id)
    y, _ = fit_frame(c["x"], k=k)
    obs = diagrams.max_ratio(diagrams.rips_diagrams(y, maxdim=1)[1])
    nm = nulls.null_max_rips_topk(c["x"], realdata.design(dataset_id), realdata.groups(dataset_id, c["labels"]), m=m,
                                  seed=nulls.dataset_seed(dataset_id + f"top{k}", seed), k=k)
    return {"id": dataset_id, "k": k, "rips_pi1": obs, "null_q95": float(np.quantile(nm, 0.95)),
            "p_loop": float(nulls.mc_pvalues(np.array([obs]), nm)[0]), "m": m}


def offset_removed(dataset_id: str, seed: int) -> dict:
    """Weekdays / months: subtract per-offset means (offset = i % 7 or i % 12; no concept labels used), then
    loop p-value (cluster-centre null, M = 999), theta_B alignment and winding."""
    c = realdata.cloud(dataset_id)
    m = 7 if "weekdays" in dataset_id else 12
    off = np.arange(len(c["x"])) % m
    x = c["x"] - np.stack([c["x"][off == o].mean(0) for o in range(m)])[off] + c["x"].mean(0)
    y, _ = fit_frame(x)
    d = diagrams.alpha_diagrams(y)
    con = source.concepts(dataset_id, c["labels"])
    nm = nulls.null_max_ratios(x, "cluster", con.index, m=config.load()["tda"]["mc_draws"],
                               seed=nulls.dataset_seed(dataset_id + "offset", seed), maxdim=1)
    p_loop = float(nulls.mc_pvalues(np.array([diagrams.max_ratio(d[1])]), nm[:, 0])[0])
    cc = circular.circular_coordinates(y)
    rec = alignment.records(dataset_id, cc["theta"], c["labels"], seed)[0] if cc["theta"] is not None else None
    return {"id": dataset_id, "p_loop": p_loop, "R": rec["R"] if rec else None, "p_align": rec["p"] if rec else 1.0,
            "winding": rec["winding"] if rec else 0}


def seed_row(dataset_id: str, seed: int) -> dict:
    """Loop p-value under another MC seed and theta_B alignment with another permutation seed."""
    c = realdata.cloud(dataset_id)
    nm = realdata.null(dataset_id, seed)
    p_loop = float(nulls.mc_pvalues(np.array([diagrams.max_ratio(realdata.alpha(dataset_id)[1])]), nm[:, 0])[0])
    cc = circular.circular_coordinates(c["y"])
    rec = alignment.records(dataset_id, cc["theta"], c["labels"], seed)[0] if cc["theta"] is not None else None
    return {"id": dataset_id, "seed": seed, "p_loop": p_loop, "p_align": rec["p"] if rec else 1.0,
            "winding": rec["winding"] if rec else 0}


def nu_variants(dataset_id: str) -> dict:
    """Method A margin ratio under the two alternative noise-scale definitions."""
    rr = source.real_results()[dataset_id]
    t = shape_topology(rr["family"], rr["params"])
    ns = shape_noise(rr["family"], rr["params"], source.load_viz(dataset_id)["points"])
    return {"id": dataset_id, "family": rr["family"], "b1": t["b1"], "b2": t["b2"],
            "rho_main": margin_ratio(t["margin"], ns["nu"]), "rho_median_only": margin_ratio(t["margin"], ns["noise"]),
            "rho_coverage_x2": margin_ratio(t["margin"], ns["noise"] + 2 * ns["coverage"])}


def run() -> None:
    cfg = config.load()
    out = out_dir("exp5")
    env_record("exp5")
    proj = pd.DataFrame([projection_row(d) for d in KEY])
    proj.to_csv(out / "projection.csv", index=False)
    log.info("projection check:\n%s", proj.to_string())
    topk = pd.DataFrame([topk_null_row(d, cfg["seed"]) for d in KEY])
    topk.to_csv(out / "topk_null.csv", index=False)
    log.info("top-10 loop test with MC null:\n%s", topk.to_string())
    off = [offset_removed(d, cfg["seed"]) for d in ("R5a_llama_weekdays", "R5b_llama_months")]
    seeds = [seed_row(d, s) for d in cfg["groups"]["cyclic_primary"] for s in (1, 2)]
    nu = pd.DataFrame([nu_variants(d) for d in source.dataset_ids()])
    nu.to_csv(out / "nu_variants.csv", index=False)
    write_json(out / "summary.json", {"offset_removed": off, "seeds": seeds,
                                      "nu_variant_resolvable_counts": {c: int((nu[c] >= 1).sum()) for c in
                                                                       ("rho_main", "rho_median_only", "rho_coverage_x2")}})
