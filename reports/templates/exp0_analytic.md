# Exp0 fitted-shape catalog and semantic coordinates (Method A)

Date: 2026-11-15; wording corrected 2026-11-22 (independent audit, D14). Code: `src/neurotopo/analytic/`, `src/neurotopo/experiments/exp0_analytic.py`. Results: `results/exp0/`. Rules and derivations: [docs/analytic_topology.md](../docs/analytic_topology.md). Preregistration: sections 3, 5 and 6 (H1-A, H2-A).

For synthetic arcs and caps, the target follows the catalog’s 0.98 closure convention. Cluster and polytope targets count centres or vertices. [Raw-domain sensitivity](../results/science/benchmark.csv)

## Question

Which catalog topology does the source assign to each fit, and which fits pass the margin heuristic?

## Method

- `shape_topology(family, params)` gives (b0, b1, b2), χ, genus, boundary components and the margin m, a family-specific gap or diameter measured in data units. The inputs are the fitted canonical parameters (`real_results.json`) or the regenerated ground-truth parameters (synthetic clouds).
- The **margin ratio** is ρ_A = m / (2ν), with ν = median point-to-shape distance + 95th-percentile shape-to-point distance. Both distances use sampled reference points from the parametrisation. A ratio of at least one passes the operational eligibility rule. Formal reconstruction requires additional conditions on sampling and geometry. [Noise and coverage code](../src/neurotopo/tda/ground_truth.py) · [Niyogi et al.](https://doi.org/10.1007/s00454-008-9053-2)
- **Hole coordinate θ_A** is the parameter of each point's nearest point on the fit, read from 4,096-point curve grids or 256×256 surface grids. For fits with a hole (cone frustum) θ_A is the azimuth. For helix fits the azimuth is reported as **axial winding**, descriptive only, with the **closure gap**: the axial distance between the first and last concept means, divided by the radius.
- **Alignment:** concept circular means, R, a permutation p (exact for 7 concepts), and the winding number.
- **Numerical check:** alpha persistent homology of dense noise-free random samples of each fitted or ground-truth shape. Bars with π > 4 that are born below m/4 are counted. Curves use 2,000 jittered samples, because the Delaunay triangulation of points on a helix grows superlinearly ([Erickson 2003](https://doi.org/10.1007/s00454-003-2927-4): Ω(n^{3/2}) for a helix with about √n points per turn, Thm 2.3; every point is joined to every point less than a full turn away, Lemma 2.1, so a helix with T turns has about n²/T edges).

## Results

- {{exp0.n_hole_fits}} of 44 fitted shapes have a hole (b1 = 1). Both are cones, fitted to years and colours. {{exp0.n_void_fits}} has a void (GPT-2 W_pos, a closed sphere).
- {{exp0.n_resolvable}} of 44 fitted topologies are resolvable (ρ_A ≥ 1).
- Families fitted: {{exp0.families}}.
- **Primary cyclic sets.** All three are helices (b1 = 0) with ρ_A = {{exp0.weekdays.rho:2}} (weekdays), {{exp0.months.rho:2}} (months) and {{exp0.grok.rho:2}} (residues). Each is a coil of {{exp0.prim_turns_min:1}}–{{exp0.prim_turns_max:1}} turns, and for {{exp0.helix_pitch_margin_n}} of the {{exp0.helix_n}} helix fits the margin is the spacing between adjacent turns (the pitch), not the gap between the ends. The margin-to-noise rule excludes these fits. The calculation does not measure the topology of a thickened coil. (The ends alone are {{exp0.weekdays.endgap_rho:2}}, {{exp0.months.endgap_rho:2}} and {{exp0.grok.endgap_rho:2}} times 2ν apart.) **H1-A: {{exp3.H1A}}/3** (preregistered rule: a b1 = 0 fit fails).
- **Axial winding** (descriptive):
  - weekdays: R = {{exp0.weekdays.azimuth.R:3}}, exact p = {{exp0.weekdays.azimuth.p}}, winding {{exp0.weekdays.azimuth.w}}, closure gap {{exp0.weekdays.azimuth.gap:2}};
  - months: R = {{exp0.months.azimuth.R:3}}, winding {{exp0.months.azimuth.w}}, closure gap {{exp0.months.azimuth.gap:2}};
  - residues: R = {{exp0.grok.azimuth.R:3}}, winding {{exp0.grok.azimuth.w}}.
- **Not specific:** {{exp0.gp_wind1}} of {{exp0.gp_helix_n}} Gaussian-process controls fitted as helices also wind (R = {{exp0.gp_R_min:2}}–{{exp0.gp_R_max:2}}), with closure gaps of {{exp0.gp_gap_min:2}}–{{exp0.gp_gap_max:2}} ([fig_exp0_helix](../docs/figures/fig_exp0_helix.png)).
- **Colours (exploratory):** the cone frustum's azimuth aligns with hue (R = {{exp0.colors.theta.R:3}}, winding {{exp0.colors.theta.w}}). **Years:** the frustum's azimuth does not wind (winding {{exp0.years.theta.w}}).
- **Numerical check:** agreement {{exp0.dense_agree:3}} over {{exp0.dense_n}} shapes; {{exp0.dense_agree_resolved:3}} where the margin exceeds 4 sample spacings. The failures are apex cones whose 0.001-unit opening is below sampling resolution, and tori whose void needs more samples: their voids are born below the counting cut, but their persistence ratio ({{audit3.tori.pi_min:1}}–{{audit3.tori.pi_max:1}}) stays below the threshold of 4 (checked in the third audit, D9).
- **Synthetic eligibility.** A fraction {{exp0.synth_resolvable:3}} of the test clouds satisfies the catalog margin criterion. [Ground-truth parameter records](../results/exp0/)

<!-- BEGIN:exp0_topology -->
<!-- END:exp0_topology -->

<!-- BEGIN:exp0_alignment -->
<!-- END:exp0_alignment -->

**Topologically equivalent families (synthetic ground truth).** Families in the same column share a homotopy type: for example, blobs, lines, helices, ringing curves, discs and paraboloids are all contractible, while closed arcs, ellipses and cone frusta are circles up to homotopy.

<!-- BEGIN:exp0_family_homotopy -->
<!-- END:exp0_family_homotopy -->

![margin ratios](../docs/figures/fig_exp0_margin.png)

## Interpretation

- A nonzero-pitch helix fit is topologically an open curve. On the primary fits the pitch sets the margin. A small pitch-to-noise ratio flags poor separation under the heuristic. A claim about the topology of its offset requires an actual offset calculation. [Parameters and margins](../results/exp0/real_topology.csv)
- For prompt-template designs (7 or 12 tight clusters), the coverage term of ν is dominated by the gaps between clusters, so a low ρ_A is largely a property of the design.
- The concepts sit around the helix axis in cyclic order, but so do the indices of smooth random processes that the fitter also calls helices, with the same minimum permutation p and winding ±1.
- **Only months stand out by closure:** a gap of {{exp0.months.azimuth.gap:2}} radii, below the controls' range ({{exp0.gp_gap_min:2}}–{{exp0.gp_gap_max:2}}). The weekdays' gap ({{exp0.weekdays.azimuth.gap:2}}) lies inside it.
- Method A therefore cannot by itself establish a semantic hole here.

## Learnings

- **What went wrong, and the fix:**
  - The source's coarse dense samples (24×24 surface grids) overstate point-to-shape distances; the fix was exact parametrisations (D2).
  - Noise-free samples on a helix produced a Delaunay triangulation large enough to exhaust 10 GB (superlinear size; see the method above); the fix was fewer samples plus jitter.
  - Persistence of dense samples finds loops at the margin scale (near-closures). Counting only features born below m/4 separates the exact topology from near-closures. Every real helix fit has one such loop: at the scale of its pitch, adjacent turns merge into a tube around the axis (independent audit, D14; not the ends meeting).
- **Decisions:** the source's own 0.98 thresholds define closed arcs and spheres, so the topology of a fit is exactly what the source reports.
