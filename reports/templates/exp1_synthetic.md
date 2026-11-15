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
- **Well-resolved topology (ρ_A ≥ 4; post hoc, D6).** {{exp1.well.n}} clouds; a fraction {{exp1.well.trivial_frac:2}} of them are always-contractible blobs, discs or paraboloids. Macro, with cluster-bootstrap CIs:
  - P: {{exp1.well.P.acc:3}} [{{exp1.well.P.lo:3}}, {{exp1.well.P.hi:3}}]
  - Ba: {{exp1.well.Ba.acc:3}} [{{exp1.well.Ba.lo:3}}, {{exp1.well.Ba.hi:3}}]
  - Bb: {{exp1.well.Bb.acc:3}} [{{exp1.well.Bb.lo:3}}, {{exp1.well.Bb.hi:3}}]
  - Bc: {{exp1.well.Bc.acc:3}}
  - Paired P − Bb: {{exp1.well.diff.Bb:3}} [{{exp1.well.diff.Bb.lo:3}}, {{exp1.well.diff.Bb.hi:3}}]. P − Ba: {{exp1.well.diff.Ba:3}} [{{exp1.well.diff.Ba.lo:3}}, {{exp1.well.diff.Ba.hi:3}}].
  - Micro-averaged accuracies in the top ρ_A bin, used in an earlier version of the text: P {{exp1.rho4.P:2}}, Ba {{exp1.rho4.Ba:2}}, Bb {{exp1.rho4.Bb:2}}.
- **False positives** (any hole on resolvable contractible shapes): {{exp1.P.fpr_min:3}}–{{exp1.P.fpr_max:3}} per N-bin for P.

<!-- BEGIN:exp1 -->
<!-- END:exp1 -->

![estimators](../docs/figures/fig_exp1_estimators.png)
![by rho](../docs/figures/fig_exp1_by_rho.png)

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
