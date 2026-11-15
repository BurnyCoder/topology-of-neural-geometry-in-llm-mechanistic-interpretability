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
