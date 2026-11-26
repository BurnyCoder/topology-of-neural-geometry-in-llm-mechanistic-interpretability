| estimator | macro exact accuracy | 95% CI | n clouds |
|---|---|---|---|
| P_alpha_universal | 0.618 | [0.610, 0.626] | 30114 |
| S_rips_universal | 0.660 | [0.651, 0.670] | 30114 |
| Ba_fixed_pi | 0.714 | [0.703, 0.725] | 30114 |
| Bb_family_implied | 0.812 | [0.807, 0.816] | 30114 |
| Bc_majority | 0.555 | [0.553, 0.557] | 30114 |
| MC_gaussian3d (subset) | 0.594 | [0.561, 0.629] | 2427 |
| P_alpha_universal (subset) | 0.615 | [0.588, 0.644] | 2427 |
| S_rips_universal (subset) | 0.674 | [0.640, 0.703] | 2427 |

Paired differences (primary minus comparator):

| comparison | difference | 95% CI |
|---|---|---|
| P - S_rips_universal | -0.042 | [-0.051, -0.033] |
| P - Ba_fixed_pi | -0.096 | [-0.108, -0.084] |
| P - Bb_family_implied | -0.194 | [-0.203, -0.185] |
| P - Bc_majority | 0.063 | [0.055, 0.071] |

False-positive rate (b1 >= 1 or b2 >= 1) on resolvable contractible clouds, by N-bin:

| estimator | N-bin 0 | N-bin 1 | N-bin 2 | N-bin 3 |
|---|---|---|---|---|
| P_alpha_universal | 0.018 | 0.045 | 0.075 | 0.065 |
| S_rips_universal | 0.002 | 0.055 | 0.107 | 0.108 |
| Ba_fixed_pi | 0.000 | 0.002 | 0.029 | 0.076 |
| Bb_family_implied | 0.108 | 0.024 | 0.005 | 0.003 |
| Bc_majority | 0.000 | 0.000 | 0.000 | 0.000 |

Universal-null calibration on blobs (FWER = fraction with any significant alpha H1 bar):

| N-bin | fwer_alpha_universal | ks_uniform_D | n_pvalues | n_clouds | by_noise_bin |
|---|---|---|---|---|---|
| 0 | 0.009 | 0.117 | 3011 | 750 | {'0': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '1': {'n': 250, 'hits': 2, 'rate': 0.008, 'cluster_ci': [0.0, 0.02]}, '2': {'n': 250, 'hits': 4, 'rate': 0.016, 'cluster_ci': [0.0, 0.036]}} |
| 1 | 0.004 | 0.066 | 34043 | 750 | {'0': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '1': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '2': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}} |
| 2 | 0.000 | 0.048 | 185130 | 750 | {'0': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '1': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '2': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}} |
| 3 | 0.000 | 0.035 | 1003790 | 750 | {'0': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '1': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '2': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}} |

Per-family exact accuracy (resolvable clouds):

| family | P_alpha_universal | S_rips_universal | Ba_fixed_pi | Bb_family_implied | Bc_majority |
|---|---|---|---|---|---|
| arc | 0.651 | 0.753 | 0.788 | 0.576 | 0.582 |
| blob | 0.990 | 0.986 | 0.998 | 0.945 | 1.000 |
| clusters | 0.340 | 0.339 | 0.341 | 0.328 | 0.000 |
| cone | 0.007 | 0.334 | 0.534 | 0.943 | 0.000 |
| disc | 0.974 | 0.963 | 0.985 | 0.954 | 1.000 |
| ellipse | 0.257 | 0.546 | 0.509 | 0.990 | 0.000 |
| helix | 0.783 | 0.654 | 0.861 | 0.987 | 1.000 |
| line | 0.953 | 0.952 | 0.963 | 0.991 | 1.000 |
| paraboloid | 0.968 | 0.956 | 0.984 | 0.911 | 1.000 |
| polytope | 0.500 | 0.500 | 0.500 | 0.351 | 0.000 |
| ringing | 0.928 | 0.927 | 0.947 | 0.970 | 1.000 |
| sphere | 0.687 | 0.675 | 0.761 | 0.609 | 0.638 |
| torus | 0.000 | 0.000 | 0.111 | 1.000 | 0.000 |

Resolvable fraction of test clouds: 0.772.
