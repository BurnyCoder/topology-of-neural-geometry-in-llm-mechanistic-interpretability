# Preregistration: topology of top-3-PCA neural activation clouds

- **Authors:** Libor "Burny" Burian (analysis executed by Claude Code to the author's specification).
- **Date:** 2026-11-15.
- **Repository:** https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability
- **Status when pushed:** no topology (Method A or B) and no alignment statistic has been computed on any real or synthetic cloud. The analysis code is not yet written. A dated **addendum** (end of this file) will add, before any real-data analysis:
  - the results of the synthetic power simulation;
  - the values tuned on the synthetic validation stream (b0 rule, baseline threshold).

  It will not change any rule below.
- **Source data:** the sibling project [shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability) at commit `4c5f3b6` (git submodule `external/shape-fitting`), with its Hugging Face model `BurnyCoder/neurogeom-shape-fitter-main-s0`. No training and no model inference is done for the confirmatory analyses.

## 1. Questions

**Q1. Which holes do the fitted shapes have?** Every source shape is uniquely parametrised (`canonicalize()` / `describe()` in `neurogeom/shapes/*.py`), so its topology follows exactly from family plus parameters:
- Betti numbers b0, b1, b2;
- Euler characteristic χ;
- genus, number of boundary components and orientability.

**Q2. Which holes do the data clouds have?** Answered with persistent homology, independently of any fit.

**Q3. Primary.** Do semantically cyclic concepts (days of the week, months, residues mod 113) have a hole whose traversal follows the semantic cycle, exactly once? Do non-cyclic concepts lack one? This "travel around the hole" test is inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); [blog](https://www.goodfire.com/research/manifold-steering)) and the [Goodfire Neural Geometry series](https://www.goodfire.com/research/neural-geometry). Manifold steering moves activations along a fitted day-of-week manifold and the output follows the days in order. We ask the observational, topological counterpart.

**Q4.** How do the 44 clouds and the 13 shape families relate topologically?

## 2. Data

All 44 real clouds of the source project are used: preprocessed top-3 PCA points and labels from `results/main_s0/real/viz/<id>.json`, fitted parameters from `real_results.json`, and raw activations from `data_cache/real/<id>.npz` (republished on Hugging Face).
- **Preprocessing** is the source's `fit_frame`: centre, project on the top-3 eigenvectors, fix signs by skewness, scale to RMS radius 1. We re-implement it in numpy and test that it reproduces the stored points.
- **Concept labels and semantic phase φ:**
  - weekdays (`R5a`, 49 = 7 days × 7 offsets): day index c = i // 7, φ = 2πc/7;
  - months (`R5b`, 144 = 12 × 12): c = i // 12, φ = 2πc/12;
  - days_time (`R5c`, 336 = 7 days × 48 half-hours): day = i // 48; time = i % 48, converted to chronological order (12:00 AM = 0);
  - grokking W_E (`R2`, 113): residue a, φ_k = 2πka/113 for Fourier frequency k;
  - colours (`R7`, 900 = 36 hues × 5 saturations × 5 lightnesses): hue/360 × 2π;
  - ordinal sets: the stored value.
- **Groups (fixed now):**
  - *Cyclic, primary:* `R5a_llama_weekdays`, `R5b_llama_months`, `R2_grokking_WE` (weight space).
  - *Cyclic, secondary:* `R5c_llama_days_time` (day phase confirmatory-secondary; time phase exploratory).
  - *Non-cyclic ordinal:* `R1_gpt2_wpos` (weight space), `R4_llama_counting`, `R4b_pythia_counting`, `R6_llama_years`, `R8a_llama_temperature`, `R8b_llama_age`.
  - *Design-matched random-init controls:* `C3_llama_weekdays_init`, `C3_llama_months_init`, `C3_grokking_WE_init`.
  - *Ordinal-process controls:* `C1_gp_0..9`, `C1_walk_0..9`.
  - *Exploratory:* `R7_llama_colors`, `R9_llama_truth_cities`, `R3_tms_n6/n8/n20`, `C3_tms_dense`, `C3_grokking_WE_memorised`, `C3_gpt2_wpos_init`, `C3_llama_counting_init`, `R5a_llama_weekdays_means`, `R5b_llama_months_means`.
- **Synthetic:** the source's fixed test set (39,000 clouds: 13 families × 4 N-bins × 3 noise bins × 250) and validation stream (1,560 clouds).
  - Ground-truth parameters are regenerated bit-exactly on CUDA with the source generator. They are expressed in the normalised frame (`generate_family` returns `gt`).
  - The source method's predicted family per cloud comes from `per_sample.csv`.

## 3. Method A: exact topology of a parametrised shape

`shape_topology(family, params)` returns (b0, b1, b2), χ = b0 − b1 + b2, the genus g (closed orientable surfaces: χ = 2 − 2g), the number of boundary components n_∂, the dimension, and a **margin** m. The margin is the length of the smallest parameter change that changes the topology. It is measured in the coordinates of the parameters. References: [Hatcher, *Algebraic Topology*](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), and the classification of compact orientable surfaces with boundary (χ = 2 − 2g − n_∂).

| Family (source definition) | Condition | (b0, b1, b2) | χ | g | n_∂ | margin m |
|---|---|---|---|---|---|---|
| blob (Gaussian; solid ellipsoid level set) | – | (1,0,0) | 1 | – | – | ∞ |
| clusters (k Gaussian balls) | – | (k,0,0) | k | – | – | min centroid distance − 4·spread |
| polytope (V vertices) | – | (V,0,0) | V | – | – | min vertex distance − 4·spread |
| line (segment) | – | (1,0,0) | 1 | – | 2 points | endpoint distance 2L |
| arc | `closed` (extent_frac ≥ 0.98, the source's own threshold) | (1,1,0) | 0 | – | 0 | hole diameter 2r |
| arc | not closed | (1,0,0) | 1 | – | 2 points | endpoint gap 2r·sin(π(1 − extent_frac)) |
| ellipse (closed) | – | (1,1,0) | 0 | – | 0 | minor axis 2b |
| helix (embedded open curve) | – | (1,0,0) | 1 | – | 2 points | min(endpoint distance, \|pitch\| if turns > 1) |
| ringing c + Σ a_k cos(kπs) e_k | – | (1,0,0) | 1 | – | 2 points | endpoint distance 2·√(a1² + a3²) |
| disc (filled ellipse) | – | (1,0,0) | 1 | 0 | 1 | ∞ |
| paraboloid patch | – | (1,0,0) | 1 | 0 | 1 | ∞ |
| sphere | `closed` (cap_frac ≥ 0.98) | (1,0,1) | 2 | 0 | 0 | void diameter 2r |
| sphere | cap, half-angle α | (1,0,0) | 1 | 0 | 1 | opening 2r·sin(max(α, π/2)) |
| cone (lateral surface of a frustum) | r_bot > 0 | (1,1,0) | 0 | 0 | 2 | narrow-end diameter 2·r_bot (r_top = r_bot + dr ≥ r_bot) |
| cone | r_bot = 0 (apex) | (1,0,0) | 1 | 0 | 1 | 0 |
| torus (r = R·ratio; source caps ratio ≤ 0.95, so r < R) | – | (1,2,1) | 0 | 1 | 0 | min(2r, 2(R − r)) |

**Margin ratio.** ρ_A = m / (2ν), where ν is the noise-and-coverage scale of the cloud with respect to the shape:

ν = median(distance from each data point to the shape) + q95(distance from each dense shape sample to its nearest data point).

The shape is represented by the fitted shape's dense samples (viz `shape`) for real clouds and by `gt_dense` for synthetic ones. ρ_A ≥ 1 means the topology is **resolvable** at the data's noise scale. ρ_A < 1 means it is not.

**Intrinsic hole coordinate θ_A.** Each data point gets the parameter of its nearest point on the fitted shape, by nearest neighbour on a dense parameter grid of our numpy re-implementation of the source's `local()` formulas. The grid has 4,096 points for curves and 256 × 256 for surfaces.
- closed arc: the angle in the circle's plane;
- ellipse: the curve parameter t;
- cone with r_bot > 0: the azimuth around the axis;
- torus: the longitude u (around the central hole) and the meridian v (around the tube), each tested separately;
- helix: the azimuth t mod 2π, reported only descriptively as **axial winding**, because a helix has b1 = 0. Also reported is the **closure gap**, the axial (e3) distance between the first and last concept means divided by the radius;
- every other case (b1 = 0): not applicable.

## 4. Method B: persistent homology of the data cloud

1. **Diagrams.** GUDHI `AlphaComplex(points, precision="safe")` on the RMS-normalised 3D cloud.
   - Filtration values are squared radii, so we take √. Homology is over Z₂, dimensions 0–2.
   - π = death/birth for finite bars with birth > 0.
2. **Universal-null p-values** ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)), for k ≥ 1:
   - ℓ = A·log log π − λ − A·L̄, with A = ½ for alpha/Čech and A = 1 for Rips. L̄ is the mean of log log π over the bars of the diagram with π > 1, and λ is the Euler–Mascheroni constant.
   - p = exp(−eˡ). Bonferroni divides α = 0.05 by the number of bars.
   - **Descriptive on real data.** It is calibrated per N-bin in Exp1.
3. **Design-matched Monte Carlo null (primary on real data).** For dimension k, the statistic is the maximum π of H_k. The null distribution comes from M = 999 null clouds, each passed through the same `fit_frame`, normalisation and alpha complex. A bar j is **significant** if p_j = (1 + #{null max π ≥ π_j}) / (M + 1) < 0.05.
   - **(a) Cluster-centre null** for prompt-template designs (`R5a`, `R5b`, `R5c`, `R7` with concept = hue, and the C3 weekday/month init controls):
     - concept means μ_c are redrawn as m̄ + (n − 1)^(−½)·Zᵀ M_c, where Z is an n×n standard normal matrix and M_c holds the centred means. This matches the covariance of the means;
     - each point keeps its own within-concept residual x_i − μ_{c_i}.
   - **(b) Full-D matched Gaussian** for one-point-per-value designs (all other datasets): X* = m̄ + (N − 1)^(−½)·Z X_c, sampled through the N×N Gram matrix.
   - Seeds: `numpy.random.default_rng(crc32(dataset_id) + seed)`, with seed = 0 for the main analysis.
4. **b0.** Single-linkage at threshold τ0 × (median Euclidean minimum-spanning-tree edge), counting components with at least max(1, ⌈f·N⌉) points.
   - τ0 ∈ {1.5, 2, 3, 4, 6, 8, 12} and f ∈ {0, 0.01, 0.02, 0.05} are chosen by exact-b0 accuracy on the synthetic **validation** stream only. The chosen values are recorded in the addendum.
5. **Invariants.**
   - Persistent counts b_k^pers = the number of significant bars (k = 1, 2) and b0 from step 4.
   - Characteristic scale r_c = √(birth·death) of the most significant H1/H2 bar, or the b0 threshold if there is none.
   - Betti numbers at r_c: significant bars alive at r_c, plus components.
   - χ(r_c).
   - Genus g = b1/2 only if b0 = 1 and b2 = 1; otherwise "undetermined", with cycle rank b1 reported for curves.
   - Homotopy class: contractible (1,0,0); circle-like (1,1,0), which cannot be told apart from an annulus or solid torus; sphere (1,0,1); torus (1,2,1); k components; other.
6. **Circular coordinate θ_B.** DREiMac `CircularCoords(points, n_landmarks=min(N, 200), prime=47, maxdim=1)` on the normalised 3D cloud, then `get_coordinates(perc=0.5, cocycle_idx=0, standard_range=True)` (the most persistent Rips cohomology class) ([de Silva et al. 2011](https://doi.org/10.1007/s00454-011-9344-x); [DREiMac](https://doi.org/10.21105/joss.05791)). We report whether this class's interval overlaps the significant alpha H1 bar.

## 5. Alignment statistics ("travel around the hole"; shared by Methods A and B)

For a hole coordinate θ (θ_A or θ_B) and concepts c = 0..n−1 with phases φ_c:
- **Concept means:** θ̄_c = arg Σ_{i∈c} e^{iθ_i}. Aggregating per concept avoids pseudo-replication across prompt templates.
- **Alignment:** R = max over s ∈ {+1, −1} of |(1/n)·Σ_c e^{i(θ̄_c − s·φ_c)}|. This is invariant to the arbitrary origin and orientation of θ.
- **Permutation p-value:** reassign the phases among concepts.
  - exact over all n! assignments for n = 7, where the minimum p is 14/7! = 1/360;
  - Monte Carlo, B = 99,999 (+1 for the observed), otherwise.
  - Grokking: each residue is a concept. The statistic is max over k ∈ {1..56} of R(k), and the null permutes residues and recomputes the maximum.
- **Winding number:** w = (1/2π)·Σ_c wrap(θ̄_{c+1 mod n} − θ̄_c), with wrap to (−π, π].
- **Exact cyclic-order test:** is the circular order of θ̄_c the semantic cycle up to rotation and reflection? p = 2/(n − 1)!.
- **Closure ratio (descriptive):** d(last, first)/median d(c, c+1) between concept means in the full activation space, using cosine distance.
- **Ordinal sets:** the value range is cut into n equal-width bins, n ∈ {7, 12}, and the bins are the concepts.

## 6. Hypotheses, decision rules and falsification

- **H1-A (co-primary, Method A).** For each of R5a, R5b and R2, "semantically circular by the fitted shape" holds if both of these hold:
  - (i) the fitted shape has b1 ≥ 1 with ρ_A ≥ 1;
  - (ii) the θ_A alignment has a Holm-adjusted permutation p < 0.05 and |w| = 1. For a torus, either angle may satisfy (ii).

  A b1 = 0 fit (for example a helix) fails.
- **H1-B (co-primary, Method B).** For each of R5a, R5b and R2, all of these hold:
  - (a) the most persistent H1 bar of the 3D alpha diagram is significant under the design-matched MC null;
  - (b) θ_B alignment has a Holm-adjusted permutation p < 0.05;
  - (c) |w| = 1;
  - (d) recomputing θ_B with DREiMac on the **top-10 PCs** of the raw activations (centred, RMS-normalised) gives an alignment with unadjusted p < 0.05 and |w| = 1. This guards against loops that exist only in the projection ([Antognini & Sohl-Dickstein 2018](https://arxiv.org/abs/1806.08805); [Shinn 2023](https://doi.org/10.1073/pnas.2311420120)).
- **Multiplicity for H1:** Holm over the 6 alignment p-values (3 datasets × 2 methods).
- **Verdict for H1 (per method):** supported if 3/3 datasets pass, partially supported if 1–2 pass, not supported if 0 pass.
- **H2 (specificity).** The H1-A and H1-B conjunctions fail on the non-cyclic ordinal sets (n ∈ {7, 12} bins) and on the design-matched C3 init controls. Holm is not applied here, which makes the test conservative for specificity.
  - **Falsified** if 2 or more of the 6 ordinal sets pass, or if any C3 init control passes.
  - The C1 controls give a false-positive rate, reported with an exact binomial CI.
  - A hole without semantic traversal does not count. For example, a frustum fitted to years only counts if the years wind once around its axis.
- **H3 (secondary).** R5c passes the H1-A and H1-B conjunctions with the day phase (n = 7), at unadjusted α = 0.05.
- **H4 (secondary, descriptive).**
  - Balanced accuracy for separating {R5a, R5b, R2, R5c} from the 6 ordinal sets, for three criteria:
    - (1) hole only (Method A b1 ≥ 1 and ρ_A ≥ 1);
    - (2) the H1-A conjunction;
    - (3) the H1-B conjunction.
  - Pairwise exact McNemar tests.
  - Agreement between the Method A and Method B Betti vectors over all 44 clouds.
- **H5 (instrument validity, Exp1; two-sided).**
  - Ground truth is Method A on the ground-truth parameters, using resolvable clouds only (ρ_A ≥ 1 with ν computed against `gt_dense`).
  - The metric is exact-vector accuracy of (b0^pers, b1^pers, b2^pers) against the ground-truth (b0, b1, b2), macro-averaged over the 13 families. Polytope is scored on b0 only, because vertex arrangements create multi-scale H1/H2.
  - Comparators:
    - (a) the universal-null estimator vs a fixed-π-threshold estimator (count bars with π > π0, π0 tuned on validation);
    - (b) vs the *family-implied* estimator: the source method's predicted family mapped to the modal ground-truth Betti vector of that family on validation;
    - (c) vs the majority vector.
  - 95% CIs from a cluster bootstrap over generator chunks of 25 clouds (2,000 resamples); paired differences.
  - Also reported:
    - the false-positive rate of b1 ≥ 1 or b2 ≥ 1 on resolvable contractible clouds per N-bin;
    - the per-N-bin calibration of universal-null p-values on blobs;
    - accuracy against ρ_A, including unresolvable clouds;
    - the MC null on the 3,120-cloud baseline subset.
- **Exploratory (Benjamini–Hochberg within this list):**
  - colours: hue alignment, predicted positive ([Modell et al. 2025](https://arxiv.org/abs/2505.18235));
  - years, temperature, age: alignment with value mod 10 (and mod 100 for years) ([Kantamneni & Tegmark 2025](https://arxiv.org/abs/2502.00873));
  - truth cities: b0 = 2 predicted;
  - toy models of superposition: descriptive;
  - grokking memorised checkpoint: no prediction;
  - the means datasets (N = 7, 12), with the full-D Gaussian null (as in [David & Fomin 2026](https://arxiv.org/abs/2607.24425));
  - R5c time phase;
  - Exp4 topological similarity.

## 7. Further experiments (exploratory)

- **Exp2.** Method B invariants of all 44 clouds; stability over 200 subsamples of 80% (re-run through `fit_frame`; source seeds `default_rng(0)`); comparison with Method A.
- **Exp4.** Bottleneck distances on significant bars (H0, H1, H2) among the 44 clouds and ideal templates (circle, 7-gon, 12-gon, helix, sphere, torus, line, Gaussian), followed by:
  - MDS and an average-linkage dendrogram;
  - the nearest template compared with the fitted family;
  - a permutation test of the cohesion of the cyclic group.
- **Exp5 (robustness):**
  - alpha vs Rips in 3D;
  - Rips H1 on the top-k PCs (k ∈ {3, 5, 10}) and on full-D cosine distances;
  - removal of the per-offset means for R5a and R5b;
  - MC seeds 1 and 2;
  - ν with only the median term, or with 2× the coverage term;
  - a DTM filtration if the outlier false-positive rate in Exp1 exceeds 10%.
- **Exp0b (optional, inference).** Re-fit the synthetic test set with the published source checkpoint to score Method A on fitted parameters against the ground truth.

## 8. Power simulation (before real-data analysis; reported in the addendum)

**Design:** k ∈ {7, 12} concept centres in ℝ⁴⁰⁹⁶, with m ∈ {1, 7, 12} points per concept, arranged in three ways:
- on a closed ring;
- on an open 300° arc;
- at random Gaussian positions.

Within-concept noise is isotropic; top-3 variance and the within/between spread ratio are swept over a grid. Only these second-order statistics of the real sets are computed before the addendum; no topology is computed on real data.

**Outputs:** power and false-positive rate of H1-B (a)–(c) and of H1-A-style alignment on ideal fits. Low power is reported, not compensated for by changing rules.

## 9. Reporting rules

- Every number is generated by `run.py report` from `results/`.
- All outcomes are reported, including failures and negative results.
- Deviations go in `reports/deviations.md` with a date and reason.
- **Claims are per dataset**, in a convenience sample. The analysis is preregistered but not blind. Before this preregistration, the author had seen:
  - the source project's figures and its shape labels (helix for weekdays, months and grokking; sphere for W_pos; cone for years and colours);
  - while checking the parameter schema, three fitted parameter values: W_pos closed sphere; years cone with r_bot ≈ 0.79 > 0; C1_gp_0 helix with 4.6 turns.

## Addendum A1 (2026-11-15): validation tuning and power simulation (before any Method B result on real data)

The values below were produced by `run.py power` on the synthetic **validation** stream and on simulated designs only. The generated values are in [generated/prereg_addendum_A1.md](generated/prereg_addendum_A1.md), and the raw results are in `results/power/`.
- The b0 rule and the fixed-π baseline thresholds are fixed to the values that file reports. The chosen τ0 is the largest value in the preregistered grid; this is reported, not changed.
- The family-implied baseline map is fixed to the map that file reports.
- **Power simulation.** Conditions (a)–(c) of H1-B detect closed rings of 7×7, 12×12 and 113×1 concepts at every between-concept variance fraction simulated (0.3–0.9), which brackets the real sets' values.
  - Random arrangements essentially never pass the conjunction.
  - Open 300° arcs of clusters pass the loop condition (a), because their gap is about one inter-cluster step, so they are nearly rings. They are mostly rejected by (b)–(c).
  - No rule is changed.

**Disclosure.** Exp0 (Method A, including its travel-around-the-hole records) ran before this addendum, as planned. Its results were seen before this addendum was written:
- the three primary fits are helices (b1 = 0);
- the helix axial winding also appears in the smooth Gaussian-process controls;
- the colour fit is a frustum that hue goes around;
- GPT-2 W_pos is fitted as a closed sphere.

## Amendment A2 (2026-11-15): the primary hypothesis is the steering hypothesis

The author clarified that the primary hypothesis is:

> Can you do semantically meaningful manifold steering around a hole in a circular loop path every time there is a hole, and can the hole be found more easily using topology?

This amendment was written before any persistent homology of real clouds (Method B), and before any steering, simulated or with a model. The disclosure in A1 applies. H1–H5 stay as preregistered. They now serve as supporting analyses: H4 compares how easily topology and shape fitting find holes.

- **H6 (primary, steering).** Whenever topology detects a hole in a concept cloud, moving a prompt's concept-token activation around the loop that encircles the hole makes the represented concept go around the semantic cycle exactly once, in order, while staying on the data manifold. This is inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)).
- **Loops.** All loops live in un-normalised top-3 PCA coordinates, mapped to the full space through the PCA basis.
  - **B (primary, fit-free):** the points' θ_B, binned into 2n equal-width bins (at most 72), with the bin means joined by a periodic cubic spline (`scipy.interpolate.CubicSpline(bc_type="periodic")`). No concept labels are used.
  - **A (fitted shape, helix and cone fits):** the circle around the fitted axis at each prompt's own axial height.
  - **Chord (linear-steering baseline of Wurgaft et al.):** the closed polygon through the concept centroids in semantic order.
  - **Random loops (null):** M loops with the same centre and mean radius as loop B, each in a uniformly random 2D plane of the top-10 PC space.
- **Steering displacement.** h(Δ) = h + (γ(φ(h) + Δ) − γ(φ(h))) @ basisᵀ, where φ(h) is the parameter of the nearest loop point and Δ = 2πj/K with K = 4n (K = 72 for colours, 2·113 for residues).
- **Step 1, simulated steering (now; no model is run).** The readout is a decoder trained on the stored activations of the *other* prompts.
  - **Cross-validation folds:**
    - weekdays: leave one offset out;
    - months: leave one offset out;
    - days_time: leave one time of day out;
    - colours: leave one (saturation, lightness) pair out;
    - one-point-per-value datasets (ordinal sets in 7 bins, C1 controls): leave one point out.
  - **Primary decoder:** the nearest concept centroid in the full activation space, with Euclidean distance.
  - **Secondary decoder:** ridge regression from the full activation to (cos φ_c, sin φ_c) of the concept phase, with α = 1 times the mean squared row norm. For grokking residues this probe is used alone, at the frequency k* that is best aligned with θ_B, because each residue has only one point.
  - **Per prompt:** the decoded phase ψ(Δ), then R, the winding number, and the on-manifold fraction. The on-manifold fraction is the share of steps whose steered activation lies within the 95th percentile of training points' distances to their own concept centroid.
  - **Per dataset:** T = mean R over prompts.
  - **H6-sim passes for a dataset if all three hold:**
    - p < 0.05 against M = 100 random loops, where p = (1 + #{T_random ≥ T_B}) / 101;
    - |winding| = 1 for at least 50% of prompts;
    - the mean on-manifold fraction is at least 0.5.
  - **Datasets:**
    - every dataset with concept structure: the cyclic primary and secondary sets, colours, the ordinal sets (7 bins), the C3 init controls, the C1 controls, and grokking (k* probe only);
    - "every time there is a hole" is evaluated on the datasets where H1-B (a) detects a significant hole;
    - the rest are reported descriptively. They show whether a hole is needed for steerability.
  - **Verdict:** H6-sim is supported if every cyclic dataset with a detected hole passes; partially supported if some do; not supported if none do.
  - **Specificity:** ordinal sets and controls with a detected hole should not pass. This is the simulated counterpart of "a hole without semantic traversal".
  - **Comparisons (descriptive):** loop B vs loop A vs chord vs random, on T and on the on-manifold fraction.
  - **Evidence type:** simulation of steering under the assumption that the model reads the concept the way a decoder trained on its activations does. It is correlational, not causal.
- **Step 2, model steering (postponed by the author; run later).** This uses the same loops and displacement, applied as a forward hook to `hidden_states[layer]` of meta-llama/Llama-3.1-8B in bf16, at the steered token of the source templates.
  - **Readout:** the next-token distribution over the concept words:
    - weekdays: "… {k} day(s) from {d} is" → (d + k) mod 7;
    - months: → (m + k) mod 12;
    - days_time: "It's {t} on {d}. The next day is" → d + 1;
    - colours: the next colour word, decoded as the hue-weighted circular mean of 8 basic colour words.
  - **Grokking:** a model retrained with the source's grokking recipe (seed 0), steered at the position-0 residual, decoding (argmax − b) mod 113 on the k* circle.
  - **Controls:** M = 20 random loops on one prompt per concept; the chord path; and the grokking model's initial and memorised checkpoints.
  - **H6 passes for a dataset if all three hold:** p < 0.05 against the random loops; |winding| = 1 for at least 50% of prompts; mean in-vocabulary probability mass of at least 0.5.
  - The code is in `src/neurotopo/steering/` and `src/neurotopo/experiments/exp6_steering.py`.
