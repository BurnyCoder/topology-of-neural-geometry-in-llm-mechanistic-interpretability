# Findings per dataset

Each row in the [dataset evidence table](../results/science/dataset_assessment.csv) identifies the design, sample size, fitted family, 3D loop and void ratios, reference ranks, multiplicity adjustments and subsampling retention. The table includes conditional Monte Carlo tail intervals and the higher-dimensional results where computed. A blank higher-dimensional entry indicates missing measurement. Every dataset remains observational.

<!-- BEGIN:readme_roles -->
| role | sets | loop in top-3 PCs (MC null, p < 0.05) | A: resolvable fitted hole, goes around | B: loop, goes around (θ_B, 3D) | B + top-10 check (full H1-B rule) | goes around once, post hoc (3D) |
|---|---|---|---|---|---|---|
| test: cyclic, primary (H1) | weekdays, months, grokking_WE | 2/3 | 0/3 | 1/3 | 0/3 | 2/3 |
| test: cyclic, secondary (H3) | days_time | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| test: cyclic, exploratory | colors | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |
| negative control: ordinal concepts (H2) | gpt2_wpos, counting, pythia_counting, years, temperature, age | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| control: random-init networks (H2) | C3_weekdays_init, C3_months_init, C3_grokking_WE_init | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| control: random walks / Gaussian processes (H2) | 20 sets | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
<!-- END:readme_roles -->

The registered H1-A and H1-B conjunctions fail in all three primary datasets. An open helix can show azimuthal order. Weekday loop p = 0.094. Month loop p = 0.002, with no strict coordinate. Residues align in a frequency-reordered circle in 3D, then lack a strict top-ten coordinate. For days with times the leading path is localized to one cluster. Colours show hue alignment in 3D, with a related pattern in the RGB stimulus baseline. H2's false-positive rule is not triggered. [Fit and coordinate outcomes](../results/science/decisions.csv) · [Measured and refused coordinates](../results/exp3/method_b.json) · [Localisation](../results/exp7_audit/summary.json)

Full and partial A/B agreement differ for four datasets when estimated components are included. The entire vector pair and classification eligibility are listed for every dataset. Both H6 phases lack outcomes. [H4 table](../results/science/h4_datasets.csv) · [H6 register](../results/science/h6_datasets.csv) · [Audit](reviews/2026-11-26-scientific-audit.md)
