# Math fact-check: persistent homology and mechanistic interpretability

Libor "Burny" Burian, 2026-11-20. Logged as deviation [D12](../deviations.md).

> **Superseded in part** by the independent second check, [math-fact-check-2.md](math-fact-check-2.md) (D13). It found that this review's "9,000–50,000 points" for the universal null is wrong (the simulations use 10⁴–10⁶), and that torsion-freeness in ℝ³ is Hatcher Cor. 3.46, not Cor. 3.45. This file is kept unchanged below as a record.

**Question.** Is the math in this repository used with the definitions, methods and conventions accepted in persistent homology (topological data analysis, TDA) and in mechanistic interpretability (MI)?

**Answer in brief.** Mostly yes. The core machinery (alpha persistence, the universal null, the Monte Carlo max-statistic null, the Gaussian samplers, circular coordinates, the traversal statistics, the multiple-testing procedures) matches its sources. Two things were wrong in code, and they affected only descriptive invariants: Method B read b0 at a different scale from b1 and b2, and called a Betti-number label a "homotopy class". One Method A rule (spindle torus) had wrong Betti numbers, in a branch the data never reach. Several sentences overstated or mis-cited results; they are corrected below with sources. **No preregistered verdict changes.**

## Method

- **Read:** the math code (`src/neurotopo/tda/`, `stats/`, `analytic/`, `geometry/pca.py`), every experiment that uses it (Exp2–Exp8, the loop and void searches, simulated steering), the [glossary](../../docs/glossary.md), [methodology](../../docs/methodology.md), [worked example](../../docs/worked_example.md), [exact topology of the families](../../docs/analytic_topology.md), [preregistration](../preregistration.md), [literature review](../literature-review.md), [state-of-the-art review](../state-of-the-art-review.md), the paper and the README.
- **Checked against the libraries actually installed:** GUDHI 3.13.0 (`AlphaComplex.create_simplex_tree` docstring, and a two-point example) and DREiMac 0.3.2 (`dreimac/emcoords.py`, `get_cover_radius`).
- **Checked against primary sources** (papers, official docs, authors' code). The sources behind every claim marked wrong, overstated or mis-cited, and every MI attribution, were opened and read. Hatcher's theorem numbers were looked up in the [PDF](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf) (Thm 2.44, Cor. 3.45). The textbook and standard-method references (Edelsbrunner & Harer, Mardia & Jupp, Holm, Benjamini & Hochberg, Clopper & Pearson, Fagerland et al., Zomorodian & Carlsson, Nichols & Holmes) are cited for standard results and were identified by title and DOI, not re-read. Every DOI was resolved through the [DOI registry](https://www.doi.org/) and [Crossref](https://api.crossref.org/).
- **Numerical checks**, now unit tests: `tests/test_tda.py`, `tests/test_invariants.py`, `tests/test_analytic.py`.
- Where a statement is our own derivation, the table says so and names the test that checks it.

Verdicts: **holds**; **fixed** (was wrong, now corrected); **overstated → fixed**; **mis-cited → fixed**; **note** (correct, a caveat added).

## A. Persistent homology (TDA)

### Complexes and filtrations

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| GUDHI's alpha filtration values are squared radii, so the code takes √ (`tda/diagrams.py`) | holds | [GUDHI `create_simplex_tree(..., output_squared_values=True)`](https://gudhi.inria.fr/python/latest/delaunay_complex_ref.html); two points at distance 2 give 1.0 (`test_alpha_radius_units_two_points`) |
| "The alpha complex is exact Čech" (paper, methodology, literature review, `diagrams.py`) | overstated, mis-cited → fixed | The alpha complex is a smaller complex. At every radius it is homotopy equivalent to the union of balls ([Edelsbrunner 1995](https://doi.org/10.1007/BF02574053)), and its filtration is collapse-equivalent to the Čech filtration, so the persistence diagrams agree ([Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991), [arXiv](https://arxiv.org/abs/1312.1231)). The paper cited [de Silva & Ghrist 2007](https://doi.org/10.2140/agt.2007.7.339) for it; that paper proves a Rips–Čech interleaving (Thm 2.5) and does not treat alpha complexes. |
| A non-Gabriel edge "enters together with a triangle" (glossary) | note → fixed | GUDHI: it gets "the minimum of the filtration values of the codimension 1 cofaces that make it not Gabriel" ([GUDHI C++ doc](https://gudhi.inria.fr/doc/latest/group__alpha__complex.html)); in 3D a triangle can itself enter with a tetrahedron. |
| Rips is only interleaved with Čech and has phantom classes; Rips on a regular 12-gon has H2 (literature review, `test_rips_12gon_has_phantom_h2_alpha_does_not`) | holds | [de Silva & Ghrist 2007](https://doi.org/10.2140/agt.2007.7.339), Thm 2.5; [Adamaszek & Adams 2017](https://doi.org/10.2140/pjm.2017.290.1), Thm 4.3: for k/n = l/(2l+1) the complex is a wedge of n − 2k − 1 copies of S^{2l}; for n = 12, k = 4 that is three 2-spheres. |
| Rips diameters ÷ 2 give radii comparable with alpha (`rips_diagrams`) | holds | Two balls of radius r meet iff their centres are ≤ 2r apart (definition of the Čech/Rips edge, [Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. III). π = d/b is unchanged by this rescaling. |
| The old GUDHI link `alpha_complex_user.html` | fixed | It returns 404; the page moved to [delaunay_complex_user.html](https://gudhi.inria.fr/python/latest/delaunay_complex_user.html). |
| "Subcomplexes of ℝ³ have torsion-free homology, so a check comparing coefficient fields would be vacuous" (literature review, plan) | half wrong → fixed | The first half holds ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), §3.3, Alexander duality). Persistence can still depend on the field through torsion in *relative* homology: in ℝ³, H0 and H2 bars are field-independent but H1 bars can change ([Obayashi & Yoshiwaki 2023](https://doi.org/10.1007/s00454-023-00544-7), [arXiv:1911.11350](https://arxiv.org/abs/1911.11350); 1 of 10,000 random alpha filtrations had such torsion). A Möbius band shows it: Z/2 gives H1 bars [0,1), [1,∞), Z/3 gives [0,∞) (`test_persistence_can_depend_on_the_coefficient_field`). |

### Significance of bars

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| Universal null: π = d/b; ℓ = A log log π − λ − A·L̄; A = ½ (Čech/alpha), 1 (Rips); p = exp(−e^ℓ); Bonferroni within a diagram (`tda/nulls.py`) | holds | [Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2) ([full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382541/)); `AVALS = {ALPHA: 0.5, RIPS: 1}` in the [authors' code](https://github.com/primozskraba/PersistenceUniversality) (`modules/PDplot.py`). The paper itself uses the alpha complex as a stand-in for Čech. |
| L̄ is averaged over bars with π > 1 (`universal_pvalues`) | note | The authors' plotting code filters π > 1; the paper averages over all of dgm_k. They agree here, because zero-length bars are dropped and every remaining finite bar has π > 1. |
| Squared or unsquared filtration values give the same universal-null p-values | holds | Our derivation: log log(π²) = log 2 + log log π, and the centring by L̄ cancels log 2 (also noted in [exp8_audit3.md](../exp8_audit3.md)). |
| The universal null is descriptive here | holds | Its examples use 9,000–50,000 points ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)); our clouds have 5–1,496. |
| Monte Carlo p = (1 + #{null maxima ≥ π}) / (M + 1) | holds | [Phipson & Smyth 2010](https://doi.org/10.2202/1544-6115.1585) |
| Comparing every bar with the null distribution of the *maximum* controls the family-wise error over bars; for non-top bars it is conservative (`mc_pvalues`, loop and void searches) | holds | The max-statistic method ([Nichols & Holmes 2002](https://doi.org/10.1002/hbm.1058)) |
| The Monte Carlo null is "in the style of" / "as in" Gardner et al.; max-over-shuffle thresholds are "the practical standard" (glossary, methodology, README, paper, SotA review) | overstated → fixed | [Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7), Methods: they pooled the bars of 1,000 shuffles and took the longest lifetime (death − birth) per dimension, which they call a heuristic. Ours is an adaptation (ratio π, one maximum per null draw, a p-value), now described as such. |
| Gaussian null: rows of Z·X_c/√(N−1) are i.i.d. N(0, sample covariance); the Gram-matrix factor gives the same PCA scores up to rotation (`GaussianNull`) | holds | Linear combinations of Gaussians: row i is Σ_j Z_ij x_j/√(N−1), with covariance X_cᵀX_c/(N−1). With X_c = U S Vᵀ and L = U S, Z X_c = Z L Vᵀ, an isometry. Checked in `test_gaussian_null_covariance_matches_input`. |
| Cluster-centre null keeps residuals and matches the covariance of the means | holds | Same argument with the n concept means; `test_cluster_centre_null_keeps_within_cluster_residuals` |
| "Significant if π exceeds the null's 95th percentile" (paper, glossary) | note → fixed | The implemented, preregistered rule is p < 0.05. It can differ from "above q95" by one null draw at the boundary; both texts now give the p-value rule. |
| The false-loop rate rising with N "is consistent with the dimension-dependent growth of maximal noise persistence" (paper) | mis-cited → fixed | [Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232), Thm 3.1: the maximal π of k-cycles is Θ((log n / log log n)^{1/k}). The rate depends on k only; the dimension d enters the constants. It is proved for densities bounded above and below on a compact set, which excludes Gaussians. |

### Invariants (Method B)

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| "χ(r_c) = b0 − b1 + b2 is the Euler characteristic of one complex, not a mix of scales" (`tda/invariants.py`) | **wrong → fixed (code)** | `betti_at_scale` passed the b0 rule's value through, so `b0_rc` equalled `b0` for all 44 clouds, while b1, b2 were read at r_c. b0(r_c) is now the number of pieces of the alpha complex at r_c: single linkage at edge length 2 r_c, since H0 of the union of balls at radius r is the graph of edges ≤ 2r (`test_b0_at_radius_equals_alpha_h0_alive`, `test_betti_at_scale_reads_all_three_numbers_at_one_radius`). b1, b2 count significant bars only, so χ(r_c) is the χ of the signal, not of the full complex; now stated. |
| Fallback r_c = the b0 cut | **unit error → fixed (code)** | The cut is an MST edge length (a diameter); r_c is a radius. The fallback is now half the cut (`test_scale_invariants_fallback_is_a_radius`). |
| "Homotopy class" read from Betti numbers: contractible (1,0,0), sphere (1,0,1), torus (1,2,1) (`invariants.py`, glossary, site) | **wrong → fixed (code)** | Betti numbers do not determine a homotopy type: the torus and S² ∨ S¹ ∨ S¹ both have (1,2,1), and (1,0,0) only says acyclic ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 0 and 2). Now a Betti label: acyclic, circle-like, sphere-like, torus-like (`test_betti_labels_do_not_claim_a_homotopy_type`). |
| "Homology cannot tell a circle from an annulus or a solid torus" (glossary, literature review, preregistration) | misattributed → fixed | Those spaces are homotopy equivalent, so no homotopy invariant can separate them ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 0). The limitation specific to Betti numbers is the one in the row above. The preregistration stays frozen; D12 records the correction. |
| r_c = √(birth · death) | holds | The midpoint of the bar on a log scale, consistent with the multiplicative persistence π ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)); a convention, stated as such. |
| Genus from χ = 2 − 2g only for closed surfaces; χ = 2 − 2g − n with n boundary circles | holds | Classification of compact surfaces ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 2; [Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. II) |
| Euler–Poincaré formula χ = Σ(−1)^k b_k | holds | [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), Thm 2.44 |

### Closed-form values and display constructions

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| A 3-point loop has π = 1/sin(largest angle) ≤ 2/√3; obtuse triangles make no loop (glossary, worked example) | holds | Our derivation: the loop is born at half the longest side c and dies at the circumradius R, and c = 2R sin C (law of sines); an obtuse triangle's longest edge is not Gabriel. Checked in the worked example. |
| A regular k-gon of points has π = 1/sin(π/k) (`test_regular_ngon_ratio`) | holds | Same derivation (born at R sin(π/k), dies at R). |
| "These values are the ceiling for a loop made of n concept clusters"; "the power for 7 clusters is bounded" (literature review, paper) | **wrong → fixed** | They are the values for n point-like centres. Spread lets neighbouring clusters connect earlier, so a ring of noisy clusters can exceed them (`test_cluster_ring_can_exceed_point_polygon_ratio`). The paper's power statement now rests on the power simulation. |
| A regular octahedron's void has π = √(3/2) (paper) | holds | Our derivation: faces (side √2) enter at circumradius √(2/3), the void dies at the circumradius 1. |
| Euler count of the 6-feature toy model, 6 − 12 + 8 = 2 = 1 − 0 + 1 (paper, voids report) | holds | Euler–Poincaré formula ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), Thm 2.44) for the complex just after the faces enter (no tetrahedra yet). |
| Loop localisation: a loop that dies at or below the connect radius lies inside one concept's cluster (glossary, worked example, `exp7_audit.py`) | holds | Our derivation: below that radius the union of balls is a disjoint union of the per-concept unions, so the persistence module on that interval is a direct sum, and by uniqueness of the barcode ([Zomorodian & Carlsson 2005](https://doi.org/10.1007/s00454-004-1146-y)) its bars are the per-concept bars. |
| Representative loop: the creating edge closed by the shortest earlier path represents the new class up to older ones (`alpha_h1_cycles`) | holds | The cycle exists at the birth simplex's entry and not before; representatives are not unique ([Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. VII). Display only. |
| Representative void: flood fill from the death tetrahedron through not-yet-entered triangles gives a shell that is filled exactly at the death radius (`alpha_h2_voids`) | holds | In ℝ³ a void is a bounded complementary region (Alexander duality, [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), Cor. 3.45). By the elder rule ([Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. VII), a region's oldest class dies when its last tetrahedron enters, so all its tetrahedra enter by then. Checked in the void-shell tests. |
| The death tetrahedron's circumcentre is uncovered by a ball of radius d − b at the birth radius | holds | The empty-circumsphere property of Delaunay tetrahedra ([Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. III); `test_void_centres_are_empty_and_inside_their_shell` |
| Harmonic smoothing of a one-cut 7-cycle gives 7 equal steps of 1/7 turn (worked example) | holds | [de Silva, Morozov & Vejdemo-Johansson 2011](https://doi.org/10.1007/s00454-011-9344-x) (least-squares smoothing of an integer cocycle); the by-hand minimisation in the worked example is correct. |

### Circular coordinates (DREiMac)

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| `standard_range=True` refuses classes whose Rips death is less than twice their birth, which guarantees a non-trivial Čech class (`tda/circular.py`, paper, glossary) | holds | Installed DREiMac 0.3.2, `emcoords.get_cover_radius`: `start = 2*cohomdeath_rips if standard_range else cohomdeath_rips`, error "too short" if start > end; docstring "non-trivial cohomology class in the Cech complex" ([DREiMac](https://github.com/scikit-tda/DREiMac); [Perea, Scoccola & Tralie 2023](https://doi.org/10.21105/joss.05791)). DREiMac's `cohomdeath` is the homological birth. |
| `cocycle_idx = 0` is the most persistent class | holds | Classes are sorted by `argsort(birth − death)`, i.e. by death − birth (additive persistence), descending. Note: this ranking can differ from the π ranking used for significance; Exp3 reports whether the two bars overlap (preregistration 4.6). |
| Diagrams in Rips diameters, halved for comparison | holds | `self._r_cover = self._rips_threshold / 2` in `emcoords.py` |

### Method A: exact topology of the families

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| Betti numbers of S¹, S², T², contractible spaces, point sets; frustum = annulus ≃ S¹; arc endpoint chord 2r sin(π(1 − f)) | holds | [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 0 and 2; chord formula: our derivation, `test_arc_closed_vs_open` |
| Closed surfaces embedded in ℝ³ are orientable | holds | Alexander duality and its corollaries, [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), §3.3 |
| Horn torus ≃ S² ∨ S¹, (1, 1, 1) | holds | Pinching a longitude of T² attaches a disc along an essential circle ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 0, cell attachment) |
| Spindle torus has Betti numbers (1, 1, 1) (`analytic/topology.py`) | **wrong → fixed (code)** | Its image is an outer and an inner sphere glued at the two axis points, ≃ S² ∨ S² ∨ S¹: (1, 1, 2), χ = 2; two bounded complementary regions = two voids (Alexander duality). A dense sample shows one long H1 bar and two long H2 bars. `test_horn_and_spindle_torus`. The source caps the torus ratio at 0.95, so no result used this branch. |
| "A cone surface with an apex deformation-retracts to a point, so it is a disc" (analytic_topology.md) | non sequitur → fixed | A deformation retraction to a point shows only that it is contractible; it is a disc because its parametrisation is polar coordinates with the apex as centre. |

### Other

| Claim (where) | Verdict | Source or evidence |
|---|---|---|
| Wasserstein distances grow with N, cited to Kerber, Morozov & Nigmetov 2017 (`exp4_similarity.py`, literature review) | mis-cited → fixed | That paper is an algorithms paper (Hera). The statement holds by the definition of the p-Wasserstein distance, which sums over all matched points ([Cohen-Steiner et al. 2010](https://doi.org/10.1007/s10208-010-9060-6)). |
| Bottleneck distance on significant bars only (Exp4) | note | Thresholding gives up the stability theorem ([Cohen-Steiner, Edelsbrunner & Harer 2007](https://doi.org/10.1007/s00454-006-1276-5)): a bar near the threshold can drop out of one diagram and not the other. Exp4 was already reported as exploratory and uninformative; the caveat is now in the [Exp4/Exp5 report](../exp4_exp5.md). |
| Full-dimensional Rips on "cosine distance" (Exp5) | note | 1 − cos is not a metric ([SciPy `cosine`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cosine.html) defines it as a dissimilarity) and is about angle²/2 for small angles, so its π is roughly the square of the angular π and not comparable with Euclidean π. Rips accepts any dissimilarity; the check is descriptive. Documented in code, methodology and the [Exp4/Exp5 report](../exp4_exp5.md). |
| Persistence diagrams are invariant to what `fit_frame` does except the projection ("rigid motions", methodology) | note → fixed | `fit_frame` also flips signs (reflections); "isometries" is the right word, and π is also scale-invariant. |

## B. Statistics

| Procedure (where) | Verdict | Source |
|---|---|---|
| Holm step-down (`stats/tests.py::holm`) | holds | [Holm 1979](https://www.jstor.org/stable/4615733); `test_holm_bh_and_ci` |
| Benjamini–Hochberg (`bh`) | holds | [Benjamini & Hochberg 1995](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) |
| Clopper–Pearson exact CI | holds | [Clopper & Pearson 1934](https://doi.org/10.1093/biomet/26.4.404); [SciPy `binomtest(...).proportion_ci(method="exact")`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html) |
| Exact McNemar = binomial test on the discordant pairs | holds | [Fagerland, Lydersen & Laake 2013](https://doi.org/10.1186/1471-2288-13-91) (who also note it is conservative) |
| Circular means arg Σ e^{iθ} | holds | [Mardia & Jupp 2000](https://doi.org/10.1002/9780470316979), ch. 2 |
| Alignment R is invariant to rotation and reflection, so the exact permutation p over 7! assignments has minimum 14/7! = 1/360 | holds | Our derivation (a cyclic relabelling multiplies the sum by a unit phase; s = ±1 covers reflection); `test_seven_cluster_ring_end_to_end` |
| Max-over-frequency permutation test for residues accounts for choosing k | holds | Max-statistic permutation ([Nichols & Holmes 2002](https://doi.org/10.1002/hbm.1058)) |
| Cyclic-order probability 2/(n−1)! | holds (conservative) | Our derivation: n!/(2n) circular orderings up to rotation and reflection; the code's match criterion also requires every step to go the same way with winding ±1, which is stricter. |
| Winding number = (1/2π) Σ wrapped steps | holds | The degree of a closed curve in S¹ ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), §1.1), valid when consecutive concept angles differ by less than π, which is what the rule checks. |
| H1-A p-value = the smallest alignment p over a fit's hole angles (`exp3_cyclic.a_pvalue`) | note (not changed) | A minimum over two torus angles would need a correction. It has no effect: all three primary fits are helices (H1-A p = 1), and no fit is a torus. Changing a preregistered rule for no effect would add a deviation without benefit. |

## C. Mechanistic interpretability and related sources

Terms are used in the field's sense: "residual stream", "hidden states", "feature", "superposition" (only for the toy models of [Elhage et al. 2022](https://arxiv.org/abs/2209.10652)), "probe/decoder", "manifold", and "steering" for interventions that change the forward pass ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)). No observational result is presented as causal: the paper calls steering "the causal question" and lists "No causal evidence yet". 27 attributions were checked against the sources; 20 hold. The 7 others, all fixed:

| Claim (where) | Verdict | What the source says |
|---|---|---|
| Engels et al. found circles "visually and through interventions" and "steered along them" (literature review, SotA review) | overstated → fixed | They clustered SAE decoder vectors by cosine similarity, scored clusters by separability and mixture indices, and patched with circular probes in Mistral-7B and Llama-3-8B; the paper never steers along the circles ([Engels et al. 2024](https://arxiv.org/abs/2405.14860)). |
| Wurgaft's r = 0.99 vs 0.89, 0.89 vs 0.53, 0.999 vs 0.71, 0.999 vs 0.36 presented as manifold vs linear steering (literature review) | wrong context → fixed | They are correlations between activation distances and output-manifold geodesics, measured "before we perform any interventions"; the steering comparison uses E_BC ([Wurgaft et al. 2026](https://arxiv.org/html/2605.05115v1)). |
| Chaudhuri et al. cited for "shuffle nulls and circular-coordinate decoding" (paper, SotA review) | overstated → fixed | Chaudhuri judged the ring by bar length and decoded with a fitted spline (SPUD) ([Chaudhuri et al. 2019](https://doi.org/10.1038/s41593-019-0460-x)); cohomological decoding is from [Rybakken, Baas & Dunn 2019](https://doi.org/10.1162/neco_a_01150), now cited. |
| Max-over-shuffle thresholds are "the practical standard" (paper, SotA review) | overstated → fixed | Gardner et al. call theirs "a heuristic" ([Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7)). |
| "We found no work that tests, with a null model, ..." (paper) | overstated → fixed | The literature review limited this to peer-reviewed work; a preprint compares the persistence ratio of imposed cycles with random points ([David & Fomin 2026](https://arxiv.org/abs/2607.24425)). Both now stated. |
| City-truth statements and line-break counts used without citation (paper) | missing → fixed | [Marks & Tegmark 2024](https://arxiv.org/abs/2310.06824); [Gurnee et al. 2025](https://transformer-circuits.pub/2025/linebreaks/index.html) ([arXiv:2601.04480](https://arxiv.org/abs/2601.04480)). |
| Nanda et al. without venue (paper bibliography) | minor → fixed | ICLR 2023 ([Nanda et al. 2023](https://arxiv.org/abs/2301.05217)). |

"Simulated steering" moves stored activations and reads them with decoders; no forward pass is run, so it is a correlational decoder read-out, not steering in the sense of [Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115) or activation addition. The preregistration already said "correlational, not causal"; [methodology.md](../../docs/methodology.md) and the README now say so too, and that it is postponed.

## D. What changed

- **Code:** `tda/invariants.py` (b0 at r_c, radius fallback, Betti label, `scale_invariants`), `experiments/exp2_invariants.py` (uses it; column `betti_label_rc`), `analytic/topology.py` (spindle torus), report and site code (column and label names), docstrings with sources in `tda/diagrams.py`, `tda/nulls.py`, `experiments/exp4_similarity.py`, `experiments/exp5_robustness.py`.
- **Tests:** 8 new tests (listed in the tables above, plus `test_method_a_reports_true_homotopy_types`).
- **Text:** glossary, methodology, worked example, exact-topology page, literature and state-of-the-art reviews, plan, Exp2 report template, paper and bibliography, README.
- **Results:** Exp2 regenerated (`uv run python run.py exp2 report site`). Only the fallback `r_c`, `b0_rc`, `chi_rc`, `genus_rc` and `betti_label_rc` can change, and a diff of the old and new `results/exp2/invariants.csv` confirms that every other column is identical ([invariants table](../exp2_invariants.md)). The month clouds, whose loop runs through the month clusters (localisation audit, [exp7_audit.md](../exp7_audit.md)), now read as one piece at r_c, as they should. No preregistered verdict depends on them.

## E. Learnings

- **Docstrings can assert more than the code does.** The "one complex" claim in `invariants.py` was never tested; a test that compares b0 at r_c with the alpha H0 bars alive at r_c would have caught it. Every invariant now has such a test.
- **Homotopy language needs the space, not its Betti numbers.** Method A knows the space and may name its homotopy type; Method B only has homology and should say "-like".
- **Closed forms for point configurations are not bounds for noisy ones.** 1/sin(π/n) describes n points; the test of a noisy ring shows it is not a ceiling.
- **Cite the theorem that says it.** Three citations pointed at papers about neighbouring results (de Silva & Ghrist for alpha complexes, Kerber et al. for Wasserstein growth, Bobrowski et al. for a dimension dependence they do not prove). Reading the theorem statements, not only the abstracts, found them.
- **Library docs move.** The GUDHI alpha-complex page moved; links to documentation are now checked when they are cited.
