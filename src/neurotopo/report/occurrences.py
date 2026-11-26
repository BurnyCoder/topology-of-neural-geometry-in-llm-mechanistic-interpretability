"""Index material claim occurrences in manuscript, docs, figures, source comments and generated displays."""
import re


import pandas as pd

from neurotopo import config

# Patterns map occurrence locations to the human adjudications in the claim ledger. A location can have several.
TERMS = {
    "Registration dates and amendment":r"amendment|preregis|pre-regis",
    "Identity of inputs and source":r"SHA-?256|bit.exact|pinned (snapshot|export|input|revision)",
    "H1 fitted-shape test":r"H1.A|primary.{0,55}helic|helix.{0,30}axis", "H1 persistent-homology test":r"H1.B|strict conjunction",
    "H2 specificity":r"\bH2\b.{0,16}specific|specificity|false.positive rule",
    "H3 days with times":r"days.with.times|days_time|R5c_|\bH3\b",
    "H4 full-vector vs loop/void agreement":r"full.vector|agree.{0,25}Betti|agree_b|A.?vs.?B",
    "H4 classifier comparison":r"balanced.accuracy|McNemar|H4",
    "H5 catalog scores":r"macro|family.implied|majority.vector|exact.vector|ground.truth topology",
    "H5 arc and cap recovery":r"extent_frac|angular.domain|near.closed|0[.]98|open vs closed",
    "Sphere-family topology":r"cap_frac|caps?.{0,14}spheres?|sphere.family",
    "Point-set and mixture targets":r"polytope|mixture component|latent centre",
    "Resolvability and generalization":r"resolvab|reach|margin ratio|rho_A|ρ_A|pitch",
    "Known clean domains":r"noiseless|analytic.controls|known.domain|120.degree",
    "H5 false-positive and DTM rule":r"outlier|DTM|flagged|false.positive",
    "Clustered uncertainty":r"bootstrap|Fisher|confidence interval|generator chunk",
    "Universal-null calibration":r"universal.null|calibrat|Bonferroni|pooled.*KS",
    "Scope of universality":r"weak universality|limiting distribution|conjecture",
    "Strong universality":r"Gumbel|strong universality|counterexample",
    "Design-matched Gaussian reference":r"Gaussian null|cluster.centre null|design.matched|null draw",
    "Finite-sample fitted-null calibration":r"outer dataset|plug.in|nuisance|nested",
    "Alpha and Rips units":r"filtration|Čech|Cech|squared radi|edge length",
    "Landmarks, fields and interval overlap":r"landmark|coordinate|DREiMac|standard_range|F47",
    "Restricted permutations, alignment and order":r"permut|winding|frequency search|Fourier frequenc|exact.order",
    "H6 simulated and causal steering":r"steer|on.manifold|vocabular|H6",
    "Projection sensitivity and seed sensitivity":r"subsampl|top.10|ten.pc|seed sensitivity|projection.specific",
    "Months and weekdays":r"months|weekdays|R5[ab]_",
    "Modular residues":r"residue|mod 113|grokking|grokked",
    "Colour stimuli and representations":r"colour|hue|RGB|R7_",
    "Ordinal PC results and negative controls":r"ordinal|random.walk|random.init|smooth.control",
    "Representative cycles and shells":r"representative|birth path|shell|death simplex|certifi",
    "Voids, triangulations and scale invariants":r"void|genus|Euler characteristic|r_c",
    "Exploratory similarity, power and selection":r"bottleneck|cohesion|power simulat|gallery",
    "Exact duplicate leakage and comparators":r"duplicate|leakage|validation|in.distribution",
    "Clock and Pizza attribution":r"pizza|Clock algorithm",
    "Steering and novelty in prior work":r"novelty|first study|as far as we|manifold steering"
}



def write_index(root, paths, ledger):
    if set(TERMS)!=set(ledger.claim):
        raise ValueError("Occurrence patterns and adjudicated claims differ")
    patterns = {k:re.compile(v,re.I) for k,v in TERMS.items()}
    files = [p for p in paths if (root/p).is_file() and (root/p).suffix in {".md",".tex",".py",".bib",".html"}
             and not p.startswith(("paper/generated/","reports/generated/","tests/","reports/reviews/2026-11-26","reports/templates/reviews/2026-11-26"))
             and p!="src/neurotopo/report/occurrences.py"]
    entries = []
    for path in files:
        lines = (root/path).read_text(encoding="utf-8").splitlines()
        for claim,pattern in patterns.items():
            found = [i for i,line in enumerate(lines,1) if pattern.search(line)]
            if found:
                entries.append((claim,path,",".join(map(str,found))))
    pd.DataFrame(entries,columns=["claim","path","line_numbers"]).to_csv(config.path("results")/"science/claim_occurrences.csv",index=False)
