"""Render the audit, paper scalars and public comparison from the same checked results."""
from html import escape
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd


from neurotopo import config
from neurotopo.experiments.common import read_json
from neurotopo.report.tables import md_table

REVIEW = "2026-11-26-scientific-audit"
GIT = "https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability/blob/main/"
METHODS = {"P_alpha_universal":"P","S_rips_universal":"S","Ba_fixed_pi":"Ba","Bb_family_implied":"Bb","Bc_majority":"Bc"}


def data():
    return config.path("results")/"science"


def scalars():
    path = data()
    if not (path/"summary.json").exists():
        return {}
    s = read_json(path/"summary.json")
    n = {f"sci.{k}":s[k] for k in ("n_real","h4_full","h4_partial","null_arrays","analytic_controls","selected_paths","exact_cloud_overlap")}
    n["sci.inputs"] = s["inputs"]["verified_files"]
    for dim,group in s["certificates"].items():
        for key,v in group.items():
            n[f"sci.rep{dim}.{key}"] = v
    for family,group in s["changes"].items():
        for key,v in group.items():
            n[f"sci.{family}.{key}"] = v
    for r in pd.read_csv(path/"benchmark.csv").itertuples():
        if r.group not in ("macro","arc","sphere"):
            continue
        for key in ("accuracy","low","high","P_minus_method","difference_low","difference_high"):
            n[f"sci.{r.target}.{r.group}.{METHODS[r.method]}.{key}"] = getattr(r,key)
    mc = pd.read_csv(path/"mc_subset.csv").set_index(["target","group","method"]).loc[("catalog","macro","MC_gaussian3d")]
    for key in ("P_minus_method","difference_low","difference_high"):
        n[f"sci.p_vs_mc.{key}"] = mc[key]
    for r in pd.read_csv(path/"false_positives.csv").itertuples():
        prefix = ("all" if r.cohort=="catalog" else "old")+"."+{"flagged":"flag","unflagged":"unflag","flagged minus unflagged":"diff"}[r.comparison]
        for key in ("n","hits","rate","low","high"):
            val = getattr(r,key)
            if pd.notna(val):
                n[f"sci.fpr.{prefix}.{key}"] = int(val) if key in ("n","hits") else val
    return n


def comparison():
    df = pd.read_csv(data()/"benchmark.csv")
    df = df[df.group.isin(["macro","arc","sphere"]) & df.method.isin(["P_alpha_universal","Bb_family_implied"])]
    rows = []
    for (group,target),v in df.groupby(["group","target"],sort=False):
        idx = v.set_index("method")
        p, b = idx.loc["P_alpha_universal"],idx.loc["Bb_family_implied"]
        rows.append({"Cohort":group, "Target":target, "Persistence (P)":p.accuracy, "Family label (Bb)":b.accuracy,
                     "Paired P − Bb (95% CI)":f"{b.P_minus_method:+.3f} [{b.difference_low:+.3f}, {b.difference_high:+.3f}]"})
    return pd.DataFrame(rows)


def figure():
    import matplotlib.pyplot as plt
    df = pd.read_csv(data()/"benchmark.csv")
    fig,axes = plt.subplots(1,3,figsize=(10,3.8),sharey=True)
    colors = {"P_alpha_universal":"#1c697c","Bb_family_implied":"#ae5925"}
    for ax,group,title in zip(axes,["macro","arc","sphere"],["Family macro-average","Arc family","Sphere family"]):
        g = df[df.group.eq(group)].set_index(["target","method"])
        for j,(m,color) in enumerate(colors.items()):
            v = g.loc[[("catalog",m),("angular",m)]]
            ax.errorbar(np.arange(2)+(j-.5)*.11,v.accuracy,
                        yerr=[v.accuracy-v.low,v.high-v.accuracy],fmt="o",capsize=3,color=color,
                        label="Persistence (P)" if j==0 else "Family label (Bb)")
        ax.set(xticks=[0,1],xticklabels=["Catalog","Angular domain"],xlim=(-.28,1.28),ylim=(0,1.02),title=title)
        ax.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Eligible-cloud accuracy")
    handles,labels = axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=2,loc="lower center",frameon=False)
    fig.tight_layout(rect=(0,.10,1,1))
    fig.savefig(config.path("figures")/"fig_scientific_audit.png",dpi=165,bbox_inches="tight")
    plt.close(fig)


def dossier():
    """Publish tabular claims with local evidence and external methodological attribution."""
    root, path = config.ROOT, data()
    ledger = pd.read_csv(root/"reports/reviews/2026-11-26-claims.tsv",sep="\t")
    if not all((root/p).is_file() for p in ledger.local_evidence):
        raise ValueError("A claim has missing local evidence")
    ledger.to_csv(path/"claims.csv", index=False)
    # This is a provenance inventory, not an automated semantic entailment score.
    files = subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard","-z"],cwd=root).decode().split("\0")
    groups = {"logs/":"Dated observations and environment records", "docs/data/":"Explorer rendering from measured arrays",
              "docs/figures/":"Rendered measurements or simulation diagrams", "reports/generated/":"Report table from results",
              "paper/generated/":"Publication scalars from results","results/":"Measured or computed artifact",
              "tests/":"Regression and implementation checks","external/":"Pinned upstream checkout",
              "src/":"Implementation or presentation source","reports/reviews/":"Dated scientific review or erratum"}
    paths = sorted(set(p for p in files if p) | {str(p.relative_to(root).as_posix()) for p in [
        root/"reports/reviews"/(REVIEW+".md"), root/"docs/scientific-audit.html", root/"reports/paper.pdf", path/"claims.csv",
        path/"inventory.csv", path/"claim_occurrences.csv", path/"reproduction.json"]})
    pd.DataFrame([(p,next((label for prefix,label in groups.items() if p.startswith(prefix)),
                          "Study documentation, configuration or release artifact")) for p in paths],
                 columns=["path","role"]).to_csv(path/"inventory.csv",index=False)
    from neurotopo.report.occurrences import write_index
    write_index(root, paths, ledger)
    frame = comparison()
    cal = pd.read_csv(path/"calibration.csv")
    controls = pd.read_csv(path/"analytic_controls.csv")
    blobs = pd.read_csv(path/"blobs.csv").drop(columns="pooled_size_ks_D")
    decisions = pd.read_csv(path/"decisions.csv")
    primary = decisions[decisions.hypothesis.isin(["H1","H3"])].copy()
    primary["strict 3D coordinate"] = primary.coordinate.map(lambda s: "available" if s=="available" else "unavailable")
    primary["strict top-ten coordinate"] = primary.coordinate10.map(lambda s: s if s in ("available","inapplicable") else "unavailable")
    from neurotopo.report import numbers
    template = root/"reports/templates/reviews"/(REVIEW+".md")
    empirical = scalars()
    markdown = numbers.render(template.read_text(encoding="utf-8"), numbers.collect())
    fpr = pd.read_csv(path/"false_positives.csv")
    fpr[["n","hits"]] = fpr[["n","hits"]].astype("Int64")
    fpr = fpr.rename(columns={"n":"Clouds","hits":"Detections","rate":"Estimate","low":"95% lower","high":"95% upper"})
    fields = {"@@primary@@":md_table(primary[["id","method","hole","p_loop","strict 3D coordinate","p_holm","winding","strict top-ten coordinate","status"]]),
              "@@comparison@@":md_table(frame), "@@calibration@@":md_table(cal), "@@blobs@@":md_table(blobs),
              "@@controls@@":md_table(controls), "@@outliers@@":md_table(fpr),
              "@@claims@@":"\n\n".join(f"**{r.claim}** ({r.disposition}). {r.assessment} [Local evidence](../../{r.local_evidence}) · [Primary source]({r.primary_source})" for r in ledger.itertuples())}
    for key,value in fields.items():
        markdown = markdown.replace(key,value)
    (root/"reports/reviews"/(REVIEW+".md")).write_text(markdown,encoding="utf-8",newline="\n")
    # Render a standalone static page. Links and the table remain readable with JavaScript off.
    link = lambda name,label: f'<a href="{GIT}{name}">{escape(label)}</a>'
    report_link = link("reports/reviews/"+REVIEW+".md","Full audit and evidence register")
    text = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scientific audit · Neural geometry</title><style>body{{font:16px/1.5 system-ui;color:#172f39;max-width:62rem;margin:2rem auto;padding:0 1rem}}
img{{width:100%;height:auto}}table{{border-collapse:collapse;font-variant-numeric:tabular-nums}}td,th{{border-bottom:1px solid #ccc;padding:.4rem;text-align:left}}section{{overflow-x:auto}}</style>
<nav><a href="index.html">Cloud explorer</a> · {report_link}</nav><h1>Independent scientific audit</h1><p>26 November 2026 · Libor “Burny” Burian</p>
<p>The strict primary-dataset conjunction fails on weekdays, months and modular residues. The amended primary steering experiment remains untested. The accuracy comparison depends on how the source labels near-complete angular domains.</p>
<img src="figures/fig_scientific_audit.png" alt="Accuracy for the persistence estimator and family baseline on the catalog and unrounded angular domains">
<h2>Fixed-cohort benchmark</h2><section>{frame.to_html(index=False,float_format=lambda x:f'{x:.3f}',border=0)}</section>
<p>Intervals use paired resampling of generator chunks. The angular-domain sensitivity preserves all predictions and catalog eligibility.</p>
<h2>Full-vector agreement and false positives</h2><p>The methods agree on components, loops and voids for {empirical['sci.h4_full']}/{empirical['sci.n_real']} datasets. Among eligible contractible clouds flagged by distance to the sampled shape, P detected a loop or void in {empirical['sci.fpr.all.flag.hits']}/{empirical['sci.fpr.all.flag.n']}. The intervals below use generator chunks.</p>
<section>{fpr.to_html(index=False,float_format=lambda x:f'{x:.3f}',na_rep='—',border=0).replace('&lt;NA&gt;','—')}</section>
<p>{link('results/science/h4_datasets.csv','Full-vector agreement by dataset')} · {link('results/science/decisions.csv','Every registered condition')} · {link('results/science/representatives.csv.gz','Cycle certificates')} · {link('results/science/claims.csv','Claim ledger')}</p></html>"""
    (root/"docs/scientific-audit.html").write_text(text,encoding="utf-8",newline="\n")
