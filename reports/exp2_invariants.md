# Exp2: persistent-homology invariants of the 44 real clouds (Method B)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp2_invariants.py`, `realdata.py`. Results: `results/exp2/`, with nulls cached in `results/nulls/`.

## Method

- **Alpha diagrams** (H0–H2, radius units) of each source-identical, RMS-normalised top-3 PCA cloud. The recomputed clouds match the source's stored points to better than 1e-3 of their scale.
- **Significance:** the maximum persistence ratio π = death/birth is compared with 999 draws of a design-matched null.
  - Cluster-centre null for prompt-template designs: weekdays, months, days_time, colours (concept = hue), and the random-init weekday and month controls.
  - Full-dimensional matched-covariance Gaussian for everything else.
  - Every null draw passes through the same top-3 PCA normalisation.
- **Descriptive extras:**
  - universal-null counts for alpha (A = ½) and Rips (A = 1);
  - b0 by the tuned single-linkage rule;
  - Betti numbers and χ at the characteristic scale r_c;
  - genus, reported only for closed surfaces;
  - stability: the fraction of 200 subsamples of 80% (source seeds) whose top π exceeds the full cloud's null threshold.

## Results

- **8 clouds have a significant loop and 6 a significant void.** The loops:
  - colours: π = 5.02 vs 2.38, p = 0.001, stable in 1.00 of subsamples;
  - grokked residues: 2.45 vs 1.83, p = 0.001, stability 0.26;
  - months: 1.72 vs 1.44, p = 0.002, stability 0.90;
  - month means: p = 0.001;
  - days with times: 2.01 vs 1.87, p = 0.013, stability 0.03;
  - the grokking model at initialisation (p = 0.046, borderline);
  - the toy-model clouds of superposition (5–8 points).
- **Weekdays have no significant loop** (π = 1.32 vs 1.36, p = 0.094).
- **No ordinal concept has a loop** (0/6), and neither do the 20 random-process controls (0/20; max π 1.37).
- **GPT-2 W_pos:** fitted as a closed sphere (Method A void), but there is no significant void in the data (H2 π = 1.02). The positions trace a spiral curve, not a surface.
- **Truth cities (exploratory prediction, preregistration section 6: b0 = 2, true vs false statements):** not supported. The tuned single-linkage rule gives b0 = 1, and b0 = 1 at the characteristic scale. The homotopy class is contractible.
- **Agreement between Method A and Method B (b1, b2):** 0.705.
- **Benjamini–Hochberg over the 44 loop tests (post hoc, D6):** 6 loops at q < 0.05: C3_tms_dense, R2_grokking_WE, R3_tms_n8, R5b_llama_months, R5b_llama_months_means, R7_llama_colors.

<!-- BEGIN:exp2 -->
| id | N | design | top_pi1 | null_q95_pi1 | p_top_loop | top_pi2 | null_q95_pi2 | p_top_void | b0_rc | b1_rc | b2_rc | chi_rc | genus_rc | homotopy_rc | b1_alpha_univ | b1_rips_univ | loop_freq | family | A_b1 | A_b2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1_gp_0 | 200 | gaussian | 1.000 | 1.931 | 1.000 | 1.000 | 1.205 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_1 | 200 | gaussian | 1.159 | 1.948 | 1.000 | 1.009 | 1.245 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 2 | 0 | 0.000 | ringing | 0 | 0 |
| C1_gp_2 | 200 | gaussian | 1.088 | 1.923 | 1.000 | 1.011 | 1.236 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 2 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_3 | 200 | gaussian | 1.164 | 1.941 | 1.000 | 1.093 | 1.243 | 0.955 | 1 | 0 | 0 | 1 | - | contractible | 3 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_4 | 200 | gaussian | 1.002 | 1.948 | 1.000 | 1.004 | 1.197 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 1 | 0 | 0.000 | ringing | 0 | 0 |
| C1_gp_5 | 200 | gaussian | 1.369 | 1.928 | 1.000 | 1.054 | 1.244 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 1 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_6 | 200 | gaussian | 1.133 | 1.955 | 1.000 | 1.064 | 1.239 | 0.996 | 1 | 0 | 0 | 1 | - | contractible | 2 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_7 | 200 | gaussian | 1.046 | 1.938 | 1.000 | 1.047 | 1.234 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 3 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_8 | 200 | gaussian | 1.005 | 1.941 | 1.000 | 1.005 | 1.205 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 1 | 0 | 0.000 | helix | 0 | 0 |
| C1_gp_9 | 200 | gaussian | 1.020 | 1.924 | 1.000 | 1.001 | 1.216 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 2 | 0 | 0.000 | helix | 0 | 0 |
| C1_walk_0 | 200 | gaussian | 1.053 | 1.901 | 1.000 | 1.000 | 1.215 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_1 | 200 | gaussian | 1.118 | 1.914 | 1.000 | 1.000 | 1.213 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_2 | 200 | gaussian | 1.065 | 1.916 | 1.000 | 1.000 | 1.212 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_3 | 200 | gaussian | 1.101 | 1.905 | 1.000 | 1.000 | 1.213 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_4 | 200 | gaussian | 1.180 | 1.922 | 1.000 | 1.003 | 1.215 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_5 | 200 | gaussian | 1.104 | 1.917 | 1.000 | 1.002 | 1.214 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_6 | 200 | gaussian | 1.065 | 1.956 | 1.000 | 1.006 | 1.216 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_7 | 200 | gaussian | 1.074 | 1.932 | 1.000 | 1.000 | 1.220 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_8 | 200 | gaussian | 1.086 | 1.904 | 1.000 | 1.000 | 1.216 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C1_walk_9 | 200 | gaussian | 1.352 | 1.923 | 1.000 | 1.000 | 1.213 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| C3_gpt2_wpos_init | 1023 | gaussian | 2.028 | 2.169 | 0.299 | 1.437 | 1.397 | 0.020 | 1 | 0 | 1 | 2 | 0.000 | sphere | 0 | 0 | 0.060 | blob | 0 | 0 |
| C3_grokking_WE_init | 113 | gaussian | 1.841 | 1.830 | 0.046 | 1.149 | 1.192 | 0.191 | 1 | 1 | 0 | 0 | - | circle-like | 0 | 0 | 0.015 | blob | 0 | 0 |
| C3_grokking_WE_memorised | 113 | gaussian | 1.502 | 1.829 | 0.831 | 1.098 | 1.188 | 0.612 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.050 | blob | 0 | 0 |
| C3_llama_counting_init | 150 | gaussian | 1.536 | 1.871 | 0.881 | 1.033 | 1.208 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.005 | clusters | 0 | 0 |
| C3_llama_months_init | 144 | cluster | 1.430 | 1.463 | 0.074 | 1.013 | 1.058 | 0.863 | 4 | 0 | 0 | 4 | - | 4 components | 0 | 0 | 0.045 | clusters | 0 | 0 |
| C3_llama_weekdays_init | 49 | cluster | 1.114 | 1.277 | 0.765 | 1.030 | 1.029 | 0.045 | 4 | 0 | 1 | 5 | - | other (4,0,1) | 0 | 0 | 0.020 | polytope | 0 | 0 |
| C3_tms_dense | 5 | gaussian | 1.235 | 1.118 | 0.001 | 1.001 | 1.000 | 0.019 | 1 | 1 | 0 | 0 | - | circle-like | 0 | 0 | 0.410 | polytope | 0 | 0 |
| R1_gpt2_wpos | 1023 | gaussian | 1.217 | 2.163 | 1.000 | 1.025 | 1.393 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 2 | 1 | 0.000 | sphere | 0 | 1 |
| R2_grokking_WE | 113 | gaussian | 2.446 | 1.830 | 0.001 | 1.049 | 1.199 | 0.990 | 1 | 2 | 0 | -1 | - | other (1,2,0) | 0 | 0 | 0.260 | helix | 0 | 0 |
| R3_tms_n20 | 20 | gaussian | 1.339 | 1.437 | 0.191 | 1.470 | 1.062 | 0.001 | 1 | 0 | 1 | 2 | 0.000 | sphere | 0 | 0 | 0.350 | sphere | 0 | 0 |
| R3_tms_n6 | 6 | gaussian | 1.155 | 1.183 | 0.087 | 1.224 | 1.013 | 0.001 | 1 | 0 | 1 | 2 | 0.000 | sphere | 0 | 0 | 0.000 | polytope | 0 | 0 |
| R3_tms_n8 | 8 | gaussian | 1.409 | 1.244 | 0.004 | 1.176 | 1.021 | 0.001 | 1 | 0 | 1 | 2 | 0.000 | sphere | 0 | 1 | 0.735 | polytope | 0 | 0 |
| R4_llama_counting | 150 | gaussian | 1.285 | 1.888 | 1.000 | 1.018 | 1.192 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| R4b_pythia_counting | 150 | gaussian | 1.323 | 1.869 | 1.000 | 1.026 | 1.184 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| R5a_llama_weekdays | 49 | cluster | 1.324 | 1.356 | 0.094 | 1.006 | 1.054 | 0.518 | 5 | 0 | 0 | 5 | - | 5 components | 0 | 0 | 0.010 | helix | 0 | 0 |
| R5a_llama_weekdays_means | 7 | gaussian | 1.052 | 1.190 | 0.731 | 1.017 | 1.020 | 0.072 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.125 | sphere | 0 | 0 |
| R5b_llama_months | 144 | cluster | 1.717 | 1.443 | 0.002 | 1.019 | 1.059 | 0.743 | 12 | 1 | 0 | 11 | - | other (12,1,0) | 0 | 1 | 0.900 | helix | 0 | 0 |
| R5b_llama_months_means | 12 | gaussian | 1.712 | 1.334 | 0.001 | 1.025 | 1.040 | 0.152 | 1 | 1 | 0 | 0 | - | circle-like | 0 | 0 | 0.340 | helix | 0 | 0 |
| R5c_llama_days_time | 336 | cluster | 2.011 | 1.873 | 0.013 | 1.061 | 1.093 | 0.268 | 6 | 1 | 0 | 5 | - | other (6,1,0) | 0 | 0 | 0.030 | ringing | 0 | 0 |
| R6_llama_years | 199 | gaussian | 1.635 | 1.937 | 0.775 | 1.124 | 1.234 | 0.739 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.080 | cone | 1 | 0 |
| R7_llama_colors | 900 | cluster | 5.025 | 2.379 | 0.001 | 1.244 | 1.346 | 0.480 | 1 | 1 | 0 | 0 | - | circle-like | 0 | 1 | 1.000 | cone | 1 | 0 |
| R8a_llama_temperature | 150 | gaussian | 1.334 | 1.889 | 1.000 | 1.020 | 1.190 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.000 | ringing | 0 | 0 |
| R8b_llama_age | 99 | gaussian | 1.580 | 1.792 | 0.449 | 1.001 | 1.166 | 1.000 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.045 | clusters | 0 | 0 |
| R9_llama_truth_cities | 1496 | gaussian | 1.931 | 2.202 | 0.861 | 1.287 | 1.411 | 0.672 | 1 | 0 | 0 | 1 | - | contractible | 0 | 0 | 0.030 | ringing | 0 | 0 |
<!-- END:exp2 -->

![gallery](../docs/figures/fig_real_gallery.png)

![null distributions](../docs/figures/fig_null_tests.png)

Grey: Monte Carlo null distribution of the largest H1 persistence ratio (999 design-matched draws). Dashed: its 95th percentile. Solid: the observed largest ratio.

## Interpretation

- Topology detects loops in four cyclic sets (hue, residues mod 113, months, days_time). It detects none in weekdays, ordinal concepts or random-process controls, and a borderline one in the random-init grokking embedding.
- **A loop is not traversal.** The day does not go around the days_time loop (Exp3). The residue loop is fragile under subsampling (stability 0.26).
- **Weekdays are the exception.** The 7 tight prompt clusters do not form a loop more persistent than random arrangements of 7 clusters with the same spread. At 7 clusters the maximum possible ratio is 1/sin(π/7) ≈ 2.3, so the power is inherently limited.
- **Caveats:** two random-init or toy controls cross the 5% line, consistent with the nominal error rate over this many tests. The days_time loop is unstable under subsampling.

## Learnings

- The cluster-centre null matters. With a plain Gaussian null, any arrangement of tight clusters would look "loopy".
- Stability under subsampling separates robust loops (colours 1.00, months 0.90) from fragile ones (days_time 0.03).
