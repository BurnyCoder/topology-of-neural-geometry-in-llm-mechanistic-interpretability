# Independent math fact-check: persistent homology and mechanistic interpretability

Libor "Burny" Burian, 2026-11-20. Logged as deviation [D13](../deviations.md).

**Question.** Are the definitions, theorems, methods, statistics and citations in this repository used the way persistent homology (topological data analysis, TDA) and mechanistic interpretability (MI) use them? Are there factual errors, and does every claim have a source?

**Independence.** This check did not rely on the earlier audits or on the first fact-check ([math-fact-check.md](math-fact-check.md), D12). Every claim was traced to its primary source again. Where the two checks disagree, this one says so; the disagreements are in the "Fixed" table below.

**Answer in brief.** The core mathematics is correct and used in the accepted way. Nothing found changes a code path, a number, a figure or a verdict; `results/` is untouched. The errors were of three kinds:
- **Mis-attributions:** the bottleneck implementation, a Hatcher corollary number, the universal null's sample sizes, the assumptions of a random-topology theorem, Delaunay complexity on a helix, and PCA horseshoes.
- **Wording that did not match the implementation:** the margin, the cyclic-order p, the DREiMac guarantee, paraboloid sampling, and a steering docstring.
- **Interpretations stated more strongly than the evidence:** single-cause explanations, and calibration from 3 controls.

All are fixed.

## Method

- **Read:**
  - all of `src/neurotopo/{tda,analytic,stats,geometry,steering}`;
  - the experiments that carry math: Exp0, Exp3, Exp4, coords, audit, audit3;
  - `paper/main.template.tex` and `references.bib`, the README template;
  - `docs/{glossary,methodology,analytic_topology}.md`, the worked-example template;
  - the literature and state-of-the-art reviews, the preregistration, the deviations and every report template.
- **Installed libraries:**
  - DREiMac 0.3.2 source: `emcoords.py::get_cover_radius`, the `circularcoords.py` defaults and docstrings.
  - GUDHI 3.13.0: `gudhi.bottleneck_distance.__module__` is `gudhi.bottleneck`.
- **Primary sources:** arXiv PDF and HTML, PMC full text, publisher pages, the Crossref API, the authors' code, and official documentation. Theorem, corollary and page numbers were read in the source itself. Three source-checking passes quoted the exact statements; quotes are short, and statements below are paraphrased.
- **Numerical check:** one new unit test, `tests/test_circular_stats.py::test_cyclic_order_p_is_an_upper_bound`.

**Verdicts:**
- **verified:** correct as stated, source confirmed.
- **fixed:** wrong, now corrected.
- **imprecise → fixed:** true in spirit, wording now exact.
- **overstated → fixed:** stated more strongly than the evidence.

## Verified (no change needed)

| Claim (where) | Source checked |
|---|---|
| The alpha complex is homotopy equivalent to the union of balls at every radius (`tda/diagrams.py`, glossary, paper) | [Edelsbrunner 1995](https://doi.org/10.1007/BF02574053), Thm 3.2 (balls in general position) |
| Alpha and Čech filtrations have the same persistence | [Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991): collapses Čech ↘ Delaunay–Čech ↘ Delaunay (Thm 5.10), persistence isomorphism (Cor. 6.1), general position (Def. 4.2) |
| Rips is only interleaved with Čech | [de Silva & Ghrist 2007](https://doi.org/10.2140/agt.2007.7.339), Thm 2.5: R_ε ⊂ Č_ε′ ⊂ R_ε′ for ε′/ε ≥ √(2d/(d+1)), with Čech balls of radius ε/2 |
| Rips on 12 evenly spaced points has three 2-spheres at some scale | [Adamaszek & Adams 2017](https://doi.org/10.2140/pjm.2017.290.1), Thm 4.3: wedge of n − 2k − 1 copies of S^{2l} when k/n = l/(2l+1); n = 12, k = 4 gives S²∨S²∨S² (closed ≤ convention) |
| GUDHI's alpha filtration values are squared radii; non-Gabriel rule | [GUDHI reference](https://gudhi.inria.fr/python/latest/delaunay_complex_ref.html) (`output_squared_values=True` default); [GUDHI C++ doc](https://gudhi.inria.fr/doc/latest/group__alpha__complex.html), verbatim: the minimum of the filtration values of the codimension-1 cofaces that make it not Gabriel |
| Ripser filtration values are pairwise distances (diameters), hence ÷ 2 for radii; `n_perm` is greedy furthest-point sampling | [ripser.py source](https://github.com/scikit-tda/ripser.py) (`ripser.cpp` edge value = `dist`; `get_greedy_perm`); [Tralie, Saul & Bar-On 2018](https://doi.org/10.21105/joss.00925) |
| In ℝ³, H0 and H2 persistence are field-independent; H1 can depend on the field (Möbius band) | [Obayashi & Yoshiwaki 2023](https://doi.org/10.1007/s00454-023-00544-7) ([arXiv v3](https://arxiv.org/abs/1911.11350)): Cor. 1 (D₀), Cor. 2 (D_{M−1} in ℝ^M), Example 1 (Möbius band); `test_persistence_can_depend_on_the_coefficient_field` |
| χ = Σ(−1)ⁿ bₙ | [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), Thm 2.44 (p. 146) |
| Spindle torus voids ↔ bounded complementary regions | Hatcher Cor. 3.45 (Alexander duality, p. 255) |
| Horn torus ≃ S²∨S¹; spindle torus ≃ S²∨S²∨S¹, Betti (1, 1, 2) | T²/C ≅ S² with two points identified ≃ S²∨S¹ (Hatcher Example 0.8; source now cited in `analytic/topology.py`); two spheres glued at two points ≃ S²∨S²∨S¹ (our derivation) |
| Betti numbers do not determine homotopy type; (1,0,0) is acyclic, not necessarily contractible | standard (Hatcher ch. 0 and 2); `test_betti_labels_do_not_claim_a_homotopy_type` |
| Void representatives via Alexander duality | [Edelsbrunner & Harer 2010](https://doi.org/10.1090/mbk/069), ch. V "Duality", §V.4 Alexander duality |
| π = death/birth; ℓ = A·log log π + B, B = −λ − A·L̄, A = ½ Čech (alpha), 1 Rips; left-Gumbel p = exp(−e^ℓ); Bonferroni over the diagram; mean over bars with π > 1 | [Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2), eqs. (1), (2), (4), Conjecture 3; [authors' code](https://github.com/primozskraba/PersistenceUniversality/blob/main/modules/PDplot.py) `AVALS = {ALPHA: 0.5, RIPS: 1}`, filter π > 1 |
| The universal null is a conjecture, tails converge slowly, and it fails for perturbed lattices and repulsive processes | Bobrowski & Skraba 2023, Conjectures 1–3, Discussion, Supp. §3.5 |
| Std of log log π of noise bars ≈ (π/√6)/A, i.e. 2.57 for alpha, 1.28 for Rips (`tests/test_tda.py`) | left-Gumbel std = π/√6 (our derivation) |
| Monte Carlo p = (1 + b)/(M + 1) | [Phipson & Smyth 2010](https://doi.org/10.2202/1544-6115.1585), §4 (for random permutations with replacement they call it valid but slightly conservative) |
| Gardner et al.: 1,000 shuffles, barcodes concatenated, the single longest lifetime per dimension as the threshold, called "a heuristic"; Z₄₇; 6 PCs; 1,200 points; least-squares smoothing of cocycles | [Gardner et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8810387/), Methods |
| Gaussian null: rows of Z·X_c/√(N−1) are N(0, cov X); the low-rank factor L with L Lᵀ = X_c X_cᵀ preserves PCA scores up to rotation (`tda/nulls.py`) | linear algebra: X_c = U S Vᵀ, L = U S R, so Z X_c and Z L differ by a right orthogonal factor (our derivation); `test_gaussian_null_covariance_matches_input` |
| b0 at radius r = single linkage at edge length 2r; an alpha H0 bar dies at half an MST edge | two balls of radius r meet iff their centres are ≤ 2r apart; `tests/test_invariants.py` |
| Regular n-gon π = 1/sin(π/n); octahedron π = √(3/2); any 3-point loop π = 1/sin(largest angle) ≤ 2/√3 | our derivations in radius units (in squared-radius units they would be 1/sin²(π/n) and 3/2); `test_regular_ngon_ratio`, `test_void_shell_octahedron` |
| Permutation p_min for n = 7 is 14/7! = 1/360 (R is invariant under the 2n rotations and reflections of the labels) | our derivation; `test_perfect_ring_alignment_exact_p` |
| Winding number w = (1/2π) Σ wrap(θ_{c+1} − θ_c) | standard discrete winding number; `test_winding_counts_turns` |
| Circular coordinates: integer lift of a Z_p cocycle, harmonic smoothing by least squares, circle-valued map | [de Silva, Morozov & Vejdemo-Johansson 2011](https://doi.org/10.1007/s00454-011-9344-x); worked-example hand calculation g = −1/7 re-derived |
| DREiMac `standard_range=True` requires Rips death ≥ 2 × birth and raises "too short"; documented as guaranteeing a non-trivial Čech class; classes ordered by persistence (death − birth) | DREiMac 0.3.2 `emcoords.py` (`get_cover_radius`), `circularcoords.py` docstrings; [docs](https://dreimac.scikit-tda.org/en/latest/notebooks/parameter_standard_range.html) |
| Holm, BH, Clopper–Pearson, exact McNemar, one-sided Fisher (`stats/tests.py`) | standard definitions; `scipy.stats.binomtest(...).proportion_ci(method="exact")` is Clopper–Pearson |
| Dual ridge W = Xcᵀ(Xc Xcᵀ + αI)⁻¹Y (`steering/offline.py`) | push-through identity (XᵀX + αI)⁻¹Xᵀ = Xᵀ(XXᵀ + αI)⁻¹ |
| Uniform random plane from QR of a Gaussian k × 2 matrix (`steering/loops.py`) | the column span of a Gaussian matrix is uniform on the Grassmannian; only the plane matters for a circle |
| Unmatched bottleneck cost = half a bar's length | bottleneck matching to the diagonal (L∞), [Cohen-Steiner, Edelsbrunner & Harer 2007](https://doi.org/10.1007/s00454-006-1276-5) |
| Interpretability citations (18 papers and posts): existence, authors, dates, quoted results | arXiv/HTML or official pages of Engels et al., Yedidia, Nanda et al., Modell et al., Kantamneni & Tegmark, Wurgaft et al. (prompt, layer 28, 64-d PCA, splines, r values), Moisescu-Pareja et al., Tang et al., David & Fomin, Gardinazzi et al., Naitzat et al., Antognini & Sohl-Dickstein, Shinn, Elhage et al., Marks & Tegmark, Gurnee et al., Zhong et al., the Goodfire Neural Geometry index; none is fabricated |

## Fixed

| Claim (where) | Verdict | Correct statement and source |
|---|---|---|
| Exp4's bottleneck distance is "computed exactly with Hera in GUDHI (Kerber, Morozov & Nigmetov 2017)" (`exp4_similarity.py`, `exp4_exp5.md`, literature review) | fixed | The code calls `gudhi.bottleneck_distance` (e = 0, exact). That is F. Godi's CGAL-based implementation after [Efrat, Itai & Katz 2001](https://doi.org/10.1007/s00453-001-0016-8). Hera is the separate `gudhi.hera.bottleneck_distance`, which is not used ([GUDHI documentation](https://gudhi.inria.fr/python/latest/bottleneck_distance_user.html)). |
| "Subcomplexes of ℝ³ have torsion-free homology (Alexander duality, Hatcher Cor. 3.45)" (literature review) | fixed | Torsion-freeness is **Cor. 3.46** (compact, locally contractible X ⊂ ℝⁿ: H_{n−1}, H_{n−2} torsion-free), a consequence of Alexander duality (Cor. 3.45). The first fact-check had only settled Thm 3.44 vs Cor. 3.45. |
| "Every closed surface embedded in ℝ³ is orientable" (no source) | source added | Hatcher, remark after Cor. 3.46 (p. 256): a closed non-orientable n-manifold does not embed in ℝⁿ⁺¹. |
| The universal null was "validated on 9,000–50,000 points" (`tda/nulls.py`, glossary, first fact-check) | fixed | Simulations use 10⁴–10⁶ points (Supp. Tables 3–4). Real data use roughly 9,000–50,000 (the paper's text says 9,000–30,000 sentences; its supplement lists 8,762–29,812). One test demo uses 1,000 points. The state-of-the-art review's "large i.i.d. samples" also omitted the non-i.i.d. examples (Brownian motion, Lorenz). |
| [Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232) "covers compactly supported densities" (paper) / "uniform-like samples" (glossary) / "uniform samples" (Exp1) / "uniform samples in a cube" (Exp8) | fixed | Thm 3.1 ([arXiv:1509.04347](https://arxiv.org/abs/1509.04347)) is proven for a homogeneous Poisson process on [0,1]^d, Čech and Rips, 1 ≤ k ≤ d − 1. Densities bounded above and below on a compact support are only remarked (§2.4). One wording is now used everywhere. |
| "The Delaunay triangulation of points on a helix grows quadratically" (Exp0 report, `exp0_analytic.py`, analytic_topology) | overstated → fixed | [Erickson 2003](https://doi.org/10.1007/s00454-003-2927-4), Thm 2.3, proves Ω(n^{3/2}) for evenly spaced helix points; Θ(n²) is the general 3D worst case. Now "superlinear", cited. |
| "PCA horseshoes" cited to Antognini & Sohl-Dickstein (paper, state-of-the-art and literature reviews) | mis-cited → fixed | [Antognini & Sohl-Dickstein 2018](https://arxiv.org/abs/1806.08805) show Lissajous curves (a parabola in PC1–PC2). The horseshoe effect is [Diaconis, Goel & Holmes 2008](https://doi.org/10.1214/08-AOAS165), now cited and in the bib. |
| Modell et al.'s colour and date loops as shapes "in activations" (paper, README, state-of-the-art review) | imprecise → fixed | They are 3D PCA views of 3,072-dimensional text-embedding vectors ([arXiv:2505.18235](https://arxiv.org/abs/2505.18235), §2.3). |
| The margin is "the smallest parameter change that changes the topology" (code, docs, paper, README, Exp0 report, preregistration) | imprecise → fixed | The implemented margins are feature sizes in data units: a hole diameter 2r (closing it by the radius is a change of r), endpoint chords, tube diameters, and 2r for caps smaller than a hemisphere. Reworded everywhere except the frozen preregistration, which D13 corrects. |
| ρ_A ≥ 1 "so the data can distinguish it" (glossary) | overstated → fixed | It is a heuristic: balls of radius ν from both sides of a gap m meet once 2ν ≥ m. The rigorous analogue, in terms of the reach τ, is [Niyogi, Smale & Weinberger 2008](https://doi.org/10.1007/s00454-008-9053-2), Prop. 3.1 (ε/2-dense sample, ε < √(3/5)·τ). Now cited. |
| "Exact cyclic-order test p = 2/(n−1)!" (`stats/circular.py`, methodology, preregistration) | imprecise → fixed | The implemented criterion also needs every wrapped step to go the same way. For fixed angles, a random labelling matches with probability 2/(n−1)! if all circular gaps are below π, and 0 otherwise, so the stated p is an upper bound (new test). |
| DREiMac `standard_range` "guarantees the class is non-trivial in the Čech complex" (code, deviations D5) | imprecise → fixed | DREiMac's theory also takes the cover radius ≥ the landmark covering radius d_H(L, X), which 0.3.2 does not check. The guarantee is therefore exact when all points are landmarks (N ≤ 200: weekdays, months, residues) and approximate for colours and days_time. DREiMac's default prime is 41; the code passes the preregistered 47 explicitly. |
| Alpha ≃ union of balls and alpha = Čech persistence, stated without hypotheses (diagrams, glossary, paper) | imprecise → fixed | Both theorems assume general position (Bauer & Edelsbrunner, Def. 4.2), which real activations satisfy generically. Degenerate test inputs only create zero-length bars, which are dropped. |
| `random_samples` is "uniform in arc length / area" (`analytic/coords.py`) | fixed (docstring) | Paraboloids have weight 1, so they are uniform over the projected disc, not the surface. The preregistration only asks for dense shape samples; no number changes. |
| `steering/metrics.traversal` returns "the fraction of steps whose decoded phase is the one expected" | fixed (docstring) | It returns R, orientation and winding only. |
| "None of these use a null model" (state-of-the-art review) / "Neither uses a null model" (paper) | imprecise → fixed | None tests individual bars against a null: Naitzat et al. calibrate on data of known topology; [Gardinazzi et al.](https://arxiv.org/html/2410.11042) compare informally with token-shuffled prompts (App. F); Moisescu-Pareja et al.'s permutation tests are MMD tests of neuron statistics; [Tang et al.](https://arxiv.org/abs/2605.06352) compare with permuted-label training. |
| Ordinal loops in 10 PCs are "as expected from Fourier-like features of numbers" (README) | overstated → fixed | Consistent both with Fourier number features ([Kantamneni & Tegmark 2025](https://arxiv.org/abs/2502.00873)) and with PCA artefacts of smooth or random-walk curves (Antognini & Sohl-Dickstein; [Shinn 2023](https://doi.org/10.1073/pnas.2311420120)); the test cannot separate them. Same fix in the Exp4/Exp5 report. |
| "1 of 3 random-init controls at p < 0.05, consistent with the nominal 5%" (Exp7, Exp3, findings) | overstated → fixed | Added that three controls say little: P(≥ 1 of 3 below 0.05) = 1 − 0.95³ ≈ 0.14 under the null. |
| "Why: noise cycles on a 2D surface live longer than in a 3D blob" (Exp1, Exp8 reports) | overstated → fixed | Now labelled a hypothesis consistent with the per-family false-loop rates, not tested directly. |
| BH "controls the expected share of false positives" (glossary) | imprecise → fixed | For independent tests or positive regression dependence ([Benjamini & Yekutieli 2001](https://doi.org/10.1214/aos/1013699998)). |
| Worked example: "the ring cannot be filled until edges span 3 concepts; edges spanning 2 are not enough" | imprecise → fixed | The ring fills when edges join concepts three steps apart (Mon–Thu). For 7 evenly spaced points, Rips with first and second neighbours is the cyclic graph power C₇² ≃ S¹ (Adamaszek & Adams Thm 4.3, k/n = 2/7 < 1/3). |
| "Same persistence as the Čech complex of the union of balls" (README) | imprecise → fixed | The Čech complex is the nerve of the balls: "same persistence as the Čech filtration, the nerve of the balls, and hence as the union of balls". |
| Obayashi & Yoshiwaki "1 in 10,000 random alpha filtrations" (glossary, diagrams, literature review) | imprecise → fixed | Alpha filtrations of Poisson clouds in [0,1]³ with 1,000 points on average (§8, arXiv v3; the published text was not accessible). |
| Small attributions (literature review) | imprecise → fixed | Engels et al.'s interventions mostly use PCA-fitted circles of hidden states. Naitzat et al. use one fixed scale only on simulated data (full barcodes on real data). Chaudhuri et al. wrote "hyperplane versus a filled ball". The `adamaszek2017rips` bib entry now has its issue, pages and DOI. |
| Wurgaft et al.: "linear steering produces off-target tokens" (state-of-the-art review) | overstated → fixed | The paper's claim is that linear paths leave the manifold and cut across the behaviour manifold ([arXiv:2605.05115](https://arxiv.org/abs/2605.05115)); the wording now says that. |

## Not checked

- The published DCG text of Obayashi & Yoshiwaki (paywalled); arXiv v3 was used.
- Chaudhuri et al.'s Supplementary Notes.
- Bauer & Edelsbrunner's journal numbering (arXiv v3 numbering is cited: Thm 5.10, Cor. 6.1, Def. 4.2).
- The printed page numbers of Edelsbrunner & Harer (the chapter and section were confirmed from the authors' manuscript).

## Learnings

- **Read the cited theorem, not the abstract.** The universal null's sample sizes are in the supplement's tables, not in the abstract or a single example. The Bobrowski–Kahle–Skraba theorem is narrower than its remarks.
- **Check which implementation a library call runs.** GUDHI ships two bottleneck implementations; only `__module__` tells which one the code uses.
- **Definitions in prose drift from the code.** The margin and the cyclic-order p were defined in words that the implemented rule no longer matched. A brute-force test now pins the cyclic-order statement.
- **Two independent checks disagree in useful places.** The first fact-check accepted the "9,000–50,000" figure and left the torsion-freeness citation on Cor. 3.45; reading the sources again found both.
