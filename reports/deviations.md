# Deviations from the preregistration and the plan

Each entry is dated and states what changed, why, and whether it was decided before or after seeing results.

## D1 (2026-11-15, before any result on the synthetic test set or on real data): add a Rips-H1 universal-null estimator

**What I found.** While writing the unit tests, I checked the universal null of [Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2) on toy clouds (`tests/test_tda.py`).
- **Calibration holds.** On 1,000 uniform points in the unit cube:
  - the standard deviation of log log π of noise bars is about 2.4 for alpha complexes (A = ½ predicts 2.57);
  - it is about 1.2 for Rips (A = 1 predicts 1.28).
- **But alpha with A = ½ is very conservative at our sample sizes.** A noisy circle (N = 400, σ = 0.03, top π = 18) is not significant after Bonferroni over its 442 H1 bars. The p-value is 2.5·10⁻⁴, against a threshold of 1.1·10⁻⁴.
- **Rips H1 with A = 1** detects the same circle and nothing in Gaussian blobs.

**Change.**
- I add the Rips-H1 universal-null count as a **secondary estimator of b1**, computed on the same normalised 3D cloud with ripser and A = 1. It is used in Exp1, alongside the preregistered estimators, and in Exp2, descriptively.
- The preregistered primary estimator for H5 (alpha, A = ½) is unchanged.
- The primary real-data criterion is unchanged: the design-matched Monte Carlo null on the maximum π, which does not use A.

**Implementation detail (not a deviation).** Degenerate inputs, such as co-circular points like a regular 12-gon, make GUDHI return bars with death equal to birth. These are dropped. They had π = 1, so they were already excluded from the universal null and its Bonferroni count.

## D2 (2026-11-15, before any Method A result was computed): exact point-to-shape distances for the noise scale ν

**Preregistered:** ν uses the fitted shape's stored dense samples (viz `shape`: 400 samples for curves, 30×30 for surfaces) for real clouds, and `gt_dense` (256 samples for curves, 24×24 for surfaces) for synthetic clouds.

**Problem:** these grids are coarse. A noise-free point on a 24×24 sphere grid can lie about 0.1 RMS units from the nearest sample, so the noise term of ν would be biased upwards.

**Change.** Both terms of ν now come from the shape's exact parametrisation:
- the noise term from point-to-shape distances on a 4,096-point curve grid or a 256×256 surface grid;
- the coverage term from 2,000 area-uniform samples.

The numpy parametrisation is tested to reproduce the source's fitted shapes to within 1e-3 of the cloud RMS (`tests/test_analytic.py`). Point sets keep their own points (cluster centroids, polytope vertices). The definition of ν is unchanged; only its numerical approximation is better.

## D3 (2026-11-15, before any Method B result on real data): what "no circular coordinate" means

DREiMac with `standard_range=True` (preregistered) raises "The cohomology class selected is too short" when the most persistent class does not outlive twice the landmark cover radius. In that case there is no loop that is non-trivial in the complex DREiMac uses.

This case is now recorded as "no θ_B": alignment p = 1 and winding 0, so H1-B (b) and (c) fail. This follows the preregistered rule "a cyclic set with no loop counts as a failure". It was found in the power simulation (random arrangements), before any real-data θ_B was computed.

## P1 (plan-level, 2026-11-15, before Exp1): dropped the "effective topology of `gt_dense` at r*" secondary ground truth

This item was in the plan but not in the preregistration.

**Why it was dropped:** the stored `gt_dense` grids (24×24 for surfaces) create spurious long H1 bars in alpha complexes. They come from anisotropic grid cells: π ≈ 4 on a torus grid, and ≈ 17 near the poles of a sphere grid (`tests/test_analytic.py`). An effective topology computed from them would be unreliable.

**What replaces it:** the primary ground truth (exact Method A topology of the ground-truth parameters, with resolvability ρ_A) and the reported accuracy as a function of ρ_A already cover multi-scale and borderline cases.

## D4 (2026-11-15): simulated steering postponed; fitted-shape coordinate check added (exploratory)

**What the author asked for:**
- Postpone the simulated steering of amendment A2, step 1, entirely. The code is in `src/neurotopo/steering/offline.py` and `experiments/exp6_sim.py`; it was not run, and the phase is removed from `run.py all`.
- Instead, check where the original labelled points lie on their fitted shapes.
- Model inference (A2, step 2) stays postponed.

**Added: phase `coords`** (`experiments/coords_check.py`; exploratory and descriptive; uses only stored data). Every point gets its intrinsic coordinates on its fitted shape. The phase then reports:
- circular alignment with the concept phases, for angular coordinates;
- Spearman correlation with the value or concept index, for linear coordinates;
- NMI and ARI with the concepts, for cluster and vertex assignments.

It also checks the prompt offset "k days from" for weekdays and months, and saturation and lightness for colours, both recovered from the source's row order and labels.

**Post hoc, flagged as such:** the harmonic content of the axial position of helix fits of cyclic concepts. It was added after seeing that the months' axial position is non-monotone in the month index.

## D5 (2026-11-15, after the Exp3 results): post hoc θ_B with DREiMac `standard_range=False`

**Observation.**
- With the preregistered `standard_range=True`, DREiMac builds a circular coordinate only for a Rips class whose death is at least twice its birth. This is the condition that guarantees the class is non-trivial in the Čech complex (`EMCoords.get_cover_radius` in DREiMac 0.3.2).
- The weekday, month and days_time loops are weaker than that, so H1-B (b)–(d) failed there before any alignment could be computed. For months this happened even though the alpha-complex loop is significant under the cluster-centre null.
- No dataset has a qualifying class in the top-10 PCs.

**Post hoc analysis** (phase `exp3posthoc`, `results/exp3/posthoc_relaxed_range.json`). θ_B is recomputed with `standard_range=False`, which guarantees the class only in the Rips complex, as DREiMac's own error message suggests. This is done in 3D and in the top-10 PCs, and the alignment tests are repeated.
- It is reported as exploratory.
- **It does not change any preregistered verdict.**
