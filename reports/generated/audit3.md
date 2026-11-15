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
