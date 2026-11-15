# Exp7: second independent audit (post hoc, deviation D8)

Date: 2026-11-15. Author: Libor "Burny" Burian. Every number is generated from `results/exp7_audit/` and earlier results by `run.py report`. Code: `src/neurotopo/experiments/exp7_audit.py` (`run.py audit`). No model inference and no training: everything uses stored activations, stored results, and the colour prompts' RGB values recomputed from the source's prompt builder.

## Why this audit

A second independent audit ignored earlier audits. It re-read the code, the preregistration, the deviations and the results, and recomputed key quantities from stored data.

**What it confirmed.**
- No preregistered verdict is wrong. H1-A 0/3 and H1-B 0/3 follow from the rules, as do H3 (fail), H4 (0.50) and H2 (not falsified).
- The design-matched nulls are implemented correctly:
  - Gaussian null: rows i.i.d. with the sample covariance, drawn through the Gram matrix;
  - cluster-centre null: concept means redrawn with their covariance, residuals kept;
  - every draw goes through the same top-k projection and normalisation as the data.
- The permutation tests, Holm and Benjamini–Hochberg are correct, and there is no leakage.

**What it found:**
1. A confounder in the strongest positive result (colours).
2. Two results described as "rings" that are loops inside a single concept's cluster (weekdays, days with times).
3. Overclaims about the months, the controls, the residues' "fragility" and the 10-dimensional winding.
4. A misdescribed power argument and a misdescribed Exp1 subset.
5. One preregistered descriptive statistic that was never reported (the closure ratio).

Each check below is post hoc and labelled as such. **No preregistered verdict changes.**

## 1. The colour loop is already in the stimuli

The source builds the 900 colour prompts from an HLS grid of 36 hues × saturation {0.4, …, 1.0} × lightness {0.25, …, 0.75} (`external/shape-fitting/src/neurogeom/realdata/llm_sets.py`, `bhalla_prompts`). Saturation ≥ 0.4 excludes the grey axis, so in RGB space the stimulus set surrounds a hole.

We ran Method B on the prompts' own RGB values (the hex-code digits), with concept = hue and the same cluster-centre null as for the activations (999 draws).

| cloud | top H1 π | null q95 | p | subsample stability |
|---|---|---|---|---|
| Llama-3.1-8B colour activations (Exp2) | 5.02 | 2.38 | 0.001 | 1.00 |
| the prompts' RGB values | 8.01 | 2.76 | 0.001 | 1.00 |

- The 36 hue means of the RGB values have a loop of π = 8.43.
- Their angles in PC1–PC2 wind once (winding -1, R = 0.70).
- θ_B on the RGB cloud:
  - preregistered setting: no coordinate;
  - relaxed setting: R = 0.03, winding 0. DREiMac's most persistent Rips class on this regular grid is not the hue loop, so the hue winding is read from the hue means instead.

**Reading.** The hue loop and its order are properties of the stimulus set. The activation loop is less persistent than the input's (0.63 of its π). The colour result therefore shows that layer 19 of Llama-3.1-8B *preserves* the hue circle of its input. It is not evidence that the model *constructs* a cyclic hue code.

Separating the two needs model inference, which is postponed:
- a random-init Llama on the same prompts;
- colour prompts by name instead of hex code.

## 2. Where the most persistent loop lives

For prompt-template designs the loop statistic is the largest persistence ratio over **all** H1 bars, so a small loop inside one concept's cluster can win it. The check is exact:
- Below half the smallest distance between points of different concepts, the balls of different concepts are disjoint.
- So a bar that dies at or below that radius is carried by one concept's points alone.

<!-- BEGIN:audit -->
Where the most persistent loop lives (normalised top-3 cloud, radius units):

| dataset | top bar birth | top bar death | clusters first touch (radius) | mean within-concept radius | loop inside one cluster | top pi of concept means alone | last->first step / median step |
|---|---|---|---|---|---|---|---|
| weekdays | 0.025 | 0.032 | 0.192 | 0.062 | yes | 1.052 | 1.946 |
| months | 0.502 | 0.861 | 0.171 | 0.032 | no | 1.713 | 1.919 |
| days_time | 0.022 | 0.045 | 0.160 | 0.124 | yes | 1.108 | 1.568 |
| colors | 0.087 | 0.438 | 0.008 | 0.426 | no | 4.327 | 1.797 |
| C3_weekdays_init | 0.022 | 0.024 | 0.140 | 0.075 | yes | 1.029 | 1.000 |
| C3_months_init | 0.091 | 0.130 | 0.023 | 0.095 | no | 1.069 | 0.384 |

Subsample stability (200 subsamples of 80%):

| dataset | null q95 (full N) | loop kept (full-N threshold) | null q95 (80% N) | loop kept (size-matched threshold) |
|---|---|---|---|---|
| colors | 2.379 | 1.000 | 2.347 | 1.000 |
| months | 1.443 | 0.900 | 1.426 | 0.925 |
| grokking_WE | 1.830 | 0.260 | 1.802 | 0.325 |
| days_time | 1.873 | 0.030 | 1.800 | 0.075 |

Corrected power simulation (power2), loop condition (a) with exact 95% CIs (40 replicates per cell):

| k | arrangement | real_top3 | nearest_top3 | loop pass (nearest cell) | 95% CI low | 95% CI high | loop pass (interpolated) | loop_min | loop_max |
|---|---|---|---|---|---|---|---|---|---|
| 7 | ring | 0.659 | 0.646 | 0.150 | 0.057 | 0.298 | 0.212 | 0.075 | 1.000 |
| 7 | arc300 | 0.659 | 0.646 | 0.150 | 0.057 | 0.298 | 0.212 | 0.050 | 0.975 |
| 7 | random | 0.659 | 0.654 | 0.050 | 0.006 | 0.169 | 0.052 | 0.000 | 0.075 |
| 12 | ring | 0.549 | 0.558 | 0.250 | 0.127 | 0.412 | 0.207 | 0.050 | 1.000 |
| 12 | arc300 | 0.549 | 0.558 | 0.200 | 0.091 | 0.356 | 0.160 | 0.025 | 0.925 |
| 12 | random | 0.549 | 0.562 | 0.050 | 0.006 | 0.169 | 0.050 | 0.050 | 0.075 |

Preregistered closure ratio (section 5; full activation space, cosine): d(last, first) / median d(c, c+1):

| id | variable | n | closure_ratio |
|---|---|---|---|
| weekdays | day of week | 7 | 2.231 |
| months | month | 12 | 1.704 |
| grokking_WE | residue mod 113 | 113 | 0.956 |
| days_time | day of week | 7 | 1.491 |
| colors | hue | 36 | 3.810 |
| gpt2_wpos | value in 7 bins | 7 | 2.203 |
| gpt2_wpos | value in 12 bins | 12 | 4.264 |
| counting | value in 7 bins | 7 | 16.154 |
| counting | value in 12 bins | 12 | 43.081 |
| pythia_counting | value in 7 bins | 7 | 33.507 |
| pythia_counting | value in 12 bins | 12 | 78.012 |
| years | value in 7 bins | 7 | 2.985 |
| years | value in 12 bins | 12 | 3.537 |
| temperature | value in 7 bins | 7 | 5.925 |
| temperature | value in 12 bins | 12 | 14.732 |
| age | value in 7 bins | 7 | 3.522 |
| age | value in 12 bins | 12 | 10.482 |
| C3_weekdays_init | day of week | 7 | 1.002 |
| C3_months_init | month | 12 | 0.961 |
| C3_grokking_WE_init | residue mod 113 | 113 | 0.921 |
| C1_gp_0 | value in 7 bins | 7 | 8.788 |
| C1_gp_0 | value in 12 bins | 12 | 24.686 |
| C1_gp_1 | value in 7 bins | 7 | 3.567 |
| C1_gp_1 | value in 12 bins | 12 | 8.787 |
| C1_gp_2 | value in 7 bins | 7 | 3.840 |
| C1_gp_2 | value in 12 bins | 12 | 9.865 |
| C1_gp_3 | value in 7 bins | 7 | 2.794 |
| C1_gp_3 | value in 12 bins | 12 | 6.425 |
| C1_gp_4 | value in 7 bins | 7 | 8.539 |
| C1_gp_4 | value in 12 bins | 12 | 23.084 |
| C1_gp_5 | value in 7 bins | 7 | 1.997 |
| C1_gp_5 | value in 12 bins | 12 | 4.063 |
| C1_gp_6 | value in 7 bins | 7 | 3.416 |
| C1_gp_6 | value in 12 bins | 12 | 8.201 |
| C1_gp_7 | value in 7 bins | 7 | 4.139 |
| C1_gp_7 | value in 12 bins | 12 | 10.858 |
| C1_gp_8 | value in 7 bins | 7 | 7.556 |
| C1_gp_8 | value in 12 bins | 12 | 20.714 |
| C1_gp_9 | value in 7 bins | 7 | 6.682 |
| C1_gp_9 | value in 12 bins | 12 | 17.741 |
| C1_walk_0 | value in 7 bins | 7 | 7.708 |
| C1_walk_0 | value in 12 bins | 12 | 14.411 |
| C1_walk_1 | value in 7 bins | 7 | 7.540 |
| C1_walk_1 | value in 12 bins | 12 | 15.215 |
| C1_walk_2 | value in 7 bins | 7 | 7.147 |
| C1_walk_2 | value in 12 bins | 12 | 13.266 |
| C1_walk_3 | value in 7 bins | 7 | 7.109 |
| C1_walk_3 | value in 12 bins | 12 | 14.881 |
| C1_walk_4 | value in 7 bins | 7 | 6.901 |
| C1_walk_4 | value in 12 bins | 12 | 12.256 |
| C1_walk_5 | value in 7 bins | 7 | 6.916 |
| C1_walk_5 | value in 12 bins | 12 | 13.522 |
| C1_walk_6 | value in 7 bins | 7 | 7.842 |
| C1_walk_6 | value in 12 bins | 12 | 15.141 |
| C1_walk_7 | value in 7 bins | 7 | 7.003 |
| C1_walk_7 | value in 12 bins | 12 | 13.372 |
| C1_walk_8 | value in 7 bins | 7 | 6.933 |
| C1_walk_8 | value in 12 bins | 12 | 13.756 |
| C1_walk_9 | value in 7 bins | 7 | 7.222 |
| C1_walk_9 | value in 12 bins | 12 | 13.849 |
<!-- END:audit -->

- **Weekdays.** The most persistent bar [0.025, 0.032] dies before any two day clusters touch (0.192). It is a loop inside one cluster.
  - The 7 day centres alone have π = 1.05; a regular 7-gon has 1/sin(π/7) ≈ 2.3.
  - The Sunday → Monday step is 1.95× the median step.
  - In the top-3 PCs there is no ring of days at all. The earlier text, "no stronger than the rings of randomly placed clusters", described this within-cluster loop.
- **Days with times.** The significant bar [0.022, 0.045] (p = 0.013, BH q = 0.082, stability 0.03) dies before clusters touch (0.160). It is a loop inside one day's cluster, not a ring.
  - The 7 day centres have π = 1.11.
  - The post hoc θ_B for this set (D5) is built on a different, non-significant Rips class [0.40, 0.43], which does not overlap the significant bar (overlap: no). So "the day does not go around the loop" did not test the significant loop.
- **Months.** The bar [0.50, 0.86] runs through the clusters (they first touch at 0.17). The 12 month centres alone show the same loop (π = 1.71).
  - The December → January step is the largest, 1.92× the median step.
  - In the power simulation at the months' top-3 variance, a ring passes the loop test in 0.21 and a 300° arc in 0.16 of replicates (interpolated). So the loop test cannot call this a closed ring rather than a nearly closed arc.
- **Colours.** The loop runs through the hue clusters. The clusters overlap: they first touch at 0.008.
- **Overlap of the relaxed-range θ_B class with the significant alpha bar** (the check of preregistration §4.6, extended to D5):
  - months yes, residues yes, colours yes;
  - weekdays no, days_time no.
  - Concepts with a constant coordinate (circular mean exactly 0) in the claimed records: months 0, residues 0, colours 3D 0, colours top-10 0.

## 3. Residues mod 113: an unstable view, not a weak circle

- The grokked W_E puts 0.90 of its variance on 5 Fourier frequencies over the residues (20, 21, 3, 15, 31), 0.16–0.22 each. This matches the "key frequencies" of [Nanda et al. 2023](https://arxiv.org/abs/2301.05217).
- The top six PCA eigenvalue shares are therefore nearly equal: 0.114, 0.111, 0.099, 0.096, 0.089, 0.086. The ratio of the 3rd to the 4th is 1.03.
  - When eigenvalues are this close, the top-3 subspace is not stable under resampling ([Yu, Wang & Samworth 2015](https://doi.org/10.1093/biomet/asv008)).
  - So different subsamples can show different mixes of frequency planes in their top 3 PCs.
- In 10 dimensions the 5 circles combine into one closed curve with no single dominant loop.
- So the low subsample stability (0.26; 0.33 against a size-matched threshold) and the failed top-10 check most likely reflect the multi-frequency code. They do not show a weak k = 20 circle.
- Exp2 also finds a second significant H1 bar for this set.

## 4. Controls that were never at risk

- The ordinal sets and the random walks and Gaussian processes are open curves. Their most persistent loops (π 1.00–1.63) lie far below their Gaussian nulls' 95th percentiles (1.79–2.16); the smallest p is 0.45.
- A matched Gaussian blob simply has more loops than a curve. "0 of 6" and "0 of 20" therefore say little about false positives on *nearly closed* curves, the relevant confound.
- The random-init networks are the informative calibration. One of 3 has p = 0.046, consistent with the nominal 5%.

## 5. Ten dimensions

In the top-10 PCs (post hoc relaxed θ_B) only colours wind once:
- colours: winding -1;
- months 0, residues 0, weekdays 0, days_time 0.

"Going around once separates the cyclic concepts" was too broad: in 10D it separates 1 of 5 cyclic sets, and that one is confounded by the input (section 1).

## 6. Subsample stability against a size-matched threshold

Exp2 compared subsamples of 80% of the points with the full-size null's 95th percentile. The table in section 2 also shows the threshold recomputed at the subsample size (5 subsamples × 199 draws, the dataset's own design). The conclusions do not change:
- colours and months stay robust;
- days_time stays unstable;
- residues stay below one half.

## 7. The power argument for weekdays

The README quoted "only 15%" for the simulated cell closest to the weekdays' top-3 variance. More precisely:
- That cell has top-3 share 0.646, against the real 0.659.
- It passes in 0.15 of 40 replicates, with an exact 95% CI of 0.06–0.30.
- Linear interpolation to the real share gives 0.21.
- The simulated within-cluster noise is isotropic in 4,096 dimensions, so the simulated clusters are much tighter in the top-3 PCs than the real weekday clusters.

Low power is real, but it does not explain the missing loop of day centres (section 2).

## 8. Exp1: the ρ_A ≥ 4 subset

The well-resolved subset (post hoc, D6) has 18454 clouds from 12 families:
- no torus reaches ρ_A ≥ 4;
- a fraction 0.49 are blobs, discs or paraboloids, which have infinite margin and no hole.

"Shapes whose holes stand well above the noise" was therefore wrong. The subset is "clouds far from a change of topology", and its macro average leaves out the family where the label is best.

The family label also comes from a fitter trained on the same 13-family generator, so it is scored in-distribution.

## 9. The preregistered closure ratio

Preregistration section 5 defines a descriptive closure ratio: d(last, first) / median d(c, c + 1) between concept means in the full activation space, with cosine distance. It was implemented but never reported. It is now reported in the table above.
- About 1 means the semantic cycle closes like a circle. Large values mean an open arc.
- Months: 1.70; weekdays 2.23; days_time 1.49; colours 3.81.
- Residues in natural order: 0.96. The natural order is not the representation's order, so this value says little.
- Ordinal sets in 7 bins: 2.20–33.51. Random-process controls in 7 bins: 2.00–8.79.
- **The ratio is a crude descriptive.**
  - Months lie below every ordinal set and every random-process control, which weakly favours a closing cycle.
  - But colours, whose loop is the clearest in the top-3 PCs, score 3.81, and the structureless random-init controls sit near 1 (weekdays init 1.00).
  - A single last-to-first distance in thousands of dimensions does not decide closure.

## What changed in the documentation

- README, summary, per-dataset findings, the Exp1/2/3 reports and the paper now say:
  - the colour loop is inherited from the stimuli;
  - weekdays and days with times have no ring of days;
  - months have a significant loop, not necessarily a closed ring;
  - the open-curve controls were never at risk, and the random-init networks give the calibration;
  - the residues' instability comes from near-equal PCA eigenvalues;
  - 10D winding holds for colours only;
  - the power numbers come with CIs;
  - the ρ_A ≥ 4 subset is post hoc and has no tori.
- "× chance" is now "× the null's 95th percentile".
- The example figure no longer labels the days_time within-cluster loop as a ring.

## Learnings

- A maximum statistic over all bars needs localising in clustered designs. Check whether the winning bar dies before the clusters touch.
- When a stimulus set is sampled from a space with its own geometry (RGB, HLS), run the topology on the stimuli themselves before reading the activations' topology as the model's.
- Report CIs for every simulated pass rate, and interpolate rather than quote the nearest grid cell.
- A control only tests specificity if it can come near the threshold.
