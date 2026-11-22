# Exp4 (similarity) and Exp5 (robustness)

Date: 2026-11-15; updated 2026-11-22 (independent audit, D14: smooth-curve controls in the top-10 test, `exp9_independent_audit.py`). Code: `src/neurotopo/experiments/exp4_similarity.py`, `exp5_robustness.py`. Results: `results/exp4/`, `results/exp5/`.

## Exp4: topological similarity (exploratory)

**Method.** The distance between two clouds is the bottleneck distance between their diagrams of significant bars (H0 from the b0 cut; H1 and H2 under the design-matched null), summed over dimensions. It is computed for the 44 clouds and 8 ideal templates (circle, rings of 7 and 12 clusters, helix, sphere, torus, line, blob), followed by MDS, a dendrogram, the nearest template, and an exact cohesion test of the cyclic group against all 4-subsets of the 10 cyclic and ordinal sets.

**Result.**
- The cyclic group is not cohesive: exact p = {{exp4.cohesion_p:3}}.
- Almost every cloud is nearest to the topologically trivial templates (helix / line / blob, tied). Only months is nearest a ring of clusters.
- Even colours, with π ≈ 5, is closest to the trivial templates. Its loop bar is short in absolute radius units, and the bottleneck distance works in absolute units.

![MDS and dendrogram](../docs/figures/fig_exp4.png)

**Caveat.** Keeping only significant bars gives up the bottleneck stability theorem ([Cohen-Steiner, Edelsbrunner & Harer 2007](https://doi.org/10.1007/s00454-006-1276-5)): a bar just above the threshold in one cloud and just below it in a nearly identical cloud changes the distance by about half its length. The distance is computed exactly with `gudhi.bottleneck_distance` (e = 0), GUDHI's CGAL-based implementation by F. Godi after [Efrat, Itai & Katz 2001](https://doi.org/10.1007/s00453-001-0016-8) ([GUDHI documentation](https://gudhi.inria.fr/python/latest/bottleneck_distance_user.html)), not GUDHI's separate Hera interface.

**Learning.** Bottleneck distance in absolute radius units is dominated by bar length, not by π. A scale-free variant, for example log-coordinates of bars, is listed in the to-do. This exploratory analysis is reported as uninformative.

## Exp5: robustness

- **Projection** (top Rips H1 π in 3D → top-5 → top-10 → full-dimensional cosine dissimilarity). The last value is not comparable with the others: 1 − cos is not a metric and is about angle²/2 for small angles, so its π is roughly the square of an angular-distance π ([math fact-check](reviews/math-fact-check.md)):
  - colours: {{exp5.colors.rips3_pi1:2}} → {{exp5.colors.rips5_pi1:2}} → {{exp5.colors.rips10_pi1:2}} → {{exp5.colors.ripsD_cos_pi1:2}};
  - residues: {{exp5.grok.rips3_pi1:2}} → {{exp5.grok.rips5_pi1:2}} → {{exp5.grok.rips10_pi1:2}} → {{exp5.grok.ripsD_cos_pi1:2}};
  - months: {{exp5.months.rips3_pi1:2}} → {{exp5.months.rips5_pi1:2}} → {{exp5.months.rips10_pi1:2}} → {{exp5.months.ripsD_cos_pi1:2}};
  - weekdays: {{exp5.weekdays.rips3_pi1:2}} → {{exp5.weekdays.rips5_pi1:2}} → {{exp5.weekdays.rips10_pi1:2}} → {{exp5.weekdays.ripsD_cos_pi1:2}}.
- **Offset removal** (subtract the per-offset means of "k days from"): the months loop stays significant (p = {{exp5.offset.months.p_loop}}); weekdays still show none (p = {{exp5.offset.weekdays.p_loop}}).
- **Monte Carlo seeds 1 and 2:**
  - months loop p = {{exp5.seed1.months.p_loop}} and {{exp5.seed2.months.p_loop}};
  - residues {{exp5.seed1.grok.p_loop}} and {{exp5.seed2.grok.p_loop}};
  - weekdays {{exp5.seed1.weekdays.p_loop}} and {{exp5.seed2.weekdays.p_loop}}.
- **Noise-scale definition of Method A:** resolvable fits number {{exp5.resolvable.rho_main}} under the main definition, {{exp5.resolvable.rho_median_only}} with the median term only, and {{exp5.resolvable.rho_coverage_x2}} with doubled coverage. The three cyclic helices stay unresolvable under all three.

- **Top-10-PC loop test with a design-matched Monte Carlo null** (post hoc, D6; 199 draws; Rips π vs null 95th percentile):
  - colours: {{exp5.top10.colors.pi:2}} vs {{exp5.top10.colors.q95:2}} (p = {{exp5.top10.colors.p}});
  - residues: {{exp5.top10.grok.pi:2}} vs {{exp5.top10.grok.q95:2}} (p = {{exp5.top10.grok.p}});
  - months: {{exp5.top10.months.pi:2}} vs {{exp5.top10.months.q95:2}} (p = {{exp5.top10.months.p}});
  - weekdays: p = {{exp5.top10.weekdays.p}};
  - significant overall: {{exp5.top10.sig_ids}}.

  ![top-10 loop test](../docs/figures/fig_top10.png)

- **DTM filtration (preregistered conditional):** {{exp1.out.dtm}}. P's false-positive rate on outlier clouds is {{exp1.out.P.outlier:3}}, below the {{exp1.out.thr:2}} threshold (deviation D7; `reports/exp1_synthetic.md`).

**Interpretation.**
- Raw persistence ratios are not comparable across dimensions and sample sizes. The top-10 statement therefore rests on the matched null above, which was added post hoc.
- **In 10 dimensions, loops are not specific to cyclic concepts.** Years, age, counting and temperature have significant top-10 loops. Months and residues do not.
- **These ordinal loops are not a generic artefact of ordered curves** (independent audit, D14; post hoc, with a decision rule committed before the run). The same test on the {{audit4.n}} smooth-curve controls (10 Gaussian processes, 10 random walks in ℝ⁷⁶⁸, N = 200) finds {{audit4.n_sig}} of {{audit4.n}} significant (exact 95% CI of the rate 0–{{audit4.ci_hi:2}}); their largest Rips ratio is {{audit4.pi_max:3}}, against null thresholds of {{audit4.q95_min:2}}–{{audit4.q95_max:2}}. Pre-specified verdict: the PCA-artefact explanation is {{audit4.decision}}. The PCA projections of such curves are open Lissajous-type curves ([Antognini & Sohl-Dickstein 2018](https://arxiv.org/abs/1806.08805): PC_k ∝ cos(kπt)), and PC1 is monotone along the curve, so the top-10 curve does not close. The ordinal loops therefore need structure the controls lack: periodic features of numbers ([Kantamneni & Tegmark 2025](https://arxiv.org/abs/2502.00873)), clusters (ages form clusters, Exp0), or noise around a smooth curve, which the controls do not have. This test cannot tell these apart.
- The post hoc traversal test shows that ordinal values do not wind around those loops. Only colours keep both a loop and a single winding in 10D, and the colour prompts' own RGB values already have that loop (audit D8, [exp7_audit.md](exp7_audit.md)).
- The months and residue loops are strongest in the top-3 PCs and fade in higher dimensions. For residues this is expected, because several Fourier circles coexist in other PC pairs.
- None of the conclusions depends on the Monte Carlo seed or on the offset nuisance factor.
