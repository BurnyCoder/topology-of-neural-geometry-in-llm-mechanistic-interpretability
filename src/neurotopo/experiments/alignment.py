"""Dataset-aware travel-around-the-hole records (used by Exp0 with theta_A and Exp3 with theta_B).

Global context: for a hole coordinate theta (one angle per point), this module picks the dataset's
preregistered concept variable(s) (reports/preregistration.md, sections 2 and 5): day / month / residue for
the cyclic sets, 7 and 12 equal-width value bins for ordinal sets, hue for colours, day and time for R5c, and
the exploratory value mod 10 / mod 100. It returns R, orientation, permutation p-value, winding number and
the exact cyclic-order check for each variable.
"""

from __future__ import annotations

import numpy as np

from neurotopo import config
from neurotopo.data import source
from neurotopo.stats import circular as cs
from neurotopo.tda.nulls import dataset_seed

CYCLIC_IDS = {"R5a_llama_weekdays", "R5b_llama_months", "R5c_llama_days_time", "R2_grokking_WE", "R7_llama_colors",
              "C3_llama_weekdays_init", "C3_llama_months_init", "C3_grokking_WE_init", "C3_grokking_WE_memorised",
              "R5a_llama_weekdays_means", "R5b_llama_months_means"}
NO_CONCEPTS = {"R3_tms_n6", "R3_tms_n8", "R3_tms_n20", "C3_tms_dense", "R9_llama_truth_cities"}
NUMERIC_EXPLORATORY = {"R6_llama_years": ["mod10", "mod100"], "R8a_llama_temperature": ["mod10"],
                       "R8b_llama_age": ["mod10"]}
GROK = {"R2_grokking_WE", "C3_grokking_WE_init", "C3_grokking_WE_memorised"}


def variables(dataset_id: str) -> list[tuple[str | None, int]]:
    """(variable, n_bins) pairs to test for a dataset; empty if it has no concept structure."""
    if dataset_id in NO_CONCEPTS:
        return []
    if dataset_id == "R5c_llama_days_time":
        return [("day", 0), ("time", 0)]
    if dataset_id in CYCLIC_IDS:
        return [(None, 0)]
    out = [("bins", n) for n in config.load()["circular"]["ordinal_bins"]]
    return out + [(v, 0) for v in NUMERIC_EXPLORATORY.get(dataset_id, [])]


def record(dataset_id: str, theta: np.ndarray, labels: list[str], variable: str | None, n_bins: int,
           seed: int = 0) -> dict:
    """Alignment statistics of theta with one concept variable of a dataset."""
    cc = config.load()["circular"]
    rng = np.random.default_rng(dataset_seed(dataset_id + str(variable) + str(n_bins), seed))
    if dataset_id in GROK:
        a = np.array([int(s) for s in labels])
        r, k, s = cs.max_over_frequency(theta, a, 113, cc["grok_kmax"])
        p = cs.max_over_frequency_pvalue(theta, a, 113, cc["grok_kmax"], cc["perm_mc"], rng)
        th = cs.concept_means(theta, (k * a) % 113, 113)          # residues ordered around the k-circle
        return {"variable": "residue (max over k)", "k": k, "n": 113, "R": r, "s": s, "p": p,
                "winding": cs.winding(th), "order_match": cs.cyclic_order_matches(th),
                "order_p": cs.cyclic_order_p(113)}
    con = source.concepts(dataset_id, labels, variable=None if variable == "bins" else variable,
                          n_bins=n_bins or 7)
    n = len(con.phase)
    th = cs.concept_means(theta, con.index, n)
    r, s = cs.alignment(th, con.phase)
    p = cs.permutation_pvalue(th, con.phase, exact_max_n=cc["exact_max_n"], mc=cc["perm_mc"], rng=rng)
    return {"variable": con.variable, "n": n, "R": r, "s": s, "p": p, "winding": cs.winding(th),
            "order_match": cs.cyclic_order_matches(th), "order_p": cs.cyclic_order_p(n),
            "concept_theta": th.tolist()}


def records(dataset_id: str, theta: np.ndarray, labels: list[str], seed: int = 0) -> list[dict]:
    """All preregistered alignment records of a dataset for one hole coordinate."""
    return [record(dataset_id, theta, labels, v, n, seed) for v, n in variables(dataset_id)]


def passes(rec: dict, alpha: float = 0.05, p_key: str = "p") -> bool:
    """Traversal criterion of one record: significant alignment and the semantic cycle winds exactly once."""
    return bool(np.isfinite(rec[p_key]) and rec[p_key] < alpha and abs(rec["winding"]) == 1)
