# Exp2: persistent-homology invariants of the 44 real clouds (Method B)

Date: 2026-11-15; wording corrected 2026-11-22 (independent audit, D14). Code: `src/neurotopo/experiments/exp2_invariants.py`, `realdata.py`. Results: `results/exp2/`, with nulls cached in `results/nulls/`.

## Method

- **Alpha diagrams** (H0–H2, radius units) of each source-identical, RMS-normalised top-3 PCA cloud. The recomputed clouds match the source's stored points to better than 1e-3 of their scale.
- **Significance:** the maximum persistence ratio π = death/birth is compared with 999 draws of a design-matched null.
  - Cluster-centre null for prompt-template designs: weekdays, months, days_time, colours (concept = hue), and the random-init weekday and month controls.
  - Full-dimensional matched-covariance Gaussian for everything else.
  - Every null draw passes through the same top-3 PCA normalisation.
- **Descriptive extras:**
  - universal-null counts for alpha (A = ½) and Rips (A = 1);
  - b0 by the tuned single-linkage rule;
  - all three Betti numbers, χ and a Betti label at the characteristic scale r_c (b0 is read at r_c too since deviation D12; the label is not a homotopy class, because Betti numbers do not determine one);
  - a genus candidate, conditional on a connected closed orientable surface;
  - stability: the fraction of 200 subsamples of 80% (source seeds) whose top π exceeds the full cloud's null threshold.

## Results

The full estimated vector agrees with the fitted catalog vector on {{sci.h4_full}}/{{sci.n_real}} clouds. Restricting the comparison to H1 and H2 gives {{sci.h4_partial}}/{{sci.n_real}}. B uses the tuned component estimator and counts bars across scales. The Betti summary at r_c describes a separate scale-specific quantity. The table below reports descriptive topology and retention frequencies over subsamples. [Full paired estimates](../results/science/h4_datasets.csv) · [Independent null replay](../results/science/null_replay.csv)

<!-- BEGIN:exp2 -->
<!-- END:exp2 -->

The fitted Gaussian or cluster-centre reference preserves specified covariance or residual structure. It can reject open curves or caps. All projection and seed results concern this fixed corpus. Conditional Monte Carlo intervals and nested design-specific calibration are recorded in the audit. [Dataset evidence](../results/science/dataset_assessment.csv) · [Calibration](../results/science/calibration.csv) · [Independent scientific audit](reviews/2026-11-26-scientific-audit.md)
