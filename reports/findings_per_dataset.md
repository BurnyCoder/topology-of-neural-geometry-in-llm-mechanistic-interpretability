# Findings per dataset

Date: 2026-11-15. Every number is generated from `results/` (`run.py report`). Compact overview: the README's evaluation tables; methods: [docs/methodology.md](../docs/methodology.md).


Here "hole" or "loop" means a significant H1 loop under the design-matched Monte Carlo null (999 draws), and "goes around" means winding exactly once in the loop's circle-valued coordinate. The nulls are Gaussian, so a significant loop means "more persistent than a covariance-matched Gaussian". That is not proof of a hole: the same test flags loops on 0.17 of hole-free synthetic clouds, and on 0.73 of spheres and caps (third audit, [exp8_audit3.md](exp8_audit3.md)). Evidence for a hole therefore comes from the traversal (tested against shuffled labels), from where the loop lives, and from the concept centres alone. For prompt-template designs, a hole counts as a ring of concepts only if it runs through the concept clusters: a loop that dies before any two clusters touch lies inside one cluster (second audit, [exp7_audit.md](exp7_audit.md)). The alignment R and its permutation p measure *ordering*; only winding ±1 carries the cyclic claim.

- **Colours (exploratory set):**
  - Hole: π = 5.02 vs null 95th percentile 2.38, p = 0.001, Benjamini–Hochberg q = 0.011, stable in 1.00 of subsamples.
  - Hue goes around it once, in θ_B (R = 0.95, winding -1) and on the fitted cone (R = 0.98, winding 1).
  - In the top-10 PCs the loop stays significant (Rips π = 2.67 vs 1.61, p = 0.005), and hue still winds once there, post hoc (R = 0.97, winding -1).
  - **Confounder (post hoc, D8):** the prompts' own RGB values already have the loop (π = 8.01 vs null 2.76, p = 0.001), and the 36 hue means wind once around it (winding -1, measured by their angle in PC1–PC2; DREiMac builds no usable circular coordinate on the RGB cloud: no coordinate in the preregistered setting, R = 0.03, winding 0 in the relaxed one, because 200 landmarks raise the Rips birth of this loop). The stimuli sample saturation ≥ 0.4 only, so they surround the grey axis. The model reads hex codes, not RGB vectors, so its loop is not trivial; but any continuous encoding of the stimulus colour would have it. The persistence ratios are not comparable as "weaker" or "stronger": one cloud is 3D by construction, the other a 3D projection of 4,096 dimensions. This shows that the model preserves the hue circle of its stimuli, not that it constructs a hue circle of its own.
- **Grokked residues mod 113:**
  - Hole: π = 2.45 vs 1.83, p = 0.001 (a second H1 bar is also significant), but stable in only 0.26 of subsamples (0.33 against a size-matched threshold).
  - Why the top-3 view is unstable (post hoc, D8): W_E puts 0.90 of its variance on 5 Fourier frequencies (20, 21, 3, 15, 31), 0.16–0.22 each, so the top six PCA eigenvalues are nearly equal (0.114, 0.111, 0.099, 0.096, …). Subsampling changes which frequency planes enter the top 3, and in 10 dimensions the 5 circles combine into a curve with no single dominant loop.
  - The residues go around it once at Fourier frequency 20 (Holm p = 6.0e-05, winding -1). This traversal, tested against shuffled residues, is the evidence for a ring. The loop test alone is not: π = 2.45 is inside the range the same Gaussian null gives hole-free synthetic clouds (1.39–2.81; D9).
  - The preregistered top-10-PC check fails (top-10 null p = 1.000).
- **Months:**
  - Hole: π = 1.72 vs 1.44, p = 0.002. It runs through the month clusters (it dies at radius 0.86; clusters first touch at 0.17), and the 12 month centres alone have the same loop (π = 1.71).
  - Hole-free arrangements are an unlikely source. In the third audit's simulation (D9), evenly spread hole-free arrangements of 12 centres (a hemisphere cap, a lattice) reached the months' π in 0 of 320 replicates, while rings and open arcs reach it at higher ring-variance shares. The pre-specified verdict on the cluster-centre null is undetermined, because at the real variance structure rings themselves rarely pass (5/40).
  - **Status: a ring is suggestive, not shown.**
  - Ring or nearly closed arc cannot be decided: the December → January step is the largest (1.92× the median step; preregistered full-space closure ratio 1.70, below the random-process controls' 2.00–8.79, but the ratio is crude: colours, with the clearest loop, score 3.81).
  - The preregistered circular-coordinate setting built no coordinate. Only post hoc (relaxed setting) do the months go around the loop once in 3D (R = 0.72, winding 1). They do not in the top-10 PCs (winding 0; top-10 null p = 0.550).
  - On the fitted helix the two ends nearly meet (closure gap 0.04 radii). Post hoc, the axial position follows the 2nd Fourier harmonic (R² = 0.83 vs 0.10 for the 1st), as a closed saddle-shaped loop would.
- **Days with times** (day phase, exploratory):
  - There is a significant loop (p = 0.013; BH q = 0.082), but it is unstable (stable in 0.03 of subsamples) and **lies inside one day's cluster**: it dies at radius 0.045, before any two day clusters touch (0.160). The 7 day centres alone form no loop (π = 1.11). So there is no ring of days.
  - Post hoc, the day does not go around a circular coordinate (R = 0.18, winding 0), but that coordinate is built on a different, non-significant class ([0.40, 0.43]; overlap with the significant loop: no). On the fitted curve the days lie in linear order (ρ = -1.00).
- **Weekdays:**
  - **No ring of days.** The 7 day centres form no loop (π = 1.05; the means set gives p = 0.731), and the Sunday → Monday step is the largest (1.95× the median).
  - This does not hinge on the third PC, whose variance nearly equals the fourth's (ratio 1.09; third audit, D9). The centres are weakly looped in PC1–PC2 too (π = 1.19; Sunday → Monday 2.5× the median step), and not at all in their own top-3 to top-6 PCs (Rips π ≤ 1.04).
  - The cloud's most persistent loop (π = 1.32 vs 1.36, p = 0.094) lies inside one day's cluster: it dies at radius 0.032, before any two day clusters touch (0.192).
  - Power is low for 7 clusters: in the corrected simulation a weekday-like ring passes the loop test in 0.15 of 40 replicates (exact 95% CI 0.06–0.30; [fig_power](../docs/figures/fig_power.png)). Its clusters are tighter than the real ones, so this does not explain the missing loop of day centres.
  - The days are ordered around the fitted helix's axis (exact p = 0.003, winding 1). **This is not specific:** 8 of 8 smooth random-process controls fitted as helices wind too, and their closure gaps (0.33–2.20) include the weekdays' 0.80.
- **Ordinal concepts and controls:**
  - Ordinal values do not wind around the top-10 loops. Only R1_gpt2_wpos has a single winding record among all non-cyclic sets.
  - In 3D no ordinal set or random process has a loop, but these open curves were never at risk: their top π (1.00–1.63) stays far below the Gaussian null's 95th percentile (1.79–2.16). The random-init networks give the informative calibration: 1 of 3 has p < 0.05 (p = 0.046), which is weak evidence either way (probability 0.14 under the null).
  - After Benjamini–Hochberg over all 44 loop tests, 6 loops remain at q < 0.05: C3_tms_dense, R2_grokking_WE, R3_tms_n8, R5b_llama_months, R5b_llama_months_means, R7_llama_colors.
  - Ordinal concepts lie in order along open curves: counts ρ = 0.999, temperature -0.997. GPT-2 positions run from pole to pole of their fitted sphere (0.978) as a spiral curve.
  - Truth cities: the exploratory prediction of two components (true vs false statements) is not supported (b0 = 1).
