# Literature review: topology of neural representation manifolds

Date: 2026-11-15. Author: Libor "Burny" Burian (compiled with Claude Code; every claim links to its source).

This file catalogues the sources, with the specific methods and numbers this project uses. The synthesis of the state of the art, the gap and the novelty are in [state-of-the-art-review.md](state-of-the-art-review.md). Facts were checked against the papers' own pages (arXiv abstract/HTML, PMC full text, GitHub READMEs) on 2026-11-15; *(summary)* marks facts checked only from a summary of a page.

## 1. Shapes found in neural activations (context)

The source project's [shape catalog](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability/blob/main/docs/shape_catalog.md) lists the shapes and where they were found. The ones that matter here are:
- **Weekday and month circles.** [Engels et al., "Not All Language Model Features Are One-Dimensionally Linear", ICLR 2025, arXiv:2405.14860](https://arxiv.org/abs/2405.14860) found circles in clusters of sparse-autoencoder features (GPT-2 layer 7, Mistral-7B layer 8) and steered along them. They identified the circles visually and through interventions; no persistent homology was used ([code, MIT](https://github.com/JoshEngels/MultiDimensionalFeatures)).
- **Helix of GPT-2 positions.** [Yedidia, "GPT-2's positional embedding matrix is a helix", LessWrong, 21 Jul 2023](https://www.lesswrong.com/posts/qvWP3aBDBaqXvPNhS/gpt-2-s-positional-embedding-matrix-is-a-helix). It reports that a 3-dimensional PCA subspace explains about 90% of the variance of gpt2-small's positional embeddings. Blog post, not peer reviewed.
- **Circles in grokked modular addition.** [Nanda, Chan, Lieberum, Smith, Steinhardt, "Progress measures for grokking via mechanistic interpretability", arXiv:2301.05217](https://arxiv.org/abs/2301.05217): embeddings of residues mod 113 lie on circles, one per key Fourier frequency k, so the order around a circle is k·a mod 113. [Zhong, Liu, Tegmark, Andreas, "The Clock and the Pizza", NeurIPS 2023, arXiv:2306.17844](https://arxiv.org/abs/2306.17844) separate circle-like ("clock") from disc-like ("pizza") solutions.
- **Number helices.** [Kantamneni & Tegmark, "Language Models Use Trigonometry to Do Addition", arXiv:2502.00873](https://arxiv.org/abs/2502.00873): numbers 0–99 lie on a generalised helix with Fourier periods T = 2, 5, 10 and 100. *Consequence for us:* non-cyclic numeric concepts (years, temperatures, ages) can still contain periodic components (value mod 10, mod 100), which could produce genuine loops.
- **Representation manifolds in general.** [Modell, Rubin-Delanchy, Whiteley, "The Origins of Representation Manifolds in Large Language Models", arXiv:2505.18235 (2025)](https://arxiv.org/abs/2505.18235), §2.3:
  - colour embeddings are "roughly arranged around a loop" in hue order;
  - a GPT-2-small layer-7 SAE feature for the years 1900–1999 shows "a clear one-dimensional curve" (a curve, not a loop);
  - calendar dates are also roughly arranged around a loop;
  - Engels et al.'s weekday and month circles show distortion in 3D.

  They warn that a 2D principal-component view can hide structure that runs through PC3. No persistent homology.
- **Supervised shape testing.** [Tiblias et al., "Hypothesis-Driven Feature Manifold Analysis in LLMs via Supervised Multi-Dimensional Scaling", arXiv:2510.01025](https://arxiv.org/abs/2510.01025) compare candidate shapes with supervised MDS; temporal features form circles, lines and clusters *(summary)*.
- **SAEs and concept manifolds.** [Bhalla et al., "Do Sparse Autoencoders Capture Concept Manifolds?", arXiv:2604.28119](https://arxiv.org/abs/2604.28119) (colours, years, temperature, age templates used by the source project).
- **Toy models of superposition.** [Elhage et al. 2022](https://transformer-circuits.pub/2022/toy_model/index.html): features arrange as digons, triangles, pentagons and tetrahedra (uniform polytopes).

The source project's own result ([README](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability#readme), commit 4c5f3b6): its fitter labels the Llama-3.1-8B weekday, month and grokked-embedding clouds "helix", GPT-2 positions "sphere", years and colours "cone". Its coarse shape class agrees with the literature on 7 of 12 preregistered datasets, which is not more often than a label-permutation null or than always answering "curve". A helix label is therefore not evidence against a closed loop, and this project checks the topology directly.

## 2. Manifold steering and Goodfire's Neural Geometry series (inspiration for "travelling around the hole")

- **Manifold steering.** [Wurgaft, Rager, Kowal, Shyam, Feucht, Bhalla, Haklay, Bigelow, Sarfati, McGrath, Lewis, Merullo, Goodman, Fel, Geiger, Lubana, "Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior", arXiv:2605.05115 (May 2026)](https://arxiv.org/abs/2605.05115). Blog post: [Steering Along Manifolds to Control Neural Networks (Goodfire, 7 May 2026)](https://www.goodfire.com/research/manifold-steering).

  Method, from the [HTML v1](https://arxiv.org/html/2605.05115v1):
  - prompts are "What day is k days after z?";
  - activations come from Llama 3.1 8B layer 28 and are reduced "to 64 dimensions via PCA";
  - cubic splines are fitted through the concept centroids;
  - linear steering interpolates (1−t)h0 + t·h1;
  - manifold steering moves along the spline, π_m(t) = s((1−t)u0 + t·u1);
  - days are "arranged in order around a loop".

  Reported results:
  - Manifold steering moves the output distribution along the behaviour manifold, while linear steering cuts across it. Geodesic correlation r: weekdays 0.99 vs 0.89; months 0.89 vs 0.53; letters 0.999 vs 0.71; ages 0.999 vs 0.36.
  - Settings beyond weekdays: months, letters, ages, in-context grid and cylinder graphs, and a Mountain Car world model.
  - The paper does not use persistent homology, as far as the parts we read show.
- **The Neural Geometry series** ([index](https://www.goodfire.com/research/neural-geometry)):
  - [The World Inside Neural Networks](https://www.goodfire.com/research/the-world-inside-neural-networks) (Geiger et al., 7 May 2026);
  - [Steering Along Manifolds to Control Neural Networks](https://www.goodfire.com/research/manifold-steering) (Wurgaft et al., 7 May 2026);
  - [A Geometric Calculator Inside a Neural Network](https://www.goodfire.com/research/a-geometric-calculator) (Feucht et al., 14 May 2026), on addition through circular number representations in Llama 3.1 8B;
  - [Can SAEs Capture Neural Geometry?](https://www.goodfire.com/research/can-saes-capture-neural-geometry) (Bhalla et al., 21 May 2026);
  - [Meandering on Manifolds: The Neural Geometry of Stories Over Time](https://www.goodfire.com/research/stories-in-space) (Bigelow et al., 23 Jun 2026);
  - [Uncovering Neural Geometry in Vision Models With Block-Sparse Featurizers](https://www.goodfire.com/research/bsf-vision) (Fel et al., 7 Jul 2026).

**How this project relates.** Manifold steering moves activations *along* a fitted manifold and shows the output follows the semantic order (Monday → Tuesday → …). That is a causal statement about travelling along the manifold. This project asks two *observational, topological* questions:
1. Is there a hole? We answer it with the exact topology of the fitted shape and with persistent homology.
2. Does the semantic order go around that hole exactly once? We measure the winding of a circular coordinate.

Steering around a detected hole is the natural causal follow-up and is listed as future work.

## 3. Persistent homology of neural representations

- [Naitzat, Zhitnikov, Lim, "Topology of Deep Neural Networks", JMLR 21(184):1–40, 2020](https://jmlr.org/papers/v21/20-345.html). Well-trained networks simplify the topology of the data, layer by layer, towards β0 = 1 and βk = 0.
  - Method: Vietoris–Rips homology at one fixed scale on a k-nearest-neighbour graph geodesic distance, with k and ε calibrated once on data whose Betti numbers are known.
- [Gardinazzi et al., "Persistent Topological Features in Large Language Models", ICML 2025 (PMLR 267), arXiv:2410.11042](https://arxiv.org/abs/2410.11042), [code](https://github.com/RitAreaSciencePark/ZigZagLLMs). Zigzag persistence of kNN flag complexes across layers (Llama-2-7B, Llama-3-8B, Mistral-7B, Pythia-6.9B), mostly H1. It is about how topology changes across layers, not about concept manifolds.
- [Jakubowski, Gašić, Zibrowius, "Topology of Word Embeddings: Singularities Reflect Polysemy", *SEM 2020](https://aclanthology.org/2020.starsem-1.11). A local, H0-based polysemy score; it measures local neighbourhoods, not global loops.
- [Ballester, Casacuberta, Escalera, "Topological Data Analysis for Neural Network Analysis: A Comprehensive Survey", arXiv:2312.05840](https://arxiv.org/abs/2312.05840). Survey of four areas: architecture, decision boundaries, internal representations, training dynamics.
- [Rieck et al., "Neural Persistence", ICLR 2019, arXiv:1812.09764](https://arxiv.org/abs/1812.09764). H0 persistence of weight graphs; this is weight space, not activation clouds.
- [Moisescu-Pareja et al., "On the geometry and topology of representations: the manifolds of modular addition", arXiv:2512.25060](https://arxiv.org/abs/2512.25060). Uses the reference Betti numbers disc (1,0,0), circle (1,1,0) and 2-torus (1,2,1), and computes Betti numbers of representations of modular-addition networks with Ripser. We found no null model in the text we read.
- [Tang, Wang, García-Redondo, Monod, "Topological Signatures of Grokking", arXiv:2605.06352](https://arxiv.org/abs/2605.06352). Reports "a sharp increase in both the maximum and total persistence of first homology (H1)" of embedding-matrix point clouds at grokking.
- [David & Fomin, "Context Is King: How In-Context Specification Shapes the Geometry of Concepts", arXiv:2607.24425](https://arxiv.org/abs/2607.24425). The main text reports "a dominant H1 loop for the imposed cycle, none for the tree".
  - Appendix I *(summary)*: a persistence ratio, the dominant H1 bar relative to random points with matched N and dimension, computed on centroid clouds of N = 7–12. Imposed cycles give 8.4×–11.5×; an imposed tree gives 2.0× in Gemma-31B (the random floor) but 4.7× in Qwen-27B.
  - It is framed as a "confirmatory diagnostic, not a primary test". This is the closest template for small-N loop tests.
- [shouvik-majumder/circular-features](https://github.com/shouvik-majumder/circular-features). A personal re-implementation of Engels et al. (README: "not the authors' code"); not peer reviewed.
  - Data: weekday × month prompts in GPT-2 small and Gemma-2-2B-IT.
  - Method: persistent homology with an ideal-torus positive control.
  - Findings: "The loops are deformed: 57% (weekdays) and 38% (months) of their variance is in the first circular harmonic", and "the joint representation is not a torus".

**Gap.** We found no peer-reviewed work that tests, with a null model, whether weekday or month representations have a significant H1 class *and* whether the semantic order winds once around it. We also found none that compares the exact topology of fitted parametric shapes with the persistent homology of the same clouds.

## 4. Neuroscience precedent: detecting rings and tori in population activity

- [Chaudhuri, Gerçek, Pandey, Peyrache, Fiete, Nat. Neurosci. 22:1512–1520 (2019)](https://doi.org/10.1038/s41593-019-0460-x); [code](https://github.com/FieteLab/SPUD_Analysis-of-manifold-structure-in-head-direction-data). A head-direction ring.
  - Pipeline in the released code: Isomap to 10 dimensions, then removal of points with few neighbours within the 1st percentile of pairwise distances, then Ripser with Z2 coefficients.
  - A long bar was judged significant by its persistence, without a shuffle test.
  - They note that persistent homology cannot distinguish topologically trivial manifolds with different geometries, such as a plane and a filled ball.
- [Gardner et al., "Toroidal topology of population activity in grid cells", Nature 602:123–128 (2022)](https://doi.org/10.1038/s41586-021-04268-7); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8810387/).
  - Preprocessing: z-scoring, the first 6 principal components, and fuzzy-kNN density downsampling to 1200 points.
  - Persistence: Vietoris–Rips persistent cohomology with Z47 coefficients.
  - Significance: 1000 shuffles; a bar is real if it is longer than the maximum lifetime over all shuffles.
  - Decoding: circular coordinates from cocycles smoothed by least squares.
- [Rybakken, Baas, Dunn, Neural Computation 31(1):68–93 (2019)](https://arxiv.org/abs/1711.07205). Blind decoding of head direction with persistent cohomology and circular coordinates.
- [de Silva, Morozov, Vejdemo-Johansson, "Persistent cohomology and circular coordinates", Discrete Comput. Geom. 45:737–759 (2011)](https://doi.org/10.1007/s00454-011-9344-x). The base algorithm: integer cocycle, then harmonic smoothing, then a circle-valued map.
- [DREiMac: Perea, Scoccola, Tralie, JOSS 8(91):5791 (2023)](https://doi.org/10.21105/joss.05791); [code, Apache-2.0](https://github.com/scikit-tda/DREiMac). A maintained implementation of sparse circular coordinates.

**What we reuse:**
- the max-over-null threshold of Gardner et al., with a design-matched null;
- coefficients Z_p with p = 47;
- circular coordinates from DREiMac;
- decoding a circle-valued coordinate per point and checking it against the semantic index. This last idea is the basis of our "travel around the hole" test.

## 5. Statistical inference for persistence diagrams

- **Universal null distribution.** [Bobrowski & Skraba, "A universal null-distribution for topological data analysis", Sci. Rep. 13:12274 (2023)](https://doi.org/10.1038/s41598-023-37842-2); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382541/); [code, GPL-3.0](https://github.com/primozskraba/PersistenceUniversality).
  - For a point p = (b, d) of the degree-k diagram (k ≥ 1), π(p) = d/b.
  - ℓ(p) = A·log log π(p) + B, with A = 1 for Vietoris–Rips and A = 1/2 for Čech, and B = −λ − A·L̄. L̄ is the mean of log log π over all points of the diagram, and λ is the Euler–Mascheroni constant.
  - Under the null, ℓ follows the left Gumbel distribution, F(x) = 1 − exp(−eˣ). The p-value is exp(−e^{ℓ(p)}).
  - Bonferroni correction divides α by |dgm_k|.
  - The paper's experiments use thousands of points or more and state that the tails converge slowly. It gives no minimum sample size.
  - The released code keeps only points with π > 1 before averaging. We do the same, since zero-persistence points have log log π = −∞.
  - The result is a conjecture, supported empirically; it fails for perturbed lattices and repulsive point processes.
  - *Consequence:* we use it descriptively on real clouds (N = 5–1496, and some clouds are deterministic grids) and calibrate it on synthetic clouds for each N bin.
- **Bootstrap confidence sets.** [Fasy, Lecci, Rinaldo, Wasserman, Balakrishnan, Singh, "Confidence sets for persistence diagrams", Ann. Statist. 42(6):2301–2339 (2014)](https://doi.org/10.1214/14-AOS1252). Subsampling and bootstrap bands with asymptotic, conservative guarantees. They are not informative at N ≲ 100.
- **Stability.** [Cohen-Steiner, Edelsbrunner, Harer, "Stability of Persistence Diagrams", DCG 37:103–120 (2007)](https://doi.org/10.1007/s00454-006-1276-5). The bottleneck distance between diagrams of distance functions is bounded by the Hausdorff distance between the point sets. Because the Hausdorff distance is not robust, one outlier can create or destroy features.
- **Permutation tests between groups of diagrams.** [Robinson & Turner, "Hypothesis testing for topological data analysis", J. Appl. Comput. Topol. 1:241 (2017)](https://doi.org/10.1007/s41468-017-0008-7).
- **Multiple testing with persistent homology.** [Vejdemo-Johansson & Mukherjee, Found. Data Sci. 4(4):667–705 (2022)](https://doi.org/10.3934/fods.2022018).

## 6. Comparing topology across clouds

- **Bottleneck and Wasserstein distances.** [Kerber, Morozov, Nigmetov, "Geometry Helps to Compare Persistence Diagrams", ACM JEA 22 (2017)](https://doi.org/10.1145/3064175). Hera is bundled in GUDHI.
  - Wasserstein distance sums over every near-diagonal (noise) point, so it grows with N. The bottleneck distance is driven by the largest mismatch.
  - We therefore compare clouds of very different N with the bottleneck distance on *significant* features only.
- **Vector representations.** Persistence images, [Adams et al., JMLR 18(8):1–35 (2017)](https://jmlr.org/papers/v18/16-337.html); persistence landscapes, [Bubenik, JMLR 16:77–102 (2015)](https://jmlr.org/papers/v16/bubenik15a.html).
- **Subsampling for large clouds.** [Chazal et al., "Subsampling Methods for Persistent Homology", ICML 2015](https://proceedings.mlr.press/v37/chazal15.html).

## 7. Practical choices for 3D point clouds

- **Alpha vs Rips.**
  - The alpha complex is a filtered subcomplex of the Delaunay triangulation. Its persistence equals that of the Čech complex (union of balls, nerve theorem), so in ℝ³ it is exact and cheap.
  - Vietoris–Rips is only interleaved with Čech ([de Silva & Ghrist, Algebr. Geom. Topol. 7:339–358 (2007)](https://doi.org/10.2140/agt.2007.7.339)) and has phantom classes.
  - Example of a phantom class: the Rips complex of points evenly spaced on a circle becomes a higher-dimensional sphere at larger scales ([Adamaszek & Adams, "The Vietoris–Rips complexes of a circle", Pacific J. Math. 290 (2017)](https://arxiv.org/abs/1503.03669)). Our own derivation: Rips on the regular 12-gon produces spurious H2 classes, while alpha does not. Our unit tests check this numerically.
  - Decision: alpha for H0/H1/H2 in 3D; Rips (ripser) for higher-dimensional checks, for H1 only.
- **Reference values (derived by us; checked numerically in our tests).** For a regular n-gon, the alpha (Čech) H1 bar is born at half the side length, R·sin(π/n), and dies at the circumradius R, so π = 1/sin(π/n). That gives 2.305 for n = 7 and 3.864 for n = 12.
  - These values are the *ceiling* for a loop made of n concept clusters. The ceiling depends on the number of distinct concepts, not on N.
- **Outliers and density.**
  - Distance to a measure (DTM): [Chazal, Cohen-Steiner, Mérigot, Found. Comput. Math. 11:733–751 (2011)](https://doi.org/10.1007/s10208-011-9098-0).
  - DTM filtrations: [Anai et al., SoCG 2019, arXiv:1811.04757](https://arxiv.org/abs/1811.04757). Implemented in GUDHI as `DTMRipsComplex`.
- **Genus and other invariants.** Standard algebraic topology ([Hatcher, *Algebraic Topology*, 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)).
  - For a closed connected orientable surface, χ = b0 − b1 + b2 = 2 − 2g, so g = b1/2. For an orientable surface with n boundary circles, χ = 2 − 2g − n, so the genus cannot be read off the Betti numbers alone.
  - In ℝ³ every closed embedded surface is orientable. Subcomplexes of ℝ³ have torsion-free homology (Alexander duality), so a check comparing different coefficient fields would be vacuous for alpha complexes in 3D.
  - A solid torus has Betti numbers (1,1,0), the same as a circle. Homology determines the homotopy type only up to such ambiguities.

## 8. Pitfalls specific to PCA projections

- [Antognini & Sohl-Dickstein, "PCA of high dimensional random walks with comparison to neural network training", NeurIPS 2018, arXiv:1806.08805](https://arxiv.org/abs/1806.08805). Projections of random walks onto PCA subspaces trace Lissajous curves. PC1–PC2 gives a horseshoe, and higher pairs give closed-looking figures, which could produce spurious H1.
- [Shinn, "Phantom oscillations in principal component analysis", PNAS 120(48):e2311420120 (2023)](https://doi.org/10.1073/pnas.2311420120). Smoothness and shifts produce oscillatory principal components.
- [Diaconis, Goel, Holmes, "Horseshoes in multidimensional scaling and local kernel methods", Ann. Appl. Stat. 2(3):777–807 (2008)](https://doi.org/10.1214/08-AOAS165).
- **Helix vs circle.** A helix is contractible (b1 = 0), but seen down its axis it looks like a circle. A closed loop of clusters with a small drift is fitted as a helix.
- **Small N and noise.** At N = 7–12 the barcode is sparse. A missing loop is not evidence that no loop exists without a power analysis.

**Mitigations used in this project:**
- Repeat the H1 test on the top-5 and top-10 principal components and on full-dimensional cosine distances.
- Require the alignment of the circular coordinate with the semantic order to survive in the top-10 principal components.
- Use design-matched nulls, for example a cluster-centre null for prompt-template designs.
- Run a synthetic power simulation before freezing the decision rules.

## 9. Tools (checked on PyPI on 2026-11-15; installed in this repository's uv environment)

| Package | Version | Licence | Use here |
|---|---|---|---|
| [GUDHI](https://gudhi.inria.fr) | 3.13.0 | MIT; AlphaComplex GPL-3.0 (CGAL) | alpha complexes, bottleneck distances |
| [ripser.py](https://github.com/scikit-tda/ripser.py) ([Tralie et al., JOSS 2018](https://doi.org/10.21105/joss.00925); [Bauer, J. Appl. Comput. Topol. 2021](https://doi.org/10.1007/s41468-021-00071-5)) | 0.6.15 | MIT | Rips persistence in higher dimensions, cocycles |
| [persim](https://github.com/scikit-tda/persim) | 0.4.1 | MIT | diagram distances, plotting |
| [DREiMac](https://github.com/scikit-tda/DREiMac) | 0.3.2 | Apache-2.0 | circular coordinates; requires Python < 3.12, which is why the project uses Python 3.11 |
| giotto-tda | 0.6.2 | AGPL-3.0 | not used: no wheels beyond Python 3.12, and it pins scikit-learn 1.3.2 |

