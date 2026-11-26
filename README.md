# Topology of neural geometry

Do months, weekdays, or modular residues trace a loop in a neural representation? This study fits geometric shapes to activations and weights, measures persistent homology after PCA, and tests whether semantic labels wind around a circular coordinate. The strict test passes for **0 of three primary datasets by fitted shape and 0 by persistent homology**. Modular residues align and wind once in three dimensions, then lose the required coordinate in ten PCs. The amended primary hypothesis asks whether steering around a loop changes model behaviour. That experiment is **untested**. [Paper](paper/main.pdf) · [Registered rules and amendments](reports/preregistration.md) · [Dataset decisions](results/science/decisions.csv)

**26 November 2026 scientific audit.** Including connected components gives full-vector agreement on **27/44** real datasets. The corrected flagged-cloud false-positive count is **350/4144**. Persistence beats the fitted-family baseline on arcs and the sphere family under the registered catalog convention. Both rankings reverse when the target uses the actual angular domains, with the same predictions and eligible examples. [Independent review and claim ledger](reports/reviews/2026-11-26-scientific-audit.md) · [Comparison with paired intervals](results/science/benchmark.csv) · [False-positive cohorts](results/science/false_positives.csv)

![Comparison of catalog and raw angular-domain scoring for the same predictions](docs/figures/fig_scientific_audit.png)

[Interactive cloud explorer](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/) · [Interactive examples](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/examples.html) · [Public audit tables](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/scientific-audit.html) · [Inputs and results on Hugging Face](https://huggingface.co/datasets/BurnyCoder/topology-of-neural-geometry)

## Findings in the measured projections

| Dataset or group | Evidence and scope |
|---|---|
| Weekdays | The top-three-PC alpha loop test gives p = 0.094. The fitted open helix can order days by azimuth. Its axis supplies no fitted hole. |
| Months | The top-three-PC loop passes (p = 0.002). DREiMac refuses the short class with its registered setting. A relaxed, post hoc coordinate aligns with months. A small gap in an underlying arc remains compatible with these observations. |
| Residues mod 113 | A frequency-reordered residue sequence aligns with the strict 3D coordinate (loop p = 0.001). This projected result fails the required ten-PC check. |
| Days with times | The leading 3D loop passes its Gaussian reference and is localized within a day cluster. The registered secondary semantic conjunction fails. |
| Colour hue | Hue winds once in the strict 3D coordinate. The input RGB values also exhibit a hue-aligned loop. The comparison leaves the model mechanism unresolved. |
| Ordinal concepts and controls | No registered strict conjunction passes. Some ordinal datasets exceed a ten-PC loop reference. Finite negative controls and low sensitivity limit claims about specificity. |

[Per-dataset measurements and conditional uncertainty](results/science/dataset_assessment.csv) · [Coordinates and winding](results/exp3/method_b.json) · [Relaxed coordinates](results/exp3/posthoc_relaxed_range.json) · [Control outcomes](reports/exp3_cyclic.md) · [RGB and localisation](results/exp7_audit/summary.json)

![Examples of projected activation clouds and controls](docs/figures/fig_examples.png)

## Synthetic benchmark

Each estimator predicts a Betti vector describing components, loops and voids. The registered score averages eligible-cloud accuracy within each family, then weights the families equally. Polytopes are scored on components alone. P applies an empirical Gumbel score to alpha bars, S uses Rips H1, Ba uses validation-tuned thresholds, Bb uses the fitted family and its validation target, and Bc predicts the majority vector. MC is a fitted Gaussian comparator on a smaller subset. The threshold method and the family baseline both outperform P on the catalog target. [Scoring code](src/neurotopo/experiments/exp1_synthetic.py) · [Ground-truth conventions](docs/analytic_topology.md) · [Empirical score](https://doi.org/10.1038/s41598-023-37842-2)

<!-- BEGIN:exp1 -->
| estimator | macro exact accuracy | 95% CI | n clouds |
|---|---|---|---|
| P_alpha_universal | 0.618 | [0.610, 0.626] | 30114 |
| S_rips_universal | 0.660 | [0.651, 0.670] | 30114 |
| Ba_fixed_pi | 0.714 | [0.703, 0.725] | 30114 |
| Bb_family_implied | 0.812 | [0.807, 0.816] | 30114 |
| Bc_majority | 0.555 | [0.553, 0.557] | 30114 |
| MC_gaussian3d (subset) | 0.594 | [0.561, 0.629] | 2427 |
| P_alpha_universal (subset) | 0.615 | [0.588, 0.644] | 2427 |
| S_rips_universal (subset) | 0.674 | [0.640, 0.703] | 2427 |

Paired differences (primary minus comparator):

| comparison | difference | 95% CI |
|---|---|---|
| P - S_rips_universal | -0.042 | [-0.051, -0.033] |
| P - Ba_fixed_pi | -0.096 | [-0.108, -0.084] |
| P - Bb_family_implied | -0.194 | [-0.203, -0.185] |
| P - Bc_majority | 0.063 | [0.055, 0.071] |

False-positive rate (b1 >= 1 or b2 >= 1) on resolvable contractible clouds, by N-bin:

| estimator | N-bin 0 | N-bin 1 | N-bin 2 | N-bin 3 |
|---|---|---|---|---|
| P_alpha_universal | 0.018 | 0.045 | 0.075 | 0.065 |
| S_rips_universal | 0.002 | 0.055 | 0.107 | 0.108 |
| Ba_fixed_pi | 0.000 | 0.002 | 0.029 | 0.076 |
| Bb_family_implied | 0.108 | 0.024 | 0.005 | 0.003 |
| Bc_majority | 0.000 | 0.000 | 0.000 | 0.000 |

Universal-null calibration on blobs (FWER = fraction with any significant alpha H1 bar):

| N-bin | fwer_alpha_universal | ks_uniform_D | n_pvalues | n_clouds | by_noise_bin |
|---|---|---|---|---|---|
| 0 | 0.009 | 0.117 | 3011 | 750 | {'0': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '1': {'n': 250, 'hits': 2, 'rate': 0.008, 'cluster_ci': [0.0, 0.02]}, '2': {'n': 250, 'hits': 4, 'rate': 0.016, 'cluster_ci': [0.0, 0.036]}} |
| 1 | 0.004 | 0.066 | 34043 | 750 | {'0': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '1': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}, '2': {'n': 250, 'hits': 1, 'rate': 0.004, 'cluster_ci': [0.0, 0.012]}} |
| 2 | 0.000 | 0.048 | 185130 | 750 | {'0': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '1': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '2': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}} |
| 3 | 0.000 | 0.035 | 1003790 | 750 | {'0': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '1': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}, '2': {'n': 250, 'hits': 0, 'rate': 0.0, 'cluster_ci': [0.0, 0.0]}} |

Per-family exact accuracy (resolvable clouds):

| family | P_alpha_universal | S_rips_universal | Ba_fixed_pi | Bb_family_implied | Bc_majority |
|---|---|---|---|---|---|
| arc | 0.651 | 0.753 | 0.788 | 0.576 | 0.582 |
| blob | 0.990 | 0.986 | 0.998 | 0.945 | 1.000 |
| clusters | 0.340 | 0.339 | 0.341 | 0.328 | 0.000 |
| cone | 0.007 | 0.334 | 0.534 | 0.943 | 0.000 |
| disc | 0.974 | 0.963 | 0.985 | 0.954 | 1.000 |
| ellipse | 0.257 | 0.546 | 0.509 | 0.990 | 0.000 |
| helix | 0.783 | 0.654 | 0.861 | 0.987 | 1.000 |
| line | 0.953 | 0.952 | 0.963 | 0.991 | 1.000 |
| paraboloid | 0.968 | 0.956 | 0.984 | 0.911 | 1.000 |
| polytope | 0.500 | 0.500 | 0.500 | 0.351 | 0.000 |
| ringing | 0.928 | 0.927 | 0.947 | 0.970 | 1.000 |
| sphere | 0.687 | 0.675 | 0.761 | 0.609 | 0.638 |
| torus | 0.000 | 0.000 | 0.111 | 1.000 | 0.000 |

Resolvable fraction of test clouds: 0.772.
<!-- END:exp1 -->

| Family | Catalog P | Catalog Bb | Angular-domain P | Angular-domain Bb |
|---|---:|---:|---:|---:|
| Arc | 0.651 | 0.576 | 0.859 | 0.978 |
| Sphere or cap | 0.687 | 0.609 | 0.610 | 0.965 |

The raw-domain sensitivity keeps predictions and catalog eligibility fixed. It changes the target for a near-complete arc or cap when its generating angular interval still has a gap. The source's 0.98 cutoff is a reporting convention. Whole-chunk resampling supplies paired uncertainty. The flagged-cloud estimate 0.0845 remains below the registered 0.10 ablation threshold. [All scores and intervals](results/science/benchmark.csv) · [Individual angular fractions](results/science/angular_domains.csv) · [False positives](results/science/false_positives.csv)

## How the methods work

![Data flow from source clouds to fitted coordinates, persistence, and semantic tests](docs/figures/fig_pipeline.png)

1. Fetch the SHA-256-verified raw inputs and the pinned shape-fitting source. Centre and project activations with PCA, apply the source frame orientation, and normalize to unit RMS radius. Both methods use these observations. [Source export and reproduction](docs/reproduce_inputs.md)
2. Method A assigns catalog topology to the fitted parameters and projects points onto the fitted shape. Its margin-to-noise ratio screens the relative sizes of selected features and sampling distances. Reconstruction guarantees require additional assumptions about the sampled space. [Catalog definitions](docs/analytic_topology.md) · [Sampling theorem](https://doi.org/10.1007/s00454-008-9053-2)
3. Method B computes alpha persistence in three dimensions. It compares maximum death/birth ratios against new clouds from a fitted Gaussian or cluster-centre reference, passing each draw through PCA. These reference comparisons are approximate. [GUDHI](https://gudhi.inria.fr/python/latest/delaunay_complex_ref.html) · [Calibration by design](results/science/calibration.csv)
4. DREiMac constructs a circle-valued coordinate from landmark Rips cohomology. The strict semantic test combines the 3D loop, alignment after label permutation, absolute winding one, and alignment and winding in ten PCs. The primary residue test repeats the frequency search under permutation. The analysis is observational. [DREiMac theory](https://dreimac.scikit-tda.org/en/latest/theory.html) · [Strict criteria](reports/preregistration.md) · [Condition-by-condition results](results/science/decisions.csv)

The explorer lets you vary ball radius, select a bar, view a path or shell, and inspect sample labels. It flags birth paths that carry older homology across their paired death. Gallery selection and relaxed coordinate settings are exploratory. [Chain certificates](results/science/representatives.csv.gz) · [Loop gallery](reports/loops.md) · [Void gallery](reports/voids.md) · [Illustrated worked example](docs/worked_example.md)

## Reproduce the results

Use Git with submodules, [uv](https://docs.astral.sh/uv/) and Python 3.11. The PDF phase uses pdfLaTeX with BibTeX, or Tectonic. For the final automated text check, install Poppler’s pdftotext or the Python package pypdf. Calculations run on CPU. The synthetic replay saves completed batches in `data/replay/exp1/` and resumes after interruption when the input manifest, parameters, code and lockfile match. Set `LOKY_MAX_CPU_COUNT` to a smaller worker count on memory-limited machines. The normal route reads the exported activations without loading a language model.

```bash
git clone --recursive https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability.git
cd topology-of-neural-geometry-in-llm-mechanistic-interpretability
uv sync --frozen
uv run --frozen pytest -q
uv run --frozen python run.py science
```

`science` fetches the pinned inputs, rebuilds catalog targets and validation tuning, computes test-cloud predictions, replays the real-data endpoints and fitted nulls, calibrates the tests, checks every illustrated chain, and renders the publication. `uv run --frozen python run.py report site pdf` rebuilds displays from existing results. `uv run --frozen python run.py all` additionally runs the historical exploratory experiments. Source outputs and settings are in [configs/base.yaml](configs/base.yaml), [run.py](run.py) and [timestamped logs](logs/). The optional environment override template is [.env.example](.env.example).

## Evidence and remaining questions

- [Independent audit](reports/reviews/2026-11-26-scientific-audit.md), [machine-readable claim ledger](results/science/claims.csv), [chronology and deviations](reports/deviations.md), [summary](reports/summary.md) and [run plan](reports/plan.md).
- [Literature review](reports/literature-review.md), [state of the art](reports/state-of-the-art-review.md), [methodology](docs/methodology.md) and [glossary](docs/glossary.md).
- [Synthetic controls](results/science/analytic_controls.csv), [benchmark](reports/exp1_synthetic.md), [projection sensitivity](reports/exp4_exp5.md) and [per-dataset findings](reports/findings_per_dataset.md).
- The outstanding experiments are the registered H6 simulated and model interventions, new colour-prompt controls, and a comparison against smooth open-curve alternatives. The existing study uses a fixed set of model checkpoints, prompt templates and projections. [Steering plan](reports/exp6_steering.md) · [Study limits and next steps](reports/plan.md)

## License

MIT for this repository. Bundled and runtime components retain their own licenses. [LICENSE](LICENSE) · [NOTICE](NOTICE)
