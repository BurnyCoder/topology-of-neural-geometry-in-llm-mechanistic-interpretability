H1 (co-primary): Method A: 0/3 datasets pass, Method B: 0/3 datasets pass

| dataset | method | p raw | p Holm | pass | hole_resolvable | traversal | a_loop | b_align | c_wind1 | d_top10 |
|---|---|---|---|---|---|---|---|---|---|---|
| R5a_llama_weekdays | A | 1.000 | 1.000 | no | no | no | - | - | - | - |
| R5a_llama_weekdays | B | 1.000 | 1.000 | no | - | - | no | no | no | no |
| R5b_llama_months | A | 1.000 | 1.000 | no | no | no | - | - | - | - |
| R5b_llama_months | B | 1.000 | 1.000 | no | - | - | yes | no | no | no |
| R2_grokking_WE | A | 1.000 | 1.000 | no | no | no | - | - | - | - |
| R2_grokking_WE | B | 1.0e-05 | 6.0e-05 | no | - | - | yes | yes | yes | no |

H2 (specificity):

| method | ordinal sets passing (of 6) | init controls passing (of 3) | C1 controls passing (of 20) | C1 rate 95% CI | falsified |
|---|---|---|---|---|---|
| A | 0 | 0 | 0 | [0.00, 0.17] | no |
| B | 0 | 0 | 0 | [0.00, 0.17] | no |

H3 (R5c day phase): Method A: fail, Method B: fail

H4 balanced accuracy (cyclic vs ordinal): hole_only_A 0.500, conj_A 0.500, conj_B 0.500; exact McNemar: hole_only_A vs conj_A p = 1.000, hole_only_A vs conj_B p = 1.000, conj_A vs conj_B p = 1.000

Exploratory alignment records (BH q-values):

| id | method | variable | R | p | q_bh | winding | loop | kind |
|---|---|---|---|---|---|---|---|---|
| R7_llama_colors | B | hue | 0.949 | 1.0e-05 | 1.3e-05 | -1 | yes | - |
| R7_llama_colors | A | hue | 0.984 | 1.0e-05 | 1.3e-05 | 1 | - | hole |
| R5b_llama_months_means | A | month | 0.927 | 1.0e-05 | 1.3e-05 | 1 | - | axial winding (descriptive) |
| R6_llama_years | A | value mod 10 | 0.561 | 0.002 | 0.002 | 0 | - | hole |
| R6_llama_years | A | value mod 100 | 0.351 | 1.0e-05 | 1.3e-05 | 0 | - | hole |
