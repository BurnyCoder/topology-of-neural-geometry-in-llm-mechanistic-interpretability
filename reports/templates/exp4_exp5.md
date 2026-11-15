# Exp4 (similarity) and Exp5 (robustness)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp4_similarity.py`, `exp5_robustness.py`. Results: `results/exp4/`, `results/exp5/`.

## Exp4: topological similarity (exploratory)

**Method.** The distance between two clouds is the bottleneck distance between their diagrams of significant bars (H0 from the b0 cut; H1 and H2 under the design-matched null), summed over dimensions. It is computed for the 44 clouds and 8 ideal templates (circle, rings of 7 and 12 clusters, helix, sphere, torus, line, blob), followed by MDS, a dendrogram, the nearest template, and an exact cohesion test of the cyclic group against all 4-subsets of the 10 cyclic and ordinal sets.

**Result.**
- The cyclic group is not cohesive: exact p = {{exp4.cohesion_p:3}}.
- Almost every cloud is nearest to the topologically trivial templates (helix / line / blob, tied). Only months is nearest a ring of clusters.
- Even colours, with π ≈ 5, is closest to the trivial templates. Its loop bar is short in absolute radius units, and the bottleneck distance works in absolute units.

**Learning.** Bottleneck distance in absolute radius units is dominated by bar length, not by π. A scale-free variant, for example log-coordinates of bars, is listed in the to-do. This exploratory analysis is reported as uninformative.

## Exp5: robustness

- **Projection** (top Rips H1 π in 3D → top-5 → top-10 → full-dimensional cosine):
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

**Interpretation.**
- The colour loop is a property of the representation, not of the 3D projection.
- The months and residue loops are strongest in the top-3 PCs and fade in higher dimensions. For residues this is expected, because several Fourier circles coexist in other PC pairs.
- None of the conclusions depends on the Monte Carlo seed or on the offset nuisance factor.
