"""Exp1: validation of the persistent-homology Betti estimators against exact ground-truth topology (H5).

Global context (reports/preregistration.md, section 6, H5): on the source's fixed synthetic test set (39,000
clouds, 13 families), the exact Betti numbers of every ground-truth shape are known (Exp0, Method A on the
regenerated parameters). We score estimators of (b0, b1, b2) on clouds whose topology is resolvable
(rho_A >= 1), macro-averaged over families (polytope on b0 only), with 95% cluster-bootstrap CIs over the
generator chunks of 25 clouds:
- P  (preregistered primary): alpha + universal null (A = 1/2) for b1/b2, single-linkage b0;
- S  (secondary, deviations D1): Rips H1 + universal null (A = 1) for b1, alpha universal for b2;
- Ba (baseline): fixed pi thresholds pi0_1, pi0_2 tuned on validation;
- Bb (baseline): family-implied (source fitter's predicted family -> modal exact Betti vector on validation);
- Bc (baseline): majority vector of the validation set;
- MC (3,120-cloud baseline subset): 3D matched-Gaussian Monte Carlo null on max pi, M = 99.
Tuned values come from results/power/val_tuning.json (validation stream only; preregistration addendum).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import stats

from neurotopo import config
from neurotopo.data import synthetic
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.stats.tests import cluster_bootstrap
from neurotopo.tda import diagrams, estimators, nulls
from neurotopo.geometry.pca import rms_normalise

log = logging.getLogger(__name__)
def contractible_cohort(df: pd.DataFrame) -> np.ndarray:
    """The registered eligible, connected, contractible catalog objects, including open arcs and caps.

    For these thirteen known families the vector determines this predicate. Acyclicity alone
    would not imply contractibility for a general topological space (Hatcher, Algebraic Topology).
    """
    return (df["resolvable"] & df["b0"].eq(1) & df["b1"].eq(0) & df["b2"].eq(0)).to_numpy()


def _summ(points, tau, frac):
    return estimators.summarize(points, [tau], [frac])


def _blob_pvalues(points) -> list:
    """All universal-null p-values of the alpha H1 diagram (calibration check on blobs)."""
    p = nulls.universal_pvalues(diagrams.alpha_diagrams(rms_normalise(points))[1], A=0.5)
    return p[np.isfinite(p)].tolist()


def _mc(points, seed, m):
    null = estimators.gaussian3d_null_max(points, m, seed)
    return estimators.mc_counts(points, null)


def predictions(df: pd.DataFrame, t: dict) -> dict[str, np.ndarray]:
    """(N, 3) predicted Betti vectors of every estimator."""
    b0 = df["b0_pred"].to_numpy()
    pi1, pi2 = np.array(df["pi1_top"].tolist()), np.array(df["pi2_top"].tolist())
    fam_pred = df["family_pred"].to_numpy()
    fmap = {f: np.array(v) for f, v in t["family_map"].items()}
    out = {
        "P_alpha_universal": np.c_[b0, df["b1_alpha_univ"], df["b2_alpha_univ"]],
        "S_rips_universal": np.c_[b0, df["b1_rips_univ"], df["b2_alpha_univ"]],
        "Ba_fixed_pi": np.c_[b0, (pi1 > t["pi0_1"]).sum(1), (pi2 > t["pi0_2"]).sum(1)],
        "Bb_family_implied": np.stack([fmap[f] for f in fam_pred]),
        "Bc_majority": np.tile(np.array(t["majority"]), (len(df), 1)),
    }
    return out


def correct(df: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    """Exact-vector correctness per cloud; polytope scored on b0 only (prereg H5)."""
    gt = df[["b0", "b1", "b2"]].to_numpy()
    poly = df["family_name"].to_numpy() == "polytope"
    return (pred[:, 0] == gt[:, 0]) & (poly | ((pred[:, 1] == gt[:, 1]) & (pred[:, 2] == gt[:, 2])))


def macro(frame: np.ndarray) -> float:
    """frame columns: (correct as float, family code); macro average over families present."""
    fam = frame[:, 1].astype(int)
    return float(np.mean([frame[fam == f, 0].mean() for f in np.unique(fam)]))


def run() -> None:
    cfg = config.load()
    out = out_dir("exp1")
    env_record("exp1")
    t = read_json(config.path("results") / "power" / "val_tuning.json")
    sset = synthetic.load("test")
    gt = pd.read_csv(config.path("results") / "exp0" / "synth_test_topology.csv.gz")
    log.info("summarising %d test clouds", len(sset))
    rows = Parallel(n_jobs=-1, batch_size=16)(delayed(_summ)(sset.cloud(i), t["b0_tau"], t["b0_minfrac"])
                                              for i in range(len(sset)))
    s = pd.DataFrame(rows)
    s["b0_pred"] = [r[f"{t['b0_tau']}|{t['b0_minfrac']}"] for r in s["b0_grid"]]
    if not np.array_equal(gt["sample_id"], sset.meta["sample_id"]):
        raise ValueError("Topology rows and point clouds have different sample identifiers")
    df = pd.concat([gt.reset_index(drop=True), s.drop(columns=["n", "b0_grid"])], axis=1)
    pred = synthetic.predictions()
    meth = pred[pred["system"] == "method"].set_index("sample_id", verify_integrity=True)["family_pred"]
    df["family_pred"] = meth.loc[df["sample_id"]].to_numpy()
    val = pd.read_json(config.path("results") / "power" / "val_summaries.json.gz", orient="records")
    vr = val[val["resolvable"]]
    t["majority"] = list(map(int, vr[["b0", "b1", "b2"]].value_counts().idxmax()))
    # Monte Carlo null on the baseline subset.
    sub = np.flatnonzero(synthetic.baseline_subset(df))
    seed = cfg["seed"]
    mc = Parallel(n_jobs=-1, batch_size=4)(delayed(_mc)(sset.cloud(i), seed * 10 ** 6 + int(i),
                                                        cfg["synthetic"]["mc_draws_synth"]) for i in sub)
    df["b1_mc"], df["b2_mc"] = np.nan, np.nan
    df.loc[sub, "b1_mc"] = [m[0] for m in mc]
    df.loc[sub, "b2_mc"] = [m[1] for m in mc]
    df.drop(columns=["pi1_top", "pi2_top"]).to_csv(out / "per_cloud.csv.gz", index=False)
    np.savez_compressed(out / "pi_top.npz", pi1=np.array(df["pi1_top"].tolist()), pi2=np.array(df["pi2_top"].tolist()))

    score_table(df, t, sset, sub, out)


def rescore() -> None:
    """Replay the published scoring analysis using the deposited row-level predictions."""
    out = out_dir("exp1")
    df = pd.read_csv(out / "per_cloud.csv.gz", low_memory=False)
    with np.load(out / "pi_top.npz") as pi:
        df["pi1_top"], df["pi2_top"] = list(pi["pi1"]), list(pi["pi2"])
    t = read_json(config.path("results") / "power/val_tuning.json")
    val = pd.read_json(config.path("results") / "power/val_summaries.json.gz")
    t["majority"] = list(map(int, val.loc[val["resolvable"], ["b0","b1","b2"]].value_counts().idxmax()))
    score_table(df, t, synthetic.load("test"), np.flatnonzero(synthetic.baseline_subset(df)), out)


def score_table(df, t, sset, sub, out):
    """Summarise the identical empirical estimands in a full run and an archived-row replay."""
    cfg = config.load()
    preds = predictions(df, t)
    res = df["resolvable"].to_numpy()
    fam_code = df["family"].to_numpy()
    nb = cfg["synthetic"]["bootstrap"]
    table, corr = {}, {}
    for name, p in preds.items():
        c = correct(df, p)
        corr[name] = c
        est, lo, hi = cluster_bootstrap(np.c_[c[res], fam_code[res]], df["chunk"].to_numpy()[res], macro, n_boot=nb)
        table[name] = {"macro_exact": est, "ci": [lo, hi], "n": int(res.sum()),
                       "per_family": pd.Series(c[res]).groupby(df["family_name"].to_numpy()[res]).mean().to_dict(),
                       "per_dim": {f"b{k}": float(np.mean(p[res, k] == df[f"b{k}"].to_numpy()[res])) for k in range(3)}}
    # MC estimator on the baseline subset (same b0 as P).
    subm = np.zeros(len(df), bool)
    subm[sub] = True
    mcpred = np.c_[df["b0_pred"], df["b1_mc"].fillna(-1), df["b2_mc"].fillna(-1)].astype(int)
    for name, p in [("MC_gaussian3d (subset)", mcpred), ("P_alpha_universal (subset)", preds["P_alpha_universal"]),
                    ("S_rips_universal (subset)", preds["S_rips_universal"])]:
        m = res & subm
        c = correct(df, p)
        est, lo, hi = cluster_bootstrap(np.c_[c[m], fam_code[m]], df["chunk"].to_numpy()[m], macro, n_boot=nb)
        table[name] = {"macro_exact": est, "ci": [lo, hi], "n": int(m.sum())}
    # Paired differences of P against each baseline (cluster bootstrap on the difference of macro accuracies).
    diffs = {}
    chunks = df["chunk"].to_numpy()[res]
    for name in ("S_rips_universal", "Ba_fixed_pi", "Bb_family_implied", "Bc_majority"):
        both = np.c_[corr["P_alpha_universal"][res], corr[name][res], fam_code[res]]
        f = lambda a: macro(a[:, [0, 2]]) - macro(a[:, [1, 2]])
        est, lo, hi = cluster_bootstrap(both, chunks, f, n_boot=nb)
        diffs[f"P - {name}"] = {"estimate": est, "ci": [lo, hi]}
    # False-positive rates on resolvable contractible clouds (GT b1 = b2 = 0, non-point-set families), per N-bin.
    contr = contractible_cohort(df)
    fpr = {}
    for name, p in preds.items():
        fp = (p[:, 1] > 0) | (p[:, 2] > 0)
        fpr[name] = {int(b): float(fp[contr & (df["n_bin"].to_numpy() == b)].mean()) for b in range(4)}
    # Universal-null calibration on blobs: fraction with any significant alpha H1 bar (FWER), KS of pooled p.
    blobs = np.flatnonzero(df["family_name"].to_numpy() == "blob")
    calib = {}
    for b in range(4):
        idx = blobs[df["n_bin"].to_numpy()[blobs] == b]
        pv = np.concatenate([np.asarray(x) for x in Parallel(n_jobs=-1)(delayed(_blob_pvalues)(sset.cloud(i)) for i in idx)])
        calib[int(b)] = {"fwer_alpha_universal": float((df["b1_alpha_univ"].to_numpy()[idx] > 0).mean()),
                         "ks_uniform_D": float(stats.kstest(pv, "uniform").statistic) if pv.size else None,
                         "n_pvalues": int(pv.size), "n_clouds": len(idx), "by_noise_bin": {}}
        for noise in sorted(df["noise_bin"].unique()):
            sel = idx[df["noise_bin"].to_numpy()[idx] == noise]
            hits = df["b1_alpha_univ"].to_numpy()[sel] > 0
            rate, lo, hi = cluster_bootstrap(hits, df["chunk"].to_numpy()[sel], np.mean, n_boot=nb)
            calib[int(b)]["by_noise_bin"][int(noise)] = {"n": len(sel), "hits": int(hits.sum()),
                                                         "rate": rate, "cluster_ci": [lo, hi]}
    # Accuracy versus resolvability (all clouds, binned rho_A).
    bins = [0, 0.25, 0.5, 1, 2, 4, np.inf]
    rb = pd.cut(df["rho_A"].replace(np.inf, 1e9), bins, right=False)
    by_rho = {name: pd.Series(c).groupby(rb, observed=True).mean().rename(str).to_dict() for name, c in corr.items()}
    # Well-resolved clouds (rho_A >= 4; audit, D6): every estimator, macro over families, cluster-bootstrap CI,
    # paired differences of the preregistered P against the family label and the fixed threshold, per family.
    wr = df["rho_A"].to_numpy() >= 4
    well = {"n": int(wr.sum()), "family_counts": pd.Series(df["family_name"].to_numpy()[wr]).value_counts().to_dict()}
    for name, c in corr.items():
        est, lo, hi = cluster_bootstrap(np.c_[c[wr], fam_code[wr]], df["chunk"].to_numpy()[wr], macro, n_boot=nb)
        well[name] = {"macro_exact": est, "ci": [lo, hi],
                      "per_family": pd.Series(c[wr]).groupby(df["family_name"].to_numpy()[wr]).mean().to_dict()}
    for other in ("Bb_family_implied", "Ba_fixed_pi", "Bc_majority"):
        both = np.c_[corr["P_alpha_universal"][wr], corr[other][wr], fam_code[wr]]
        f = lambda a: macro(a[:, [0, 2]]) - macro(a[:, [1, 2]])
        est, lo, hi = cluster_bootstrap(both, df["chunk"].to_numpy()[wr], f, n_boot=nb)
        well[f"P - {other}"] = {"estimate": est, "ci": [lo, hi]}
    write_json(out / "summary.json", {"well_resolved": well, "table": table, "paired_differences": diffs, "fpr_contractible": fpr,
                                      "calibration_blobs": calib, "accuracy_by_rho": by_rho,
                                      "resolvable_fraction": float(res.mean()), "tuning": t,
                                      "resolvable_by_family": df.groupby("family_name")["resolvable"].mean().to_dict()})
    for name, v in table.items():
        log.info("%-28s macro exact %.3f [%.3f, %.3f] (n=%d)", name, v["macro_exact"], *v["ci"], v["n"])


def expected_outlier_rate(n: np.ndarray, prob: float, frac_max: float) -> float:
    """Generator's expected fraction of clouds with >= 1 injected outlier (source add_outliers: a cloud gets
    outliers with probability `prob`, then each point independently with f ~ U(0, frac_max)):
    prob * (1 - E[(1 - f)^n]), with E[(1 - f)^n] = (1 - (1 - frac_max)^(n + 1)) / (frac_max (n + 1))."""
    n = np.asarray(n, dtype=np.float64)
    return float(np.mean(prob * (1 - (1 - (1 - frac_max) ** (n + 1)) / (frac_max * (n + 1)))))


def outlier_check() -> None:
    """Deviation D7: the preregistered DTM conditional (section 7) needs Exp1's outlier false-positive rate.

    Outlier clouds = clouds with >= 1 point farther than far_factor x their median distance to the ground-truth
    shape (tda.ground_truth.far_points). Reported: FPR of every estimator on resolvable contractible clouds with
    and without detected outliers (cluster-bootstrap CI over generator chunks, legacy unclustered Fisher statistic), the
    decision (DTM ablation iff P's outlier FPR > dtm_fpr_threshold), and the proxy's flag rate per N bin next to
    the generator's expected rate of clouds with at least one injected outlier (a model expectation for a different quantity).
    """
    import yaml
    from neurotopo.stats.tests import fisher_exact
    from neurotopo.tda.ground_truth import far_points
    cfg = config.load()
    out = out_dir("exp1")
    sset = synthetic.load("test")
    df = pd.read_csv(out / "per_cloud.csv.gz", low_memory=False)
    pi = np.load(out / "pi_top.npz")
    df["pi1_top"], df["pi2_top"] = list(pi["pi1"]), list(pi["pi2"])
    k = cfg["outliers"]["far_factor"]
    df["n_far"] = Parallel(n_jobs=-1, batch_size=64)(delayed(far_points)(sset.cloud(i), sset.gt(i), k)
                                                      for i in range(len(sset)))
    with open(config.path("submodule") / "configs" / "base.yaml", encoding="utf-8") as f:
        gen = yaml.safe_load(f)["synth"]
    flag = df["n_far"].to_numpy() > 0
    nbin = df["n_bin"].to_numpy()
    proxy = {int(b): {"flagged": float(flag[nbin == b].mean()), "n_min": int(df["n"][nbin == b].min()),
                      "n_max": int(df["n"][nbin == b].max()),
                      "expected_with_outliers": expected_outlier_rate(df["n"].to_numpy()[nbin == b],
                                                                      gen["outlier_prob"], gen["outlier_frac_max"])}
             for b in range(4)}
    contr = contractible_cohort(df)
    chunks = df["chunk"].to_numpy()
    nb = cfg["synthetic"]["bootstrap"]
    rates = {}
    for name, p in predictions(df, read_json(out / "summary.json")["tuning"]).items():
        fp = ((p[:, 1] > 0) | (p[:, 2] > 0)).astype(float)
        r = {}
        for lab, m in (("outlier", contr & flag), ("clean", contr & ~flag)):
            est, lo, hi = cluster_bootstrap(fp[m], chunks[m], np.mean, n_boot=nb)
            r[lab] = {"fpr": est, "ci": [lo, hi], "fp": int(fp[m].sum()), "n": int(m.sum()),
                      "by_n_bin": {int(b): float(fp[m & (nbin == b)].mean()) if (m & (nbin == b)).any() else None
                                   for b in range(4)}}
        r["fisher_p_outlier_gt_clean"] = fisher_exact([[r["outlier"]["fp"], r["outlier"]["n"] - r["outlier"]["fp"]],
                                                       [r["clean"]["fp"], r["clean"]["n"] - r["clean"]["fp"]]])
        rates[name] = r
    # Post-hoc sensitivity of the decision to the proxy's factor (point estimates of P and S only).
    sens = {}
    preds = predictions(df, read_json(out / "summary.json")["tuning"])
    for kf in cfg["outliers"]["far_factor_sensitivity"]:
        fl = np.array(Parallel(n_jobs=-1, batch_size=64)(delayed(far_points)(sset.cloud(i), sset.gt(i), kf)
                                                          for i in range(len(sset)))) > 0
        sens[str(kf)] = {"flagged_fraction": float(fl.mean()), "n_outlier_contractible": int((contr & fl).sum()),
                         **{name: float((((preds[name][:, 1] > 0) | (preds[name][:, 2] > 0))[contr & fl]).mean())
                            for name in ("P_alpha_universal", "S_rips_universal")}}
    thr = cfg["outliers"]["dtm_fpr_threshold"]
    p_fpr = rates["P_alpha_universal"]["outlier"]["fpr"]
    res = {"far_factor": k, "threshold": thr, "generator": {"outlier_prob": gen["outlier_prob"],
                                                            "outlier_frac_max": gen["outlier_frac_max"]},
           "flagged_fraction": float(flag.mean()), "proxy_by_n_bin": proxy, "fpr": rates,
           "P_outlier_fpr": p_fpr, "dtm_required": bool(p_fpr > thr), "sensitivity": sens}
    write_json(out / "outliers.json", res)
    log.info("outlier proxy: %.3f of clouds flagged; P outlier FPR %.3f (threshold %.2f) -> DTM %s",
             res["flagged_fraction"], p_fpr, thr, "required" if res["dtm_required"] else "not required")
