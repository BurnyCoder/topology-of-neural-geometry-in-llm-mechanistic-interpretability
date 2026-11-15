Validation-tuned values (validation stream only, 1,560 clouds; results/power/val_tuning.json):

- b0 rule: tau = 12.0, min_frac = 0.02 (exact-b0 accuracy on 1228 resolvable validation clouds: 0.897).
- Fixed-pi baseline: pi0_1 = 3.0, pi0_2 = 1.4 (validation macro exact accuracy 0.711).
- Family-implied baseline map (family -> modal exact Betti vector): arc (1, 0, 0), blob (1, 0, 0), clusters (2, 0, 0), cone (1, 1, 0), disc (1, 0, 0), ellipse (1, 1, 0), helix (1, 0, 0), line (1, 0, 0), paraboloid (1, 0, 0), polytope (4, 0, 0), ringing (1, 0, 0), sphere (1, 0, 0), torus (1, 2, 1).

Second-order statistics of the real sets used to place the simulation grid (no topology computed):

| id | N | D | between_fraction | top3_explained |
|---|---|---|---|---|
| R5a_llama_weekdays | 49 | 4096 | 0.841 | 0.659 |
| R5b_llama_months | 144 | 4096 | 0.914 | 0.549 |
| R5c_llama_days_time | 336 | 4096 | 0.772 | 0.580 |
| R2_grokking_WE | 113 | 128 | 1.000 | 0.324 |
| C3_llama_weekdays_init | 49 | 4096 | 0.620 | 0.342 |
| C3_llama_months_init | 144 | 4096 | 0.584 | 0.185 |

Power / false-positive rates of H1-B conditions (a)-(c) (40 replicates per cell, M = 199 null draws; results/power/power_summary.csv):

| k | m | arrangement | between fraction | (a) loop | (b) align p<0.05/6 | (c) |w|=1 | (a)-(c) |
|---|---|---|---|---|---|---|---|
| 7 | 7 | arc300 | 0.300 | 1.000 | 0.250 | 0.250 | 0.250 |
| 7 | 7 | arc300 | 0.500 | 1.000 | 0.150 | 0.150 | 0.150 |
| 7 | 7 | arc300 | 0.700 | 1.000 | 0.025 | 0.025 | 0.025 |
| 7 | 7 | arc300 | 0.900 | 1.000 | 0.000 | 0.000 | 0.000 |
| 7 | 7 | random | 0.300 | 0.025 | 0.000 | 0.000 | 0.000 |
| 7 | 7 | random | 0.500 | 0.025 | 0.000 | 0.000 | 0.000 |
| 7 | 7 | random | 0.700 | 0.025 | 0.000 | 0.000 | 0.000 |
| 7 | 7 | random | 0.900 | 0.025 | 0.000 | 0.000 | 0.000 |
| 7 | 7 | ring | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 |
| 7 | 7 | ring | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 |
| 7 | 7 | ring | 0.700 | 1.000 | 1.000 | 1.000 | 1.000 |
| 7 | 7 | ring | 0.900 | 1.000 | 1.000 | 1.000 | 1.000 |
| 12 | 12 | arc300 | 0.300 | 1.000 | 0.025 | 0.025 | 0.025 |
| 12 | 12 | arc300 | 0.500 | 1.000 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | arc300 | 0.700 | 1.000 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | arc300 | 0.900 | 1.000 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | random | 0.300 | 0.025 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | random | 0.500 | 0.025 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | random | 0.700 | 0.025 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | random | 0.900 | 0.100 | 0.000 | 0.000 | 0.000 |
| 12 | 12 | ring | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 |
| 12 | 12 | ring | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 |
| 12 | 12 | ring | 0.700 | 1.000 | 1.000 | 1.000 | 1.000 |
| 12 | 12 | ring | 0.900 | 1.000 | 1.000 | 1.000 | 1.000 |
| 113 | 1 | arc300 | 0.300 | 0.250 | 0.125 | 0.075 | 0.075 |
| 113 | 1 | arc300 | 0.500 | 0.275 | 0.075 | 0.075 | 0.075 |
| 113 | 1 | arc300 | 0.700 | 0.250 | 0.000 | 0.000 | 0.000 |
| 113 | 1 | arc300 | 0.900 | 0.075 | 0.000 | 0.000 | 0.000 |
| 113 | 1 | random | 0.300 | 0.025 | 0.000 | 0.000 | 0.000 |
| 113 | 1 | random | 0.500 | 0.025 | 0.000 | 0.000 | 0.000 |
| 113 | 1 | random | 0.700 | 0.050 | 0.000 | 0.000 | 0.000 |
| 113 | 1 | random | 0.900 | 0.025 | 0.000 | 0.025 | 0.000 |
| 113 | 1 | ring | 0.300 | 1.000 | 1.000 | 1.000 | 1.000 |
| 113 | 1 | ring | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 |
| 113 | 1 | ring | 0.700 | 1.000 | 1.000 | 1.000 | 1.000 |
| 113 | 1 | ring | 0.900 | 1.000 | 1.000 | 1.000 | 1.000 |
