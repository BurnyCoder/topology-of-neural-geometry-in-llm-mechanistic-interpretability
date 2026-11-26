"""Exp2: persistent-homology invariants of all 44 real clouds (Method B), compared with Method A.

Global context (reports/preregistration.md, sections 4 and 7): per cloud we report the significant H1/H2
bars under the design-matched MC null (primary) and the universal null (alpha A = 1/2, Rips A = 1;
descriptive), b0 by the validation-tuned single-linkage rule, the characteristic scale r_c, all three Betti
numbers and chi at r_c (deviation D12: b0 is now also read at r_c), genus (closed surfaces only), a Betti-number
label (not a homotopy class; invariants.betti_label), stability over 200 subsamples of 80% (the source's
subsample seeds), and agreement with the fitted catalog vector (Exp0).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.geometry.pca import fit_frame
from neurotopo.tda import diagrams, invariants, nulls

log = logging.getLogger(__name__)


def stability(dataset_id: str, q95: np.ndarray, reps: int, frac: float) -> dict:
    """Fraction of 80% subsamples (re-run through fit_frame; rng = default_rng(0) as in the source) whose top
    H1 / H2 pi exceeds the full cloud's null 95th percentile (the per-cloud MC threshold)."""
    c = realdata.cloud(dataset_id)
    n = len(c["x"])
    rng = np.random.default_rng(0)
    hits = np.zeros(2)
    for _ in range(reps):
        sub = rng.choice(n, int(round(frac * n)), replace=False)
        if len(sub) < 4:
            continue
        y, _ = fit_frame(c["x"][sub])
        d = diagrams.alpha_diagrams(y)
        hits += [diagrams.max_ratio(d[1]) > q95[0], diagrams.max_ratio(d[2]) > q95[1]]
    return {"loop_freq": hits[0] / reps, "void_freq": hits[1] / reps}


def invariants_row(dataset_id: str, seed: int, t: dict, stab: bool = True) -> dict:
    cfg = config.load()
    c = realdata.cloud(dataset_id)
    d = realdata.alpha(dataset_id)
    mc = realdata.mc_significance(dataset_id, seed)
    y = c["y"]
    sig = [None, mc["sig"][1], mc["sig"][2]]
    pv = [None, mc["p"][1], mc["p"][2]]
    s = invariants.scale_invariants(y, d, sig, pv, t["b0_tau"], t["b0_minfrac"])   # b0 rule, r_c, Betti at r_c
    b0, rc, bc = s["b0"], s["r_c"], s["betti_rc"]
    pi1, pi2 = diagrams.ratios(d[1]), diagrams.ratios(d[2])
    row = {"id": dataset_id, "N": len(y), "D": c["x"].shape[1], "design": realdata.design(dataset_id),
           "top_pi1": float(np.nanmax(pi1)) if pi1.size else 1.0,
           "top_pi2": float(np.nanmax(pi2)) if pi2.size else 1.0,
           "p_top_loop": float(np.nanmin(mc["p"][1])) if pi1.size else 1.0,
           "p_top_void": float(np.nanmin(mc["p"][2])) if pi2.size else 1.0,
           "null_q95_pi1": float(mc["null_q95"][0]), "null_q95_pi2": float(mc["null_q95"][1]),
           "b0": b0, "b1_mc": int(mc["sig"][1].sum()), "b2_mc": int(mc["sig"][2].sum()),
           "b1_alpha_univ": int(nulls.universal_significant(d[1], A=0.5).sum()),
           "b2_alpha_univ": int(nulls.universal_significant(d[2], A=0.5).sum()),
           "b1_rips_univ": int(nulls.universal_significant(diagrams.rips_diagrams(y)[1], A=1.0).sum()),
           "r_c": rc, "b0_rc": bc[0], "b1_rc": bc[1], "b2_rc": bc[2], "chi_rc": s["chi_rc"],
           "genus_rc": s["genus_rc"], "betti_label_rc": s["label_rc"],
           "source_deviation": c["dev"]}
    if stab:
        row.update(stability(dataset_id, mc["null_q95"], cfg["stability"]["reps"], cfg["stability"]["frac"]))
    return row


def agreement(df: pd.DataFrame) -> np.ndarray:
    """Compare the complete per-cloud vectors required by the descriptive H4 endpoint."""
    fitted = df[["A_b0", "A_b1", "A_b2"]].to_numpy()
    persistent = df[["b0", "b1_mc", "b2_mc"]].to_numpy()
    return np.all(fitted == persistent, axis=1)


def save_summary(df, out):
    """Expose the full vector and the loop/void-only endpoint side by side."""
    # Regenerating a historical table must produce the same schema as a fresh run.
    df = df.drop(columns=["agree_betti", "agree_b1b2", "q_top_loop", "q_top_void"], errors="ignore")
    df["agree_betti"] = agreement(df)
    df["agree_b1b2"] = (df["A_b1"] == df["b1_mc"]) & (df["A_b2"] == df["b2_mc"])
    from neurotopo.stats.tests import bh
    df["q_top_loop"] = bh(df["p_top_loop"].to_numpy())
    df["q_top_void"] = bh(df["p_top_void"].to_numpy())
    df.to_csv(out / "invariants.csv", index=False)
    write_json(out / "summary.json", {"n": len(df), "agree_full_n": int(df["agree_betti"].sum()),
               "agree_full_A_vs_B": float(df["agree_betti"].mean()), "agree_b1b2_n": int(df["agree_b1b2"].sum()),
               "agree_b1b2_A_vs_B": float(df["agree_b1b2"].mean()), "n_with_loop_mc": int((df["b1_mc"] > 0).sum()),
               "n_with_void_mc": int((df["b2_mc"] > 0).sum()), "n_loop_q05": int((df["q_top_loop"] < .05).sum()),
               "loops_q05": df.loc[df["q_top_loop"] < .05, "id"].tolist()})


def run() -> None:
    cfg = config.load()
    out = out_dir("exp2")
    env_record("exp2")
    t = read_json(config.path("results") / "power" / "val_tuning.json")
    rows = []
    for did in source.dataset_ids():
        r = invariants_row(did, cfg["seed"], t)
        rows.append(r)
        log.info("%-28s N=%4d pi1=%.2f (q95 %.2f, p=%.4f) pi2=%.2f b=(%d,%d,%d)@r_c %s, stab loop %.2f",
                 did, r["N"], r["top_pi1"], r["null_q95_pi1"], r["p_top_loop"], r["top_pi2"], r["b0_rc"],
                 r["b1_rc"], r["b2_rc"], r["betti_label_rc"], r["loop_freq"])
    df = pd.DataFrame(rows)
    a = pd.read_csv(config.path("results") / "exp0" / "real_topology.csv")
    df = df.merge(a[["id", "family", "b0", "b1", "b2", "rho_A"]].rename(columns={"b0": "A_b0", "b1": "A_b1", "b2": "A_b2"}),
                  on="id")
    save_summary(df, out)
