# Method and terms

This page explains the method and every technical term used in the [README](../README.md), the [interactive explorer](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/) and the [examples page](https://burnycoder.github.io/topology-of-neural-geometry-in-llm-mechanistic-interpretability/examples.html).
- For every step carried out with numbers on a toy cloud, see the [worked example](worked_example.md).
- The primary reference for the idea of counting holes with persistent homology is the video [What is...persistent homology?](https://www.youtube.com/watch?v=w6Jx1vFp_Gk) (VisualMath).
- The exact rules are in the [preregistration](../reports/preregistration.md); the reasons for each choice are in [methodology.md](methodology.md).

## The method in one minute

1. **Take a point cloud.** It holds a model's activations for one concept set, for example the residual stream of Llama-3.1-8B at the token of each weekday, flattened to its top-3 principal components.
2. **Method A: read the topology off a fitted shape.** A sibling project fitted one of 13 shape families to each cloud. Each family's holes are known exactly. A margin ratio says whether the data's noise is small enough to tell.
3. **Method B: measure the holes of the cloud itself.** Grow a ball around every point and record when loops appear and when they are filled in (persistent homology).
   - A loop counts as significant only if it persists longer than the most persistent loop of most random clouds built to match the data's design (a Monte Carlo null).
4. **Check where the loop lives.** If it dies before two concepts' clusters ever touch, it is a small loop inside one cluster, not a ring of concepts.
5. **Travel around the hole.** Give every point an angle around the loop, then ask whether the concepts sit around it in their natural order (Monday, Tuesday, …) and go around exactly once.
6. **Say what was found.** The words loop, ring, goes around once and suggestive have the strict meanings defined at the end of this page.

## Data

### Point cloud
One point per prompt or per item. Each point is the model's internal vector (activation or weight row) for that input, as stored by the source project ([shape-fitting](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability)). There are 44 clouds: language-model concepts, toy networks, random-init controls and random processes.

### Top-3 PCA coordinates
How each cloud is flattened to 3D (`fit_frame`):
- centre it;
- project it on the 3 directions of largest variance (principal components, PC1–PC3);
- flip each axis so its skewness is positive;
- divide by the RMS radius, so every cloud has root-mean-square distance 1 from its centre.

Holes are measured in these 3D coordinates; checks repeat the loop test in the top-5 and top-10 PCs. Radii (r, birth, death) are in these normalised units, so they are comparable across clouds.

### Concept and semantic cycle
The **concept** of a point is what it stands for: a weekday, a month, a hue, a residue mod 113, or, for ordinal sets such as years, an equal-width value bin.
- A concept's **semantic phase** φ_c = 2πc/n is its place in its natural cycle (Monday = 0, Tuesday = 1/7 of a turn, …).
- For residues the phase is 2π·k·r/113, where k is the Fourier frequency that fits best.

### Prompt-template design
Several prompts per concept (for example several sentences ending in the same weekday), so the points form one cluster per concept. These clouds get the cluster-centre null (see below).

## Method A: exact topology of the fitted shape

### Fitted shape (13 families)
The source project fitted each cloud with one of 13 parametrised families: blob, clusters, polytope, line, arc, ellipse, helix, ringing curve, disc, paraboloid, sphere or cap, cone, torus. In the explorer the fitted shape is drawn as grey dots. The family table is in [analytic_topology.md](analytic_topology.md).

### Betti numbers
(b0, b1, b2) count the pieces, the independent loops (1-dimensional holes) and the enclosed voids (2-dimensional cavities) of a space.
- Examples: a circle has (1, 1, 0), a sphere (1, 0, 1), a torus (1, 2, 1), and a disc or ball (1, 0, 0).
- **Method A** reads them exactly off the fitted family and its parameters ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), chapter 2).
- **Method B** reads all three at the characteristic scale r_c: b0 is the number of pieces of the alpha complex at r_c (pieces smaller than the b0 rule's minimum size do not count), and b1, b2 count the significant loops and voids alive at r_c. Before deviation D12, b0 came from the b0 rule's own cut, a different scale. Separately, the b0 rule (a single-linkage clustering rule tuned on validation clouds) gives the cloud's number of clusters.

### Euler characteristic
χ = b0 − b1 + b2 (the Euler–Poincaré formula, [Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), Thm 2.44). One number that summarises the Betti numbers: 2 for a sphere, 0 for a circle or a torus, 1 for a disc. For Method B this alternating sum uses filtered estimates and is a descriptive summary. Establishing the Euler characteristic of an actual space requires its full Betti numbers.

### Genus
For a connected closed orientable surface, χ = 2 − 2g and g counts handles: 0 for a sphere, 1 for a torus. "–" when the space is not a closed surface.

### Homotopy type and Betti label
Two spaces have the same **homotopy type** if one can be continuously deformed into the other, for example a circle, an annulus and a solid torus, or a point and a disc ([Hatcher 2002](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf), ch. 0). No homotopy invariant, homology included, can tell such spaces apart.
- **Method A** knows the fitted space itself, so it reports its true homotopy type: point, circle, sphere, torus, k points.
- **Method B** has only Betti numbers, which do not determine a homotopy type: a torus and a sphere with two circles attached at a point both have (1, 2, 1), and (1, 0, 0) means "acyclic", which is weaker than contractible. Its **Betti label** therefore says acyclic (1,0,0), circle-like (1,1,0), sphere-like (1,0,1), torus-like (1,2,1), k components, or other (deviation D12).

### Margin ratio rho_A
ρ_A = m / (2ν) asks whether the data can resolve the fitted shape's topology.
- m is the size of the smallest geometric feature whose closing or collapse would change the topology: a gap, for example between a helix's two ends or between two adjacent turns of a helix (its pitch), or a diameter, for example of a hole or a torus tube. It is a length in the data's units, not the parameter change itself.
- ν is the cloud's noise-and-coverage scale: the median distance from the points to the shape plus the 95th-percentile distance from the shape to the points.

### Resolvable
ρ_A ≥ 1: the topological feature is larger than twice the noise-and-coverage scale. This is a heuristic, not a theorem: balls of radius ν grown from both sides of a gap m meet once 2ν ≥ m. A rigorous counterpart, in terms of the shape's reach rather than its margin, is the covering condition of [Niyogi, Smale & Weinberger 2008](https://doi.org/10.1007/s00454-008-9053-2) (Prop. 3.1; its random-sample version is Thm 3.1). Below one, the fit fails the specified eligibility rule. For several helices the pitch drives the ratio. An offset must be measured to determine whether it contains a loop. [Margins and fits](../results/exp0/real_topology.csv)

## Method B: persistent homology of the cloud

The primary reference for this idea is the video [What is...persistent homology?](https://www.youtube.com/watch?v=w6Jx1vFp_Gk) (VisualMath).

### Union of balls and radius r
Put a ball of radius r around every point and let r grow from 0. Small r gives separate dots. As r grows, balls merge into pieces, pieces close into loops, and loops fill in. Persistent homology records these events.
- The explorer and the examples page draw the balls with the "balls of radius r" switch (each drawn as an icosahedron with its corners on the sphere).
- The README's animations of the strongest results show them in 3D and in slices (a ball at distance h from the slice cuts it in a disc of radius √(r² − h²)).

### Simplicial complex
Vertices, edges, triangles and tetrahedra glued along shared faces. It is a combinatorial stand-in for the union of balls that a computer can count holes in.

### Alpha complex
The simplicial complex used here, computed with [GUDHI](https://gudhi.inria.fr/python/latest/delaunay_complex_user.html).
- At every radius it is homotopy equivalent to the union of balls, so it has exactly the same holes ([Edelsbrunner 1995](https://doi.org/10.1007/BF02574053), Thm 3.2; the nerve theorem gives the same). It is a smaller complex than the Čech complex, but the two filtrations have the same persistence diagrams ([Bauer & Edelsbrunner 2017](https://doi.org/10.1090/tran/6991), Cor. 6.1, [arXiv](https://arxiv.org/abs/1312.1231)). Both results assume points in general position, which real activations satisfy generically; in degenerate inputs such as a regular polygon, ties only create zero-length bars, which are dropped. It uses only Delaunay simplices, so it stays small.
- An edge enters at half its length if no other point lies inside the circle (sphere, in 3D) that has the edge as diameter (a Gabriel edge); otherwise it enters together with the earliest triangle on it whose third corner lies inside that sphere ([GUDHI](https://gudhi.inria.fr/doc/latest/group__alpha__complex.html)).
- A triangle enters at the radius of its circumcircle if that circle's smallest sphere is empty; otherwise, by the same rule, together with a tetrahedron. In general a simplex enters at the radius of its smallest empty circumsphere.
- The examples page draws its edges as r grows.

### Rips complex
Adds a simplex whenever all its points are pairwise within distance 2r. It is cheaper in high dimensions but can create holes the union of balls does not have: 12 evenly spaced points on a circle get three 2-spheres at some scales ([Adamaszek & Adams 2017](https://doi.org/10.2140/pjm.2017.290.1), Thm 4.3; checked in `tests/test_tda.py`). It is only interleaved with the Čech complex ([de Silva & Ghrist 2007](https://doi.org/10.2140/agt.2007.7.339), Thm 2.5). Here it is used for the top-10-PC checks and for the hole coordinate θ_B.

### Filtration
The nested sequence of complexes as r grows. Every simplex has an entry radius, and nothing is ever removed.

### Homology H0 H1 H2
H0 = connected pieces, H1 = loops, H2 = voids, computed with coefficients mod 2. For complexes in ℝ³, H0 and H2 bars do not depend on that choice; H1 bars can, in rare cases such as a Möbius band ([Obayashi & Yoshiwaki 2023](https://doi.org/10.1007/s00454-023-00544-7), Cor. 1–2; Example 1 is the Möbius band; §8: 1 in 10,000 alpha filtrations of Poisson clouds in [0,1]³ with 1,000 points on average; `tests/test_tda.py`). In the explorer's persistence diagram, H1 loops are dots and H2 voids are triangles.

### Birth and death
A loop is **born** at the radius where it first closes and **dies** at the radius where it is filled in. A piece (H0) is born at 0 and dies when it merges with an older piece.

### Persistence diagram
One dot (birth, death) per loop or void. Dots on the diagonal live for no time; dots far above it persist over a wide range of scales. The examples page draws it on log axes, where the distance above the diagonal is log π.

### Representative loop
For a positive alpha H1 interval the drawing closes its birth edge by an earlier shortest edge path. The path is present at birth and can carry an older class through the paired death. The explorer identifies which chains bound when that death simplex enters. A certified chain is one of several possible representatives over F₂. [All certificates](../results/science/representatives.csv.gz)

### Representative void
One closed surface of triangles that encloses a given void (an H2 bar). The explorer draws it as a see-through shell in the void's own colour while the void is alive, so each triangle in the persistence diagram can be matched with a shell in the cloud.
- In ℝ³ a void is an empty region of space walled in by the complex (Alexander duality; Edelsbrunner & Harer 2010, *Computational Topology*, ch. V). The region is found just after the triangle that closes the void enters: start in the tetrahedron whose entry fills the void (both come from GUDHI's persistence pairs) and move to neighbouring tetrahedra through triangles that have not entered yet. The triangles where this stops are the shell.
- Every shell triangle is in the complex when the void is born, and the shell is filled in exactly when that tetrahedron enters, so it carries the void for its whole bar.
- **The void's empty middle** (the blue ball in the README's void figure): the centre of the sphere through that tetrahedron's 4 corners. No point lies inside that sphere (a Delaunay property), so no point is closer to the centre than the death radius d. At the birth radius b, a ball of radius d − b around the centre is therefore still uncovered, and the centre is the last place the growing balls reach.
- A void has many such shells; this one is for display, and the statistics never use it.

### Persistence ratio pi
π = death / birth ([Bobrowski & Skraba 2023](https://doi.org/10.1038/s41598-023-37842-2)).
- Because it is a ratio, it does not change if the cloud is scaled.
- Loops made by noise have π close to 1. Any loop of 3 points has π ≤ 2/√3, and a regular k-gon of points gives 1/sin(π/k) (our derivation, checked in `tests/test_tda.py` and the [worked example](worked_example.md)).
- 1/sin(π/k) is the value for k point-like concept centres, not a ceiling for a ring of k clusters: spread within the clusters lets neighbours connect earlier, so a ring of noisy clusters can have a larger π (`tests/test_tda.py::test_cluster_ring_can_exceed_point_polygon_ratio`).
- The largest π of pure noise grows slowly with the number of points, like (log N / log log N)^(1/k) for k-dimensional holes ([Bobrowski, Kahle & Skraba 2017](https://doi.org/10.1214/16-AAP1232), Thm 3.1, proven for a homogeneous Poisson process in the unit cube; densities bounded above and below on a compact support are only remarked).

### Top H1 pi
The largest π among a cloud's loops: its most persistent loop. This is the statistic of the loop test. In the README's example figure, the bars show it divided by the null's 95th percentile.

### Monte Carlo null
M = 999 random clouds that match the data's design. Each goes through the same top-3 PCA and alpha complex, and its largest π is recorded. The data's loop is compared with this distribution of maxima, which controls for the many loops every cloud has. This is adapted from [Gardner et al. 2022](https://doi.org/10.1038/s41586-021-04268-7), who pooled the bars of 1,000 shuffled datasets and used the longest lifetime (death − birth) as a threshold, which they call a heuristic; here the statistic is the scale-free ratio π, one maximum per null cloud, with a Monte Carlo p-value.
- **Cluster-centre null** (prompt-template designs): the concept centres are redrawn from a Gaussian with their own covariance, and every prompt keeps its offset from its concept centre.
- **Matched Gaussian** (one point per value): a Gaussian cloud with the data's full covariance.
- The rank is relative to the fitted design-specific reference. Fitting nuisance parameters can alter finite-sample size. [Nested calibration](../results/science/calibration.csv) · [Dufour](https://doi.org/10.1016/j.jeconom.2005.06.007)

### Null 95th percentile q95
The 95th percentile of the 999 null maxima. In the persistence diagrams it is the red line d = q95 · b: loops above it are significant at about the 5% level. The exact rule is the Monte Carlo p-value below (p < 0.05), which can differ from "above q95" by one null draw at the boundary.

### Monte Carlo p-value
p = (1 + number of null maxima ≥ the observed π) / (M + 1) ([Phipson & Smyth 2010](https://doi.org/10.2202/1544-6115.1585)). With M = 999 the smallest possible value is 0.001. "loop p (MC)" in the explorer is this p for the cloud's most persistent loop.

### Universal null
P and S use the proposed score ℓ = A log(log π) − γ − A mean(log(log π)) and exp(−exp ℓ), with a within-diagram Bonferroni threshold. This is an empirical score for the present benchmark. Weak universality fixes dimension, degree and complex type. The proposed left-Gumbel form fails in degree-one Čech counterexamples. [Original method](https://doi.org/10.1038/s41598-023-37842-2) · [Weak universality](https://arxiv.org/html/2406.05553v1) · [Counterexamples](https://arxiv.org/html/2610.08257v1) · [Observed calibration](../results/science/blobs.csv)

### Characteristic scale r_c
r_c = √(birth · death) of the most significant loop or void: the middle of its bar on a log scale, where that feature is most clearly alive. If there is none, r_c is half the b0 rule's cut length (the cut is an edge length, a diameter). Method B's Betti numbers (all three), Euler characteristic, genus and Betti label are read at r_c.

### Stability over subsamples
The share of 200 random 80% subsamples in which the cloud's most persistent loop still beats the null's 95th percentile.

### Connect radius (loop inside one cluster)
Half the smallest distance between points of two different concepts. Below this radius, balls of different concepts never touch. So a loop that dies at or below it is made of one concept's points: a small loop inside one cluster, not a ring of concepts (audit D8).

## Travel around the hole

### theta_A and theta_B (hole coordinates)
When the construction succeeds it assigns an angle to each point. The label sequence can have zero, one or several turns.
- **θ_A** is the point's position along the fitted shape (Method A).
- **θ_B** comes from persistent cohomology ([de Silva, Morozov & Vejdemo-Johansson 2011](https://doi.org/10.1007/s00454-011-9344-x), computed with [DREiMac](https://github.com/scikit-tda/DREiMac)):
  - the most persistent loop gives a **cocycle**, a cut across the ring;
  - least squares (harmonic smoothing) spreads that cut evenly into an angle.
- The preregistered setting (`standard_range=True`) refuses loops whose Rips death is less than twice their birth ("too short"). The relaxed setting (`standard_range=False`) was used only post hoc.

### Loop B
A closed curve through the cloud that follows θ_B: the mean of the points in each of 24 equal bins of θ_B, joined by a periodic cubic spline. It is drawn in red in the explorer, and it is the path planned for (postponed) steering experiments.

### Circular mean
The average direction of angles, arg Σ e^{iθ}. An ordinary average would put 359° and 1° at 180°; the circular mean gives 0°. Each concept's angle is the circular mean of its points' angles.

### Alignment R
R = max over s ∈ {+1, −1} of |mean_c e^{i(θ_c − s·φ_c)}|. It measures how well the concepts' angles θ_c match their semantic phases φ_c, allowing any starting point and either direction (s). R = 1 is a perfect match; R near 0 means no relation.

### Permutation p-value
How often R would be at least as large if the concepts' phases were shuffled. It is exact over all n! shuffles for 7 or fewer concepts; otherwise it uses 99,999 random shuffles.

### Winding number
How many times the concepts' cycle (Monday → … → Sunday → Monday) goes around the circle: the sum of the shortest signed steps between consecutive concepts' angles, divided by 2π. ±1 means exactly once (the sign is only the direction).

### Preregistered and post hoc
**Preregistered** analyses were fixed before any topology was computed ([preregistration](../reports/preregistration.md)). **Post hoc** analyses were added after seeing results; they are logged as deviations ([deviations](../reports/deviations.md)) and weigh less.

## Verdict words

### Loop
The cloud's most persistent loop has p < 0.05 against the design-matched Monte Carlo null. This alone is not evidence of a hole: the null also rejects many hole-free shapes such as curved sheets and caps (deviation D9).

### Ring
The earlier galleries used this shorthand for a projected loop and aligned labels. Neither measurement determines whether the underlying full-dimensional concept space is a closed continuous curve.

### Goes around once
Alignment p < 0.05 and winding number ±1 for the concept variable.

### Suggestive
A loop through the clusters that the concept goes around once only in a post hoc analysis (as for months).

## Statistics

### Holm and Benjamini-Hochberg
Corrections for testing many hypotheses. Holm controls the chance of any false positive among the primary tests. Benjamini–Hochberg controls the expected share of false positives among the exploratory tests (its adjusted values are called q), for independent tests or tests with positive regression dependence ([Benjamini & Yekutieli 2001](https://doi.org/10.1214/aos/1013699998)).
