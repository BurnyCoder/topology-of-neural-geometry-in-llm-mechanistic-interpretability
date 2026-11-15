# Plan and status

Last updated: 2026-11-15.

## Status

| Step | State |
|---|---|
| 1. Setup (uv, submodule, GitHub repo) | done |
| 2. Literature and state-of-the-art reviews | done ([literature-review.md](literature-review.md), [state-of-the-art-review.md](state-of-the-art-review.md)) |
| 3. Preregistration, plan, README | done (pushed before any topology was computed) |
| 4. Core modules (TDD), export, Hugging Face inputs | done (inputs pinned at revision 02e4d50; regeneration of synthetic ground truth bit-exact) |
| 5. Exp0: exact topology of fitted shapes (+ Method A traversal) | done |
| 5b. Fitted-shape coordinate check (author request, D4) | done |
| 6. Power simulation and preregistration addendum A1; steering amendment A2 | done |
| 7. Exp1: synthetic validation | done |
| 8. Exp2/Exp3: real-data topology and cyclic tests (+ post hoc D5) | done |
| 9. Exp4/Exp5: similarity, robustness | done |
| 10. Audit (independent reviewer) | in progress |
| 11. Reports, paper, site, Hugging Face results | done (paper/main.pdf; explorer on GitHub Pages; results on the HF dataset) |
| 12. Clean-room replication test | in progress |
| Exp6: simulated steering and LLM steering (primary H6) | **postponed by the author**; code ready, not run |
| Optional Exp0b (refit synthetic clouds with the source checkpoint) | not done (needs model inference; postponed) |

The full plan, as approved on 2026-11-15, follows unchanged. Changes to it are logged in [deviations.md](deviations.md).

---


## Context
The source project, the [shape-fitting repo](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability), sorted top-3-PCA activation clouds into 13 geometric shape families.
- Local copy: `../fitting-geometrical-shapes-in-llm-mechanistic-interpretability`. It is clean and matches GitHub `main` at 4c5f3b6. The GitHub repo was renamed from `geometrical-shape-fitting-…`.
- Hugging Face model `BurnyCoder/neurogeom-shape-fitter-main-s0`, in collection `BurnyCoder/fitting-geometric-shapes-to-neural-geometry-6ae635f979b04232274230ee`.

Each fitted shape in the source is **uniquely parametrized** (`canonicalize()` in `neurogeom/shapes/*.py`), so its topology is fixed exactly by family plus parameters. Examples:
- a torus with R > r > 0 is T², with Betti numbers (1,2,1) and genus 1;
- an arc with `closed=True` (extent_frac ≥ 0.98) is S¹;
- a cone frustum with r_bot > 0 is an annulus;
- a sphere with `closed=True` is S².

So the project works in two complementary ways:
1. **First, exact topology of the fitted shapes.** Closed-form Betti numbers, Euler characteristic, genus, boundary components and dimension, plus a "topological margin": how far the parameters are from a change in topology.
2. **Then persistent homology of the data clouds themselves,** as an independent, fit-free check of whether the data actually have the holes the fitted shape implies.

Together these:
- computes topological invariants of exactly those clouds: Betti numbers, Euler characteristic at a stated scale, genus where it is defined, and homotopy class;
- compares the clouds topologically;
- tests the user's hypothesis: semantically cyclic concepts (weekdays, months, residues mod 113) carry a 1-cycle, and travelling around that cycle follows the semantic cycle. Non-cyclic ordinal concepts (years, temperature, age, positions, character counts) carry no such cycle.

There is **no training and no model inference**. All inputs already exist in the source repo.

Literature check: no peer-reviewed paper reports Betti numbers for weekday or month representations. The closest work:
- [David & Fomin 2026, App. I](https://arxiv.org/abs/2607.24425): persistent homology on centroids of *imposed* cycles.
- [Modell et al. 2025](https://arxiv.org/abs/2505.18235): colours and dates form loops, judged by eye.
- [Moisescu-Pareja et al. 2025](https://arxiv.org/abs/2512.25060): Betti numbers of modular-addition representations, with no null model.
- [Tang et al. 2026](https://arxiv.org/abs/2605.06352): H1 of grokked embeddings, with no null model.

So the novelty is a preregistered, null-controlled topological test that a hole *aligns with the semantic cycle*, applied to clouds that already carry geometric labels.

**Inspiration for "travelling around the hole"** (to be stated in the README, the reports and the paper):
- **Manifold steering:** Wurgaft, Rager, Kowal et al., *Manifold Steering Reveals the Shared Geometry of Neural Network Representation and Behavior*, [arXiv:2605.05115](https://arxiv.org/abs/2605.05115) (May 2026), and the [Goodfire blog post](https://www.goodfire.com/research/manifold-steering).
  - They fit a 1-D manifold to the seven day-of-week clusters of Llama-3.1-8B. The clusters form a rough circle.
  - Moving activations *along* that manifold shifts the output from Monday to Tuesday to Wednesday and onward. Linear steering cuts across the manifold and produces off-target tokens.
  - They also study months, letters, ages and in-context graph geometries.
- **Goodfire's [Neural Geometry series](https://www.goodfire.com/research/neural-geometry)**, including:
  - *The World Inside Neural Networks* (Geiger et al.);
  - *A Geometric Calculator Inside a Neural Network* (Feucht et al.), on circular number representations;
  - *Can SAEs Capture Neural Geometry?* (Bhalla et al.);
  - *Meandering on Manifolds* (Bigelow et al.);
  - *Block-Sparse Featurizers* (Fel et al.).

Manifold steering travels along the manifold *causally*. This project asks the *observational, topological* counterpart:
- Is there a hole, by exact topology of the fitted shape and by persistent homology?
- Does the semantic order travel around it once?

Steering along θ_A or θ_B around the detected hole, as a causal follow-up, is out of scope (it needs inference) and goes on the README to-do list. The literature review reads arXiv:2605.05115 in full (the HTML version) for the details of its method: layer, how the manifold is fitted, how it is parametrised.

## Inputs (found during exploration)
- **Real clouds (44):** `results/main_s0/real/viz/<id>.json` holds the preprocessed top-3 PCA points and labels. It is tracked in git, so it is available from the submodule.
  - The fitter's output is in `real_results.json`: family, probabilities, fitted params, `gap_flag`, `top3_explained`.
  - Raw activations are in `data_cache/real/*.npz` (`X`, `labels`, `meta`). They are local only (48 MB). I need them for the top-k PC and null-model checks.
  - Factors not stored as labels are recovered from the row index (from `realdata/llm_sets.py`):
    - weekday offset = i%7;
    - month offset = i%12;
    - days_time time = i%48, put into chronological order (12 AM = 0);
    - colour hue is parsed from `"hue|sat|lum"`.
- **Synthetic test set (39,000 clouds):** cached in `data_cache/testset_test_dataseed0_250.pt` (533 MB, local only). Each cloud has `x`, `mask`, `n`, `sigma`, `family`, `embed_dim`, and the dense noise-free ground truth `gt_dense`/`gt_w`. Chunks of 25 share N and the embedding draw.
  - The validation stream (1,560 clouds) is also cached.
  - The fitter's per-cloud predictions are in local `results/main_s0/synth/per_sample.csv`, which is not in git.
  - On CUDA the source generator reproduces the set bit-exactly, including the full parameter dict (`extent_frac`, `cap_frac`, `r_bot`, …). Exporting those parameters gives the **exact ground-truth topology** (Method A).
- **Reusable source code (reference only, not installed):**
  - `neurogeom/geometry/preprocess.py::fit_frame`: centre, top-3 eigenvectors, skewness sign, RMS = 1.
  - `realdata/controls.py::matched_gaussian`.
  - `baselines/features_gbm.py` uses ripser only for H0/H1 features; there is no existing Betti or cohomology code.

## Reproducibility: GitHub + Hugging Face only (user requirement)
Anyone with only the GitHub repo and the Hugging Face Hub must be able to replicate every number. Nothing may depend on files that exist only on this machine.
- **Inputs that are local-only today go to a public HF dataset**, `BurnyCoder/topology-of-neural-geometry`, under `inputs/`:
  - the 44 raw activation `.npz` files;
  - the exported synthetic test cells (39,000) and validation cells (1,560): points, mask, n, σ, family, embed_dim, chunk/cell ids, `gt_dense`/`gt_w`;
  - the CUDA-regenerated ground-truth parameter dicts;
  - `per_sample.csv` and `probs.npz`;
  - `manifest.json` with the SHA-256 of every file, plus the source commit (4c5f3b6) and the exact export command.
  - The dataset card states provenance and licences: MIT for the source code; Llama 3.1 Community License for activations derived from Llama-3.1-8B; GPT-2 (MIT) and Pythia (Apache-2.0) for the others.
- **The pipeline reads only from two places:** the git submodule (viz JSON, `real_results.json`) and `data/source/`, which `run.py fetch` fills from HF.
  - `fetch` pins the dataset revision (commit SHA in `configs/base.yaml`) and verifies the SHA-256 hashes.
  - The pipeline never reads the sibling folder. Its path appears only in `scripts/export_source_artifacts.py`, which is configurable through `.env` and defaults to the submodule.
  - After the first upload, I delete local `data/source/` and re-fetch from HF, so every result in the repo is produced from the HF copies.
- **Regenerating inputs from scratch** (optional; needs a GPU) is documented in `docs/reproduce_inputs.md`, using only the public source repo and its HF checkpoint:
  - `git clone --recursive`;
  - `uv sync` inside the submodule;
  - the source's `run.py extract-real` (needs the gated Llama-3.1-8B), `eval-synth`, and the synthetic cache build;
  - then `export_source_artifacts.py`.
  - Expected outcome: the synthetic set and parameters match bit-exactly on CUDA, and the hashes are compared against the manifest.
- **Determinism:**
  - every seed is set in the config;
  - `uv.lock` is committed;
  - package versions and the git commit are written into `results/*/env.json`;
  - no GPU is needed for the analysis.
- **Clean-room replication test** (part of Verification): fresh `git clone --recursive` from GitHub into `D:\AI\replication-test\`, with no `.env` pointing at local data. Then run:

  ```bash
  uv sync && uv run python run.py fetch all
  ```

  Pass condition: every file in `results/` and every generated table matches the committed ones (exactly, or to within 1e-9 for floats). Any mismatch gets fixed and re-tested.

## Setup decisions
- **Python 3.11 with uv**, local `.venv`. DREiMac (circular coordinates, Apache-2.0, [JOSS 2023](https://doi.org/10.21105/joss.05791)) requires Python below 3.12. gudhi 3.13, ripser 0.6.15 and persim 0.4.1 all ship cp311 Windows wheels (checked on PyPI).
  - Dependencies: numpy, scipy, scikit-learn, pandas, gudhi, ripser, persim, dreimac, matplotlib, pyyaml, python-dotenv, joblib, huggingface_hub, pytest.
- **The source repo becomes a git submodule** at `external/shape-fitting`, pinned to 4c5f3b6. It provides provenance, the viz JSON and `real_results.json`.
  - It is **not installed as a dependency**: it pins Python 3.12, torch cu130, transformers and bitsandbytes.
  - `fit_frame` is re-implemented in about 25 lines of numpy, and a test checks it reproduces the viz points to within 1e-4.
- **One-off export, then upload to HF:** `scripts/export_source_artifacts.py` runs with the *source* venv's python (`-I`), which has torch. It writes to `data/source/` (gitignored), with a SHA-256 manifest. `run.py publish-inputs` then uploads this to the HF dataset (see Reproducibility). The export contains:
  - the synthetic test and validation cells as ragged npz;
  - the `per_sample.csv` predictions;
  - the 44 raw `.npz` files;
  - a CUDA regeneration of the ground-truth parameter dicts (the exact ground-truth topology), verified against the cache with max diff 0. This is the only GPU use apart from the optional Exp0b. The rest is CPU-bound persistent homology, parallelised with joblib over 16 cores.
- **License:** our code is MIT. GUDHI's AlphaComplex is GPL-3 through CGAL. It stays a normal PyPI dependency (we don't redistribute binaries), and README/NOTICE say so.
- **Complexes:**
  - Primary: alpha complex in ℝ³. It is exact Čech, H2 is cheap, and it has no Rips "phantom" classes ([de Silva & Ghrist 2007](https://doi.org/10.2140/agt.2007.7.339); [Adamaszek & Adams 2017](https://arxiv.org/abs/1503.03669)). GUDHI returns squared filtration values, so I take √ to get radii.
  - Rips (ripser) is used for the top-k PC and full-D checks and for cocycles, H1 only. H2 is computed with alpha only.

## Method A (done first): exact topology of the fitted parametric shapes
**Inputs.** Canonical fitted parameters per real cloud, from `real_results.json` `params`. Schema checked during planning:
- arc: `closed`, `extent_rad`, `radius`;
- sphere: `closed`, `cap_half_angle_rad`;
- cone: `r_bot`, `dr` (so r_top = r_bot + dr), `half_height`;
- torus: `R`, `r`;
- helix: `radius`, `pitch`, `turns`;
- clusters: `k`, `centroids`, `spread`;
- polytope: `subtype`, `vertices`;
- ellipse: `a`, `b`;
- the other families likewise.

For synthetic clouds, the ground-truth parameters come from the CUDA export.

**Closed-form rules** go in `src/neurotopo/analytic/topology.py::shape_topology(family, params)`. Derivations are written up in `docs/analytic_topology.md`, citing [Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf) for the homology of S¹, S², T² and contractible spaces, and the classification of compact surfaces with boundary, χ = 2 − 2g − n_boundary for orientable surfaces. Each rule returns b0, b1, b2, χ, genus, number of boundary components, orientability, dimension, manifold yes/no, homotopy class and margin.

| Family | Rule (exact) | (b0, b1, b2), χ, genus | Topological margin (distance to a topology change) |
|---|---|---|---|
| blob | solid ellipsoid level set | (1,0,0), 1 | ∞ |
| clusters | k disjoint balls | (k,0,0), k | min centroid gap − 2·spread |
| polytope | V vertices; the template surface (S²) is also reported | (V,0,0), V | min vertex gap − 2·spread |
| line | segment | (1,0,0), 1, 2 endpoints | ∞ (unless length 0) |
| arc | `closed` → S¹; otherwise interval | (1,1,0), 0 / (1,0,0), 1 | \|extent_frac − 0.98\| · 2πr (the source's own closure threshold) |
| ellipse | S¹ | (1,1,0), 0 | minor axis b (collapse to a segment) |
| helix | embedded open curve | (1,0,0), 1 | endpoint gap relative to radius (axial pitch·turns, angular gap) |
| ringing | injective curve (cos πs is injective on [0, 1]) | (1,0,0), 1 | endpoint distance |
| disc / paraboloid patch | disc, 1 boundary circle | (1,0,0), 1 | ∞ |
| sphere | `closed` → S²; otherwise cap (disc) | (1,0,1), 2, g = 0 / (1,0,0), 1 | cap-opening chord |
| cone | r_bot, r_top > 0 → annulus with 2 boundary circles; one radius 0 → disc | (1,1,0), 0 / (1,0,0), 1 | min(r_bot, r_top) |
| torus | R > r > 0 → T²; R = r horn torus ≃ S²∨S¹ (1,1,1); r > R flagged as self-intersecting | (1,2,1), 0, g = 1 | min(r, R − r) |

**Travel around the hole, Method A version.** This is inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)) and the [Goodfire Neural Geometry series](https://www.goodfire.com/research/neural-geometry); see Context. The fitted shape is an explicit parametrisation, so every data point gets an **intrinsic coordinate on the fitted shape**: the parameter of its nearest point on the shape. The circle/hole coordinate θ_A is defined per family:
- closed arc or circle, ellipse: the curve angle;
- cone frustum/cylinder (annulus): the azimuth around the axis;
- torus: both angles. The longitude goes around the central hole and the meridian around the tube. Each angle is tested, so days_time can align day with one and time with the other;
- helix: the azimuth around the axis is reported as **"axial winding"** with a closure gap. The closure gap is the axial drift per semantic period divided by the radius. This is labelled descriptive, because a helix is topologically contractible (b1 = 0). It directly measures the reading "helix = circle + drift" for weekdays and months;
- closed sphere, disc, clusters and other b1 = 0 shapes: no 1-cycle, so not applicable.

How θ_A is computed:
- The families' parametrisations are re-implemented in numpy, following the formulas in the source `shapes/curves.py` and `shapes/surfaces.py` (cited line by line).
- The shape is sampled on a fine parameter grid, and each point is assigned the parameter of its nearest grid sample (scipy `cKDTree`).

θ_A then goes through **the same statistics as Method B**, with shared code: per-concept circular means, the alignment R with a permutation null over concept labels, winding number, the exact cyclic-order test, and the max over k for grokking.

**Margin normalisation.** Each margin is divided by the fit's residual scale (`residual_normalised` × the cloud's RMS) to give a dimensionless robustness ratio. A ratio below 1 means the fitted shape's topology is not resolvable from the data.

**Checking the rules numerically.** Run alpha persistent homology on the dense noise-free samples of each fitted shape (the viz JSON `shape` field for real clouds; `gt_dense` for synthetic). The significant features must reproduce the analytic Betti numbers wherever the margin exceeds the sampling resolution. This is a unit and integration test, and its agreement rate is reported.

**Outputs:**
- Per real cloud: the fitted shape's exact invariants and margin ratio. The same is done for the subsample-majority family where its parameters exist (only the selected family's parameters are stored).
- Per synthetic cloud: exact ground-truth topology from the ground-truth parameters. This is the primary ground truth for Exp1.
- These analytic invariants are the "fitter-implied topology" used in H4 and as Exp1 baseline (b).

**Disclosure for the preregistration.** While checking the schema during planning, I saw a few fitted parameter values: W_pos is a closed sphere, years is a frustum with r_bot > 0, and C1_gp_0 is a helix with 4.6 turns.

## Method B: persistent homology (the fit-free instrument)
1. **Diagrams:** alpha persistence diagrams H0, H1 and H2 of the RMS-normalised 3D cloud, in radius units. π = death/birth.
2. **Significance of H1/H2 features, two nulls, both reported:**
   - **Monte Carlo design-matched null** (primary on real data). A feature counts if its π exceeds the 95th percentile of the null distribution of the *maximum* π in that dimension (in the style of [Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7); the max-statistic controls the family-wise error rate). M = 999.
     - (a) **Cluster designs** (weekdays 7×7, months 12×12, days_time 7×48 and their init controls): a *cluster-centre null*. Draw concept means from a Gaussian matched to the covariance of the means, add back each point's within-concept residual, then re-run `fit_frame` and alpha.
     - (b) **One point per value:** a full-D matched-covariance Gaussian, sampled through the N×N Gram matrix (`K = XcXcᵀ`; a draw is `G K Gᵀ` plus an N×N eigendecomposition), then `fit_frame`.
   - **Universal null** ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)): ℓ = A·log log π − λ − A·mean(log log π); A = ½ for alpha/Čech and 1 for Rips; p = exp(−eˡ); Bonferroni within each diagram.
     - It was validated on N ≥ 1000 iid samples, so it is **descriptive on real data**. Exp1 calibrates it per N bin.
3. **b0:** H0 bars whose MST edge divided by the median MST edge exceeds τ0, with a minimum component size of 2. τ0 is tuned on the synthetic validation stream only.
4. **Invariants at one stated scale** (this avoids mixing b0 from one scale with b1 from another):
   - Characteristic scale r_c = √(birth·death) of the most significant H1/H2 feature.
   - Betti numbers b_k(r_c): significant features alive at r_c, and components of size ≥ 2.
   - χ(r_c) = b0 − b1 + b2.
   - **Genus g = b1/2 only if b0 = 1 and b2 = 1** (a closed surface). Otherwise it is reported as "undetermined", and curves get cycle rank b1.
   - Homotopy class: contractible (1,0,0); circle-like (1,1,0), which homology cannot tell apart from an annulus or solid torus (stated); sphere (1,0,1); torus (1,2,1); k components; or other.
   - Betti curves and Euler-characteristic curves go in the figures.
   - Not computed, with the reasons stated in the methods:
     - Torsion and orientability: subcomplexes of ℝ³ have torsion-free homology (Alexander duality), and closed surfaces embedded in ℝ³ are orientable.
     - TwoNN dimension: unreliable at small N and on clustered clouds.
5. **"Travel around the hole"** (inspired by manifold steering and the Goodfire Neural Geometry series; see Context):
   - Circular coordinate θ from the top H1 class, using DREiMac (prime 47, landmarks = min(N, 200), coordinate scale fixed in the preregistration). The method is [de Silva, Morozov & Vejdemo-Johansson 2011](https://doi.org/10.1007/s00454-011-9344-x).
   - θ is aggregated per concept as a circular mean, to avoid pseudo-replication.
   - Alignment R = max over s = ±1 of |mean_c exp(i(θ̄_c − s·φ_c))|, with φ_c = 2π·c/P.
   - Permutation null over concept labels: exact over all 7! orderings for weekdays; 99,999 Monte Carlo draws otherwise.
   - For grokking, the max-statistic is taken over Fourier frequencies k = 1..56, with residues permuted.
   - Also reported:
     - winding number of the semantic cycle in θ;
     - the exact cyclic-order test, p = 2/(n−1)!;
     - closure ratio d(last, first)/median d(consecutive) on full-D concept means, using cosine distance.

## Hypotheses (preregistered before any real-data persistent homology is computed)
- **H1-A, co-primary: fitted-shape topology (Method A).** For each of R5a weekdays, R5b months and R2 grokking W_E, the dataset is semantically circular if:
  - the fitted shape has an exact hole: b1 ≥ 1 with margin ratio ≥ 1;
  - the semantic cycle travels around that hole: alignment R of θ_A has a permutation p-value below the Holm-adjusted α, and winding = ±1.

  A helix or other b1 = 0 fit counts as a failure. Its axial winding and closure gap are still reported, descriptively.
- **H1-B, co-primary: persistent homology (Method B).** For each of the same three datasets, the data are semantically circular if all four hold:
  - (a) a significant H1 loop under the design-matched MC null;
  - (b) alignment R with a permutation p-value below the Holm-adjusted α;
  - (c) winding = ±1;
  - (d) the alignment survives recomputation of θ from Rips H1 on the **top-10 PCs** of the raw activations (unadjusted p < 0.05, winding ±1). This guards against loops that are only an artefact of PCA projection ([Antognini & Sohl-Dickstein 2018](https://arxiv.org/abs/1806.08805); [Shinn 2023](https://doi.org/10.1073/pnas.2311420120)).

  Verdict, per method: supported if 3/3 pass, partial if 1–2 pass, not supported if 0 pass. A cyclic set with no loop counts as a failure, not as "not applicable".

  **Multiplicity:** Holm over the 6 alignment tests (3 datasets × 2 methods). The smallest exact p for weekdays is 14/7! ≈ 0.0028, which is below 0.05/6 ≈ 0.0083, so the test can pass.
- **H2, specificity.** The same conjunctions (A and B) fail for the sets below. Under Method A this includes ordinal sets whose fitted shape *does* have a hole: a hole without semantic traversal does not count. For example, the years fit is a frustum, so the test is whether the years wind around its axis.
  - the 6 non-cyclic ordinal sets: GPT-2 W_pos (weight space), Llama and Pythia counting, years, temperature, age. Their θ is aggregated into 7 and 12 equal bins of the range, so n matches the cyclic sets;
  - the design-matched random-init controls C3 (weekdays, months, grokking init);
  - the 20 C1 GP/random-walk controls.

  Falsified if 2 or more of the 6 ordinal sets pass, or if any C3 init control passes.
- **H3, secondary.** In R5c days_time, the day phase passes the conjunction. Time of day is exploratory, in chronological order; a torus is possible.
- **H4, secondary: does topology help classify cyclicity?**
  - Compare the balanced accuracy of three verdicts on cyclic {R5a, R5b, R2, R5c} versus the 6 ordinal sets:
    - hole only, Method A: b1 ≥ 1 and margin ratio ≥ 1;
    - the full Method A conjunction;
    - the Method B conjunction.
  - Descriptive, with an exact McNemar test. Also reported: agreement between the fitted shape's exact Betti numbers and the data cloud's PH Betti numbers on all 44 real clouds.
- **H5, instrument validity (Exp1).** Ground truth is the exact topology from the ground-truth parameters (Method A). The persistent-homology estimator's exact Betti-vector accuracy, macro-averaged over the 13 families, is computed on clouds whose topology is *resolvable*. A cloud is resolvable if its ground-truth margin is at least 2 × the noise scale (σ̂ + r_cov). It is compared (two-sided) with:
  - (a) a fixed lifetime threshold tuned on validation;
  - (b) family-implied topology: the fitter's predicted family mapped to that family's modal exact Betti vector, learned on validation. The fitter's synthetic parameters are not stored; see the optional Exp0b;
  - (c) the majority vector.

  Also reported:
  - the false-positive rate on resolvable contractible cases per N bin;
  - the calibration of the universal null on blobs;
  - accuracy as a function of margin/noise, including the unresolvable clouds, so selection bias is visible.
- **Exploratory (BH correction):**
  - colours: hue winding, predicted positive (Modell et al.);
  - years, temperature, age: alignment with value mod 10 or mod 100, possible because of base-10 features ([Kantamneni & Tegmark 2025](https://arxiv.org/abs/2502.00873));
  - truth cities: b0 = 2 predicted;
  - toy models of superposition: descriptive;
  - grokking memorised checkpoint;
  - topological similarity (Exp4).
- **Phrasing:** a convenience sample, preregistered but not blind (the source project's 3D plots exist), and claims made per dataset. The only multiple-testing family is H1 (Holm); everything else is exploratory.

## Experiments
- **Exp0 (first): exact topology of the fitted shapes.** Method A applied to:
  - all 44 real clouds: a table of family, parameters, (b0, b1, b2), χ, genus, boundary components, homotopy class, margin ratio;
  - the 39k synthetic ground-truth shapes.

  Plus the numeric check against PH of the dense noise-free shape samples, and the **Method A travel-around-the-hole tests**: H1-A and H2-A, with intrinsic coordinates θ_A, plus the descriptive axial winding and closure gap for helix fits.

  The topology needs no nulls (it is exact); only the alignment uses permutation tests. All of its rules are fixed in the preregistration, so it runs first and immediately answers two questions: which fitted shapes have holes, and whether the semantic cycle travels around them. For example: is the fitted weekday helix one turn per week with a small drift?
- **Exp0b (optional, after the main experiments, needs a GPU):**
  - Re-run the source fitter, using the published HF checkpoint `BurnyCoder/neurogeom-shape-fitter-main-s0` and the submodule code, on the synthetic test set. This gives the fitted parameters, so the fitted shape's exact topology can be scored against the ground-truth topology.
  - This is inference, which the task does not require. It is done only if time allows, and it stays replicable from GitHub plus HF.
- **Power/FPR simulation** (synthetic only; done before the preregistration addendum):
  - k ∈ {7, 12} concept clusters × m points in ℝ⁴⁰⁹⁶, arranged as a closed ring, an open arc or random positions. Within/between spreads and top-3 variance are swept over a grid that covers the real sets' *second-order* statistics. Only variances are computed from real data; no topology.
  - Gives the power and false-positive rate of conditions (a)–(d). Thresholds are frozen in a dated addendum, pushed before any real-data run.
- **Exp1, synthetic validation (all 39k clouds, alpha plus universal null; MC null on the 3,120-cloud subset):**
  - **Primary ground truth:** the exact topology from the ground-truth parameters (Exp0).
  - **Resolvability:** ground-truth margin / (σ̂ + r_cov) ≥ 2, computed in the normalised frame:
    - σ̂ = median distance from points to `gt_dense`;
    - r_cov = 95th-percentile distance from `gt_dense` to the points.
  - **Secondary ground truth:** the "effective topology at noise scale", taken from the alpha diagram of `gt_dense` at r* = max(σ̂ + r_cov, h_gt), with h_gt the ground-truth grid spacing. This covers multi-scale cases such as clusters or polytope vertices that form a loop at a larger scale.
  - Detection curves are plotted against margin/noise.
  - CIs: cluster bootstrap over generator chunks of 25. A family × homotopy-class table shows which geometric families are topologically equivalent.
- **Exp2, invariants of all 44 real clouds:**
  - Diagrams, significant features under both nulls, invariants at r_c, genus or cycle rank, homotopy class.
  - Stability over 200 subsamples of 80%, re-run through `fit_frame` with the source's seeds.
  - Compared with the fitter's family and its implied topology.
- **Exp3:** H1-B, H2-B, H3 and H4 (which combines Exp0's Method A verdicts with the PH verdicts), plus the exploratory alignment tests under both methods.
- **Exp4, similarity:**
  - Bottleneck distances on *significant* features only (Wasserstein grows with N), for H0, H1 and H2.
  - Covers the 44 clouds plus ideal templates: circle, 7-gon, 12-gon, helix, sphere, torus, line, Gaussian.
  - MDS and a dendrogram; nearest template compared with the fitter's family; a permutation test of how tightly the cyclic set clusters.
- **Exp5, robustness:**
  - alpha vs Rips in 3D;
  - Rips H1 on the top-k PCs (k ∈ {3, 5, 10}) and on full-D cosine distance;
  - subtracting the per-offset means for weekdays and months (the offset is a nuisance factor);
  - 3 seeds for the MC nulls and subsampling;
  - c ∈ {1, 4} for r*;
  - DTM filtration ([Anai et al. 2019](https://arxiv.org/abs/1811.04757)) only if Exp1's outlier false-positive rate is above 10%.

## Code layout
- `run.py` phases: `fetch exp0 power exp1 exp2 exp3 exp4 exp5 report site publish all`, plus maintainer-only `publish-inputs` and the optional `exp0b`.
  - `all` = fetch through site; it needs no GPU and no local files.
  - The export script is separate because it needs the source venv.
- Configuration in `configs/base.yaml` and `.env`.
- Timestamped logs in `logs/`.

```
src/neurotopo/
  config.py, log.py
  data/source.py        # viz JSON, real_results, raw npz, factor parsing, semantic phases
  data/synthetic.py     # exported cells + GT params + per_sample join
  analytic/topology.py  # Method A: shape_topology(family, params) -> exact invariants + margin
  analytic/coords.py    # numpy parametrisations of the 13 families; intrinsic_coords(family, params, pts) -> hole angle(s)
  stats/circular.py     # shared by A and B: concept circular means, R, permutation (exact/MC, max over k), winding, order p, closure
  geometry/pca.py       # numpy fit_frame
  tda/diagrams.py       # alpha (sqrt radii), rips, pi, betti_at_scale
  tda/nulls.py          # universal_pvalues, mc_pvalue, gram_gaussian, cluster_centre_null
  tda/invariants.py     # significant features, b0 rule, r_c, chi, genus, homotopy class
  tda/ground_truth.py   # resolvability (margin / noise), effective topology of gt_dense at r*
  tda/circular.py       # DREiMac wrapper -> theta_B from the top H1 cocycle
  tda/compare.py        # bottleneck on significant features, MDS, dendrogram, templates
  stats/tests.py        # exact binomial CI, Fisher, McNemar, cluster bootstrap, Holm/BH
  experiments/{exp0_analytic,power,exp1_synthetic,exp2_invariants,exp3_cyclic,exp4_similarity,exp5_robustness,exp0b_refit}.py
  report/{numbers,tables,figures,site}.py
tests/                  # TDD, see Verification
scripts/export_source_artifacts.py
reports/ docs/ paper/ results/ data/(gitignored) external/shape-fitting (submodule)
```

## Order of work
Each step is done on a branch, then a PR, then merged with `gh`, with no AI attribution.
1. `uv init` (3.11), git init, submodule, `.gitignore`, `.env(.example)`. Create the public GitHub repo `BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability` and push the skeleton.
2. `reports/state-of-the-art-review.md`, built from the review with every claim linked. It includes manifold steering (arXiv:2605.05115, read in full) and the Goodfire Neural Geometry series posts as the inspiration for the traversal test. Re-verify the uncertain items: the Sci. Rep. article number, David & Fomin App. I details, the circular-features README figures, the Nanda et al. venue, and the authorship of the helix post. Fact-check pass.
3. `reports/preregistration.md`, `reports/plan.md`, and a detailed README. Push **before any code touches real-data topology**. Fact and rigor check.
4. TDD implementation of the core modules, the export script and `fetch`/`publish-inputs`.
   - Run the export and upload the inputs to the HF dataset (public). Add the dataset to the existing collection.
   - Pin the revision in the config, delete local `data/source/`, then run `run.py fetch` and check the hashes.
   - From here on, all experiments read the HF-fetched copies. Push.
5. **Exp0: exact topology of the fitted shapes**, with `docs/analytic_topology.md` and the numeric PH check on the dense shape samples. Report, then push.
6. Power simulation, then the preregistration addendum with the frozen thresholds. Push.
7. Exp1, then the report. Push.
8. Exp3 and Exp2. Push.
9. Exp5 and Exp4. Push. Then the optional Exp0b if time allows. Push.
10. Audit:
    - an independent review subagent gets the code and results, not my conclusions;
    - fact-check every claim;
    - leakage, null, confounder and multiple-testing checks.
11. Deliverables, each followed by a push:
    - per-experiment reports, `summary.md` (with a layman's glossary and an overview table), `deviations.md`, `docs/methodology.md`;
    - LaTeX paper (author Libor "Burny" Burian, date 2026-11-15, pipeline diagram, eval table, example figures, AI statement at the end);
    - README with results tables and figures generated between markers;
    - GitHub Pages explorer (plotly: the 3D cloud coloured by θ, the representative cycle, the barcode and diagram, the fitter label);
    - HF dataset `BurnyCoder/topology-of-neural-geometry` with inputs, a hash manifest and results, added to the existing collection.

Every number comes from `run.py report`, which reads `results/`.

Not applicable, and stated as such: training, checkpoints and the live training dashboard. Total compute is under about 1–2 CPU-hours.

## Verification
- **Unit tests (TDD):**
  - Method A rules, one test per family and per topology-changing branch:
    - torus R > r gives (1,2,1), χ = 0, g = 1; horn torus gives (1,1,1);
    - arc `closed` gives (1,1,0), open gives (1,0,0);
    - sphere `closed` gives (1,0,1), g = 0; a cap gives (1,0,0);
    - frustum gives (1,1,0) with 2 boundaries; apex cone gives (1,0,0);
    - k clusters give (k,0,0); a polytope with V vertices gives (V,0,0);
    - helix and ringing give (1,0,0);
    - χ = b0 − b1 + b2 always, and χ = 2 − 2g − n_boundary for the surfaces.
  - The margin is 0 exactly at the source's own thresholds: arc extent_frac 0.98, the sphere FULL cap threshold, r_bot = 0, r = R.
  - Analytic Betti numbers equal the significant PH features on dense noise-free samples of each family, for the viz `shape` samples and for `gt_dense`.
  - Intrinsic coordinates:
    - points sampled on a parametrised circle, ellipse, frustum, torus or helix at known parameters recover them (angular error < 1e-2 rad), including after a random rotation and translation;
    - the numpy parametrisations reproduce the viz JSON `shape` samples (Chamfer distance ≈ 0);
    - a 7-cluster ring placed on a fitted circle gives R ≈ 1 and winding ±1;
    - a one-turn helix with zero pitch has axial winding 1 and closure gap 0.
  - A noisy circle gives one significant H1; a sphere gives one H2; a torus gives (1,2,1); a blob gives none.
  - Two points at distance 2 give an H0 death of 1.0 (checks the √ of squared values).
  - A regular n-gon gives alpha π = 1/sin(π/n) to 1e-6.
  - Universal-null p-values on N = 1000 blobs are uniform (KS test) for alpha and for Rips.
  - The Gram sampler's covariance equals `matched_gaussian`'s, and MC p-values lie in [1/(M+1), 1] and are reproducible with a seed.
  - 3 clusters plus 5% outliers give b0 = 3.
  - Ground truth: closed arc (1,1,0), half arc (1,0,0), full sphere (1,0,1), torus (1,2,1), frustum (1,1,0), apex cone (1,0,0), and an ambiguity flag near r*.
  - θ on a noisy circle has |circular correlation| > 0.99 with the true angle.
  - A 7-cluster ring gives R ≈ 1 and exact p = 14/7! (the minimum; this passes the first Holm step for 3 tests); a shuffled order gives p ≈ 1.
  - The order test returns 2/(n−1)!; a 3-turn helix gives winding 3 and a large closure ratio.
  - Index-to-factor parsing matches the prompt templates; the numpy `fit_frame` matches the viz JSON to 1e-4.
- **Clean-room replication from GitHub and HF only:**
  - fresh `git clone --recursive` into `D:\AI\replication-test\`, with no local data paths;
  - `uv sync`, then `run.py fetch all`;
  - every results file and generated table must match the committed ones.
  - I run this after Exp3 and again at the very end. The README's "Reproduce" section is exactly these commands.
- **End-to-end:** run `uv run python run.py all` like a user would; inspect the logs and outputs; check that the generated README, report and paper numbers match `results/*.json`. The paper must compile with `pdflatex`/`bibtex`. Open the Pages explorer in the browser pane and check the 3D plots and cycles render.
