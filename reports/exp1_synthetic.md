# Exp1: validation of the persistent-homology Betti estimators (H5)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp1_synthetic.py`, `src/neurotopo/tda/estimators.py`. Results: `results/exp1/`.

## Question

How well do persistent-homology estimators recover the exact topology of noisy point clouds? How does that compare with reading topology off the source fitter's predicted family?

## Data

- The source's fixed synthetic test set: 39,000 clouds, 13 families × 4 N-bins (5–1024 points) × 3 noise bins. Each cloud comes with its **exact ground-truth parameters**, regenerated bit-exactly on CUDA.
- Ground truth is Method A on those parameters. Only resolvable clouds are scored (ρ_A ≥ 1): 30114 clouds, a fraction of 0.772.

## Estimators

- **P (preregistered):** alpha-complex universal null (Bobrowski & Skraba 2023, A = ½, Bonferroni) for b1 and b2, plus single-linkage b0 (τ = 12.0, minimum component fraction 0.02, tuned on validation).
- **S (D1):** Rips-H1 universal null (A = 1).
- **Ba:** fixed thresholds, π > 3.0 for H1 and π > 1.4 for H2, tuned on validation.
- **Bb:** the source method's predicted family mapped to its modal ground-truth Betti vector (validation).
- **Bc:** the majority vector.
- **MC:** a 3D matched-Gaussian Monte Carlo null, 99 draws, on the 3,120-cloud subset.

**Metric:** exact (b0, b1, b2) accuracy, macro-averaged over families. Polytope is scored on b0 only. CIs are a cluster bootstrap over generator chunks of 25 clouds, with 2,000 resamples.

## Results

- **P:** 0.618 [0.610, 0.626]
- **S:** 0.660 [0.651, 0.670]
- **Ba:** 0.714 [0.703, 0.725]
- **Bb:** 0.812 [0.807, 0.816]
- **Bc:** 0.555 [0.553, 0.557]
- **MC (subset):** 0.594 [0.561, 0.629]
- **Paired differences (P minus comparator):**
  - vs Ba: -0.096 [-0.108, -0.084]
  - vs Bb: -0.194 [-0.203, -0.185]
  - vs Bc: 0.063 [0.055, 0.071]
- **H5:** the preregistered estimator is significantly *worse* than the fixed-threshold and family-implied baselines, and better than the majority vector.
- **The family label is scored in-distribution.** It comes from the source's shape fitter, which was trained on clouds from the same 13-family generator as this test set, whereas the persistence estimators are generic. The comparison says which instrument is more accurate on these 13 families, not in general.
- **Well-resolved topology (ρ_A ≥ 4; post hoc, D6).** 18454 clouds from 12 of the 13 families: no torus reaches ρ_A ≥ 4 (0 tori), and a fraction 0.49 are blobs, discs or paraboloids, whose topology cannot change (infinite margin) and which have no hole. The macro average is therefore over a different family mix than the main table, and it drops the family where the label is best (tori). Macro, with cluster-bootstrap CIs:
  - P: 0.751 [0.739, 0.763]
  - Ba: 0.923 [0.915, 0.931]
  - Bb: 0.820 [0.812, 0.829]
  - Bc: 0.600
  - Paired P − Bb: -0.070 [-0.084, -0.056]. P − Ba: -0.172 [-0.184, -0.160].
  - Micro-averaged accuracies in the top ρ_A bin, used in an earlier version of the text: P 0.87, Ba 0.94, Bb 0.86.
- **False positives** (any hole on resolvable contractible shapes): 0.019–0.054 per N-bin for P.
- **Outlier clouds and the preregistered DTM conditional (deviation D7).**
  - The source generator replaces random points by uniform draws from the padded bounding box but does not record which ones. The proxy was fixed before computing: an "outlier cloud" has at least one point farther than 6 × its median distance from the ground-truth shape. That covers 0.193 of all test clouds.
  - False-positive rate on resolvable contractible clouds (95% cluster-bootstrap CI):

    | Estimator | outlier clouds | clean clouds | one-sided Fisher p |
    |---|---|---|---|
    | P | 0.065 [0.053, 0.078] (n = 3547) | 0.031 [0.025, 0.037] (n = 12880) | 2.3e-18 |
    | S | 0.085 [0.070, 0.101] | 0.048 [0.041, 0.057] | 5.0e-16 |
    | Ba | 0.017 [0.012, 0.022] | 0.015 [0.012, 0.019] | 0.220 |
    | Bb | 0.014 [0.011, 0.018] | 0.035 [0.029, 0.041] | 1.000 |

  - **Decision:** outliers roughly double the false positives of the universal-null estimators (P, S), while the tuned fixed threshold (Ba) is unaffected. P stays below the preregistered threshold of 0.10, so the DTM filtration is **not required**.
  - With factors 4 and 8 instead of 6 (post hoc), P's outlier false-positive rate ranges over 0.050–0.074, so the decision does not depend on the factor.
  - **Proxy check:** flagged fraction vs the generator's expected fraction of clouds with at least one injected outlier, per N bin:
    - N 5–12: 0.05 vs 0.09;
    - N 13–64: 0.15 vs 0.20;
    - N 65–254: 0.26 vs 0.28;
    - N 257–1020: 0.32 vs 0.29.

    The proxy misses outliers that land near the shape. In the largest clouds it also flags some extreme noise points, because there the flagged fraction exceeds the expected one.

<!-- BEGIN:exp1 -->
| estimator | macro exact accuracy | 95% CI | n clouds |
|---|---|---|---|
| P_alpha_universal | 0.618 | [0.610, 0.626] | 30114 |
| S_rips_universal | 0.660 | [0.651, 0.670] | 30114 |
| Ba_fixed_pi | 0.714 | [0.703, 0.725] | 30114 |
| Bb_family_implied | 0.812 | [0.807, 0.816] | 30114 |
| Bc_majority | 0.555 | [0.553, 0.557] | 30114 |
| MC_gaussian3d (subset) | 0.594 | [0.561, 0.629] | 2427 |
| P_alpha_universal (subset) | 0.615 | [0.588, 0.644] | 2427 |
| S_rips_universal (subset) | 0.674 | [0.640, 0.703] | 2427 |

Paired differences (primary minus comparator):

| comparison | difference | 95% CI |
|---|---|---|
| P - S_rips_universal | -0.042 | [-0.051, -0.033] |
| P - Ba_fixed_pi | -0.096 | [-0.108, -0.084] |
| P - Bb_family_implied | -0.194 | [-0.203, -0.185] |
| P - Bc_majority | 0.063 | [0.055, 0.071] |

False-positive rate (b1 >= 1 or b2 >= 1) on resolvable contractible clouds, by N-bin:

| estimator | N-bin 0 | N-bin 1 | N-bin 2 | N-bin 3 |
|---|---|---|---|---|
| P_alpha_universal | 0.019 | 0.039 | 0.054 | 0.038 |
| S_rips_universal | 0.003 | 0.051 | 0.084 | 0.077 |
| Ba_fixed_pi | 0.000 | 5.0e-04 | 0.010 | 0.047 |
| Bb_family_implied | 0.110 | 0.020 | 0.004 | 0.003 |
| Bc_majority | 0.000 | 0.000 | 0.000 | 0.000 |

Universal-null calibration on blobs (FWER = fraction with any significant alpha H1 bar):

| N-bin | fwer_alpha_universal | ks_uniform_D | n_pvalues |
|---|---|---|---|
| 0 | 0.003 | 0.118 | 1133.000 |
| 1 | 0.003 | 0.074 | 12182.000 |
| 2 | 0.000 | 0.048 | 77109.000 |
| 3 | 0.000 | 0.035 | 444404.000 |

Per-family exact accuracy (resolvable clouds):

| family | P_alpha_universal | S_rips_universal | Ba_fixed_pi | Bb_family_implied | Bc_majority |
|---|---|---|---|---|---|
| arc | 0.651 | 0.753 | 0.788 | 0.576 | 0.582 |
| blob | 0.990 | 0.986 | 0.998 | 0.945 | 1.000 |
| clusters | 0.340 | 0.339 | 0.341 | 0.328 | 0.000 |
| cone | 0.007 | 0.334 | 0.534 | 0.943 | 0.000 |
| disc | 0.974 | 0.963 | 0.985 | 0.954 | 1.000 |
| ellipse | 0.257 | 0.546 | 0.509 | 0.990 | 0.000 |
| helix | 0.783 | 0.654 | 0.861 | 0.987 | 1.000 |
| line | 0.953 | 0.952 | 0.963 | 0.991 | 1.000 |
| paraboloid | 0.968 | 0.956 | 0.984 | 0.911 | 1.000 |
| polytope | 0.500 | 0.500 | 0.500 | 0.351 | 0.000 |
| ringing | 0.928 | 0.927 | 0.947 | 0.970 | 1.000 |
| sphere | 0.687 | 0.675 | 0.761 | 0.609 | 0.638 |
| torus | 0.000 | 0.000 | 0.111 | 1.000 | 0.000 |

Resolvable fraction of test clouds: 0.772.
<!-- END:exp1 -->

![estimators](../docs/figures/fig_exp1_estimators.png)
![by rho](../docs/figures/fig_exp1_by_rho.png)
![outliers](../docs/figures/fig_exp1_outliers.png)

## Interpretation

- **Where persistent homology adds information beyond the family label:** whenever the label does not fix the topology. The fixed-threshold estimator Ba is quoted here:
  - open vs closed arcs: 0.79 vs 0.58;
  - caps vs full spheres: 0.76 vs 0.61.
- **The preregistered estimator P is not better than the family label,** even on well-resolved clouds.
- **Where it loses:** wherever the label fixes the topology but the hole is thin or two-dimensional. Ellipses: 0.51 vs 0.99. Tori: 0.11 vs 1.00. Frusta: 0.53 vs 0.94.
- **The alpha-complex universal null is calibrated but conservative.** Its family-wise error on blobs is about 0. This is why it loses to a tuned threshold (deviation D1).

## Learnings

- At N ≤ 1024 the universal null of Bobrowski & Skraba is too conservative for alpha complexes in ℝ³. A Rips complex (A = 1) or a tuned threshold is more powerful.
- Resolvability (ρ_A) is the main determinant of accuracy, so reporting accuracy against ρ_A is essential.
- The tuned b0 rule chose the largest τ in the grid (deviation note A1). The clusters family is the weakest b0 case.
