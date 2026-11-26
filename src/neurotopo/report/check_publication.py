"""Check agreement between the rendered release and the row-level evidence. Optional second-checkout comparison."""
import argparse

from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.experiments.common import read_json, write_json
from neurotopo.report import science


def pdf_text(file):
    if shutil.which("pdftotext"):
        return subprocess.check_output(["pdftotext","-enc","UTF-8",str(file),"-"]).decode()
    from pypdf import PdfReader
    return "\n".join(page.extract_text() for page in PdfReader(file).pages)


def run():
    root = config.ROOT
    s = science.scalars()
    if not s:
        raise ValueError("No audit results to verify")
    path = science.data()
    pdf = (root/"paper/main.pdf").read_bytes()
    if pdf != (root/"reports/paper.pdf").read_bytes():
        raise ValueError("The PDF copies differ")
    publication = pdf_text(root/"paper/main.pdf")
    docs = {p:(root/p).read_text(encoding="utf-8") for p in ["README.md","reports/summary.md",
            f"reports/reviews/{science.REVIEW}.md","docs/scientific-audit.html","paper/main.tex"]}
    docs["PDF"] = publication
    for name in ("README.md","reports/summary.md",f"reports/reviews/{science.REVIEW}.md","PDF"):
        compact = re.sub(r"\s","",docs[name])
        for a,b in [("sci.h4_full","sci.n_real"),("sci.fpr.all.flag.hits","sci.fpr.all.flag.n")]:
            value = f"{s[a]}/{s[b]}"
            if value not in compact:
                raise ValueError(f"{name}: missing corrected numerator/denominator {value}")
    for name in ("README.md","paper/main.tex","PDF"):
        for target in ("catalog","angular"):
            for fam in ("arc","sphere"):
                for m in ("P","Bb"):
                    value = f"{s[f'sci.{target}.{fam}.{m}.accuracy']:.3f}"
                    if value not in docs[name]:
                        raise ValueError(f"{name}: missing {value} for {target}, {fam}, {m}")
    if science.comparison().to_html(index=False,float_format=lambda x:f"{x:.3f}",border=0) not in docs["docs/scientific-audit.html"]:
        raise ValueError("Public table differs from benchmark records")
    for p in [root/"README.md",root/"paper/main.tex",*sorted((root/"reports").glob("*.md")),root/"reports/reviews"/(science.REVIEW+".md")]:
        if re.search(r"\?\?[\w.]+\?\?|@@\w+@@|\{\{[a-z][\w.:]+\}\}", p.read_text(encoding="utf-8")):
            raise ValueError(f"Unexpanded evidence field in {p}")
    for figure in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", docs["paper/main.tex"]):
        if not (root/"docs/figures"/figure).is_file():
            raise ValueError(f"Missing figure {figure}")
    paths = pd.read_csv(path/"representatives.csv.gz")
    manifest = read_json(root/"docs/data/manifest.json")
    ids = {x["id"] for group in manifest.values() for x in group}
    assessment = pd.read_csv(path/"dataset_assessment.csv").set_index("id")
    if ids != set(assessment.index):
        raise ValueError("Cloud explorer dataset inventory does not match the evidence")
    for d in ids:
        item = read_json(root/f"docs/data/{d}.json")
        for dim in [1,2]:
            rows = paths[(paths.id==d)&(paths.dimension==dim)].sort_values("k")
            if not np.allclose(rows[["birth","death"]].to_numpy(), np.asarray(item[f"h{dim}"]).reshape(-1,2),atol=.0000051):
                raise ValueError(f"{d}: rendered intervals differ")
            if dim==1 and rows.certified.tolist()!=item["cycle_certified"]:
                raise ValueError(f"{d}: rendered path certificates differ")
        vector = tuple(map(int,assessment.loc[d,["b0","b1_mc","b2_mc"]]))
        expected = "("+",".join(map(str,vector))+") across scales"
        if item["rows"][0][2] != expected:
            raise ValueError(f"{d}: H4 explorer vector differs")
        if not np.isclose(item["q95_pi1"],assessment.at[d,"null_q95_pi1"]):
            raise ValueError(f"{d}: reference threshold differs")
    for e in read_json(root/"docs/data/examples.json"):
        if e["cycle_certified"]!=read_json(root/f"docs/data/{e['id']}.json")["cycle_certified"]:
            raise ValueError("Selected example has different certificates")
    print(f"Verified the PDF, both documented denominators, both targets, figure references and {len(ids)} explorer datasets.")


def compare_json(a, b, path):
    """Match structure and discrete results exactly, allowing roundoff in continuous outputs."""
    if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
        for key in a:
            compare_json(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (left, right) in enumerate(zip(a,b)):
            compare_json(left,right,f"{path}[{i}]")
    elif isinstance(a,float) and isinstance(b,(float,int)):
        if not np.isclose(a,b,rtol=1e-9,atol=1e-10,equal_nan=True):
            raise ValueError(f"{path}: {a!r} vs {b!r}")
    elif type(a) is not type(b) or a != b:
        raise ValueError(f"{path}: clean-run values differ")


def compare(replica):
    """Compare every numerical result behind the audit across two checkouts, excluding timestamped environments."""
    root = config.path("results")
    summary = {}
    files = ["science/"+n for n in ("decisions.csv","matrix.csv","h4_datasets.csv","h6_datasets.csv",
             "null_replay.csv","calibration_draws.csv","calibration.csv","representatives.csv.gz","analytic_controls.csv",
             "benchmark.csv","sensitivity_differences.csv","false_positives.csv","false_positive_rows.csv.gz","closure_counts.csv","angular_domains.csv",
             "dataset_assessment.csv","blobs.csv","false_positive_strata.csv")] + ["exp0/real_topology.csv","exp1/per_cloud.csv.gz","exp2/invariants.csv","exp4/bottleneck_matrix.csv",
            "exp5/projection.csv","exp5/topk_null.csv","exp5/nu_variants.csv",
            "exp0/dense_check.csv","exp0/synth_val_topology.csv.gz","exp0/synth_test_topology.csv.gz",
            "power/power_simulation.csv","power/power_summary.csv","power/power_v2_simulation.csv","power/power_v2_summary.csv",
            "coords/point_coordinates.csv","loops/all_loops.csv","voids/all_voids.csv","exp7_audit/closure_ratio.csv",
            "exp8_audit3/synthetic_by_family.csv","exp8_audit3/cluster_null_simulation.csv","exp9_audit4/c1_top10.csv"]
    for name in files:
        a = pd.read_csv(root/name,low_memory=False)
        b = pd.read_csv(replica/"results"/name,low_memory=False)
        pd.testing.assert_frame_equal(a,b,check_exact=False,atol=1e-10,rtol=1e-9)
        summary[name] = len(a)
    json_files = ["science/hypotheses.json","science/splits.json","science/inputs.json","science/chronology.json",
                  "science/summary.json","exp0/summary.json","exp0/real_alignment.json","exp1/outliers.json",
                  "exp1/summary.json","exp2/summary.json","exp3/summary.json","exp3/method_b.json",
                  "exp3/posthoc_relaxed_range.json","exp4/summary.json","exp5/summary.json","exp7_audit/summary.json",
                  "exp8_audit3/summary.json","exp9_audit4/summary.json","loops/summary.json","voids/summary.json",
                  "toy/summary.json","power/val_tuning.json","power/real_second_order.json"]
    for name in json_files:
        compare_json(read_json(root/name),read_json(replica/"results"/name),name)
    write_json(root/"science/reproduction.json",{"replica_commit":subprocess.check_output(
        ["git","rev-parse","HEAD"],cwd=replica,text=True).strip(),"input_manifest_sha256":read_json(root/"science/inputs.json")["manifest_sha256"],
        "table_rows_compared":summary,"absolute_tolerance":1e-10,"relative_tolerance":1e-9,
        "json_compared":json_files})


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replica",type=Path)
    opt = parser.parse_args()
    run()
    if opt.replica:
        compare(opt.replica)
