"""Rebuild membership of the catalog-defined false-positive cohort from the cloud-level inputs."""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import kstest

from neurotopo import config
from neurotopo.data import synthetic
from neurotopo.experiments import exp1_batches, exp1_synthetic as exp1
from neurotopo.experiments.common import out_dir, read_json
from neurotopo.geometry.pca import rms_normalise
from neurotopo.stats.tests import cluster_bootstrap
from neurotopo.tda import diagrams, nulls
from neurotopo.tda.ground_truth import far_points


def interval_pair(fp, flag, chunks, repetitions):
    """Sample chunks jointly, retaining the flagged and unflagged denominators in each draw."""
    _, ix = np.unique(chunks, return_inverse=True)
    by_chunk = np.zeros((ix.max()+1, 4))
    np.add.at(by_chunk, ix, np.column_stack((flag & fp, flag, ~flag & fp, ~flag)))
    rng = np.random.default_rng(0)
    draws = np.empty((repetitions, 3))
    for j in range(repetitions):
        a,b,c,d = by_chunk[rng.integers(len(by_chunk), size=len(by_chunk))].sum(axis=0)
        draws[j] = a/b, c/d, a/b-c/d
    return np.quantile(draws, [.025,.975], axis=0).T


def blob_scores(points):
    """Retain finite alpha bar scores by degree using the actual within-diagram transformation."""
    dgm = diagrams.alpha_diagrams(rms_normalise(points))
    by_degree = []
    for h in (1, 2):
        p = nulls.universal_pvalues(dgm[h], A=.5)
        by_degree.append(p[np.isfinite(p)])
    return by_degree


def calibrate_blob_strata(clouds, df, out, repetitions):
    """Report within-cloud detections and descriptive pooled bar KS distances in every size/noise cell."""
    rows = []
    for (size,noise), group in df[df.family_name.eq("blob")].groupby(["n_bin","noise_bin"]):
        scores = Parallel(n_jobs=exp1_batches.worker_count())(delayed(blob_scores)(clouds.cloud(i)) for i in group.index)
        for h in (1,2):
            values = [r[h-1] for r in scores]
            detections = np.array([int((p<.05/max(1,len(p))).sum()) for p in values])
            if not np.array_equal(detections,group[f"b{h}_alpha_univ"].to_numpy()):
                raise ValueError(f"Raw blob bar counts differ in size {size}, noise {noise}, degree {h}")
            pooled = np.concatenate(values)
            hit = detections>0
            rate,low,high = cluster_bootstrap(hit,group.chunk.to_numpy(),np.mean,n_boot=repetitions)
            rows.append(dict(dimension=h,n_bin=size,noise_bin=noise,n_clouds=len(hit),hits=int(hit.sum()),
                             rate=rate,low=low,high=high,valid_bars=len(pooled),
                             pooled_bar_KS_D=kstest(pooled,"uniform").statistic if pooled.size else None))
    pd.DataFrame(rows).to_csv(out/"blob_score_strata.csv",index=False)


def run():
    out = out_dir("science")
    cfg = config.load()
    s = synthetic.load("test")
    df = pd.read_csv(config.path("results")/"exp1/per_cloud.csv.gz")
    ids = s.meta.sample_id
    if not ids.reset_index(drop=True).equals(df.sample_id.reset_index(drop=True)):
        raise ValueError("Outlier flag and prediction sample IDs are misaligned")
    counts = Parallel(n_jobs=-1, batch_size=64)(delayed(far_points)(s.cloud(i), s.gt(i), cfg["outliers"]["far_factor"]) for i in range(len(s)))
    df["flag"] = np.asarray(counts)>0
    df["fp"] = (df.b1_alpha_univ>0) | (df.b2_alpha_univ>0)
    df["eligible"] = exp1.contractible_cohort(df)
    df["legacy"] = df.eligible & ~df.family_name.isin(["arc","sphere"])
    df[["sample_id","chunk","family_name","eligible","legacy","flag","fp"]].to_csv(
        out/"false_positive_rows.csv.gz", index=False, compression={"method":"gzip","mtime":0})
    rows = []
    for cohort, sub in [("catalog", df[df.eligible]), ("six families", df[df.legacy])]:
        flag, fp = sub.flag.to_numpy(), sub.fp.to_numpy()
        intervals = interval_pair(fp, flag, sub.chunk.to_numpy(), cfg["synthetic"]["bootstrap"])
        rates = []
        for j, (name, mask) in enumerate([("flagged",flag), ("unflagged",~flag)]):
            rate = fp[mask].mean()
            rates.append(rate)
            rows.append(dict(cohort=cohort, comparison=name, hits=int(fp[mask].sum()), n=int(mask.sum()),
                             rate=rate, low=intervals[j,0], high=intervals[j,1]))
        rows.append(dict(cohort=cohort, comparison="flagged minus unflagged", hits=None, n=None,
                         rate=rates[0]-rates[1], low=intervals[2,0], high=intervals[2,1]))
    pd.DataFrame(rows).to_csv(out/"false_positives.csv",index=False)
    expdir = config.path("results")/"exp1"
    with np.load(expdir/"pi_top.npz") as pi:
        df["pi1_top"],df["pi2_top"] = list(pi["pi1"]),list(pi["pi2"])
    estimators = exp1.predictions(df,read_json(expdir/"summary.json")["tuning"])
    measured = {m:pd.Series((p[:,1]>0)|(p[:,2]>0),index=df.index) for m,p in estimators.items()}
    mc = df[["b1_mc","b2_mc"]]
    measured["MC_gaussian3d (subset)"] = mc.gt(0).any(axis=1).where(mc.notna().all(axis=1))
    strata = []
    for method,hit in measured.items():
        cohort = df.loc[df.eligible & hit.notna(),["n_bin","noise_bin","flag"]].copy()
        cohort["hit"] = hit.loc[cohort.index].astype(int)
        table = cohort.groupby(["n_bin","noise_bin","flag"]).hit.agg(hits="sum",n="size").reset_index()
        table["method"],table["rate"] = method,table.hits/table.n
        strata.append(table)
    pd.concat(strata,ignore_index=True).to_csv(out/"false_positive_strata.csv",index=False)
    calibrate_blob_strata(s,df,out,cfg["synthetic"]["bootstrap"])
