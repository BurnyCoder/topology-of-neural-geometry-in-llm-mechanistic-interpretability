# Deviations from the preregistration and the plan

Each entry is dated and states what changed, why, and whether it was decided before or after seeing results.

## D1 (2026-11-15, before any result on the synthetic test set or on real data): add a Rips-H1 universal-null estimator

**What I found.** While writing the unit tests, I checked the universal null of [Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2) on toy clouds (`tests/test_tda.py`).
- **Calibration holds.** On 1,000 uniform points in the unit cube:
  - the standard deviation of log log π of noise bars is about 2.4 for alpha complexes (A = ½ predicts 2.57);
  - it is about 1.2 for Rips (A = 1 predicts 1.28).
- **But alpha with A = ½ is very conservative at our sample sizes.** A noisy circle (N = 400, σ = 0.03, top π = 18) is not significant after Bonferroni over its 442 H1 bars. The p-value is 2.5·10⁻⁴, against a threshold of 1.1·10⁻⁴.
- **Rips H1 with A = 1** detects the same circle and nothing in Gaussian blobs.

**Change.**
- I add the Rips-H1 universal-null count as a **secondary estimator of b1**, computed on the same normalised 3D cloud with ripser and A = 1. It is used in Exp1, alongside the preregistered estimators, and in Exp2, descriptively.
- The preregistered primary estimator for H5 (alpha, A = ½) is unchanged.
- The primary real-data criterion is unchanged: the design-matched Monte Carlo null on the maximum π, which does not use A.

**Implementation detail (not a deviation).** Degenerate inputs, such as co-circular points like a regular 12-gon, make GUDHI return bars with death equal to birth. These are dropped. They had π = 1, so they were already excluded from the universal null and its Bonferroni count.
