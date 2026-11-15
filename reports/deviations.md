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

## D6 (2026-11-15, after the results): fixes and additions from the independent audit

An independent reviewer (a separate agent given the code and results, not the conclusions) found no errors in the core mathematics. It did find overclaims, methodological gaps and bugs. All of the following were decided after seeing the results and are labelled post hoc where they add analyses.

**Bugs fixed** (affected phases re-run):
- `cyclic_order_matches` returned True for a monotone arc, for example post hoc weekdays spanning 0.38 rad with winding 0. It now requires that the closed semantic cycle winds exactly once.
- In Exp3, variable matching used substring tests, so "day" also matched "time of day". It now uses exact names. No outcome changed.
- The DREiMac wrapper's `except Exception` hid an IndexError raised when a cloud has no H1 class at all. That case is now recorded as "no H1 class", and only DREiMac's "class too short" message is treated as "no usable loop". Any other error is raised.
- `pytest` at the repository root collected the submodule's torch-based tests. Added `testpaths = ["tests"]`.

**Analyses added (post hoc):**
- **Corrected power simulation (`run.py power2`).**
  - The preregistered simulation (A1) put all between-concept variance on the ring and spread the within-concept noise isotropically over 4,096 dimensions. Almost no noise reached the top-3 PCs, so rings were detected trivially. The simulation was also not swept over top-3 explained variance, as section 8 had promised.
  - The A1 claim that the grid "brackets the real sets" was wrong for months (0.914) and grokking (1.0). A1 also did not mention that open 300° arcs pass the full conjunction up to 25% of the time (k = 7, f_B = 0.3).
  - Version 2 draws concept centres as a ring plus random per-concept offsets in 20 further dimensions. f_B is fixed to the real value and the ring's variance share is swept so that the simulated top-3 explained variance covers the real one.
- **Top-10-PC loop test with a design-matched Monte Carlo null** (Exp5, 199 draws). "Only the colour loop persists beyond the top-3 PCs" previously rested on raw π, which is not comparable across dimensions without a null.
- **Exp1, well-resolved clouds (ρ_A ≥ 4).** The preregistered estimator P is now reported with a macro average, a cluster-bootstrap CI, paired differences against the family label and the fixed threshold, and per-family accuracies. The earlier text quoted the best baseline (Ba) as "persistent homology".
- **Benjamini–Hochberg q-values across the 44 loop and void tests** (Exp2, descriptive).
- **The preregistered (section 4.6) check that the DREiMac class overlaps the alpha H1 bar** is now reported.

**Claims rewritten:**
- No "holes appear exactly for the cyclic concepts" without listing the exceptions: weekdays have no loop; days_time has a loop the day does not travel around; the grokking random-init control has a borderline loop.
- No "helices are closed loops within noise". ρ_A < 1 means open vs closed is unresolvable, and for cluster designs low ρ_A is largely a property of the design.
- "Specificity holds" is reported together with its weakness: sensitivity is zero (H4 balanced accuracy 0.5), and the controls never approach the null threshold.
- The weekday "exact cyclic order" is reported as non-specific: 7 of 8 Gaussian-process helix controls reach the same minimum p with winding ±1.
- The alignment R and its permutation p measure *ordering*. Only |winding| = 1 carries the cyclic claim.

## D7 (2026-11-15, after the results, during the plan-completion check): the outlier false-positive rate behind the DTM conditional

Preregistration section 7 runs a DTM filtration ([Anai et al. 2019](https://arxiv.org/abs/1811.04757)) only "if the outlier false-positive rate in Exp1 exceeds 10%". Exp1 did not compute that rate, so the conditional was never evaluated.

**Problem:** the source generator gives 30% of clouds outliers, replacing up to 10% of their points with uniform draws from the padded bounding box (`neurogeom/data/nuisance.py::add_outliers`; `outlier_prob`, `outlier_frac_max` in the source `configs/base.yaml`). It does not store *which* clouds or points were replaced, and neither does the Hugging Face export.

**Proxy, fixed in `configs/base.yaml` (`outliers.far_factor = 6`) before the rate was computed:** a cloud is an "outlier cloud" if at least one point lies farther from the ground-truth shape (`gt_dense`) than 6 × the cloud's median point-to-shape distance (`tda.ground_truth.far_points`). The false-positive rate is computed exactly as in Exp1: any H1 or H2 feature on a resolvable cloud of an always-contractible family. It is reported for outlier clouds and for clean clouds, with cluster-bootstrap CIs over generator chunks. The decision uses the preregistered primary estimator P.

**Why this proxy:** Gaussian noise almost never puts a point 6 median distances from a curve. For a surface it is about 4σ, so large clouds of surfaces get a few false flags. Box outliers that land near the shape are missed, but those cannot create spurious holes anyway. The proxy is checked against the generator's expected fraction of clouds with at least one injected outlier, per N bin (reported in `reports/exp1_synthetic.md`).

**Post hoc addition:** a sensitivity check with factors 4 and 8, to show the decision does not hinge on the factor.

**Outcome and code:**
- Outcome: see `reports/exp1_synthetic.md`. The DTM ablation was not triggered.
- Code: `run.py exp1outliers` (`experiments/exp1_synthetic.py::outlier_check`), results in `results/exp1/outliers.json`.

## D8 (2026-11-15, after the results): second independent audit

A second independent audit ignored the earlier audits. It re-read the code, the preregistration and the results, and recomputed key quantities from stored data. No model was run.

**Confirmed:** every preregistered verdict (H1-A, H1-B, H2, H3, H4) follows correctly from the rules. The design-matched nulls, permutation tests, Holm and Benjamini–Hochberg procedures are implemented correctly. There is no leakage.

**Found and fixed:**
- **Confounder.** The colour stimuli sample saturation ≥ 0.4 only, so their RGB values already have the hue loop, with hue winding once. The colour result shows that the model preserves its input's hue circle, not that it builds one.
- **Loops inside a cluster.** For prompt-template designs, the maximum-π statistic can be won by a loop inside one concept's cluster. The weekday and days-with-times loops are such loops: each dies before any two day clusters touch. The text that called them a weak ring or "a ring, but not the days' ring" was wrong. The post hoc days-with-times coordinate (D5) is built on a different, non-significant Rips class, so it did not test the significant loop.
- **Overclaims:**
  - months "a real ring" (the test cannot tell a ring from a nearly closed arc);
  - "the controls behaved" (the open-curve controls never came near the threshold);
  - residues "fragile" (the top PCA eigenvalues are nearly equal because W_E uses 5 Fourier frequencies);
  - "going around once separates the cyclic concepts" in 10D (only colours wind there);
  - "× chance" (it is × the null's 95th percentile).
- **Misdescriptions:**
  - The weekday power figure was the nearest grid cell, without a CI, from a simulation whose clusters are tighter than the real ones.
  - The ρ_A ≥ 4 Exp1 subset has no tori and is mostly hole-free blobs, discs and paraboloids, so it is not "shapes whose holes stand well above the noise".
  - The family-label baseline is in-distribution.
- **Preregistration adherence.** The descriptive closure ratio (section 5) was implemented but never reported. It is now reported.

**Analyses added (post hoc), phase `run.py audit`** (`experiments/exp7_audit.py`, `results/exp7_audit/`):
- the colour stimulus baseline;
- loop localisation for cluster designs, with an exact criterion: the bar dies at or below half the smallest distance between points of different concepts;
- the closure ratio;
- PCA eigenvalue shares and the grokking Fourier spectrum;
- subsample stability against a size-matched threshold;
- the overlap of the relaxed-range θ_B class with the significant alpha bar;
- exact binomial CIs for the power simulation.

Results: [exp7_audit.md](exp7_audit.md). The claims are rewritten in the README, the summary, the per-dataset findings, the Exp1/2/3/5 reports and the paper. The example figure no longer labels a loop inside one cluster as a ring.

**No preregistered verdict changes,** and no earlier result file is modified.

## P2 (plan-level): two planned unit tests superseded by the preregistration's definitions

- **"The margin is 0 exactly at the source's thresholds (arc extent_frac 0.98, sphere cap threshold, r_bot = 0, r = R)."**
  - The plan defined the arc margin as |extent_frac − 0.98| · 2πr.
  - The preregistration (section 3) instead defines every margin as a geometric distance to a change in topology: endpoint gap, cap-opening chord, min(r_bot, r_top), min(r, R − r). This avoids treating the source's 0.98 classification threshold as a topological boundary.
  - `tests/test_analytic.py` checks these margins, including margin 0 for an apex cone (r_bot = 0).
- **"An ambiguity flag near r*."** This belonged to the effective-topology ground truth at the scale r*, which was dropped (P1). Accuracy as a function of ρ_A replaces it.
