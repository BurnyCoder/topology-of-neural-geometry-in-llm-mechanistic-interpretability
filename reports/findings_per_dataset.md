# Findings per dataset

Date: 2026-11-15. Every number is generated from `results/` (`run.py report`). Compact overview: the README's evaluation tables; methods: [docs/methodology.md](../docs/methodology.md).


Here "hole" means a significant H1 loop under the design-matched Monte Carlo null (999 draws), and "goes around" means winding exactly once in the loop's circle-valued coordinate. The alignment R and its permutation p measure *ordering*; only winding ±1 carries the cyclic claim.

- **Colours (exploratory set):**
  - Hole: π = 5.02 vs null 95th percentile 2.38, p = 0.001, Benjamini–Hochberg q = 0.011, stable in 1.00 of subsamples.
  - Hue goes around it once, in θ_B (R = 0.95, winding -1) and on the fitted cone (R = 0.98, winding 1).
  - In the top-10 PCs the loop stays significant (Rips π = 2.67 vs 1.61, p = 0.005), and hue still winds once there, post hoc (R = 0.97, winding -1).
- **Grokked residues mod 113:**
  - Hole: π = 2.45 vs 1.83, p = 0.001, but stable in only 0.26 of subsamples.
  - The residues go around it once at Fourier frequency 20 (Holm p = 6.0e-05, winding -1).
  - The preregistered top-10-PC check fails (top-10 null p = 1.000).
- **Months:**
  - Hole: π = 1.72 vs 1.44, p = 0.002.
  - The preregistered circular-coordinate setting built no coordinate. Only post hoc (relaxed setting) do the months go around the loop once in 3D (R = 0.72, winding 1). They do not in the top-10 PCs (winding 0; top-10 null p = 0.550).
  - On the fitted helix the two ends nearly meet (closure gap 0.04 radii). Post hoc, the axial position follows the 2nd Fourier harmonic (R² = 0.83 vs 0.10 for the 1st), as a closed saddle-shaped loop would.
- **Days with times** (day phase, exploratory):
  - There is a loop (p = 0.013), but it is unstable (stable in 0.03 of subsamples).
  - **The day does not go around it**, even post hoc (R = 0.18, winding 0). On the fitted curve the days lie in linear order (ρ = -1.00).
- **Weekdays:**
  - **No detectable hole** (π = 1.32 vs 1.36, p = 0.094).
  - The test has little power here (corrected power simulation: a true weekday-like ring passes the loop test in 0.15 of replicates; [fig_power](../docs/figures/fig_power.png)).
  - The days are ordered around the fitted helix's axis (exact p = 0.003, winding 1). **This is not specific:** 8 of 8 smooth random-process controls fitted as helices wind too, and their closure gaps (0.33–2.20) include the weekdays' 0.80.
- **Ordinal concepts and controls:**
  - Ordinal values do not wind around the top-10 loops. Only R1_gpt2_wpos has a single winding record among all non-cyclic sets.
  - After Benjamini–Hochberg over all 44 loop tests, 6 loops remain at q < 0.05: C3_tms_dense, R2_grokking_WE, R3_tms_n8, R5b_llama_months, R5b_llama_months_means, R7_llama_colors.
  - Ordinal concepts lie in order along open curves: counts ρ = 0.999, temperature -0.997. GPT-2 positions run from pole to pole of their fitted sphere (0.978) as a spiral curve.
  - Truth cities: the exploratory prediction of two components (true vs false statements) is not supported (b0 = 1).
