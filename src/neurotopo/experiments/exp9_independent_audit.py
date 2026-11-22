"""Independent audit (deviation D14, post hoc): do smooth random curves get top-10-PC loops?

Global context: Exp5's top-10-PC loop test (design-matched Monte Carlo null, deviations D6) found significant loops in
four ordinal concepts (years, age, counting, temperature), and the documentation said these are "consistent both with
Fourier features of numbers (Kantamneni & Tegmark 2025) and with the PCA artefacts of smooth or random-walk curves
(Antognini & Sohl-Dickstein 2018; Shinn 2023)". The project's 20 ordinal-process controls (10 Gaussian processes and 10
random walks in R^768, `C1_*`) are exactly such curves, with no periodic structure, but Exp5 never tested them. This phase
runs the identical test (exp5_robustness.topk_null_row: Rips H1 in the RMS-normalised top-10 PCs, 199 draws of the
full-D matched Gaussian null) on all 20.

Decision rule, written before the run (reports/deviations.md, D14):
- >= 5 of 20 significant at p < 0.05 (one-sided exact binomial p = 0.016 against the nominal 0.05): smooth random curves
  alone produce such loops, so the PCA-artefact explanation of the ordinal loops is plausible;
- <= 2 of 20: the project's own smooth-curve controls do not support that explanation;
- 3 or 4: undetermined.
No model is run and nothing is trained; the raw control clouds come from the pinned Hugging Face inputs.
"""

from __future__ import annotations

import logging

import pandas as pd
from scipy import stats

from neurotopo import config
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.experiments.exp5_robustness import topk_null_row
from neurotopo.stats.tests import binom_ci

log = logging.getLogger(__name__)
C1 = [f"C1_{kind}_{i}" for kind in ("gp", "walk") for i in range(10)]   # the 20 ordinal-process controls


def decision(k: int, n: int = 20) -> str:
    """The pre-specified verdict for k significant controls out of n (see the module docstring)."""
    if k >= 5:
        return "PCA-artefact explanation plausible"
    if k <= 2:
        return "not supported by the smooth-curve controls"
    return "undetermined"


def run() -> None:
    cfg = config.load()
    out = out_dir("exp9_audit4")
    env_record("exp9_audit4")
    rows = pd.DataFrame([topk_null_row(d, cfg["seed"]) for d in C1])     # same k = 10, m = 199 and seeds as Exp5
    rows["kind"] = rows["id"].str.split("_").str[1]                      # "gp" or "walk"
    rows.to_csv(out / "c1_top10.csv", index=False)
    k = int((rows["p_loop"] < cfg["tda"]["alpha_level"]).sum())
    summary = {"n": len(rows), "n_significant": k, "rate_ci": binom_ci(k, len(rows)),
               # exact one-sided binomial test of k against the nominal 5% level (scipy.stats.binomtest)
               "binom_p_vs_005": float(stats.binomtest(k, len(rows), 0.05, alternative="greater").pvalue),
               "by_kind": {kd: int((g["p_loop"] < cfg["tda"]["alpha_level"]).sum()) for kd, g in rows.groupby("kind")},
               "pi_max": float(rows["rips_pi1"].max()), "q95_min": float(rows["null_q95"].min()),
               "q95_max": float(rows["null_q95"].max()), "decision": decision(k)}
    write_json(out / "summary.json", summary)
    log.info("C1 controls, top-10 loop test:\n%s", rows.to_string())
    log.info("significant: %d of %d (%s); decision: %s", k, len(rows), summary["by_kind"], summary["decision"])
