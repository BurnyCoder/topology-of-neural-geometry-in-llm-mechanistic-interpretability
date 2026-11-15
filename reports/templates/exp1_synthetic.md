# Exp1: validation of the persistent-homology Betti estimators (H5)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp1_synthetic.py`, `src/neurotopo/tda/estimators.py`. Results: `results/exp1/`.

## Question

How well do persistent-homology estimators recover the exact topology of noisy point clouds? How does that compare with reading topology off the source fitter's predicted family?

## Data

- The source's fixed synthetic test set: 39,000 clouds, 13 families × 4 N-bins (5–1024 points) × 3 noise bins. Each cloud comes with its **exact ground-truth parameters**, regenerated bit-exactly on CUDA.
- Ground truth is Method A on those parameters. Only resolvable clouds are scored (ρ_A ≥ 1): {{exp1.n}} clouds, a fraction of {{exp1.resolvable:3}}.

## Estimators

- **P (preregistered):** alpha-complex universal null (Bobrowski & Skraba 2023, A = ½, Bonferroni) for b1 and b2, plus single-linkage b0 (τ = {{power.b0_tau:1}}, minimum component fraction {{power.b0_minfrac:2}}, tuned on validation).
- **S (D1):** Rips-H1 universal null (A = 1).
- **Ba:** fixed thresholds, π > {{power.pi0_1:1}} for H1 and π > {{power.pi0_2:1}} for H2, tuned on validation.
- **Bb:** the source method's predicted family mapped to its modal ground-truth Betti vector (validation).
- **Bc:** the majority vector.
- **MC:** a 3D matched-Gaussian Monte Carlo null, 99 draws, on the 3,120-cloud subset.

**Metric:** exact (b0, b1, b2) accuracy, macro-averaged over families. Polytope is scored on b0 only. CIs are a cluster bootstrap over generator chunks of 25 clouds, with 2,000 resamples.

## Results

- **P:** {{exp1.P.acc:3}} [{{exp1.P.lo:3}}, {{exp1.P.hi:3}}]
- **S:** {{exp1.S.acc:3}} [{{exp1.S.lo:3}}, {{exp1.S.hi:3}}]
- **Ba:** {{exp1.Ba.acc:3}} [{{exp1.Ba.lo:3}}, {{exp1.Ba.hi:3}}]
- **Bb:** {{exp1.Bb.acc:3}} [{{exp1.Bb.lo:3}}, {{exp1.Bb.hi:3}}]
- **Bc:** {{exp1.Bc.acc:3}} [{{exp1.Bc.lo:3}}, {{exp1.Bc.hi:3}}]
- **MC (subset):** {{exp1.MC.acc:3}} [{{exp1.MC.lo:3}}, {{exp1.MC.hi:3}}]
- **Paired differences (P minus comparator):**
  - vs Ba: {{exp1.diff.Ba:3}} [{{exp1.diff.Ba.lo:3}}, {{exp1.diff.Ba.hi:3}}]
  - vs Bb: {{exp1.diff.Bb:3}} [{{exp1.diff.Bb.lo:3}}, {{exp1.diff.Bb.hi:3}}]
  - vs Bc: {{exp1.diff.Bc:3}} [{{exp1.diff.Bc.lo:3}}, {{exp1.diff.Bc.hi:3}}]
- **H5:** the preregistered estimator is significantly *worse* than the fixed-threshold and family-implied baselines, and better than the majority vector.
- **The family label is scored in-distribution.** It comes from the source's shape fitter, which was trained on clouds from the same 13-family generator as this test set, whereas the persistence estimators are generic. The comparison says which instrument is more accurate on these 13 families, not in general.
- **Well-resolved topology (ρ_A ≥ 4; post hoc, D6).** {{exp1.well.n}} clouds from {{exp1.well.n_families}} of the 13 families: no torus reaches ρ_A ≥ 4 ({{exp1.well.n_torus}} tori), and a fraction {{exp1.well.trivial_frac:2}} are blobs, discs or paraboloids, whose topology cannot change (infinite margin) and which have no hole. The macro average is therefore over a different family mix than the main table, and it drops the family where the label is best (tori). Macro, with cluster-bootstrap CIs:
  - P: {{exp1.well.P.acc:3}} [{{exp1.well.P.lo:3}}, {{exp1.well.P.hi:3}}]
  - Ba: {{exp1.well.Ba.acc:3}} [{{exp1.well.Ba.lo:3}}, {{exp1.well.Ba.hi:3}}]
  - Bb: {{exp1.well.Bb.acc:3}} [{{exp1.well.Bb.lo:3}}, {{exp1.well.Bb.hi:3}}]
  - Bc: {{exp1.well.Bc.acc:3}}
  - Paired P − Bb: {{exp1.well.diff.Bb:3}} [{{exp1.well.diff.Bb.lo:3}}, {{exp1.well.diff.Bb.hi:3}}]. P − Ba: {{exp1.well.diff.Ba:3}} [{{exp1.well.diff.Ba.lo:3}}, {{exp1.well.diff.Ba.hi:3}}].
  - Micro-averaged accuracies in the top ρ_A bin, used in an earlier version of the text: P {{exp1.rho4.P:2}}, Ba {{exp1.rho4.Ba:2}}, Bb {{exp1.rho4.Bb:2}}.
- **False positives** (any hole on resolvable contractible shapes): {{exp1.P.fpr_min:3}}–{{exp1.P.fpr_max:3}} per N-bin for P.
- **Loop detection, not only exact vectors (third audit, D9; post hoc).** Exact-vector accuracy mixes b0, b1 and b2. The question the real data ask is narrower: does the estimator find a loop when there is one, and stay silent when there is none? Shown below is the fraction of resolvable clouds with at least one significant H1 bar, with cluster-bootstrap 95% CIs ([exp8_audit3.md](exp8_audit3.md)).

  | Estimator | true holes detected (b1 ≥ 1) | false loops (b1 = 0) |
  |---|---|---|
  | P (all resolvable) | {{audit3.P.sens:3}} [{{audit3.P.sens_lo:3}}, {{audit3.P.sens_hi:3}}] (n = {{audit3.P.n_hole}}) | {{audit3.P.fpr:3}} [{{audit3.P.fpr_lo:3}}, {{audit3.P.fpr_hi:3}}] (n = {{audit3.P.n_free}}) |
  | S (all resolvable) | {{audit3.S.sens:3}} [{{audit3.S.sens_lo:3}}, {{audit3.S.sens_hi:3}}] | {{audit3.S.fpr:3}} [{{audit3.S.fpr_lo:3}}, {{audit3.S.fpr_hi:3}}] |
  | Ba (all resolvable) | {{audit3.Ba.sens:3}} [{{audit3.Ba.sens_lo:3}}, {{audit3.Ba.sens_hi:3}}] | {{audit3.Ba.fpr:3}} [{{audit3.Ba.fpr_lo:3}}, {{audit3.Ba.fpr_hi:3}}] |
  | MC (3,120-cloud subset) | {{audit3.mc.sens:3}} [{{audit3.mc.sens_lo:3}}, {{audit3.mc.sens_hi:3}}] (n = {{audit3.mc.n_hole}}) | {{audit3.mc.fpr:3}} [{{audit3.mc.fpr_lo:3}}, {{audit3.mc.fpr_hi:3}}] (n = {{audit3.mc.n_free}}) |

  - **P is conservative.** It finds {{audit3.P.fam.cone_b1:2}} of cone holes, {{audit3.P.fam.torus_b2:2}} of tori and {{audit3.P.fam.ellipse_b1:2}} of ellipses (subset).
  - **MC is not specific to holes.** It is the design-(b) null of the real data in 3D: a matched Gaussian, with the same distribution as the real-data sampler on rank-3 clouds (median q95 difference {{audit3.eq.median_rel:3}}). It flags loops on hole-free clouds by family as follows:
    - blobs {{audit3.mc.fam.blob_b0:2}} (its own model, so calibrated), lines {{audit3.mc.fam.line_b0:2}}, open curves {{audit3.mc.fam.ringing_b0:2}}, open arcs {{audit3.mc.fam.arc_b0:2}};
    - polytopes {{audit3.mc.fam.polytope_b0:2}}, discs {{audit3.mc.fam.disc_b0:2}}, helices {{audit3.mc.fam.helix_b0:2}};
    - paraboloids {{audit3.mc.fam.paraboloid_b0:2}}, spheres and caps {{audit3.mc.fam.sphere_b0:2}}.
  - The false-loop rate grows with N, from {{audit3.mc.fpr_bin0:2}} in the smallest N bin to {{audit3.mc.fpr_bin3:2}} in the largest. It is not caused by outliers: {{audit3.mc.fpr_outlier:2}} with outliers vs {{audit3.mc.fpr_clean:2}} without.
  - The flagged hole-free clouds have top π {{audit3.mc.flag_pi_q10:2}}–{{audit3.mc.flag_pi_q90:2}} (10th–90th percentile; median {{audit3.mc.flag_pi_q50:2}}). True holes that MC detects have {{audit3.mc.det_pi_q10:2}}–{{audit3.mc.det_pi_q90:2}}.
  - Why: a Gaussian null fixes the covariance, not the intrinsic dimension. Noise cycles on a 2D surface live longer than in a 3D blob of the same spread. The largest multiplicative persistence of noise cycles grows with the number of points, with constants that depend on dimension ([Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232)). This is consistent with the rise with N; the theorem is for uniform samples, so it explains the pattern rather than proving it here.
- **Outlier clouds and the preregistered DTM conditional (deviation D7).**
  - The source generator replaces random points by uniform draws from the padded bounding box but does not record which ones. The proxy was fixed before computing: an "outlier cloud" has at least one point farther than {{exp1.out.factor:0}} × its median distance from the ground-truth shape. That covers {{exp1.out.flagged:3}} of all test clouds.
  - False-positive rate on resolvable contractible clouds (95% cluster-bootstrap CI):

    | Estimator | outlier clouds | clean clouds | one-sided Fisher p |
    |---|---|---|---|
    | P | {{exp1.out.P.outlier:3}} [{{exp1.out.P.outlier.lo:3}}, {{exp1.out.P.outlier.hi:3}}] (n = {{exp1.out.P.outlier.n}}) | {{exp1.out.P.clean:3}} [{{exp1.out.P.clean.lo:3}}, {{exp1.out.P.clean.hi:3}}] (n = {{exp1.out.P.clean.n}}) | {{exp1.out.P.fisher}} |
    | S | {{exp1.out.S.outlier:3}} [{{exp1.out.S.outlier.lo:3}}, {{exp1.out.S.outlier.hi:3}}] | {{exp1.out.S.clean:3}} [{{exp1.out.S.clean.lo:3}}, {{exp1.out.S.clean.hi:3}}] | {{exp1.out.S.fisher}} |
    | Ba | {{exp1.out.Ba.outlier:3}} [{{exp1.out.Ba.outlier.lo:3}}, {{exp1.out.Ba.outlier.hi:3}}] | {{exp1.out.Ba.clean:3}} [{{exp1.out.Ba.clean.lo:3}}, {{exp1.out.Ba.clean.hi:3}}] | {{exp1.out.Ba.fisher}} |
    | Bb | {{exp1.out.Bb.outlier:3}} [{{exp1.out.Bb.outlier.lo:3}}, {{exp1.out.Bb.outlier.hi:3}}] | {{exp1.out.Bb.clean:3}} [{{exp1.out.Bb.clean.lo:3}}, {{exp1.out.Bb.clean.hi:3}}] | {{exp1.out.Bb.fisher}} |

  - **Decision:** outliers roughly double the false positives of the universal-null estimators (P, S), while the tuned fixed threshold (Ba) is unaffected. P stays below the preregistered threshold of {{exp1.out.thr:2}}, so the DTM filtration is **{{exp1.out.dtm}}**.
  - With factors {{exp1.out.sens.factors}} instead of {{exp1.out.factor:0}} (post hoc), P's outlier false-positive rate ranges over {{exp1.out.sens.P.min:3}}–{{exp1.out.sens.P.max:3}}, so the decision does not depend on the factor.
  - **Proxy check:** flagged fraction vs the generator's expected fraction of clouds with at least one injected outlier, per N bin:
    - N {{exp1.out.bin0.range}}: {{exp1.out.bin0.flagged:2}} vs {{exp1.out.bin0.expected:2}};
    - N {{exp1.out.bin1.range}}: {{exp1.out.bin1.flagged:2}} vs {{exp1.out.bin1.expected:2}};
    - N {{exp1.out.bin2.range}}: {{exp1.out.bin2.flagged:2}} vs {{exp1.out.bin2.expected:2}};
    - N {{exp1.out.bin3.range}}: {{exp1.out.bin3.flagged:2}} vs {{exp1.out.bin3.expected:2}}.

    The proxy misses outliers that land near the shape. In the largest clouds it also flags some extreme noise points, because there the flagged fraction exceeds the expected one.

<!-- BEGIN:exp1 -->
<!-- END:exp1 -->

![estimators](../docs/figures/fig_exp1_estimators.png)
![by rho](../docs/figures/fig_exp1_by_rho.png)
![outliers](../docs/figures/fig_exp1_outliers.png)

## Interpretation

- **Where persistent homology adds information beyond the family label:** whenever the label does not fix the topology. The fixed-threshold estimator Ba is quoted here:
  - open vs closed arcs: {{exp1.Ba.arc:2}} vs {{exp1.Bb.arc:2}};
  - caps vs full spheres: {{exp1.Ba.sphere:2}} vs {{exp1.Bb.sphere:2}}.
- **The preregistered estimator P is not better than the family label,** even on well-resolved clouds.
- **Where it loses:** wherever the label fixes the topology but the hole is thin or two-dimensional. Ellipses: {{exp1.Ba.ellipse:2}} vs {{exp1.Bb.ellipse:2}}. Tori: {{exp1.Ba.torus:2}} vs {{exp1.Bb.torus:2}}. Frusta: {{exp1.Ba.cone:2}} vs {{exp1.Bb.cone:2}}.
- **The alpha-complex universal null is calibrated but conservative.** Its family-wise error on blobs is about 0. This is why it loses to a tuned threshold (deviation D1).

## Learnings

- At N ≤ 1024 the universal null of Bobrowski & Skraba is too conservative for alpha complexes in ℝ³. A Rips complex (A = 1) or a tuned threshold is more powerful.
- Resolvability (ρ_A) is the main determinant of accuracy, so reporting accuracy against ρ_A is essential.
- The tuned b0 rule chose the largest τ in the grid (deviation note A1). The clusters family is the weakest b0 case.
