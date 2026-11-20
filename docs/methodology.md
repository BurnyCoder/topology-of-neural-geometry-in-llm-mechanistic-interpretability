# Methodology and design decisions

This page explains *why* each choice was made. The exact rules are in [reports/preregistration.md](../reports/preregistration.md), and changes to them are in [reports/deviations.md](../reports/deviations.md). This page does not repeat either. For every step of the loop and ring test carried out with numbers on a toy cloud, see [worked_example.md](worked_example.md). Every technical term is defined in [glossary.md](glossary.md).

## Objects of study

**The 44 clouds** are exactly the source project's top-3 PCA clouds (`fit_frame`: centre, top-3 eigenvectors, skewness signs, RMS radius 1).
- The re-implementation reproduces the stored points to 1e-4 (`tests/test_pca.py`).
- Persistence diagrams are unchanged by the isometries (rotations, reflections, translations) that `fit_frame` applies, and π is unchanged by its uniform scaling. Only the projection to 3D matters. That is why condition (d) of H1-B and Exp5 repeat the loop analysis in the top-5 and top-10 PCs and in full-dimensional cosine dissimilarity (1 − cos is not a metric and is about angle²/2 for small angles, so that check is descriptive).

## Two ways to find holes

**Method A: exact topology of the fitted shape.** The fitted shape is a parametrised manifold, so its Betti numbers are exact ([docs/analytic_topology.md](analytic_topology.md)). What is uncertain is whether the *data* resolve that topology. The margin ratio ρ_A = m/(2ν) answers that, heuristically: m is the size of the smallest gap or diameter whose closing or collapse would alter the topology, and ν is the cloud's noise plus coverage gaps. Balls of radius ν from both sides of a gap m meet once 2ν ≥ m; this is a rule of thumb, not a recovery theorem such as [Niyogi, Smale & Weinberger 2008](https://doi.org/10.1007/s00454-008-9053-2).
- Why: a fitted helix says "no hole". If its two ends are closer than the noise (ρ_A < 1), the data cannot distinguish it from a closed loop.

**Method B: persistent homology of the data.** Primary reference for the idea of counting holes with persistent homology: [What is...persistent homology?](https://www.youtube.com/watch?v=w6Jx1vFp_Gk) (VisualMath). We use alpha complexes, not Rips, in ℝ³:
- the alpha complex is homotopy equivalent to the union of balls at every radius ([Edelsbrunner 1995](https://doi.org/10.1007/BF02574053)), and its filtration has the same persistence diagrams as the Čech filtration ([Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991));
- H2 is cheap;
- it has no Rips phantom classes. Our test shows a regular 12-gon gets spurious H2 under Rips and none under alpha.

**Significance** uses a Monte Carlo null of the *maximum* persistence ratio π = death/birth, adapted from the shuffle threshold of [Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7) (they used the longest lifetime death − birth over all bars of 1,000 shuffles, a heuristic in their words).
- The ratio is scale-free.
- The max-statistic controls family-wise error across bars.
- The null is matched to the design: a cluster-centre null for prompt-template designs, whose clusters would otherwise make any arrangement look loopy against a plain Gaussian, and a full-dimensional matched Gaussian for one-point-per-value designs.
- **What it does not test (deviation D9).** Both nulls are Gaussian, so a significant loop means "more persistent than a covariance-matched Gaussian".
  - Hole-free surfaces, caps and helices often pass too, and for clustered designs so do nearly closed arcs of centres. On synthetic clouds of known topology, the matched-Gaussian null flags a sizeable share of hole-free clouds; the rates are in [reports/exp8_audit3.md](../reports/exp8_audit3.md).
  - Claims of a hole therefore rest on independent evidence: traversal against a label-permutation null, loop localisation, and the concept centres alone.
  - A hole-specific null (resampling hole-free fitted shapes at the cloud's noise) is future work.

The universal null of Bobrowski & Skraba (2023) is reported, but it is descriptive. It is calibrated (unit tests), but at our sample sizes it is very conservative on alpha complexes (deviation D1).

## Travel around the hole, and steering

A hole matters for semantics only if the concept *travels around it*. Both methods give a circle-valued coordinate:
- θ_A: the parameter of each point's nearest point on the fitted shape;
- θ_B: DREiMac's persistent-cohomology circular coordinate.

We then test, at the level of concept means, whether the concepts sit around the circle in their semantic order and wind exactly once:
- a permutation test over concept labels (exact for weekdays);
- the winding number;
- the cyclic-order probability 2/(n−1)!, an upper bound on the null probability of the implemented criterion (exact when every circular gap between concept means is below π; `stats/circular.py::cyclic_order_p`).

This follows manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)), which moves activations along a fitted manifold. Here the path is the loop that topology finds.
- **Simulated steering** (postponed, deviation D4) would move stored activations around that loop and decode the concept with cross-validated decoders. No model is run, so it is a decoder read-out, correlational evidence, not steering in the sense of an intervention on a forward pass ([preregistration](../reports/preregistration.md), amendment A2).
- **LLM steering** (postponed) applies the same displacement inside Llama-3.1-8B.

## Controls and confounds

- **Design-matched negatives:**
  - random-init Llama on the same prompts;
  - the grokking model at initialisation;
  - ordinal concepts in 7 and 12 bins, so the number of concepts matches;
  - 20 ordinal-process controls (Gaussian processes and random walks), which produce PCA horseshoes ([Diaconis, Goel & Holmes 2008](https://doi.org/10.1214/08-AOAS165)), Lissajous-like projections ([Antognini & Sohl-Dickstein 2018](https://arxiv.org/abs/1806.08805)) and helices without any cyclic semantics.
- **Nuisance factors:** the "k days from" offset word precedes the concept token. Exp5 removes the per-offset means.
- **Instrument validity:** the persistent-homology estimators are validated on 39,000 synthetic clouds with *exact* ground-truth topology (Exp1), restricted to clouds whose topology is resolvable, and reported as a function of ρ_A.

## Statistics

- Holm correction over the 6 co-primary alignment tests.
- Benjamini–Hochberg correction within the exploratory list.
- Clopper–Pearson CIs for rates over few datasets.
- Cluster bootstrap over the source generator's chunks of 25 clouds, which share N and the embedding draw.
- All seeds are fixed in `configs/base.yaml`. Monte Carlo seeds are crc32(dataset id) + seed. Exp5 repeats the main tests with seeds 1 and 2.
