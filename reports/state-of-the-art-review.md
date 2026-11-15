# State-of-the-art review: topology of neural representation manifolds

Date: 2026-11-15. Author: Libor "Burny" Burian (review compiled with Claude Code; every claim below links to its source).

Scope: what is known about (i) low-dimensional shapes in neural activations, (ii) topological data analysis (TDA) of neural representations, (iii) statistical inference for persistent homology, and (iv) practical tooling, as needed for this project. The project computes the topology of the top-3-PCA activation clouds that the sibling project [shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability) classified into 13 geometric shape families, and tests whether semantically cyclic concepts travel around a hole.

Verification status: facts were checked against the papers' own pages (arXiv abstract or HTML, PMC full text, GitHub READMEs) on 2026-11-15. Items that could only be checked from a summary of a page, not its text, are marked *(summary)*. Items that could not be checked are listed in the last section and are not used for any claim.

## State of the art in one page

The full source catalogue, with methods and numbers, is in [literature-review.md](literature-review.md).

1. **Neural geometry is mostly identified by eye or by fitting.**
   - Weekday and month circles ([Engels et al.](https://arxiv.org/abs/2405.14860)), helices ([Yedidia](https://www.lesswrong.com/posts/qvWP3aBDBaqXvPNhS/gpt-2-s-positional-embedding-matrix-is-a-helix); [Kantamneni & Tegmark](https://arxiv.org/abs/2502.00873)) and loops for colours and dates ([Modell et al.](https://arxiv.org/abs/2505.18235)) were found visually, or by interventions and supervised fits.
   - The source project ([shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability)) automated the fitting. It labels the weekday, month and grokked-embedding clouds "helix".
2. **Causal use of curved geometry.** Manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); Goodfire's [Neural Geometry series](https://www.goodfire.com/research/neural-geometry)) moves activations along a spline through concept centroids. It changes outputs in semantic order (weekdays, months, letters, ages), whereas linear steering produces off-target tokens. Holes and topology are not used to choose the path.
3. **Topology of neural representations.**
   - Persistent homology is used to describe how layers change data topology ([Naitzat et al.](https://jmlr.org/papers/v21/20-345.html); [Gardinazzi et al.](https://arxiv.org/abs/2410.11042)) and to count Betti numbers of modular-addition representations ([Moisescu-Pareja et al.](https://arxiv.org/abs/2512.25060); [Tang et al.](https://arxiv.org/abs/2605.06352)). None of these use a null model.
   - A persistence ratio against random points is used for small centroid clouds of *imposed* cycles ([David & Fomin](https://arxiv.org/abs/2607.24425)).
   - In neuroscience, ring and torus detection with shuffle nulls and circular-coordinate decoding is established ([Chaudhuri et al.](https://doi.org/10.1038/s41593-019-0460-x); [Gardner et al.](https://doi.org/10.1038/s41586-021-04268-7)).
4. **Inference.** The universal null distribution ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)) gives per-bar p-values but was validated on large i.i.d. samples. Max-over-shuffle Monte Carlo thresholds ([Gardner et al.](https://doi.org/10.1038/s41586-021-04268-7)) are the practical standard.
5. **Known pitfalls.** PCA projections create horseshoes and Lissajous loops ([Antognini & Sohl-Dickstein](https://arxiv.org/abs/1806.08805); [Shinn](https://doi.org/10.1073/pnas.2311420120)). Rips complexes create phantom classes ([Adamaszek & Adams](https://arxiv.org/abs/1503.03669)).

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

- The venue of Nanda et al. 2023: the arXiv page gives none, so we cite the arXiv version.
- The library and filtration used in David & Fomin's Appendix I.
- What the "k = 250" kNN parameter in Moisescu-Pareja et al. is used for, and their numeric Betti results.
- The detailed parts of arXiv:2605.05115 beyond about the first 40% of its HTML. The layer, PCA dimension, spline method and results quoted above are from the verbatim part.
- The exact constant in Rips stability bounds relative to the Gromov–Hausdorff distance.
