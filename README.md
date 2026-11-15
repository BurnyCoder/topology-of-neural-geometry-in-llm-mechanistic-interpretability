# Topology of neural geometry

**Status (2026-11-15):** all preregistered topology analyses are done. They use only stored activations; no model inference was run. Model steering and simulated steering are preregistered and **postponed by the author**.

**Links:** [paper (PDF)](paper/main.pdf) · [interactive explorer](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/) · [inputs and results on Hugging Face](https://huggingface.co/datasets/BurnyCoder/topology-of-neural-geometry) · [preregistration](reports/preregistration.md) · [summary of all experiments](reports/summary.md)

Interpretability research keeps finding **shapes** in neural activations:
- circles for weekdays and months ([Engels et al. 2024](https://arxiv.org/abs/2405.14860));
- a helix for GPT-2 positions ([Yedidia 2023](https://www.lesswrong.com/posts/qvWP3aBDBaqXvPNhS/gpt-2-s-positional-embedding-matrix-is-a-helix));
- circles of residues in grokked modular addition ([Nanda et al. 2023](https://arxiv.org/abs/2301.05217)).

The sibling project [shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability) fits one of 13 uniquely parametrised shapes to the **top-3 PCA coordinates** of 44 such activation and weight clouds.

**This project asks the topological question behind the hypothesis.** Does a concept have a **hole you can travel around**, and does the concept's semantic cycle (Monday → … → Sunday → Monday) go around it exactly once? Steering activations around such a loop should then be semantically meaningful. That idea comes from **manifold steering** ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); [Goodfire](https://www.goodfire.com/research/manifold-steering); the [Neural Geometry series](https://www.goodfire.com/research/neural-geometry)).

We answer it in two independent ways:
1. **Method A, exact topology of the fitted shape.** The shapes are uniquely parametrised, so Betti numbers, Euler characteristic and genus are exact. A *margin ratio* ρ_A says whether the data's noise can resolve that topology. Every point is projected onto its fitted shape, and we test whether the concepts are ordered along it.
2. **Method B, persistent homology of the cloud.** We use alpha complexes with a design-matched Monte Carlo null. The circle-valued coordinate of the hole comes from persistent cohomology via [DREiMac](https://github.com/scikit-tda/DREiMac).

![Pipeline](docs/figures/fig_pipeline.png)

## Highlights (all numbers generated from `results/`)

Results per dataset. "Hole" means a significant H1 loop under the design-matched Monte Carlo null (999 draws); "goes around" means the concept's semantic cycle winds exactly once in the loop's circle-valued coordinate. The alignment R and its permutation p measure *ordering*; only winding ±1 carries the cyclic claim.

- **Colours (exploratory set):**
  - Hole: π = 5.02 vs null 95th percentile 2.38, p = 0.001, Benjamini–Hochberg q = 0.011, stable in 1.00 of subsamples.
  - Hue goes around it once, in the cohomology coordinate (R = 0.95, winding -1) and on the fitted cone (R = 0.98, winding 1).
  - In the top-10 PCs, against a matched null (post hoc), the loop is still significant: Rips π = 2.67 vs 1.61, p = 0.005. Hue still winds once there (R = 0.97, winding -1).
  - In 10D a loop by itself is not specific: ordinal concepts have significant top-10 loops too (see below). What singles out colours is that hue goes around its loop.
- **Grokked residues mod 113:**
  - Hole: π = 2.45 vs 1.83, p = 0.001, but stable in only 0.26 of subsamples.
  - The residues go around it once at Fourier frequency 20 (Holm p = 6.0e-05, winding -1).
  - The preregistered top-10-PC check (d) fails. Top-10 null p = 1.000.
- **Months:**
  - Hole: π = 1.72 vs 1.44, p = 0.002. It is robust to removing the prompt-offset means (p = 0.003) and to the Monte Carlo seed.
  - The preregistered circular-coordinate setting built no coordinate. Only post hoc (relaxed setting) do the months go around the loop once in 3D (R = 0.72, winding 1); not in the top-10 PCs (winding 0; top-10 null p = 0.550).
  - On the fitted helix the two ends nearly meet (closure gap 0.04 radii). Post hoc, the axial position follows the 2nd Fourier harmonic (R² = 0.83 vs 0.10 for the 1st), as a closed saddle-shaped loop would.
- **Days with times** (day phase, exploratory):
  - There is a loop (p = 0.013), but it is unstable (stable in 0.03 of subsamples).
  - **The day does not go around it**, even post hoc (R = 0.18, winding 0).
  - On the fitted curve, the days lie in linear order (ρ = -1.00).
- **Weekdays:**
  - **No detectable hole** (π = 1.32 vs 1.36, p = 0.094), across seeds and after offset removal.
  - The test has little power here. In the corrected power simulation (post hoc), a true ring of 7 clusters with weekday-like statistics (top-3 variance 0.65; real 0.66) passes the loop test in 0.15 of replicates. It passes the full preregistered conjunction in at most 0.00, because the circular-coordinate step fails on such loops.
  - So the preregistered H1-B test was nearly incapable of passing for 7- or 12-cluster designs. For 12-cluster rings like months, the conjunction passes in at most 0.05 of replicates.
  - The days are ordered around the fitted helix's axis (exact p = 0.003, winding 1). **This is not specific:** 8 of 8 smooth random-process controls fitted as helices wind too, and their closure gaps (0.33–2.20) include the weekdays' 0.80.
- **Ordinal concepts and controls:**
  - In the top-3 PCs, none of the 6 ordinal sets has a loop (0/6), and none of the 20 random walks or Gaussian processes (0/20).
  - In the top-10 PCs (post hoc, matched null), loops are significant for R5c_llama_days_time, R4_llama_counting, R6_llama_years, R8a_llama_temperature, R8b_llama_age, R7_llama_colors. Ordinal values do not wind around them; only R1_gpt2_wpos has a single winding record among all non-cyclic sets.
  - The random-init grokking embedding has a borderline loop (p = 0.046, q = 0.253).
  - After Benjamini–Hochberg over all 44 loop tests, 6 loops remain at q < 0.05: C3_tms_dense, R2_grokking_WE, R3_tms_n8, R5b_llama_months, R5b_llama_months_means, R7_llama_colors.
  - Ordinal concepts lie in order along open curves: counts ρ = 0.999, temperature -0.997. GPT-2 positions run from pole to pole of their fitted sphere (0.978) as a spiral curve.
- **Fitted helices.** The helix fits of weekdays, months and residues have margin ratios of 0.11, 0.11 and 0.23. Whether they are open or closed is **unresolvable** at the data's noise scale. For prompt-template designs, this low ratio is partly a property of the design (gaps between clusters).
- **Preregistered verdicts:**
  - H1-A (fitted-shape hole + traversal): 0/3.
  - H1-B (persistent homology + traversal + top-10 robustness): 0/3.
  - H3 (days_time): fail.
  - H4: balanced accuracy 0.50 for every criterion. No criterion identified any cyclic set, so the "found more easily" comparison is uninformative.
  - H2 (specificity) is not falsified. That is weak evidence: sensitivity is zero, and the controls never come near the null threshold.
- **Instrument check on 39,000 synthetic clouds with exact ground-truth topology** (30114 resolvable):
  - The preregistered estimator (alpha complex + universal null) recovers the exact Betti vector for 0.618 [0.610, 0.626] of clouds (macro). A fixed-threshold baseline scores 0.714, and reading topology off the fitter's family label scores 0.812.
  - On well-resolved clouds (ρ_A ≥ 4; 18454 clouds, 0.49 of them trivially contractible), the preregistered estimator scores 0.751 vs 0.820 for the family label; paired difference -0.070 [-0.084, -0.056].
  - The fixed-threshold persistence estimator beats the family label where the label cannot fix the topology: open vs closed arcs, 0.79 vs 0.58; caps vs full spheres, 0.76 vs 0.61.

**In plain words.**
- Topology finds a hole that the concept goes around for **colours** (robustly) and **residues mod 113**. For **months** there is a hole, and the months go around it, but only in a post hoc analysis and only in the top-3 PCs.
- It does **not** find one for weekdays. The corrected power simulation shows the test rarely detects 7-cluster rings. It finds a loop in days-with-times, but the day does not go around it.
- It finds no loops in ordinal concepts or random controls in the top-3 PCs. In 10 dimensions ordinal concepts do get loops, but their values do not travel around them; going around the hole, not having one, is what distinguishes the cyclic concepts. Since the strict tests never fired for any cyclic set, the specificity evidence is weak.
- The shape fitter's "helices" for cyclic concepts cannot be told apart from closed loops at this noise level. Months come closest to closing.
- Whether steering around these loops changes the model's answers in semantic order is the next experiment. It is designed, and postponed by the author.

![Real activation clouds and their persistence](docs/figures/fig_real_gallery.png)

## Results

### Method A: exact topology of the 44 fitted shapes (Exp0)

- 2 fitted shapes have a hole (b1 = 1; both are cones) and 1 has a void (b2 = 1: GPT-2 W_pos, a closed sphere).
- 27 of the 44 fitted topologies are resolvable at the data's noise scale (ρ_A ≥ 1).
- The analytic rules agree with persistent homology of dense noise-free shape samples for 0.970 of 234 shapes.
- Full tables: [reports/exp0_analytic.md](reports/exp0_analytic.md); point coordinates on the shapes: [reports/coords_check.md](reports/coords_check.md).

![Helix fits: winding vs closure](docs/figures/fig_exp0_helix.png)

### Method B: persistent homology of the clouds (Exp2) and the cyclic tests (Exp3)

| Dataset | top H1 π | null q95 | p (loop) | BH q | traversal: R, winding (θ_B, preregistered) | traversal post hoc, 3D (relaxed range) | top-10 PCs: Rips π vs null q95, p (post hoc) |
|---|---|---|---|---|---|---|---|
| colours (hue) | 5.02 | 2.38 | 0.001 | 0.011 | 0.95, -1 | 0.94, -1 | 2.67 vs 1.61, p = 0.005 |
| grokked residues (k = 20) | 2.45 | 1.83 | 0.001 | 0.011 | 0.97, -1 | 0.96, -1 | 1.16 vs 1.32, p = 1.000 |
| months | 1.72 | 1.44 | 0.002 | 0.018 | no coordinate | 0.72, 1 | 1.13 vs 1.23, p = 0.550 |
| days with times (day) | 2.01 | 1.87 | 0.013 | 0.082 | no coordinate | 0.18, 0 | 1.48 vs 1.41, p = 0.010 |
| weekdays | 1.32 | 1.36 | 0.094 | 0.376 | no coordinate | 0.06, 0 | 1.22 vs 1.39, p = 0.945 |
| years | 1.63 | 1.94 | 0.775 | 1.000 | no coordinate | 0.21, 0 | 1.39 vs 1.35, p = 0.005 |
| GPT-2 positions | 1.22 | 2.16 | 1.000 | 1.000 | no coordinate | 0.30, 0 | 1.01 vs 1.51, p = 1.000 |

**How to read the table:**
- The null is a cluster-centre null for prompt-template designs and a full-dimensional matched Gaussian otherwise, with 999 draws.
- "No coordinate" means DREiMac's preregistered setting, which requires Rips death ≥ 2 × birth, built no circular coordinate.

All 44 clouds: [reports/exp2_invariants.md](reports/exp2_invariants.md). Hypothesis tests: [reports/exp3_cyclic.md](reports/exp3_cyclic.md).

### Instrument validation on synthetic clouds with exact topology (Exp1)

| Estimator | exact (b0,b1,b2) accuracy, macro over 13 families [95% CI] |
|---|---|
| P: alpha + universal null (preregistered primary) | 0.618 [0.610, 0.626] |
| S: Rips H1 + universal null (deviation D1) | 0.660 [0.651, 0.670] |
| Ba: fixed π thresholds (tuned on validation) | 0.714 [0.703, 0.725] |
| Bb: family-implied (fitter's label → modal Betti vector) | 0.812 [0.807, 0.816] |
| Bc: majority vector | 0.555 [0.553, 0.557] |

**Better or worse, in plain words:**
- The preregistered persistent-homology estimator (P) and the fixed-threshold one (Ba) are **worse** than the family label (Bb) overall. Ba misses thin loops (ellipse: 0.51 vs 0.99) and tori (0.11 vs 1.00).
- Ba is **better** where the label is topologically ambiguous: arcs, open or closed (0.79 vs 0.58), and spheres, cap or full (0.76 vs 0.61).
- On well-resolved clouds (ρ_A ≥ 4), the preregistered P scores 0.751 [0.739, 0.763] vs 0.820 [0.812, 0.829] for the family label (macro, cluster-bootstrap CIs).
- P rarely invents holes: 0.019–0.054 false positives on contractible shapes.

![Estimators](docs/figures/fig_exp1_estimators.png)
![Accuracy vs resolvability](docs/figures/fig_exp1_by_rho.png)

## Architecture

```mermaid
flowchart LR
    S["shape-fitting repo (submodule 4c5f3b6)<br/>44 clouds, labels, fitted shapes"] --> A["Method A<br/>exact topology of fitted shape<br/>(b0,b1,b2), chi, genus, rho_A"]
    H["Hugging Face inputs<br/>raw activations, 39k synthetic clouds<br/>+ exact GT parameters"] --> B["Method B<br/>alpha persistent homology<br/>design-matched MC null"]
    S --> B
    H --> A
    A --> C["point coordinates on the fit<br/>(theta_A, t, s, height)"]
    B --> D["cohomology coordinate theta_B<br/>(DREiMac)"]
    C --> T["travel around the hole<br/>alignment R, permutation p, winding"]
    D --> T
    A --> V["Exp1: estimators vs exact GT"]
    B --> V
    T --> G["steering around the loop<br/>(postponed)"]
```

## What happens when you run it

```text
run.py <phase>
  fetch        download inputs/ from the Hugging Face dataset at the pinned revision, verify SHA-256
  exp0         Method A: exact topology + margin of the 44 fits and 40,560 synthetic GT shapes; theta_A tests
  coords       where the labelled points sit on their fitted shapes (curve parameter, azimuth, height, clusters)
  power        validation-stream tuning (b0 rule, baseline thresholds) and the power simulation
  exp1         synthetic validation of the persistent-homology Betti estimators against exact GT topology
  exp2         persistent homology of the 44 clouds with 999-draw design-matched nulls (cached in results/nulls)
  exp3         preregistered cyclic hypotheses H1-H4 (theta_B, top-10-PC check, Holm)
  exp3posthoc  post hoc: theta_B with DREiMac standard_range=False (deviation D5)
  exp4         bottleneck distances between clouds and ideal templates
  exp5         robustness: Rips vs alpha, top-k PCs, full-D cosine, offset removal, seeds, noise scale
  report       regenerate every table, figure and number in README / reports / paper from results/
  site         GitHub Pages explorer (docs/index.html)
  all          everything above, CPU only (about 1.5 h on 16 cores)
  exp6sim, exp6  simulated / LLM steering around the loops (postponed; exp6 needs a GPU and Llama-3.1-8B)
```

## Installation and usage

Requirements: [uv](https://docs.astral.sh/uv/). Python 3.11 is installed by uv; it is pinned because DREiMac requires Python below 3.12. No GPU is needed.

```bash
git clone --recursive https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability.git
```

```bash
cd topology-of-neural-geometry-in-llm-mechanistic-interpretability && uv sync
```

```bash
uv run python run.py all
```

Run the tests:

```bash
uv run pytest
```

Regenerate the documentation numbers and figures from the committed results without recomputing:

```bash
uv run python run.py report site
```

Reproducing the inputs from scratch, which needs a GPU and the source project, is described in [docs/reproduce_inputs.md](docs/reproduce_inputs.md).

## Features

- Exact topology (Betti numbers, χ, genus, boundary, margin) of the source's 13 parametrised shape families, with tests against persistent homology of dense samples.
- Intrinsic coordinates of points on fitted shapes. The numpy parametrisations reproduce the source's fitted shapes to 1e-5.
- Alpha and Rips persistence, the universal null, and design-matched Monte Carlo nulls (cluster-centre and full-dimensional Gaussian, sampled through the Gram matrix).
- Circular coordinates from persistent cohomology, and the travel-around-the-hole statistics: exact permutation tests, winding, cyclic order.
- Validation against exact ground truth on 39,000 synthetic clouds, with cluster-bootstrap CIs.
- Reproducible from GitHub + Hugging Face: pinned revision, SHA-256 manifest, bit-exact regeneration of the synthetic ground truth.
- Every documentation number is generated from `results/`.

## Repository layout

- `src/neurotopo/`:
  - `analytic/`: Method A rules and coordinates.
  - `tda/`: diagrams, nulls, invariants, circular coordinates.
  - `stats/`: alignment and tests.
  - `experiments/`: one module per phase.
  - `steering/`: postponed steering code.
  - `report/`: tables, figures, site, numbers.
- `external/shape-fitting/`: the source project (git submodule, commit 4c5f3b6).
- `reports/`: literature and state-of-the-art reviews, preregistration (with addendum and amendment), deviations, plan, one report per experiment, summary. `reports/templates/` holds the report sources; `reports/generated/` holds generated tables.
- `docs/`: [methodology](docs/methodology.md), [exact topology of the families](docs/analytic_topology.md), [reproducing the inputs](docs/reproduce_inputs.md), figures, explorer.
- `paper/`: LaTeX source and PDF.
- `results/`: machine-readable results of every phase.
- `logs/`: timestamped run logs.

## Technologies

uv, Python 3.11, NumPy, SciPy, scikit-learn, pandas, [GUDHI](https://gudhi.inria.fr) (alpha complexes, bottleneck), [ripser.py](https://github.com/scikit-tda/ripser.py), [persim](https://github.com/scikit-tda/persim), [DREiMac](https://github.com/scikit-tda/DREiMac), matplotlib, plotly.js (explorer), Hugging Face Hub, pytest.

## To do

- **Steering around the detected loops** (preregistered, postponed by the author):
  - simulated steering with cross-validated decoders, then
  - Llama-3.1-8B steering of weekdays, months, days and colours;
  - steering of the grokked modular-addition model, retrained with the source recipe.
- A loop test for weekdays with more prompt templates per day: 7 clusters of 7 points are close to the power limit.
- A distance for comparing clouds that is not dominated by absolute scale (Exp4 was uninformative). For example, bottleneck distance in log-π coordinates.
- Torus and thin-loop detection: the synthetic accuracy for tori is near zero at our sample sizes.

## License

MIT ([LICENSE](LICENSE)). GUDHI's alpha complex is GPL-3.0 through CGAL; see [NOTICE](NOTICE).
