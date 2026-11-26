"""Rebuild membership of the catalog-defined false-positive cohort from the cloud-level inputs."""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from neurotopo import config
from neurotopo.data import synthetic
from neurotopo.experiments import exp1_synthetic as exp1
from neurotopo.experiments.common import out_dir
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
