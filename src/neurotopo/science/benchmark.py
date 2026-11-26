"""Audit H5 on a fixed cohort against the catalog and unrounded angular domains.

The source's Arc.local/Sphere.local and describe methods define the targets (pinned upstream 4c5f3b6).
Whole generator chunks are resampled jointly across predictions and targets.
"""
import hashlib
import json

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import synthetic
from neurotopo.experiments import exp1_synthetic as exp1
from neurotopo.experiments.common import out_dir, read_json, write_json


def angular_target(family, raw, catalog):
    """Betti vector of the ideal, pre-noise angular domain before the source's reporting threshold."""
    if family in ("arc", "sphere"):
        frac = raw["extent_frac" if family == "arc" else "cap_frac"]
        if not 0 < frac <= 1:
            raise ValueError(f"{family}: unexpected angular fraction {frac}")
        if frac < 1:
            return (1, 0, 0)
    return tuple(catalog)


def chunk_intervals(correct, family, chunks, repetitions):
    """Bootstrap all methods and targets with the same cluster draw, then macro-average the family means."""
    family_id, f = np.unique(family, return_inverse=True)
    _, ch, counts = np.unique(chunks, return_inverse=True, return_counts=True)
    chunk_f = np.full(len(counts), -1)
    chunk_f[ch] = f
    if not np.all(chunk_f[ch] == f):
        raise ValueError("Generator chunk crosses family boundaries")
    sums = np.zeros((len(counts), correct.shape[1]))
    np.add.at(sums, ch, correct)
    rng = np.random.default_rng(0)
    groups = [np.flatnonzero(chunk_f == i) for i in range(len(family_id))]
    observed = np.stack([sums[ix].sum(0) / counts[ix].sum() for ix in groups])
    draws = np.empty((repetitions, len(groups), correct.shape[1]))
    for b in range(repetitions):
        weight = np.bincount(rng.integers(len(counts), size=len(counts)), minlength=len(counts))
        for j, ix in enumerate(groups):
            den = weight[ix] @ counts[ix]
            draws[b, j] = weight[ix] @ sums[ix] / den if den else np.nan
    return (["macro", *family_id], np.concatenate([observed.mean(0)[None, :], observed]),
            np.concatenate([np.nanmean(draws, axis=1, keepdims=True), draws], axis=1))


def run():
    """Join original exports by sample ID before reconstructing family and exact-vector scores."""
    out = out_dir("science")
    root = config.path("results")
    inp = config.path("inputs") / "synth"
    df = pd.read_csv(root / "exp1/per_cloud.csv.gz", low_memory=False)
    truth = df[["b0", "b1", "b2"]].to_numpy()
    alternate = np.empty_like(truth)
    records = []
    with (inp / "test_gt_params.jsonl").open(encoding="utf-8") as stream:
        positions = dict(zip(df["sample_id"], range(len(df)), strict=True))
        for line in stream:
            row = json.loads(line)
            key = f"{row['n_bin']}-{row['noise_bin']}-{row['idx']}"
            i = positions.pop(key)
            family = row["family"]
            if family != df["family_name"].iat[i]:
                raise ValueError(f"{key}: family differs between exports")
            alternate[i] = angular_target(family, row["raw"], truth[i])
            if family in ("sphere", "arc"):
                records.append(dict(sample_id=key, family=family, catalog_closed=row["describe"]["closed"],
                                    fraction=row["raw"]["cap_frac" if family == "sphere" else "extent_frac"],
                                    eligible=bool(df["resolvable"].iat[i]), changed=bool((truth[i] != alternate[i]).any())))
    if positions or not df.sample_id.is_unique:
        raise ValueError("Unmatched test sample identifiers")
    pd.DataFrame(records).to_csv(out / "angular_domains.csv", index=False)
    archive = synthetic.predictions().query("system == 'method'").set_index("sample_id", verify_integrity=True)
    if not np.array_equal(archive.loc[df.sample_id, "family_pred"].to_numpy(), df.family_pred.to_numpy()):
        raise ValueError("Published fitter predictions differ from the input export")
    with np.load(root / "exp1/pi_top.npz") as pi:
        df["pi1_top"], df["pi2_top"] = list(pi["pi1"]), list(pi["pi2"])
    methods = exp1.predictions(df, read_json(root / "exp1/summary.json")["tuning"])
    mask = df.resolvable.to_numpy()
    poly = df.family_name.eq("polytope").to_numpy()
    cols, labels = [], []
    for lab, target in [("catalog", truth), ("angular", alternate)]:
        for name, pred in methods.items():
            ok = (pred[:, 0] == target[:, 0]) & (poly | (pred[:, 1:] == target[:, 1:]).all(1))
            cols.append(ok[mask])
            labels.append((lab, name))
    group, est, boots = chunk_intervals(np.column_stack(cols), df.family_name[mask], df.chunk[mask],
                                         config.load()["synthetic"]["bootstrap"])
    rows = []
    for i, g in enumerate(group):
        for j, (target, method) in enumerate(labels):
            ref = labels.index((target, "P_alpha_universal"))
            lo, hi = np.nanquantile(boots[:, i, j], [.025, .975])
            dl, dh = np.nanquantile(boots[:, i, ref]-boots[:, i, j], [.025, .975])
            rows.append(dict(target=target, group=g, method=method, accuracy=est[i,j], low=lo, high=hi,
                             P_minus_method=est[i,ref]-est[i,j], difference_low=dl, difference_high=dh))
    pd.DataFrame(rows).to_csv(out / "benchmark.csv", index=False)
    # Sample identifiers are scoped to a split. Hash actual ordered point content for cross-split duplicates.
    hashes = []
    for split in ("val", "test"):
        data = synthetic.load(split)
        hashes.append({hashlib.sha256(data.points[a:b].tobytes()).digest()
                       for a, b in zip(data.offsets[:-1], data.offsets[1:])})
    write_json(out / "splits.json", dict(unique_val=len(hashes[0]), unique_test=len(hashes[1]),
                                         exact_point_cloud_overlap=len(hashes[0] & hashes[1])))
