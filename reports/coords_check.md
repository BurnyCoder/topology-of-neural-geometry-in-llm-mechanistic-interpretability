# Where the labelled points sit on their fitted shapes (exploratory, deviation D4)

Date: 2026-11-15; wording corrected 2026-11-22 (independent audit, D14). Code: `src/neurotopo/experiments/coords_check.py`. Results: `results/coords/`. No model is run: only the stored clouds and the source fits are used.

## Question

The author asked: project the original labelled points onto the fitted shape, and check whether the concept values are ordered along it.

## Method

- **Intrinsic coordinates of every point:**
  - helix: curve parameter t, azimuth and axial position;
  - ringing and line curves: parameter s;
  - cone: azimuth and height s;
  - sphere: azimuth and polar height z;
  - clusters and polytope: nearest centroid or vertex.
- **Statistics:**
  - angular coordinates: circular alignment with the semantic phases (concept means, permutation p, winding);
  - linear coordinates: Spearman ρ with the value (ordinal sets, per point) or with the concept index (cyclic sets, per concept mean; exact permutation p for n ≤ 8);
  - assignments: NMI and ARI with the concepts.
- **Variables implicit in the source's row order and labels:** the prompt offset "k days from" for weekdays and months, and saturation and lightness for colours.
- **Post hoc:** the harmonic content (R² of 1st, 2nd and 3rd Fourier harmonics) of the axial position of the cyclic helix fits.

## Results

- **Weekdays** (helix):
  - the days sit around the axis in cyclic order (R = 0.834, exact p = 0.003, winding 1);
  - curve parameter t vs day: ρ = 0.00 (p = 1.00);
  - axial position vs offset k: ρ = 0.10.
- **Months** (helix):
  - around the axis: R = 0.931, winding 1;
  - t vs month: ρ = -0.21;
  - axial position vs offset: ρ = -0.00;
  - post hoc, axial harmonics: R² = 0.10 / 0.83 / 0.01 for h = 1 / 2 / 3. Weekdays: 0.38 / 0.39 / 0.23.
- **Residues** (helix): around the axis at k = 20, R = 0.976.
- **Days with times** (ringing curve): days are ordered *along* the open curve (ρ = -1.00, p = 4.0e-04); time of day also (ρ = -0.86).
- **Colours** (cone): hue goes around the axis (R = 0.984, winding 1). Height follows lightness (ρ = -0.67) more than saturation (ρ = 0.34).
- **Ordinal sets:**
  - counting: ρ = 0.999 along the curve;
  - temperature: -0.997;
  - GPT-2 positions (sphere fit): ordered from pole to pole, polar height 0.978; the positions trace a spiral curve on the fitted sphere;
  - years (cone): height -0.36, no winding;
  - age (clusters): NMI with 7 age bins 0.62.

<!-- BEGIN:coords -->
| id | family | coordinate | variable | statistic | n | R | p | winding | rho | NMI | ARI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_gp_0 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 0.090 | - | 0.120 | - | - |
| C1_gp_0 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.855 | 0.003 | 1.000 | - | - | - |
| C1_gp_0 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.852 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_0 | helix | axial position | value | Spearman (points) | 200.000 | - | 0.090 | - | -0.120 | - | - |
| C1_gp_1 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_gp_2 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_gp_2 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.978 | 0.003 | -1.000 | - | - | - |
| C1_gp_2 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.977 | 1.0e-05 | -1.000 | - | - | - |
| C1_gp_2 | helix | axial position | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_gp_3 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 2.6e-81 | - | 0.918 | - | - |
| C1_gp_3 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.967 | 0.003 | 1.000 | - | - | - |
| C1_gp_3 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.966 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_3 | helix | axial position | value | Spearman (points) | 200.000 | - | 2.6e-81 | - | -0.918 | - | - |
| C1_gp_4 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_gp_5 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 6.4e-86 | - | 0.926 | - | - |
| C1_gp_5 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.902 | 0.006 | 1.000 | - | - | - |
| C1_gp_5 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.899 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_5 | helix | axial position | value | Spearman (points) | 200.000 | - | 6.4e-86 | - | -0.926 | - | - |
| C1_gp_6 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 2.6e-96 | - | -0.943 | - | - |
| C1_gp_6 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.943 | 0.003 | 1.000 | - | - | - |
| C1_gp_6 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.942 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_6 | helix | axial position | value | Spearman (points) | 200.000 | - | 2.6e-96 | - | 0.943 | - | - |
| C1_gp_7 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 4.6e-15 | - | 0.517 | - | - |
| C1_gp_7 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.973 | 0.003 | -1.000 | - | - | - |
| C1_gp_7 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.971 | 1.0e-05 | -1.000 | - | - | - |
| C1_gp_7 | helix | axial position | value | Spearman (points) | 200.000 | - | 4.6e-15 | - | -0.517 | - | - |
| C1_gp_8 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 3.3e-05 | - | 0.289 | - | - |
| C1_gp_8 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.896 | 0.003 | 1.000 | - | - | - |
| C1_gp_8 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.893 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_8 | helix | axial position | value | Spearman (points) | 200.000 | - | 3.3e-05 | - | -0.289 | - | - |
| C1_gp_9 | helix | curve parameter t | value | Spearman (points) | 200.000 | - | 2.0e-11 | - | -0.451 | - | - |
| C1_gp_9 | helix | azimuth | value in 7 bins | circular alignment | 7.000 | 0.937 | 0.003 | 1.000 | - | - | - |
| C1_gp_9 | helix | azimuth | value in 12 bins | circular alignment | 12.000 | 0.935 | 1.0e-05 | 1.000 | - | - | - |
| C1_gp_9 | helix | axial position | value | Spearman (points) | 200.000 | - | 2.0e-11 | - | 0.451 | - | - |
| C1_walk_0 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_walk_1 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_walk_2 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_3 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_4 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C1_walk_5 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_6 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_7 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_8 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | -1.000 | - | - |
| C1_walk_9 | ringing | curve parameter s | value | Spearman (points) | 200.000 | - | 0.000 | - | 1.000 | - | - |
| C3_llama_counting_init | clusters | nearest centroid/vertex | value in 7 bins | - | - | - | - | - | - | 0.026 | -5.5e-05 |
| C3_llama_counting_init | clusters | nearest centroid/vertex | value in 12 bins | - | - | - | - | - | - | 0.026 | -7.4e-06 |
| C3_llama_months_init | clusters | nearest centroid/vertex | month | - | - | - | - | - | - | 0.647 | 0.261 |
| C3_llama_weekdays_init | polytope | nearest centroid/vertex | day of week | - | - | - | - | - | - | 0.792 | 0.515 |
| R1_gpt2_wpos | sphere | azimuth | value in 7 bins | circular alignment | 7.000 | 0.274 | 0.875 | 2.000 | - | - | - |
| R1_gpt2_wpos | sphere | azimuth | value in 12 bins | circular alignment | 12.000 | 0.291 | 0.664 | 2.000 | - | - | - |
| R1_gpt2_wpos | sphere | polar height z | value | Spearman (points) | 1023.000 | - | 0.000 | - | 0.978 | - | - |
| R2_grokking_WE | helix | curve parameter t | position on the k=20 circle | Spearman (points) | 113.000 | - | 0.606 | - | -0.049 | - | - |
| R2_grokking_WE | helix | azimuth | residue (max over k) | circular alignment | 113.000 | 0.976 | 1.0e-05 | -1.000 | - | - | - |
| R2_grokking_WE | helix | axial position | position on the k=20 circle | Spearman (points) | 113.000 | - | 0.606 | - | 0.049 | - | - |
| R4_llama_counting | ringing | curve parameter s | value | Spearman (points) | 150.000 | - | 3.1e-189 | - | 0.999 | - | - |
| R4b_pythia_counting | ringing | curve parameter s | value | Spearman (points) | 150.000 | - | 2.0e-251 | - | 1.000 | - | - |
| R5a_llama_weekdays | helix | curve parameter t | offset k | Spearman (points) | 49.000 | - | 0.479 | - | -0.104 | - | - |
| R5a_llama_weekdays | helix | curve parameter t | day of week | Spearman (concept means) | 7.000 | - | 1.000 | - | 0.000 | - | - |
| R5a_llama_weekdays | helix | azimuth | day of week | circular alignment | 7.000 | 0.834 | 0.003 | 1.000 | - | - | - |
| R5a_llama_weekdays | helix | axial position | offset k | Spearman (points) | 49.000 | - | 0.479 | - | 0.104 | - | - |
| R5a_llama_weekdays | helix | axial position | day of week | Spearman (concept means) | 7.000 | - | 1.000 | - | 0.000 | - | - |
| R5a_llama_weekdays_means | sphere | azimuth | day of week | circular alignment | 7.000 | 0.863 | 0.003 | 1.000 | - | - | - |
| R5a_llama_weekdays_means | sphere | polar height z | day of week | Spearman (concept means) | 7.000 | - | 0.354 | - | -0.429 | - | - |
| R5b_llama_months | helix | curve parameter t | offset k | Spearman (points) | 144.000 | - | 0.958 | - | 0.004 | - | - |
| R5b_llama_months | helix | curve parameter t | month | Spearman (concept means) | 12.000 | - | 0.513 | - | -0.210 | - | - |
| R5b_llama_months | helix | azimuth | month | circular alignment | 12.000 | 0.931 | 1.0e-05 | 1.000 | - | - | - |
| R5b_llama_months | helix | axial position | offset k | Spearman (points) | 144.000 | - | 0.958 | - | -0.004 | - | - |
| R5b_llama_months | helix | axial position | month | Spearman (concept means) | 12.000 | - | 0.513 | - | 0.210 | - | - |
| R5b_llama_months_means | helix | curve parameter t | month | Spearman (concept means) | 12.000 | - | 0.513 | - | -0.210 | - | - |
| R5b_llama_months_means | helix | azimuth | month | circular alignment | 12.000 | 0.927 | 1.0e-05 | 1.000 | - | - | - |
| R5b_llama_months_means | helix | axial position | month | Spearman (concept means) | 12.000 | - | 0.513 | - | 0.210 | - | - |
| R5c_llama_days_time | ringing | curve parameter s | day of week | Spearman (concept means) | 7.000 | - | 4.0e-04 | - | -1.000 | - | - |
| R5c_llama_days_time | ringing | curve parameter s | time of day | Spearman (concept means) | 48.000 | - | 6.0e-15 | - | -0.859 | - | - |
| R6_llama_years | cone | azimuth | value in 7 bins | circular alignment | 7.000 | 0.536 | 0.200 | 0.000 | - | - | - |
| R6_llama_years | cone | azimuth | value in 12 bins | circular alignment | 12.000 | 0.494 | 0.034 | 0.000 | - | - | - |
| R6_llama_years | cone | azimuth | value mod 10 | circular alignment | 10.000 | 0.561 | 0.002 | 0.000 | - | - | - |
| R6_llama_years | cone | azimuth | value mod 100 | circular alignment | 100.000 | 0.351 | 1.0e-05 | 0.000 | - | - | - |
| R6_llama_years | cone | height s | value | Spearman (points) | 199.000 | - | 1.4e-07 | - | -0.363 | - | - |
| R7_llama_colors | cone | azimuth | hue | circular alignment | 36.000 | 0.984 | 1.0e-05 | 1.000 | - | - | - |
| R7_llama_colors | cone | height s | saturation | Spearman (points) | 900.000 | - | 5.7e-26 | - | 0.341 | - | - |
| R7_llama_colors | cone | height s | lightness | Spearman (points) | 900.000 | - | 5.4e-119 | - | -0.671 | - | - |
| R7_llama_colors | cone | height s | hue | Spearman (concept means) | 36.000 | - | 0.001 | - | 0.522 | - | - |
| R8a_llama_temperature | ringing | curve parameter s | value | Spearman (points) | 150.000 | - | 2.4e-164 | - | -0.997 | - | - |
| R8b_llama_age | clusters | nearest centroid/vertex | value in 7 bins | - | - | - | - | - | - | 0.616 | 0.430 |
| R8b_llama_age | clusters | nearest centroid/vertex | value in 12 bins | - | - | - | - | - | - | 0.611 | 0.328 |
<!-- END:coords -->

## Interpretation

- **The helices of the cyclic concepts carry the concept order around their axis.**
  - This ordering is not specific: random smooth processes fitted as helices show the same (Exp0).
  - The concept order is on the azimuth.
  - The axial direction is neither the concept order nor the prompt offset.
  - For months, the axial position is a second harmonic of the month angle. That is the shape a closed, saddle-shaped loop (cos φ, sin φ, cos 2φ), like a tennis-ball seam, would give, and the helix family can only approximate it. The fit is periodic by construction, so it assumes closure rather than testing it; in 3D the December → January step is the largest of the 12 (1.92× the median; audit D8).
- **Ordinal concepts lie in order along curves:** a PCA horseshoe for counts and temperature, a spiral on a sphere fit for GPT-2 positions.
- **Days with times** (Llama layer 19, last token) represent the day linearly along an open curve. Monday and Sunday are at opposite ends.

## Learnings

- The analysis was added at the author's request instead of simulated steering. It answers "does it make semantic sense on the fit?" without running any model.
- The harmonic analysis is post hoc. It was prompted by the non-monotone axial means.
