# Topology of neural geometry

Do months, weekdays, or modular residues trace a loop in a neural representation? This study fits geometric shapes to activations and weights, measures persistent homology after PCA, and tests whether semantic labels wind around a circular coordinate. The strict test passes for **{{exp3.H1A}} of three primary datasets by fitted shape and {{exp3.H1B}} by persistent homology**. Modular residues align and wind once in three dimensions, then lose the required coordinate in ten PCs. The amended primary hypothesis asks whether steering around a loop changes model behaviour. That experiment is **untested**. [Paper](paper/main.pdf) · [Registered rules and amendments](reports/preregistration.md) · [Dataset decisions](results/science/decisions.csv)

**26 November 2026 scientific audit.** Including connected components gives full-vector agreement on **{{sci.h4_full}}/{{sci.n_real}}** real datasets. The corrected flagged-cloud false-positive count is **{{sci.fpr.all.flag.hits}}/{{sci.fpr.all.flag.n}}**. Persistence beats the fitted-family baseline on arcs and the sphere family under the registered catalog convention. Both rankings reverse when the target uses the actual angular domains, with the same predictions and eligible examples. [Independent review and claim ledger](reports/reviews/2026-11-26-scientific-audit.md) · [Comparison with paired intervals](results/science/benchmark.csv) · [False-positive cohorts](results/science/false_positives.csv)

![Comparison of catalog and raw angular-domain scoring for the same predictions](docs/figures/fig_scientific_audit.png)

[Interactive cloud explorer](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/) · [Interactive examples](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/examples.html) · [Public audit tables](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/scientific-audit.html) · [Inputs and results on Hugging Face](https://huggingface.co/datasets/BurnyCoder/topology-of-neural-geometry)

## Findings in the measured projections

| Dataset or group | Evidence and scope |
|---|---|
| Weekdays | The top-three-PC alpha loop test gives p = {{exp2.weekdays.p_top_loop}}. The fitted open helix can order days by azimuth. Its axis supplies no fitted hole. |
| Months | The top-three-PC loop passes (p = {{exp2.months.p_top_loop}}). DREiMac refuses the short class with its registered setting. A relaxed, post hoc coordinate aligns with months. A small gap in an underlying arc remains compatible with these observations. |
| Residues mod 113 | A frequency-reordered residue sequence aligns with the strict 3D coordinate (loop p = {{exp2.grok.p_top_loop}}). This projected result fails the required ten-PC check. |
| Days with times | The leading 3D loop passes its Gaussian reference and is localized within a day cluster. The registered secondary semantic conjunction fails. |
| Colour hue | Hue winds once in the strict 3D coordinate. The input RGB values also exhibit a hue-aligned loop. The comparison leaves the model mechanism unresolved. |
| Ordinal concepts and controls | No registered strict conjunction passes. Some ordinal datasets exceed a ten-PC loop reference. Finite negative controls and low sensitivity limit claims about specificity. |

[Per-dataset measurements and conditional uncertainty](results/science/dataset_assessment.csv) · [Coordinates and winding](results/exp3/method_b.json) · [Relaxed coordinates](results/exp3/posthoc_relaxed_range.json) · [Control outcomes](reports/exp3_cyclic.md) · [RGB and localisation](results/exp7_audit/summary.json)

![Examples of projected activation clouds and controls](docs/figures/fig_examples.png)

## Synthetic benchmark

Each estimator predicts a Betti vector describing components, loops and voids. The registered score averages eligible-cloud accuracy within each family, then weights the families equally. Polytopes are scored on components alone. P applies an empirical Gumbel score to alpha bars, S uses Rips H1, Ba uses validation-tuned thresholds, Bb uses the fitted family and its validation target, and Bc predicts the majority vector. MC is a fitted Gaussian comparator on a smaller subset. The threshold method and the family baseline both outperform P on the catalog target. [Scoring code](src/neurotopo/experiments/exp1_synthetic.py) · [Ground-truth conventions](docs/analytic_topology.md) · [Empirical score](https://doi.org/10.1038/s41598-023-37842-2)

<!-- BEGIN:exp1 -->
<!-- END:exp1 -->

| Family | Catalog P | Catalog Bb | Angular-domain P | Angular-domain Bb |
|---|---:|---:|---:|---:|
| Arc | {{sci.catalog.arc.P.accuracy:3}} | {{sci.catalog.arc.Bb.accuracy:3}} | {{sci.angular.arc.P.accuracy:3}} | {{sci.angular.arc.Bb.accuracy:3}} |
| Sphere or cap | {{sci.catalog.sphere.P.accuracy:3}} | {{sci.catalog.sphere.Bb.accuracy:3}} | {{sci.angular.sphere.P.accuracy:3}} | {{sci.angular.sphere.Bb.accuracy:3}} |

The raw-domain sensitivity keeps predictions and catalog eligibility fixed. It changes the target for a near-complete arc or cap when its generating angular interval still has a gap. The source's 0.98 cutoff is a reporting convention. Whole-chunk resampling supplies paired uncertainty. The flagged-cloud estimate {{sci.fpr.all.flag.rate:4}} remains below the registered 0.10 ablation threshold. [All scores and intervals](results/science/benchmark.csv) · [Individual angular fractions](results/science/angular_domains.csv) · [False positives](results/science/false_positives.csv)

## How the methods work

![Data flow from source clouds to fitted coordinates, persistence, and semantic tests](docs/figures/fig_pipeline.png)

1. Fetch the SHA-256-verified raw inputs and the pinned shape-fitting source. Centre and project activations with PCA, apply the source frame orientation, and normalize to unit RMS radius. Both methods use these observations. [Source export and reproduction](docs/reproduce_inputs.md)
2. Method A assigns catalog topology to the fitted parameters and projects points onto the fitted shape. Its margin-to-noise ratio screens the relative sizes of selected features and sampling distances. Reconstruction guarantees require additional assumptions about the sampled space. [Catalog definitions](docs/analytic_topology.md) · [Sampling theorem](https://doi.org/10.1007/s00454-008-9053-2)
3. Method B computes alpha persistence in three dimensions. It compares maximum death/birth ratios against new clouds from a fitted Gaussian or cluster-centre reference, passing each draw through PCA. These reference comparisons are approximate. [GUDHI](https://gudhi.inria.fr/python/latest/delaunay_complex_ref.html) · [Calibration by design](results/science/calibration.csv)
4. DREiMac constructs a circle-valued coordinate from landmark Rips cohomology. The strict semantic test combines the 3D loop, alignment after label permutation, absolute winding one, and alignment and winding in ten PCs. The primary residue test repeats the frequency search under permutation. The analysis is observational. [DREiMac theory](https://dreimac.scikit-tda.org/en/latest/theory.html) · [Strict criteria](reports/preregistration.md) · [Condition-by-condition results](results/science/decisions.csv)

The explorer lets you vary ball radius, select a bar, view a path or shell, and inspect sample labels. It flags birth paths that carry older homology across their paired death. Gallery selection and relaxed coordinate settings are exploratory. [Chain certificates](results/science/representatives.csv.gz) · [Loop gallery](reports/loops.md) · [Void gallery](reports/voids.md) · [Illustrated worked example](docs/worked_example.md)

## Reproduce the results

Use Git with submodules, [uv](https://docs.astral.sh/uv/) and Python 3.11. The PDF phase uses pdfLaTeX with BibTeX, or Tectonic. For the final automated text check, install Poppler’s pdftotext or the Python package pypdf. Calculations run on CPU. The normal route reads the exported activations without loading a language model.

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
