"""Cross-check independently rebuilt estimands, and join the evidence supporting the publication."""
import numpy as np
import pandas as pd
from scipy.stats import binomtest

from neurotopo import config
from neurotopo.experiments.common import out_dir, read_json, write_json


def run():
    root, out = config.path("results"), out_dir("science")
    inputs = read_json(out/"inputs.json")
    inv = pd.read_csv(root/"exp2/invariants.csv").set_index("id")
    null = pd.read_csv(out/"null_replay.csv")
    hyp = read_json(out/"hypotheses.json")
    exp = read_json(root/"exp1/summary.json")
    bench = pd.read_csv(out/"benchmark.csv")
    fpr = pd.read_csv(out/"false_positives.csv")
    reps = pd.read_csv(out/"representatives.csv.gz")
    all_indices = set(inv.index)
    cfg = config.load()
    expected_seeds = {(d,s) for d in all_indices for s in ([0,1,2] if d in cfg["groups"]["cyclic_primary"] else [0])}
    expected = {(d,s,k) for d,s in expected_seeds for k in (1,2)}
    if expected != set(null[["id","seed","dimension"]].itertuples(index=False,name=None)) or len(null)!=len(expected):
        raise ValueError("Incomplete null replay")
    primary = null[null.seed.eq(0)]
    if not (null.p==null.deposited_p).all() or not np.allclose(primary.p,primary.registered_p,rtol=0,atol=1e-14):
        raise ValueError("Fresh Monte Carlo ranks disagree with the reference")
    # These intervals quantify finite simulation noise, conditional on the fitted reference distribution.
    for k in (1,2):
        df = primary[primary.dimension.eq(k)].set_index("id")
        for d,row in df.iterrows():
            ci = binomtest(int(row.exceedances), int(row.draws)).proportion_ci(method="exact")
            inv.loc[d,[f"tail{k}_low",f"tail{k}_high"]] = [ci.low, ci.high]
    projection = pd.read_csv(root/"exp5/projection.csv").set_index("id")
    top10 = pd.read_csv(root/"exp5/topk_null.csv").query("k == 10").set_index("id")
    inv = inv.join(projection, rsuffix="_robust").join(top10[["p_loop"]].rename(columns={"p_loop":"p_top10_rips"}))
    inv["causal_intervention"] = "untested"
    inv["stability_definition"] = "retention versus full-sample threshold under subsampling"
    inv.to_csv(out/"dataset_assessment.csv")
    controls = pd.read_csv(out/"analytic_controls.csv")
    if len(controls)!=4 or not controls.agrees.all() or not hyp["registered_replay_agrees"]:
        raise ValueError("Known-domain or endpoint replay failed")
    for row in bench.query("target == 'catalog' and group == 'macro'").itertuples():
        if not np.isclose(exp["table"][row.method]["macro_exact"],row.accuracy,rtol=0,atol=1e-12):
            raise ValueError(f"{row.method}: catalog accuracy does not reproduce")
    p = read_json(root/"exp1/outliers.json")["fpr"]["P_alpha_universal"]
    for row in fpr.query("cohort == 'catalog' and comparison != 'flagged minus unflagged'").itertuples():
        ref = p["outlier" if row.comparison=="flagged" else "clean"]
        if (row.hits,row.n) != (ref["fp"], ref["n"]):
            raise ValueError("Raw flags and Exp1 counts disagree")
    calibrated = []
    for size,vals in exp["calibration_blobs"].items():
        for noise,r in vals["by_noise_bin"].items():
            calibrated.append(dict(n_bin=size,noise_bin=noise,n=r["n"],hits=r["hits"],rate=r["rate"],
                                   low=r["cluster_ci"][0],high=r["cluster_ci"][1],pooled_size_ks_D=vals["ks_uniform_D"]))
    pd.DataFrame(calibrated).to_csv(out/"blobs.csv",index=False)
    gallery = read_json(root/"loops/summary.json")["interesting"]
    index = reps.set_index(["id","dimension","k"])
    selection_ok = all(index.at[(r["id"],1,r["k"]),"certified"] for r in gallery)
    if not selection_ok:
        raise ValueError("Selected loop gallery includes an uncertified death")
    t = pd.read_csv(out/"angular_domains.csv")
    f = pd.read_csv(out/"false_positive_rows.csv.gz")
    summary = {"inputs":inputs,"h1":hyp["H1"],"h4_full":hyp["H4_full"],
               "h4_partial":int(inv.agree_b1b2.sum()),"n_real":len(inv),"null_arrays":len(expected_seeds),
               "max_draw_error":float(null.max_draw_difference.max()),"max_rank_error":float((null.p-null.deposited_p).abs().max()),
               "certificates":{str(k):{"total":len(v),"certified":int(v.certified.sum()),"failed":int((~v.certified).sum())}
                               for k,v in reps.groupby("dimension")},
               "selected_paths_certified":bool(selection_ok), "selected_paths":len(gallery),
               "analytic_controls":int(controls.agrees.sum()),"exact_cloud_overlap":read_json(out/"splits.json")["exact_point_cloud_overlap"],
               "changes":{family:{"test":int(v.changed.sum()),"eligible":int((v.changed & v.eligible).sum()),
                                  "omitted_from_fpr":int((f.eligible & ~f.legacy & f.family_name.eq(family)).sum())}
                          for family,v in t.groupby("family")}}
    write_json(out/"summary.json",summary)
