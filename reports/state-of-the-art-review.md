# State-of-the-art review: topology of neural representation manifolds

Date: 2026-11-15; corrected 2026-11-20 by the independent math fact-check ([reviews/math-fact-check-2.md](reviews/math-fact-check-2.md)) and 2026-11-22 by the independent audit ([reviews/independent-audit.md](reviews/independent-audit.md)). Author: Libor "Burny" Burian (review compiled with Claude Code; every claim below links to its source).

Scope: what is known about (i) low-dimensional shapes in neural activations, (ii) topological data analysis (TDA) of neural representations, (iii) statistical inference for persistent homology, and (iv) practical tooling, as needed for this project. The project computes the topology of the top-3-PCA activation clouds that the sibling project [shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability) classified into 13 geometric shape families, and tests whether semantically cyclic concepts travel around a hole.

Verification status: facts were checked against the papers' own pages (arXiv abstract or HTML, PMC full text, GitHub READMEs) on 2026-11-15. Items that could only be checked from a summary of a page, not its text, are marked *(summary)*. Items that could not be checked are listed in the last section and are not used for any claim.

## State of the art in one page

The full source catalogue, with methods and numbers, is in [literature-review.md](literature-review.md).

1. **Neural geometry is mostly identified by eye or by fitting.**
   - Weekday and month circles ([Engels et al.](https://arxiv.org/abs/2405.14860)), helices ([Yedidia](https://www.lesswrong.com/posts/qvWP3aBDBaqXvPNhS/gpt-2-s-positional-embedding-matrix-is-a-helix); [Kantamneni & Tegmark](https://arxiv.org/abs/2502.00873)) and loops for colours and dates in text-embedding vectors ([Modell et al.](https://arxiv.org/abs/2505.18235)) were found visually, by clustering sparse-autoencoder features, or by interventions and supervised fits.
   - The source project ([shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability)) automated the fitting. It labels the weekday, month and grokked-embedding clouds "helix".
2. **Causal use of curved geometry.** Manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); Goodfire's [Neural Geometry series](https://www.goodfire.com/research/neural-geometry)) moves activations along a spline through concept centroids. It moves the output distribution along the behaviour manifold in semantic order (weekdays, months, letters, ages), whereas linear steering cuts across it. Holes and topology are not used to choose the path.
3. **Topology of neural representations.**
   - Persistent homology is used to describe how layers change data topology ([Naitzat et al.](https://jmlr.org/papers/v21/20-345.html); [Gardinazzi et al.](https://arxiv.org/abs/2410.11042)) and to count Betti numbers of modular-addition representations ([Moisescu-Pareja et al.](https://arxiv.org/abs/2512.25060); [Tang et al.](https://arxiv.org/abs/2605.06352)). None of these tests individual bars against a null model: Naitzat et al. calibrate on data of known topology, Gardinazzi et al. compare informally with token-shuffled prompts, Moisescu-Pareja et al.'s permutation tests compare neuron statistics, and Tang et al. compare with networks trained on permuted labels.
   - A persistence ratio against random points is used for small centroid clouds of *imposed* cycles ([David & Fomin](https://arxiv.org/abs/2607.24425)).
   - Month tokens' zigzag barcodes across layers are shown, without a null, in [Gardinazzi et al.](https://arxiv.org/abs/2410.11042) (App. C). A re-implementation of Engels et al. that is not peer reviewed ([shouvik-majumder/circular-features](https://github.com/shouvik-majumder/circular-features)) states that weekday and month loops are correctly ordered and exceed a covariance-matched Gaussian null, without test statistics.
   - Weekday representations may be seven discrete states on a circle rather than a continuous ring ([Gupta, Fruengel & Heimersheim 2026](https://arxiv.org/abs/2610.37796), abstract).
   - In neuroscience, rings and tori are detected by persistent homology, by bar length ([Chaudhuri et al.](https://doi.org/10.1038/s41593-019-0460-x), who decode with a fitted spline) or against shuffled data ([Gardner et al.](https://doi.org/10.1038/s41586-021-04268-7)), and decoded with persistent-cohomology circular coordinates ([Rybakken, Baas & Dunn](https://arxiv.org/abs/1711.07205); Gardner et al.).
4. **Inference.** The universal null distribution ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)) gives per-bar p-values; it is a conjecture supported empirically on large samples (simulations with 10^4–10^6 points, real data with roughly 9,000–50,000). Max-over-shuffle thresholds ([Gardner et al.](https://doi.org/10.1038/s41586-021-04268-7): the longest lifetime over all bars of 1,000 shuffles) are a heuristic, in Gardner et al.'s own word.
5. **Known pitfalls.** PCA and MDS projections create horseshoes ([Diaconis, Goel & Holmes 2008](https://doi.org/10.1214/08-AOAS165)), PCA projections of random walks are Lissajous curves ([Antognini & Sohl-Dickstein](https://arxiv.org/abs/1806.08805)), and smooth data produce phantom oscillations in PCA ([Shinn](https://doi.org/10.1073/pnas.2311420120)). Rips complexes create phantom classes ([Adamaszek & Adams](https://arxiv.org/abs/1503.03669)).

## 10. What this project builds on, and what is new

Built on:
- the source project's clouds, labels, fitted parameters and synthetic generator;
- alpha complexes and persistence;
- the universal null of Bobrowski & Skraba, with the max-over-null threshold of Gardner et al.;
- the circular coordinates of de Silva et al., via DREiMac;
- manifold steering's framing of travelling along a manifold.

New here, as far as we found:
1. The **exact topology of uniquely parametrised fitted shapes**, with a topological margin, compared against the persistent homology of the same clouds.
2. A **preregistered, null-controlled test** that semantically cyclic concepts have a 1-cycle whose traversal follows the semantic order (winding ±1). The test uses a fitted-shape coordinate and a persistent-cohomology coordinate, with design-matched negative controls: random-init networks, ordinal concepts and random walks.
3. A synthetic validation of a Betti-number estimator against exact ground-truth topology over 39,000 clouds of 13 families.

## 11. Not verified, so not used for claims

- The library and filtration used in David & Fomin's Appendix I.
- What the "k = 250" kNN parameter in Moisescu-Pareja et al. is used for, and their numeric Betti results.
- The detailed parts of arXiv:2605.05115 beyond about the first 40% of its HTML. The layer, PCA dimension, spline method and results quoted above are from the verbatim part.
- The exact constant in Rips stability bounds relative to the Gromov–Hausdorff distance.
