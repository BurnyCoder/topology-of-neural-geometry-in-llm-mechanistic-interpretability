# H5 synthetic instrument comparison

The registered target is the source's catalog vector at exported parameters. Eligibility requires ρ_A ≥ 1 and polytopes are scored on components alone. The majority and predicted-family targets and fixed persistence thresholds are determined on validation. The fixed-target sensitivity uses identical predictions and eligible test clouds. A cluster-bootstrap resample draws whole source generator chunks. [Registration](preregistration.md) · [Estimator implementation](../src/neurotopo/experiments/exp1_synthetic.py) · [Independent target reconstruction](../src/neurotopo/science/benchmark.py)

<!-- BEGIN:exp1 -->
<!-- END:exp1 -->

The registered P minus Ba difference is {{exp1.diff.Ba:3}} [{{exp1.diff.Ba.lo:3}}, {{exp1.diff.Ba.hi:3}}]. P minus Bb is {{exp1.diff.Bb:3}} [{{exp1.diff.Bb.lo:3}}, {{exp1.diff.Bb.hi:3}}]. P exceeds the majority comparator by {{exp1.diff.Bc:3}} [{{exp1.diff.Bc.lo:3}}, {{exp1.diff.Bc.hi:3}}]. The methods vary in access to generator-specific information, so the comparisons are in-distribution. [Result table](../results/exp1/summary.json)

The pinned generators report closed arcs and spheres at an angular fraction of 0.98. A positive gap remains for {{sci.arc.test}} test arcs and {{sci.sphere.test}} sphere-family objects labeled closed. Changing only those targets reverses P versus Bb on both families. The conditional flagged-cloud false-positive rate is {{sci.fpr.all.flag.hits}}/{{sci.fpr.all.flag.n}} with all eligible contractible targets. Flag status measures distance to a sampled shape and can be affected by sample size or family. DTM remains below its registered activation threshold. The audit reports separate blob calibration by noise and size and exact-domain controls at a specified radius. [Paired intervals](../results/science/benchmark.csv) · [False-positive analysis](../results/science/false_positives.csv) · [Calibration](../results/science/blobs.csv) · [Known-domain controls](../results/science/analytic_controls.csv)

![Comparison under catalog and unrounded angular labels](../docs/figures/fig_scientific_audit.png)
