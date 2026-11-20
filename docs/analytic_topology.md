# Exact topology of the 13 shape families (Method A)

The source project's fitter returns one of 13 shape families with canonical parameters (`describe()` in [`external/shape-fitting/src/neurogeom/shapes/`](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability/tree/main/src/neurogeom/shapes)). Every family is a known topological space, so its invariants follow exactly from the family and its parameters. The implementation is [`src/neurotopo/analytic/topology.py`](../src/neurotopo/analytic/topology.py); the tests are in [`tests/test_analytic.py`](../tests/test_analytic.py).

## Facts used

All are textbook facts, from [Hatcher, *Algebraic Topology* (2002)](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), chapter 2:
- **Contractible spaces** (point, segment, disc, ball) have Betti numbers (b0, b1, b2) = (1, 0, 0).
- **Circle S¹:** (1, 1, 0).
- **Sphere S²:** (1, 0, 1).
- **Torus T²:** (1, 2, 1).
- **A finite set of k points:** (k, 0, 0).
- **Euler–Poincaré formula:** χ = b0 − b1 + b2.
- **Compact orientable surfaces:** with genus g and n boundary circles, χ = 2 − 2g − n. Every closed surface embedded in ℝ³ is orientable.
- **Cone and frustum:** a cone surface with an apex is a disc: its parametrisation (s, φ) ↦ (s·r cos φ, s·r sin φ, h s) is polar coordinates on a disc, with the apex as centre. (It also deformation-retracts to its apex, but that only shows it is contractible.) The lateral surface of a frustum (r_bot > 0) is an annulus, S¹ × [0, 1], which is homotopy equivalent to S¹ (Hatcher, ch. 0).

## Rules and margins

The **margin** m is the length of the smallest parameter change that changes the topology. ρ_A = m / (2ν) compares it with the cloud's noise-and-coverage scale ν, where ν = median distance from points to the shape + 95th-percentile distance from the shape to the points (see the [preregistration](../reports/preregistration.md), section 3, and deviation D2).

| Family | Topological space | (b0, b1, b2) | χ | genus | boundary | margin m |
|---|---|---|---|---|---|---|
| blob | solid ellipsoid (any Gaussian level set) | (1,0,0) | 1 | – | – | ∞ |
| clusters (k) | k disjoint balls | (k,0,0) | k | – | – | min centroid distance − 4·spread |
| polytope (V vertices) | V points | (V,0,0) | V | – | – | min vertex distance − 4·spread |
| line | segment | (1,0,0) | 1 | – | 2 endpoints | 2·half_length |
| arc, closed (extent_frac ≥ 0.98) | S¹ | (1,1,0) | 0 | – | 0 | 2r (hole diameter) |
| arc, open | segment | (1,0,0) | 1 | – | 2 endpoints | 2r·sin(π(1 − extent_frac)) (endpoint gap) |
| ellipse | S¹ | (1,1,0) | 0 | – | 0 | 2b (minor axis) |
| helix | embedded open curve | (1,0,0) | 1 | – | 2 endpoints | min(endpoint distance, \|pitch\| if turns > 1) |
| ringing | embedded open curve (cos πs is injective on [0, 1]) | (1,0,0) | 1 | – | 2 endpoints | 2·√(a1² + a3²) |
| disc, paraboloid | disc | (1,0,0) | 1 | 0 | 1 circle | ∞ |
| sphere, closed (cap_frac ≥ 0.98) | S² | (1,0,1) | 2 | 0 | 0 | 2r (void diameter) |
| sphere, cap (half-angle α) | disc | (1,0,0) | 1 | 0 | 1 circle | 2r·sin(max(α, π/2)) |
| cone, r_bot > 0 | annulus | (1,1,0) | 0 | 0 | 2 circles | 2·r_bot (narrow end) |
| cone, r_bot = 0 | disc | (1,0,0) | 1 | 0 | 1 circle | 0 |
| torus (r = R·ratio < R) | T² | (1,2,1) | 0 | 1 | 0 | min(2r, 2(R − r)) |

**Notes on the rules:**
- The 0.98 thresholds for closed arcs and closed spheres are the source's own (`Arc.FULL`, `Sphere.FULL`). Below the threshold, the source reports an open arc or a cap.
- The source caps the torus ratio at 0.95, so horn and spindle tori cannot occur. They are handled anyway: a horn torus is homotopy equivalent to S² ∨ S¹, with Betti numbers (1, 1, 1); a spindle torus is an outer and an inner sphere glued at the two axis points, homotopy equivalent to S² ∨ S² ∨ S¹, with Betti numbers (1, 1, 2) (fixed in the math fact-check; it had (1, 1, 1)).
- The ringing curve c + Σₖ aₖ cos(kπs) eₖ is embedded: its first coordinate a1·cos(πs) is strictly monotone on [0, 1].

## Numerical check

The analytic Betti numbers are compared with alpha-complex persistent homology of dense noise-free random samples of each shape: 10,000 samples for surfaces, and 2,000 slightly jittered samples for curves, whose Delaunay triangulation can otherwise grow quadratically. Only bars with π > 4 that are born below m/4 are counted.
- The exact topology holds at scales below the margin. A loop born at about m/2 is a near-closure, for example the two ends of a helix with a small gap. It is reported separately as `near_closure_loops`.
- Results are in `results/exp0/dense_check.csv` and summarised in [reports/exp0_analytic.md](../reports/exp0_analytic.md).
