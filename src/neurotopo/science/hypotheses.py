"""Reconstruct registered endpoints from original fits, coordinates and row-level observations."""
from itertools import combinations
import logging

import numpy as np
import pandas as pd
from scipy.stats import binomtest, false_discovery_control

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import exp0_analytic, exp2_invariants, exp3_cyclic, exp3_posthoc
from neurotopo.experiments.common import out_dir, read_json, write_json

log = logging.getLogger(__name__)


def recompute_real():
    """Rebuild the fitted coordinates and both DREiMac analyses through their normal entry points."""
    rows, coordinates = [], []
    for did in source.dataset_ids():
        result, record = exp0_analytic.real_fit(did, config.load()["seed"])
        rows.append(result)
        coordinates.extend(record)
    out = out_dir("exp0")
    pd.DataFrame(rows).to_csv(out / "real_topology.csv", index=False)
    write_json(out / "real_alignment.json", coordinates)
    out = out_dir("exp2")
    exp2_invariants.save_summary(pd.read_csv(out / "invariants.csv", float_precision="round_trip"), out)
    exp3_cyclic.run()
    exp3_posthoc.run()


def _holm(values):
    """Step-down Holm over the complete registered family, including unavailable coordinates assigned one."""
    order = np.argsort(values)
    adjusted = np.empty(len(values))
    adjusted[order] = np.minimum(1, np.maximum.accumulate(np.asarray(values)[order] * np.arange(len(order),0,-1)))
    return adjusted


def run():
    """Re-evaluate the logical conjunctions independently of the experiment's pass/fail helpers."""
    root, out = config.path("results"), out_dir("science")
    groups = config.load()["groups"]
    main = groups["cyclic_primary"]
    fitted = pd.read_csv(root / "exp0/real_topology.csv").set_index("id")
    a = read_json(root / "exp0/real_alignment.json")
    b = read_json(root / "exp3/method_b.json")
    summary = read_json(root / "exp3/summary.json")
    inv = pd.read_csv(root / "exp2/invariants.csv").set_index("id")
    ordinal, init = groups["ordinal"], groups["init_controls"]
    c1 = [d for d in inv.index if d.startswith("C1_")]
    rows = []
    for d in main + groups["cyclic_secondary"] + ordinal + init + c1:
        hypothesis = "H1" if d in main else ("H3" if d in groups["cyclic_secondary"] else "H2")
        if d in ordinal or d in c1:
            variables = ["value in 7 bins", "value in 12 bins"]
        else:
            variables = ["month" if "months" in d else "residue (max over k)" if "grokking" in d else "day of week"]
        for var in variables:
            fit = fitted.loc[d]
            holes = [r for r in a if r["id"] == d and r["kind"] == "hole" and r["variable"] == var]
            for rec in holes or [{}]:
                rows.append(dict(hypothesis=hypothesis, id=d, variable=var, method="A", fit=fit.family,
                                 hole=bool(fit.b1 >= 1), eligible_margin=bool(fit.rho_A >= 1), rho=fit.rho_A,
                                 coordinate=rec.get("coordinate", "unavailable"), p_raw=rec.get("p"),
                                 winding=rec.get("winding"), coordinate10="inapplicable"))
            r3 = next((r for r in b[d]["records3"] if r["variable"]==var), {})
            r10 = next((r for r in b[d]["records10"] if r["variable"]==var), {})
            rows.append(dict(hypothesis=hypothesis, id=d, variable=var, method="B", hole=bool(b[d]["p_loop"]<.05),
                             p_loop=b[d]["p_loop"], coordinate=b[d]["theta3_error"] or "available",
                             p_raw=r3.get("p"), winding=r3.get("winding"), coordinate10=b[d]["theta10_error"] or "available",
                             p10=r10.get("p"), winding10=r10.get("winding"), frequency=r3.get("k"),
                             uncovered=b[d].get("coverage3"), uncovered10=b[d].get("coverage10")))
    primary = [r for r in rows if r["hypothesis"]=="H1"]
    if len(primary)!=6:
        raise ValueError("This audit expects the six registered primary comparisons in this study")
    for rec, p in zip(primary, _holm([r["p_raw"] if r["p_raw"] is not None else 1. for r in primary])):
        rec["p_holm"] = p
    for r in rows:
        prob = r.get("p_holm", r["p_raw"])
        align = prob is not None and prob < .05 and abs(r["winding"] or 0)==1
        gate = r["eligible_margin"] if r["method"]=="A" else r["p10"] is not None and r["p10"]<.05 and abs(r["winding10"])==1
        r["passed"] = bool(r["hole"] and align and gate)
        r["multiplicity"] = "Holm over six alignments" if r in primary else "unadjusted"
    df = pd.DataFrame(rows)
    df.to_csv(out / "decisions.csv", index=False)
    verdict = df.groupby(["id","method"])["passed"].any().unstack()
    h1 = {m:int(verdict.loc[main,m].sum()) for m in ("A","B")}
    h2 = {m: {"ordinal":int(verdict.loc[ordinal,m].sum()), "init":int(verdict.loc[init,m].sum()),
              "process":int(verdict.loc[c1,m].sum())} for m in ("A","B")}
    h3 = {m:bool(verdict.loc[groups["cyclic_secondary"][0],m]) for m in ("A","B")}
    cyc = main + groups["cyclic_secondary"]
    pool = cyc + ordinal
    truth = np.array([d in cyc for d in pool])
    predictions = {"hole_only_A": np.array([fitted.loc[d,"b1"]>=1 and fitted.loc[d,"rho_A"]>=1 for d in pool]),
                   "conj_A":verdict.loc[pool,"A"].to_numpy(), "conj_B":verdict.loc[pool,"B"].to_numpy()}
    h4, mcn = {}, {}
    for key, pred in predictions.items():
        h4[key] = (pred[truth].mean()+(~pred[~truth]).mean())/2
    for i,j in combinations(predictions,2):
        vi,vj = predictions[i]==truth, predictions[j]==truth
        n = int((vi!=vj).sum())
        mcn[f"{i} vs {j}"] = binomtest(int((vi & ~vj).sum()),n).pvalue if n else 1.
    full = (inv[["b0","b1_mc","b2_mc"]].to_numpy()==fitted.loc[inv.index,["b0","b1","b2"]].to_numpy()).all(1)
    per = pd.DataFrame({"id":inv.index,"H4_full_vector":full,
                        **{k:[p[pool.index(d)] if d in pool else None for d in inv.index] for k,p in predictions.items()}})
    per.to_csv(out / "h4_datasets.csv",index=False)
    steer = []
    for d in [*cyc,"R7_llama_colors",*ordinal,*init,*c1]:
        steer.append(dict(id=d, detected_top3_loop=bool(inv.loc[d,"p_top_loop"]<.05),
                          simulated="untested", model="untested" if d in cyc+["R7_llama_colors"] else "control or outside model phase",
                          random_loop_p=None, proportion_winding_once=None, on_manifold=None, vocabulary_mass=None))
    pd.DataFrame(steer).to_csv(out / "h6_datasets.csv", index=False)
    bh = summary["exploratory"]
    discrepancy = np.max(np.abs(false_discovery_control([v["p"] for v in bh]) - [v["q_bh"] for v in bh])) if bh else 0
    checks = [h1==summary["H1_verdict_passes_of_3"], h4==summary["H4"]["balanced_accuracy"],
              mcn==summary["H4"]["mcnemar"], all(h3[m]==summary["H3"][m]["pass"] for m in h3),
              all(h2[m][k]==summary["H2_summary"][m][{"ordinal":"ordinal_pass","init":"init_pass","process":"c1_pass"}[k]]
                  for m in h2 for k in h2[m]), discrepancy<1e-12, np.array_equal(full,inv["agree_betti"])]
    write_json(out / "hypotheses.json", dict(H1=h1,H2=h2,H3=h3,H4=h4,H4_McNemar=mcn,H4_full=int(full.sum()),
               H5="benchmark.csv",H6="untested", registered_replay_agrees=all(checks),exploratory_BH_max_error=discrepancy))
    if not all(checks):
        raise ValueError("Independent hypothesis evaluation disagrees with a published endpoint")
