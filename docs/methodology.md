# Methodology and design decisions

This page explains *why* each choice was made. The exact rules are in [reports/preregistration.md](../reports/preregistration.md), and changes to them are in [reports/deviations.md](../reports/deviations.md). This page does not repeat either. For every step of the loop and ring test carried out with numbers on a toy cloud, see [worked_example.md](worked_example.md). Every technical term is defined in [glossary.md](glossary.md).

The amended primary steering hypothesis is untested. For registered and post hoc endpoints, the clean replay and projection-specific sampling uncertainty, see the [dated audit](../reports/reviews/2026-11-26-scientific-audit.md).

## Objects of study

**The 44 clouds** are exactly the source project's top-3 PCA clouds (`fit_frame`: centre, top-3 eigenvectors, skewness signs, RMS radius 1).
- The re-implementation reproduces the stored points to 1e-4 (`tests/test_pca.py`).
- Persistence diagrams are unchanged by the isometries (rotations, reflections, translations) that `fit_frame` applies, and π is unchanged by its uniform scaling. Changing the projection, dissimilarity, or analysis sample can change the observed persistence. That is why condition (d) of H1-B and Exp5 repeat the loop analysis in the top-5 and top-10 PCs and in full-dimensional cosine dissimilarity (1 − cos is not a metric and is about angle²/2 for small angles, so that check is descriptive).

## Two ways to find holes

**Method A assigns a topology to the fitted parameters.** A finite open helix is contractible and an ellipse with positive axes is a circle. Other catalog targets count cluster centres or polytope vertices, or call nearly closed arcs and caps closed. The margin ratio ρ_A = m/(2ν) compares a selected gap or diameter with sampled distances between points and the fitted object. A small pitch can bring neighbouring turns close. Whether the resulting offset has a loop depends on geometry and radius. [Catalog definitions](analytic_topology.md) · [Measured margins](../results/exp0/real_topology.csv) · [Unrounded domains](../results/science/angular_domains.csv) · [Sampling assumptions in Niyogi et al.](https://doi.org/10.1007/s00454-008-9053-2)

**Method B: persistent homology of the data.** Primary reference for the idea of counting holes with persistent homology: [What is...persistent homology?](https://www.youtube.com/watch?v=w6Jx1vFp_Gk) (VisualMath). We use alpha complexes, not Rips, in ℝ³:
- the alpha complex is homotopy equivalent to the union of balls at every radius ([Edelsbrunner 1995](https://doi.org/10.1007/BF02574053)), and its filtration has the same persistence diagrams as the Čech filtration ([Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991));
- In three dimensions the Delaunay triangulation supports the H2 calculation with vertices, edges, triangles and tetrahedra. [GUDHI alpha complexes](https://gudhi.inria.fr/python/latest/delaunay_complex_user.html)
- it has no Rips phantom classes. Our test shows a regular 12-gon gets spurious H2 under Rips and none under alpha.

**Significance** uses a Monte Carlo null of the *maximum* persistence ratio π = death/birth, adapted from the shuffle threshold of [Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7) (they used the longest lifetime death − birth over all bars of 1,000 shuffles, a heuristic in their words).
- The ratio is scale-free.
- Each draw contributes one maximum per homology dimension, accounting for the search across bars within that dimension. Exact rank calibration requires exchangeability. Nuisance covariances are fitted from the observations and calendar residuals are held fixed. [Calibration experiment](../results/science/calibration.csv) · [Monte Carlo tests with nuisance parameters](https://doi.org/10.1016/j.jeconom.2005.06.007)
- The null is matched to the design: a cluster-centre null for prompt-template designs, which retains within-concept residuals and redraws the concept centres, and a full-dimensional matched Gaussian for one-point-per-value designs.
- **What it does not test (deviation D9).** The fitted reference draws Gaussian points or Gaussian concept centres with fixed residuals. A rejection identifies high persistence relative to that reference.
  - Hole-free surfaces, caps and helices often pass too, and for clustered designs so do nearly closed arcs of centres. On synthetic clouds assigned contractible catalog targets, the matched-Gaussian comparison can also detect features; the rates are in [reports/exp8_audit3.md](../reports/exp8_audit3.md).
  - Traversal, localisation and centre-only calculations reuse these observations. Together they describe the measured projection. The dataset provides no independently sampled representation or steering intervention. [Dataset evidence](../results/science/dataset_assessment.csv)
  - A hole-specific null (resampling hole-free fitted shapes at the cloud's noise) is future work.

P uses the empirical Gumbel score proposed by Bobrowski and Skraba. Report observed calibration by blob size and noise. A subsequent preprint rules out its exact limiting form in specific degree-one Čech settings. [Stratified calibration](../results/science/blobs.csv) · [Original score](https://doi.org/10.1038/s41598-023-37842-2) · [Counterexamples](https://arxiv.org/html/2610.08257v1)

## Travel around the hole, and steering

The semantic test requires a usable circular coordinate. Each method attempts a different construction.
- θ_A: the parameter of each point's nearest point on the fitted shape;
- θ_B: DREiMac's persistent-cohomology circular coordinate.

We then test, at the level of concept means, whether the concepts sit around the circle in their semantic order and wind exactly once:
- a permutation test over concept labels (exact for weekdays);
- the winding number;
- an additional exact-order indicator requiring monotone wrapped steps. For fixed phases and distinct angles, its null probability is bounded by 2/(n−1)!. The test assigns one to nonmatches and applies a search correction when the frequency was selected. Each residue permutation repeats the alignment frequency search. [Tests and definitions](../src/neurotopo/stats/circular.py)

This follows manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)), which moves activations along a fitted manifold. The proposed path interpolates bin means in the inferred coordinate.
- **Simulated steering** (postponed, deviation D4) would move stored activations around that loop and decode the concept with cross-validated decoders. No model is run, so it is a decoder read-out, correlational evidence, not steering in the sense of an intervention on a forward pass ([preregistration](../reports/preregistration.md), amendment A2).
- **LLM steering** (postponed) applies the same displacement inside Llama-3.1-8B.

## Controls and confounds

- **Design-matched negatives:**
  - random-init Llama on the same prompts;
  - the grokking model at initialisation;
  - ordinal concepts in 7 and 12 bins, so the number of concepts matches;
  - Smooth Gaussian-process and random-walk controls have an ordered index without cyclic labels. Their low-dimensional projections can have oscillatory structure. The measured fits and the original theoretical examples are available separately. [Control fits](../results/exp0/real_topology.csv) · [Random walks under PCA](https://arxiv.org/abs/1806.08805) · [Horseshoes under distance-based embeddings](https://doi.org/10.1214/08-AOAS165)
- **Nuisance factors:** the "k days from" offset word precedes the concept token. Exp5 removes the per-offset means.
- **Synthetic benchmark.** The evaluation uses catalog targets and a validation-tuned analysis on the eligible subset of the generator's test export. A fixed-cohort sensitivity changes only the arc and sphere-family labels using their raw angular domains. [Catalog and sensitivity scores](../results/science/benchmark.csv) · [Known-domain controls](../results/science/analytic_controls.csv)

## Statistics

- Holm correction over the 6 co-primary alignment tests.
- Benjamini–Hochberg correction within the exploratory list.
- Clopper–Pearson CIs for rates over few datasets.
- Cluster bootstrap over the source generator's chunks of 25 clouds, which share N and the embedding draw.
- All seeds are fixed in `configs/base.yaml`. Monte Carlo seeds are crc32(dataset id) + seed. Exp5 repeats the main tests with seeds 1 and 2.
