# Exp8: third independent audit (post hoc, deviation D9)

Date: 2026-11-15. Author: Libor "Burny" Burian.
- Every number is generated from `results/exp8_audit3/` and earlier results by `run.py report`.
- Code: `src/neurotopo/experiments/exp8_null_specificity.py` (`run.py audit3`).
- No model inference and no training. Everything uses stored activations, stored results, the stored synthetic test set, and CPU simulations of the null models.

## Why this audit

A third audit ignored the earlier audits (D6, D8). It re-read the code, the preregistration and the results, and recomputed quantities from stored data.

**What it confirmed.**
- **Verdicts.** No preregistered verdict is wrong: H1-A {{exp3.H1A}}/3, H1-B {{exp3.H1B}}/3, H3 {{exp3.H3.B}}, H4 {{exp3.H4.conj_B:2}}, H2 {{exp3.H2.B.falsified}}.
- **Cloud reconstruction.** The clouds are rebuilt from raw activations, and the run aborts if they deviate from the source.
- **Null samplers.** The cluster-centre and Gaussian samplers implement preregistration §4.3. The p-values are max-statistic Monte Carlo p-values.
- **Persistence ratios.** Alpha radii are square roots of GUDHI's filtration values. In the universal null, squared or unsquared filtration values give the same result (an additive log 2 cancels in ℓ).
- **Permutation tests.** The tests are exact for 7 concepts and use 99,999 Monte Carlo permutations otherwise. The residues use a max-over-frequency null that permutes residues. Holm and Benjamini–Hochberg are correct.
- **The D8 localisation rule is an exact sufficient condition.** When the balls of different concepts are disjoint, the union of balls is a disjoint union of per-concept unions, so its persistence splits too (alpha has the persistence of Čech).
- **The closing step** (Sunday → Monday, December → January, last day → first) is the largest of all steps for weekdays, months and days_time.

**What it found:**
1. **The loop test does not test for a hole** (substantive). Both Monte Carlo nulls are Gaussian. On synthetic clouds of known topology, the design-(b) null flags loops on {{audit3.mc.fpr:2}} of hole-free clouds. The instrument validated on 39,000 clouds (P) is not the test used for the real loops.
2. **Instrument reporting.** Exact-vector accuracy hid that P finds few true holes ({{audit3.P.sens:2}}).
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

Exp1 ran a 3D matched-Gaussian Monte Carlo null ("MC", 99 draws) on the 3,120-cloud baseline subset, but reported only its exact-vector accuracy ({{exp1.MC.acc:3}}).

On a rank-3 cloud this is the same sampler as the real data's design-(b) null:
- `GaussianNull` draws Z X_c / √(N−1), i.e. rows from N(0, cov X).
- Exp1 draws N(0, cov X) directly.
- After RMS normalisation the two are equal in distribution.
- Checked on {{audit3.eq.n}} stored paraboloid clouds: the median |q95 ratio − 1| is {{audit3.eq.median_rel:3}} (maximum {{audit3.eq.max_rel:3}}), and a two-sample KS test rejects in {{audit3.eq.ks_frac:2}} of clouds, the rate expected by chance.

Results on resolvable clouds, with cluster-bootstrap 95% CIs over generator chunks:

| Estimator | true holes detected | hole-free clouds flagged |
|---|---|---|
| MC (design-(b) null; subset) | {{audit3.mc.sens:3}} [{{audit3.mc.sens_lo:3}}, {{audit3.mc.sens_hi:3}}] (n = {{audit3.mc.n_hole}}) | **{{audit3.mc.fpr:3}}** [{{audit3.mc.fpr_lo:3}}, {{audit3.mc.fpr_hi:3}}] (n = {{audit3.mc.n_free}}) |
| P (preregistered; all) | {{audit3.P.sens:3}} [{{audit3.P.sens_lo:3}}, {{audit3.P.sens_hi:3}}] | {{audit3.P.fpr:3}} [{{audit3.P.fpr_lo:3}}, {{audit3.P.fpr_hi:3}}] |
| S (Rips universal; all) | {{audit3.S.sens:3}} [{{audit3.S.sens_lo:3}}, {{audit3.S.sens_hi:3}}] | {{audit3.S.fpr:3}} [{{audit3.S.fpr_lo:3}}, {{audit3.S.fpr_hi:3}}] |
| Ba (tuned threshold; all) | {{audit3.Ba.sens:3}} [{{audit3.Ba.sens_lo:3}}, {{audit3.Ba.sens_hi:3}}] | {{audit3.Ba.fpr:3}} [{{audit3.Ba.fpr_lo:3}}, {{audit3.Ba.fpr_hi:3}}] |

- **Which hole-free shapes MC flags:**
  - blobs {{audit3.mc.fam.blob_b0:2}} (its own model, so calibrated), lines {{audit3.mc.fam.line_b0:2}}, open curves {{audit3.mc.fam.ringing_b0:2}};
  - open arcs {{audit3.mc.fam.arc_b0:2}}, polytopes {{audit3.mc.fam.polytope_b0:2}}, discs {{audit3.mc.fam.disc_b0:2}}, helices {{audit3.mc.fam.helix_b0:2}};
  - **paraboloids {{audit3.mc.fam.paraboloid_b0:2}}, spheres and caps {{audit3.mc.fam.sphere_b0:2}}.**
  - The false loops come from surfaces and helices, not from open curves or open arcs. Closed arcs (true b1 = 1) are detected in {{audit3.mc.fam.arc_b1:2}}.
- **It rises with N:** {{audit3.mc.fpr_bin0:2}} in the smallest N bin, {{audit3.mc.fpr_bin3:2}} in the largest.
- **Outliers do not cause it:** {{audit3.mc.fpr_outlier:2}} [{{audit3.mc.fpr_outlier_lo:2}}, {{audit3.mc.fpr_outlier_hi:2}}] on outlier clouds vs {{audit3.mc.fpr_clean:2}} [{{audit3.mc.fpr_clean_lo:2}}, {{audit3.mc.fpr_clean_hi:2}}] on clean ones (D7 proxy).
- **The false loops are not small.** The flagged hole-free clouds have top π {{audit3.mc.flag_pi_q10:2}}–{{audit3.mc.flag_pi_q90:2}} (10th–90th percentile; median {{audit3.mc.flag_pi_q50:2}}). The real loops of residues ({{exp2.grok.top_pi1:2}}), days_time ({{exp2.daystime.top_pi1:2}}) and months ({{exp2.months.top_pi1:2}}) fall inside that range; only colours ({{exp2.colors.top_pi1:2}}) is far above it. N differs between these clouds, so this comparison is a rough guide.
- **Why.** A Gaussian null matches the covariance, not the intrinsic dimension or the shape.
  - Hypotheses consistent with the per-family rates (not tested directly): noise cycles on a 2D surface may live longer than in a 3D blob of the same spread, and a helix's adjacent turns can enclose a tube-like loop at scales above the pitch.
  - The largest multiplicative persistence of noise cycles grows with the number of points as (log n / log log n)^{1/k}, with constants that depend on the dimension ([Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232), Thm 3.1). That is consistent with the rise with N and the dependence on shape. The theorem is proven for a homogeneous Poisson process in the unit cube (densities bounded above and below on a compact support are only remarked), so it does not prove the pattern for these clouds.
- **Why it was missed.** H5 scored exact (b0, b1, b2) vectors, which mix all three Betti numbers. The real-data question is narrower: is there a loop?
  - P, the preregistered estimator, rarely finds one ({{audit3.P.sens:2}} of true holes; cones {{audit3.P.fam.cone_b1:2}}, tori {{audit3.P.fam.torus_b2:2}}, ellipses {{audit3.P.fam.ellipse_b1:2}}).
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
| 7 clusters (weekdays-like; top-3 {{audit3.k7.sim_top3:3}} vs real {{audit3.k7.real_top3:3}}) | {{audit3.k7.ring.n_pass}}/40 | {{audit3.k7.arc300.n_pass}}/40 | {{audit3.k7.cap.n_pass}}/40 [{{audit3.k7.cap.ci_lo:2}}, {{audit3.k7.cap.ci_hi:2}}] | {{audit3.k7.grid.n_pass}}/40 [{{audit3.k7.grid.ci_lo:2}}, {{audit3.k7.grid.ci_hi:2}}] | {{audit3.k7.random.n_pass}}/40 | {{audit3.k7.verdict}} |
| 12 clusters (months-like; top-3 {{audit3.k12.sim_top3:3}} vs real {{audit3.k12.real_top3:3}}) | {{audit3.k12.ring.n_pass}}/40 | {{audit3.k12.arc300.n_pass}}/40 | {{audit3.k12.cap.n_pass}}/40 [{{audit3.k12.cap.ci_lo:2}}, {{audit3.k12.cap.ci_hi:2}}] | {{audit3.k12.grid.n_pass}}/40 [{{audit3.k12.grid.ci_lo:2}}, {{audit3.k12.grid.ci_hi:2}}] | {{audit3.k12.random.n_pass}}/40 | {{audit3.k12.verdict}} |

- **Pre-specified verdict: undetermined for both designs.** At the real sets' variance structure, rings themselves rarely pass, so nothing is told apart there.
- **Across all cells:**
  - Hole-free caps and lattices pass at most {{audit3.k7.holefree_pass_max:3}} (7 clusters) and {{audit3.k12.holefree_pass_max:3}} (12 clusters).
  - Rings and open arcs pass in up to {{audit3.k12.ring.pass_max:2}} of replicates when the arrangement carries more variance.
  - So the cluster-centre null is far more specific to loops than the design-(b) null, but it does not separate rings from nearly closed arcs (as power2 already showed).
- **Months.** The real months' loop (π = {{audit3.k12.real_pi:2}}) is reached by {{audit3.k12.holefree_pi_ge_real_all}} of {{audit3.k12.holefree_n_all}} hole-free cap and lattice replicates over all cells, and by {{audit3.k12.ring.n_pi_ge_real_all}} of {{audit3.k12.ring.n_all}} rings and {{audit3.k12.arc300.n_pi_ge_real_all}} of {{audit3.k12.arc300.n_all}} open arcs. So the months' loop is unlikely to come from evenly spread hole-free centres; a ring or a nearly closed arc remains.
- **Caveat.** The simulated clusters are tighter than the real ones (as in power2), and only two hole-free arrangements were simulated.

## 3. What this means per dataset

- **Colours.** The loop (π = {{exp2.colors.top_pi1:2}}, cluster-centre null) is far beyond the false-loop range of section 1, the 36 hue centres alone have π = {{audit.loc.colors.means_pi:2}}, and hue winds once in the preregistered θ_B. **Stands,** with the stimulus confounder of D8.
- **Residues mod 113.** The loop test alone (π = {{exp2.grok.top_pi1:2}}, design b) is inside the false-loop range, so it is not evidence of a hole by itself. The residues go around it once at frequency {{exp3.grok.thetaB.k}} (R = {{exp3.grok.thetaB.R:2}}, Holm p = {{exp3.grok.B.holm}}), against a null that shuffles residues. That matches the known Fourier circles of grokked networks. **Stands,** on the traversal.
- **Months.** A loop through the month centres (π = {{exp2.months.top_pi1:2}}). Section 2 makes hole-free centres an unlikely source of it. But ring vs nearly closed arc is undecided, and the months go around it only post hoc. **"Ring: suggestive"** (the README and figure said "ring: yes").
- **Days with times, weekdays:** unchanged. There is no ring of days.
- **Controls.** Unchanged. Open curves (ordinal sets, random processes) are almost never flagged even by the design-(b) null (open curves {{audit3.mc.fam.ringing_b0:2}}, lines {{audit3.mc.fam.line_b0:2}}).
- **Exploratory loops in small sets** (toy-model polytopes, the 12 month means): read them with section 1 in mind. Polytopes are flagged {{audit3.mc.fam.polytope_b0:2}} of the time.

## 4. Weekday centres in other projections

- The weekdays' third PC carries almost the same variance as the fourth (ratio {{audit.pca.weekdays.gap34:2}}), so the top-3 view could depend on an arbitrary axis.
- It does not. The 7 day centres have π = {{audit3.cen.weekdays.pc12:2}} in the cloud's PC1–PC2 plane, with Sunday → Monday {{audit3.cen.weekdays.pc12_last:1}}× the median step. They have {{audit3.cen.weekdays.pc123:2}} in 3D, and at most {{audit3.cen.weekdays.own36_max:2}} in their own top-3 to top-6 PCs (Rips).
- The flat picture looks round, but even there the loop is weak. A regular 7-gon gives 2.30.
- The month centres keep their loop in their own top-2 ({{audit3.cen.months.own2:2}}) and top-3 ({{audit3.cen.months.own3:2}}) PCs and lose it by the top-5 ({{audit3.cen.months.own5:2}}).

## 5. The colour confounder: wording and statistic

- **Wording.** The model reads hex codes, not RGB vectors. The hole around the grey axis belongs to the stimulus design (HLS with saturation ≥ 0.4), not literally to "the input". The accurate statement: any continuous encoding of the stimulus colour would have this loop, so the loop does not show a hue circle beyond the stimuli's.
- **Statistic.** "The 36 hue means wind once around the RGB loop" uses their angle in PC1–PC2 (R = {{audit.rgb.means_R:2}}), not θ_B. DREiMac builds no usable coordinate on the RGB cloud: {{audit.rgb.thetaB.prereg}} (preregistered), {{audit.rgb.thetaB.relaxed}} (relaxed). The RGB loop is the strongest in the study (alpha π = {{audit.rgb.pi:2}}), but 200 landmarks raise its Rips birth. So "no coordinate" in condition (b) cannot be read as "no loop".
- **Comparing persistence.** The D8 text called the activation loop "weaker than the input's" ({{audit.llama_over_rgb:2}} of its π). One cloud is 3D by construction and the other a projection of 4,096 dimensions, so that ratio is not a measure of information loss. The sentence is removed.

## 6. Exp1: the family comparison

The README listed the families where the tuned persistence baseline beats the family label (arcs, spheres) and where it loses (ellipses, tori). It omitted three families:
- cones ({{exp1.Ba.cone:2}} vs {{exp1.Bb.cone:2}}) and helices ({{exp1.Ba.helix:2}} vs {{exp1.Bb.helix:2}}), where the label wins;
- polytopes ({{exp1.Ba.polytope:2}} vs {{exp1.Bb.polytope:2}}), where persistence wins.

All are now listed.

## 7. A refuted hypothesis: the dense-check tori

- **Hypothesis.** Exp0's dense check misses the void of {{audit3.tori.n}} ground-truth tori. The audit suspected the counting cut (bars born above margin/4), which would fail for fat tori whose margin is 2(R − r).
- **Result.** Refuted. The margin of all three is set by {{audit3.tori.terms}}. The voids are born at {{audit3.tori.birth_over_cut_min:2}}–{{audit3.tori.birth_over_cut_max:2}} of the cut ({{audit3.tori.n_above_cut}} above it), but their persistence ratio is {{audit3.tori.pi_min:1}}–{{audit3.tori.pi_max:1}}, below the counting threshold of 4.
- This is what the Exp0 report already said: these tori need more samples.
- One remaining diagnostic detail: `margin_over_spacing` estimates the sample spacing on the first 2,000 of the 10,000 points, which overstates the spacing.

## 8. Minor fixes

- "A ring passes the loop test in 0.15 of 40 replicates" now reads "in {{audit.power.k7.ring.nearest_count}} of 40 replicates ({{audit.power.k7.ring.nearest_loop:2}})".
- "Random placements pass at most 0.07" was 0.075 rounded down. It now shows {{power2.weekdays.random_loop_max:3}}.

## Tables

<!-- BEGIN:audit3 -->
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
