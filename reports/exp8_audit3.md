# Exp8: third independent audit (post hoc, deviation D9)

Date: 2026-11-15. Author: Libor "Burny" Burian.
- Every number is generated from `results/exp8_audit3/` and earlier results by `run.py report`.
- Code: `src/neurotopo/experiments/exp8_null_specificity.py` (`run.py audit3`).
- No model inference and no training. Everything uses stored activations, stored results, the stored synthetic test set, and CPU simulations of the null models.

## Why this audit

A third audit ignored the earlier audits (D6, D8). It re-read the code, the preregistration and the results, and recomputed quantities from stored data.

**What it confirmed.**
- **Verdicts.** No preregistered verdict is wrong: H1-A 0/3, H1-B 0/3, H3 fail, H4 0.50, H2 not falsified.
- **Cloud reconstruction.** The clouds are rebuilt from raw activations, and the run aborts if they deviate from the source.
- **Null samplers.** The cluster-centre and Gaussian samplers implement preregistration §4.3. The p-values are max-statistic Monte Carlo p-values.
- **Persistence ratios.** Alpha radii are square roots of GUDHI's filtration values. In the universal null, squared or unsquared filtration values give the same result (an additive log 2 cancels in ℓ).
- **Permutation tests.** The tests are exact for 7 concepts and use 99,999 Monte Carlo permutations otherwise. The residues use a max-over-frequency null that permutes residues. Holm and Benjamini–Hochberg are correct.
- **The D8 localisation rule is an exact sufficient condition.** When the balls of different concepts are disjoint, the union of balls is a disjoint union of per-concept unions, so its persistence splits too (alpha has the persistence of Čech).
- **The closing step** (Sunday → Monday, December → January, last day → first) is the largest of all steps for weekdays, months and days_time.

**What it found:**
1. **The loop test does not test for a hole** (substantive). Both Monte Carlo nulls are Gaussian. On synthetic clouds of known topology, the design-(b) null flags loops on 0.17 of hole-free clouds. The instrument validated on 39,000 clouds (P) is not the test used for the real loops.
2. **Instrument reporting.** Exact-vector accuracy hid that P finds few true holes (0.16).
3. **Minor wording and statistics issues:**
   - the colour confounder, its statistic, and the weekday caption;
   - the Exp1 family comparison;
   - two power-simulation numbers.

**No preregistered verdict changes.** One hypothesis of this audit was refuted (section 7).

## Analysis plan (fixed before the new computations ran)

- **Metric:** the fraction of clouds with at least one significant H1 bar.
  - On clouds with true b1 ≥ 1 this is the sensitivity. On clouds with true b1 = 0 it is the false-loop rate.
  - For the simulated concept centres it is the loop-pass rate of condition (a), with exact binomial CIs.
- **Decision rule (cluster-centre null).** For each design (7 and 12 clusters), take the simulated cell nearest the real set's top-3 variance share:
  - "hole-specific" if every hole-free arrangement (cap, grid) passes with a 95% upper bound ≤ 0.10;
  - "not hole-specific" if any lower bound is > 0.05;
  - otherwise "undetermined".
- **Reported whatever the outcome:** how often hole-free centre arrangements reach the real months' persistence ratio.

## 1. The loop test on synthetic clouds of known topology

Exp1 ran a 3D matched-Gaussian Monte Carlo null ("MC", 99 draws) on the 3,120-cloud baseline subset, but reported only its exact-vector accuracy (0.594).

On a rank-3 cloud this is the same sampler as the real data's design-(b) null:
- `GaussianNull` draws Z X_c / √(N−1), i.e. rows from N(0, cov X).
- Exp1 draws N(0, cov X) directly.
- After RMS normalisation the two are equal in distribution.
- Checked on 20 stored paraboloid clouds: the median |q95 ratio − 1| is 0.012 (maximum 0.036), and a two-sample KS test rejects in 0.05 of clouds, the rate expected by chance.

Results on resolvable clouds, with cluster-bootstrap 95% CIs over generator chunks:

| Estimator | true holes detected | hole-free clouds flagged |
|---|---|---|
| MC (design-(b) null; subset) | 0.845 [0.774, 0.909] (n = 445) | **0.174** [0.126, 0.225] (n = 1982) |
| P (preregistered; all) | 0.162 [0.132, 0.194] | 0.019 [0.015, 0.023] |
| S (Rips universal; all) | 0.452 [0.415, 0.491] | 0.038 [0.032, 0.043] |
| Ba (tuned threshold; all) | 0.566 [0.524, 0.609] | 0.016 [0.013, 0.018] |

- **Which hole-free shapes MC flags:**
  - blobs 0.06 (its own model, so calibrated), lines 0.04, open curves 0.00;
  - open arcs 0.08, polytopes 0.10, discs 0.19, helices 0.20;
  - **paraboloids 0.37, spheres and caps 0.73.**
  - The false loops come from surfaces and helices, not from open curves or open arcs. Closed arcs (true b1 = 1) are detected in 0.82.
- **It rises with N:** 0.11 in the smallest N bin, 0.26 in the largest.
- **Outliers do not cause it:** 0.21 [0.14, 0.28] on outlier clouds vs 0.16 [0.12, 0.21] on clean ones (D7 proxy).
- **The false loops are not small.** The flagged hole-free clouds have top π 1.39–2.81 (10th–90th percentile; median 2.17). The real loops of residues (2.45), days_time (2.01) and months (1.72) fall inside that range; only colours (5.02) is far above it. N differs between these clouds, so this comparison is a rough guide.
- **Why.** A Gaussian null matches the covariance, not the intrinsic dimension or the shape.
  - Noise cycles on a 2D surface live longer than in a 3D blob of the same spread. A helix's adjacent turns can enclose a tube-like loop at scales above the pitch.
  - The largest multiplicative persistence of noise cycles grows with the number of points as (log n / log log n)^{1/k}, with constants that depend on the dimension ([Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232)). That is consistent with the rise with N and the dependence on shape. The theorem is for uniform samples in a cube, so it explains the pattern rather than proving it for these clouds.
- **Why it was missed.** H5 scored exact (b0, b1, b2) vectors, which mix all three Betti numbers. The real-data question is narrower: is there a loop?
  - P, the preregistered estimator, rarely finds one (0.16 of true holes; cones 0.00, tori 0.00, ellipses 0.29).
  - The real-data loop test (MC) finds most true holes but is not specific.

## 2. The cluster-centre null on hole-free concept centres

Months, weekdays, days_time and colours use the cluster-centre null (design a): concept means are redrawn from a Gaussian with their covariance, and residuals are kept. Is it fooled by evenly spread centres without a hole?

**Design.** The corrected power simulation (power2, D6), with five arrangements of the k concept centres in 3D:
- a ring (positive control);
- an open 300° arc;
- a hemisphere cap (evenly spread, Fibonacci lattice);
- a planar lattice (7: a centred hexagon; 12: 3 × 4);
- Gaussian centres (the null's own model).

Other settings:
- 20 dimensions of random offsets, and isotropic within-concept noise in ℝ⁴⁰⁹⁶.
- Between-concept share fixed to the real set's value. Arrangement share 0.2–0.6.
- 40 replicates per cell, 199 null draws.

The tables are at the end of this report. At the cell nearest the real top-3 share:

| design | ring | open arc | cap | lattice | Gaussian | verdict (pre-specified) |
|---|---|---|---|---|---|---|
| 7 clusters (weekdays-like; top-3 0.648 vs real 0.659) | 4/40 | 12/40 | 2/40 [0.01, 0.17] | 5/40 [0.04, 0.27] | 1/40 | undetermined |
| 12 clusters (months-like; top-3 0.550 vs real 0.549) | 5/40 | 6/40 | 4/40 [0.03, 0.24] | 1/40 [0.00, 0.13] | 1/40 | undetermined |

- **Pre-specified verdict: undetermined for both designs.** At the real sets' variance structure, rings themselves rarely pass, so nothing is told apart there.
- **Across all cells:**
  - Hole-free caps and lattices pass at most 0.125 (7 clusters) and 0.100 (12 clusters).
  - Rings and open arcs pass in up to 1.00 of replicates when the arrangement carries more variance.
  - So the cluster-centre null is far more specific to loops than the design-(b) null, but it does not separate rings from nearly closed arcs (as power2 already showed).
- **Months.** The real months' loop (π = 1.72) is reached by 0 of 320 hole-free cap and lattice replicates over all cells, and by 48 of 160 rings and 35 of 160 open arcs. So the months' loop is unlikely to come from evenly spread hole-free centres; a ring or a nearly closed arc remains.
- **Caveat.** The simulated clusters are tighter than the real ones (as in power2), and only two hole-free arrangements were simulated.

## 3. What this means per dataset

- **Colours.** The loop (π = 5.02, cluster-centre null) is far beyond the false-loop range of section 1, the 36 hue centres alone have π = 4.33, and hue winds once in the preregistered θ_B. **Stands,** with the stimulus confounder of D8.
- **Residues mod 113.** The loop test alone (π = 2.45, design b) is inside the false-loop range, so it is not evidence of a hole by itself. The residues go around it once at frequency 20 (R = 0.97, Holm p = 6.0e-05), against a null that shuffles residues. That matches the known Fourier circles of grokked networks. **Stands,** on the traversal.
- **Months.** A loop through the month centres (π = 1.72). Section 2 makes hole-free centres an unlikely source of it. But ring vs nearly closed arc is undecided, and the months go around it only post hoc. **"Ring: suggestive"** (the README and figure said "ring: yes").
- **Days with times, weekdays:** unchanged. There is no ring of days.
- **Controls.** Unchanged. Open curves (ordinal sets, random processes) are almost never flagged even by the design-(b) null (open curves 0.00, lines 0.04).
- **Exploratory loops in small sets** (toy-model polytopes, the 12 month means): read them with section 1 in mind. Polytopes are flagged 0.10 of the time.

## 4. Weekday centres in other projections

- The weekdays' third PC carries almost the same variance as the fourth (ratio 1.09), so the top-3 view could depend on an arbitrary axis.
- It does not. The 7 day centres have π = 1.19 in the cloud's PC1–PC2 plane, with Sunday → Monday 2.5× the median step. They have 1.05 in 3D, and at most 1.04 in their own top-3 to top-6 PCs (Rips).
- The flat picture looks round, but even there the loop is weak. A regular 7-gon gives 2.30.
- The month centres keep their loop in their own top-2 (1.55) and top-3 (1.57) PCs and lose it by the top-5 (1.01).

## 5. The colour confounder: wording and statistic

- **Wording.** The model reads hex codes, not RGB vectors. The hole around the grey axis belongs to the stimulus design (HLS with saturation ≥ 0.4), not literally to "the input". The accurate statement: any continuous encoding of the stimulus colour would have this loop, so the loop does not show a hue circle beyond the stimuli's.
- **Statistic.** "The 36 hue means wind once around the RGB loop" uses their angle in PC1–PC2 (R = 0.70), not θ_B. DREiMac builds no usable coordinate on the RGB cloud: no coordinate (preregistered), R = 0.03, winding 0 (relaxed). The RGB loop is the strongest in the study (alpha π = 8.01), but 200 landmarks raise its Rips birth. So "no coordinate" in condition (b) cannot be read as "no loop".
- **Comparing persistence.** The D8 text called the activation loop "weaker than the input's" (0.63 of its π). One cloud is 3D by construction and the other a projection of 4,096 dimensions, so that ratio is not a measure of information loss. The sentence is removed.

## 6. Exp1: the family comparison

The README listed the families where the tuned persistence baseline beats the family label (arcs, spheres) and where it loses (ellipses, tori). It omitted three families:
- cones (0.53 vs 0.94) and helices (0.86 vs 0.99), where the label wins;
- polytopes (0.50 vs 0.35), where persistence wins.

All are now listed.

## 7. A refuted hypothesis: the dense-check tori

- **Hypothesis.** Exp0's dense check misses the void of 3 ground-truth tori. The audit suspected the counting cut (bars born above margin/4), which would fail for fat tori whose margin is 2(R − r).
- **Result.** Refuted. The margin of all three is set by 2r. The voids are born at 0.54–0.60 of the cut (0 above it), but their persistence ratio is 3.4–3.7, below the counting threshold of 4.
- This is what the Exp0 report already said: these tori need more samples.
- One remaining diagnostic detail: `margin_over_spacing` estimates the sample spacing on the first 2,000 of the 10,000 points, which overstates the spacing.

## 8. Minor fixes

- "A ring passes the loop test in 0.15 of 40 replicates" now reads "in 6 of 40 replicates (0.15)".
- "Random placements pass at most 0.07" was 0.075 rounded down. It now shows 0.075.

## Tables

<!-- BEGIN:audit3 -->
Loop detection on synthetic clouds of known topology (resolvable clouds; >= 1 significant H1 bar; cluster-bootstrap 95% CIs over generator chunks):

| estimator | clouds | hole sensitivity | sens. 95% CI | n (true b1 >= 1) | false-loop rate | FPR 95% CI | n (true b1 = 0) |
|---|---|---|---|---|---|---|---|
| P | all | 0.162 | [0.132, 0.194] | 5342 | 0.019 | [0.015, 0.023] | 24772 |
| P | subset | 0.146 | [0.058, 0.246] | 445 | 0.021 | [0.011, 0.034] | 1982 |
| S | all | 0.452 | [0.415, 0.491] | 5342 | 0.038 | [0.032, 0.043] | 24772 |
| S | subset | 0.501 | [0.384, 0.616] | 445 | 0.040 | [0.025, 0.058] | 1982 |
| Ba | all | 0.566 | [0.524, 0.609] | 5342 | 0.016 | [0.013, 0.018] | 24772 |
| Ba | subset | 0.560 | [0.425, 0.690] | 445 | 0.013 | [0.006, 0.021] | 1982 |
| MC | subset | 0.845 | [0.774, 0.909] | 445 | 0.174 | [0.126, 0.225] | 1982 |

Fraction of clouds with >= 1 significant H1 bar, per family (resolvable clouds of the 3,120-cloud subset; true_b1 = 0 rows are false loops):

| family | true_b1 | Ba | MC | P | S | n |
|---|---|---|---|---|---|---|
| arc | 0 | 0.061 | 0.078 | 0.009 | 0.113 | 115 |
| arc | 1 | 0.565 | 0.815 | 0.174 | 0.565 | 92 |
| blob | 0 | 0.000 | 0.062 | 0.004 | 0.004 | 240 |
| clusters | 0 | 0.000 | 0.027 | 0.007 | 0.007 | 150 |
| cone | 1 | 0.564 | 0.921 | 0.000 | 0.495 | 101 |
| disc | 0 | 0.013 | 0.188 | 0.013 | 0.025 | 240 |
| ellipse | 1 | 0.532 | 0.766 | 0.287 | 0.632 | 171 |
| helix | 0 | 0.078 | 0.203 | 0.141 | 0.258 | 128 |
| line | 0 | 0.000 | 0.038 | 0.017 | 0.008 | 238 |
| paraboloid | 0 | 0.008 | 0.371 | 0.013 | 0.033 | 240 |
| polytope | 0 | 0.000 | 0.104 | 0.009 | 0.030 | 231 |
| ringing | 0 | 0.000 | 0.000 | 0.030 | 0.013 | 230 |
| sphere | 0 | 0.024 | 0.729 | 0.006 | 0.029 | 170 |
| torus | 2 | 0.605 | 0.951 | 0.000 | 0.160 | 81 |

Cluster-centre null on concept centres in five arrangements (cell nearest the real top-3 share; 40 replicates; exact 95% CIs):

| design | arrangement | loop pass | 95% CI | max over cells | median top pi | share with pi >= real | verdict (cap, grid) |
|---|---|---|---|---|---|---|---|
| 7 clusters (weekdays-like) | ring | 0.100 | [0.028, 0.237] | 1.000 | 1.217 | 0.100 | undetermined |
| 7 clusters (weekdays-like) | arc300 | 0.300 | [0.166, 0.465] | 1.000 | 1.250 | 0.250 | undetermined |
| 7 clusters (weekdays-like) | cap | 0.050 | [0.006, 0.169] | 0.125 | 1.214 | 0.050 | undetermined |
| 7 clusters (weekdays-like) | grid | 0.125 | [0.042, 0.268] | 0.125 | 1.222 | 0.150 | undetermined |
| 7 clusters (weekdays-like) | random | 0.025 | [6.3e-04, 0.132] | 0.075 | 1.159 | 0.025 | undetermined |
| 12 clusters (months-like) | ring | 0.125 | [0.042, 0.268] | 1.000 | 1.394 | 0.025 | undetermined |
| 12 clusters (months-like) | arc300 | 0.150 | [0.057, 0.298] | 0.925 | 1.375 | 0.000 | undetermined |
| 12 clusters (months-like) | cap | 0.100 | [0.028, 0.237] | 0.100 | 1.344 | 0.000 | undetermined |
| 12 clusters (months-like) | grid | 0.025 | [6.3e-04, 0.132] | 0.075 | 1.294 | 0.000 | undetermined |
| 12 clusters (months-like) | random | 0.025 | [6.3e-04, 0.132] | 0.075 | 1.318 | 0.000 | undetermined |

Largest H1 pi of the concept centres in other projections:

| dataset | cloud PC1-PC2 (alpha) | cloud top-3 (alpha) | own top-2 (Rips) | own top-3 (Rips) | own top-4 (Rips) | own top-5 (Rips) | own top-6 (Rips) |
|---|---|---|---|---|---|---|---|
| weekdays | 1.195 | 1.052 | 1.175 | 1.002 | 1.033 | 1.037 | 1.030 |
| months | 1.634 | 1.713 | 1.553 | 1.568 | 1.316 | 1.006 | 1.016 |
| days_time | 1.398 | 1.108 | 1.332 | 1.075 | 1.087 | 1.074 | 1.093 |

Dense-check tori without a counted void:

| id | R | r | margin | margin_term | cut | void_birth | void_death | void_pi | born_above_cut |
|---|---|---|---|---|---|---|---|---|---|
| 2-1-3050 | 0.978 | 0.175 | 0.351 | 2r | 0.088 | 0.052 | 0.175 | 3.359 | no |
| 2-1-3200 | 0.950 | 0.193 | 0.387 | 2r | 0.097 | 0.052 | 0.194 | 3.732 | no |
| 3-0-3000 | 0.987 | 0.202 | 0.403 | 2r | 0.101 | 0.054 | 0.202 | 3.738 | no |
<!-- END:audit3 -->

## What changed in the documentation

- **README:**
  - The two questions now say "loop" and define "ring" as a loop that the concept also goes around.
  - Months: "ring: suggestive". Residues: the ring rests on the traversal.
  - Instrument check: MC null false-loop rate.
  - Exp1 family comparison complete.
  - Colour confounder wording; weekday caption; power wording.
  - New to-do: a hole-specific null.
- **Example figure:** "ring: yes" only where the concept goes around the loop in the preregistered analysis. The months panel now reads "loop: yes; ring: suggestive".
- **Other documents:**
  - findings per dataset, summary, Exp1 report and paper: the same corrections;
  - the paper adds a specificity paragraph and a limitation;
  - deviations: D9.

## Learnings

- **Validate the deployed instrument, not a proxy.** The preregistration validated the universal-null estimator, while the real data were judged with a Monte Carlo null. The data to validate the latter already existed (Exp1's MC subset). Only its summary statistic, exact-vector accuracy, was the wrong one.
- **A matched-moment null tests the moments, not the topology.** "More persistent than a Gaussian with the same covariance" is a statement about non-Gaussianity. Surfaces, caps and helices are non-Gaussian without a hole. For clustered designs, nearly closed arcs of centres pass too (power2).
- **Independent evidence carries the claims.** For the shapes that survive (colours, residues), the claim rests on a test with a different null: concept labels shuffled over a fixed coordinate. That is what made the claims robust to this finding.
- **Check your own hypotheses too.** The torus explanation the audit expected was wrong. Recomputing took seconds.

## Limitations of this audit

- The synthetic check is the 3D analogue of design (b). The real one-point-per-value clouds are top-3 projections of 128–4,096 dimensions.
- The cluster-centre simulation uses tight clusters and two hole-free arrangements. A hole-specific null for real data (resampling hole-free fitted shapes at the cloud's noise) is left as future work.
- No model was run. The steering test (H6), which would settle whether the loops matter causally, stays postponed.
