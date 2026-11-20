# Exp0: exact topology of the fitted shapes (Method A)

Date: 2026-11-15. Code: `src/neurotopo/analytic/`, `src/neurotopo/experiments/exp0_analytic.py`. Results: `results/exp0/`. Rules and derivations: [docs/analytic_topology.md](../docs/analytic_topology.md). Preregistration: sections 3, 5 and 6 (H1-A, H2-A).

## Question

The source fits each cloud with a uniquely parametrised shape. What is the exact topology of that shape, and do the data resolve it?

## Method

- `shape_topology(family, params)` gives (b0, b1, b2), χ, genus, boundary components and the margin m, the size of the smallest gap or diameter whose closing or collapse alters the topology (a feature size in data units, not a parameter change). The inputs are the fitted canonical parameters (`real_results.json`) or the regenerated ground-truth parameters (synthetic clouds).
- The **margin ratio** is ρ_A = m / (2ν), with ν = median point-to-shape distance + 95th-percentile shape-to-point distance. Both distances use the exact parametrisation (deviation D2). ρ_A ≥ 1 means the topology is resolvable, a heuristic criterion (balls of radius ν from both sides of a gap m meet once 2ν ≥ m), not a recovery theorem ([Niyogi, Smale & Weinberger 2008](https://doi.org/10.1007/s00454-008-9053-2) give one in terms of the reach).
- **Hole coordinate θ_A** is the parameter of each point's nearest point on the fit, read from 4,096-point curve grids or 256×256 surface grids. For fits with a hole (cone frustum) θ_A is the azimuth. For helix fits the azimuth is reported as **axial winding**, descriptive only, with the **closure gap**: the axial distance between the first and last concept means, divided by the radius.
- **Alignment:** concept circular means, R, a permutation p (exact for 7 concepts), and the winding number.
- **Numerical check:** alpha persistent homology of dense noise-free random samples of each fitted or ground-truth shape. Bars with π > 4 that are born below m/4 are counted. Curves use 2,000 jittered samples, because the Delaunay triangulation of points on a helix grows superlinearly (Ω(n^{3/2}) for evenly spaced helix points, [Erickson 2003](https://doi.org/10.1007/s00454-003-2927-4), Thm 2.3).

## Results

- {{exp0.n_hole_fits}} of 44 fitted shapes have a hole (b1 = 1). Both are cones, fitted to years and colours. {{exp0.n_void_fits}} has a void (GPT-2 W_pos, a closed sphere).
- {{exp0.n_resolvable}} of 44 fitted topologies are resolvable (ρ_A ≥ 1).
- Families fitted: {{exp0.families}}.
- **Primary cyclic sets.** All three are helices (b1 = 0) with ρ_A = {{exp0.weekdays.rho:2}} (weekdays), {{exp0.months.rho:2}} (months) and {{exp0.grok.rho:2}} (residues). Their "openness" is not resolvable. **H1-A: 0/3** (preregistered rule: a b1 = 0 fit fails).
- **Axial winding** (descriptive):
  - weekdays: R = {{exp0.weekdays.azimuth.R:3}}, exact p = {{exp0.weekdays.azimuth.p}}, winding {{exp0.weekdays.azimuth.w}}, closure gap {{exp0.weekdays.azimuth.gap:2}};
  - months: R = {{exp0.months.azimuth.R:3}}, winding {{exp0.months.azimuth.w}}, closure gap {{exp0.months.azimuth.gap:2}};
  - residues: R = {{exp0.grok.azimuth.R:3}}, winding {{exp0.grok.azimuth.w}}.
- **Not specific:** {{exp0.gp_wind1}} of {{exp0.gp_helix_n}} Gaussian-process controls fitted as helices also wind (R = {{exp0.gp_R_min:2}}–{{exp0.gp_R_max:2}}), with closure gaps of {{exp0.gp_gap_min:2}}–{{exp0.gp_gap_max:2}} ([fig_exp0_helix](../docs/figures/fig_exp0_helix.png)).
- **Colours (exploratory):** the cone frustum's azimuth aligns with hue (R = {{exp0.colors.theta.R:3}}, winding {{exp0.colors.theta.w}}). **Years:** the frustum's azimuth does not wind (winding {{exp0.years.theta.w}}).
- **Numerical check:** agreement {{exp0.dense_agree:3}} over {{exp0.dense_n}} shapes; {{exp0.dense_agree_resolved:3}} where the margin exceeds 4 sample spacings. The failures are apex cones whose 0.001-unit opening is below sampling resolution, and tori whose void needs more samples: their voids are born below the counting cut, but their persistence ratio ({{audit3.tori.pi_min:1}}–{{audit3.tori.pi_max:1}}) stays below the threshold of 4 (checked in the third audit, D9).
- **Synthetic ground truth:** {{exp0.synth_resolvable:3}} of the 39,000 test clouds have resolvable topology.

<!-- BEGIN:exp0_topology -->
<!-- END:exp0_topology -->

<!-- BEGIN:exp0_alignment -->
<!-- END:exp0_alignment -->

**Topologically equivalent families (synthetic ground truth).** Families in the same column share a homotopy type: for example, blobs, lines, helices, ringing curves, discs and paraboloids are all contractible, while closed arcs, ellipses and cone frusta are circles up to homotopy.

<!-- BEGIN:exp0_family_homotopy -->
<!-- END:exp0_family_homotopy -->

![margin ratios](../docs/figures/fig_exp0_margin.png)

## Interpretation

- A fitted helix is topologically an open curve. For the cyclic concepts, though, ρ_A = {{exp0.weekdays.rho:2}} (weekdays), {{exp0.months.rho:2}} (months) and {{exp0.grok.rho:2}} (residues): whether the curve is open or closed is **unresolvable** at the data's noise scale. That is not evidence of closure.
- For prompt-template designs (7 or 12 tight clusters), the coverage term of ν is dominated by the gaps between clusters, so a low ρ_A is largely a property of the design.
- The concepts sit around the helix axis in cyclic order, but so do the indices of smooth random processes that the fitter also calls helices, with the same minimum permutation p and winding ±1.
- **Only months stand out by closure:** a gap of {{exp0.months.azimuth.gap:2}} radii, below the controls' range ({{exp0.gp_gap_min:2}}–{{exp0.gp_gap_max:2}}). The weekdays' gap ({{exp0.weekdays.azimuth.gap:2}}) lies inside it.
- Method A therefore cannot by itself establish a semantic hole here.

## Learnings

- **What went wrong, and the fix:**
  - The source's coarse dense samples (24×24 surface grids) overstate point-to-shape distances; the fix was exact parametrisations (D2).
  - Noise-free samples on a helix produced a Delaunay triangulation large enough to exhaust 10 GB (superlinear size; see the method above); the fix was fewer samples plus jitter.
  - Persistence of dense samples finds loops at the margin scale (near-closures). Counting only features born below m/4 separates the exact topology from near-closures. It also shows that every real helix fit is a near-closed loop at its own scale.
- **Decisions:** the source's own 0.98 thresholds define closed arcs and spheres, so the topology of a fit is exactly what the source reports.
