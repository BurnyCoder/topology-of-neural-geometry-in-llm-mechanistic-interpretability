# Summary of all experiments

Date: 2026-11-15. Author: Libor "Burny" Burian. Every number below is generated from `results/` by `run.py report`.

## The question in plain words

Language models seem to store some concepts on loops: days of the week, months, colours on a colour wheel, numbers modulo 113 in a model trained on modular arithmetic. If a concept really lives on a loop, there is a **hole** in the middle that you can walk around. Walking around it should step through the concept in order (Monday, Tuesday, …, Sunday, back to Monday). That would make "steering around the hole" a meaningful way to control the model.

We checked, without running any model, whether the activation clouds really have such holes, and whether the concepts go around them in order.

## Experiments overview

| Exp | What | Data | Method | Main result |
|---|---|---|---|---|
| 0 | Exact topology of the fitted shapes | 44 real fits, 40,560 synthetic ground-truth shapes | closed-form Betti numbers, margin ratio, point coordinates on the fit | cyclic sets are fitted as helices (no hole); whether they are open or closed is unresolvable (ρ_A ≈ 0.11); concepts sit around the helix axis in order, but so do the indices of 8 of 8 random-process helix controls |
| coords | Where labelled points sit on the fit | 44 real fits | intrinsic coordinates; Spearman, circular alignment, NMI | months lie on a closed saddle loop (2nd harmonic R² 0.83, post hoc); ordinal concepts lie along open curves |
| power | Tuning and power | validation stream; simulated rings, arcs and random sets | Monte Carlo | preregistered simulation misspecified (rings trivially detected, D6). Corrected simulation (post hoc): the loop test detects weekday-like rings in 0.15, month-like in 0.25, residue-like in 1.00 of replicates; the full conjunction passes cluster rings in ≤ 0.05 |
| 1 | Are the persistent-homology estimators right? | 39,000 synthetic clouds, exact topology | alpha and Rips persistence, universal and Monte Carlo nulls, baselines | preregistered estimator 0.62 vs fixed threshold 0.71 vs family label 0.81; on clouds far from a topology change (ρ_A ≥ 4, post hoc, no tori) P 0.75 vs family label 0.82 (the label is in-distribution); persistence beats the label for open/closed arcs and caps/spheres; outliers raise P's false-positive rate to 0.065 (D7), below the DTM threshold of 0.10 |
| 2 | Holes in the real clouds | 44 real clouds | alpha persistence + design-matched null (999 draws) | loops through the concept clusters in colours, residues and months; in days_time only a small loop inside one day's cluster (unstable); borderline in the random-init grokking embedding; none in weekdays, ordinal concepts or random-process controls (open curves, never near the threshold); after BH over 44 tests: C3_tms_dense, R2_grokking_WE, R3_tms_n8, R5b_llama_months, R5b_llama_months_means, R7_llama_colors |
| 3 | Do cyclic concepts go around the hole? | cyclic, ordinal and control sets | DREiMac circular coordinate, permutation tests, winding | preregistered H1-A 0/3, H1-B 0/3, H4 balanced accuracy 0.50; specificity not falsified but weakly informative; post hoc, months, residues and colours wind once in 3D, days_time does not |
| 4 | Topological similarity | 44 clouds + templates | bottleneck distance on significant bars | uninformative (dominated by absolute scale); MDS map and dendrogram in `fig_exp4.png` |
| 5 | Robustness | key sets | top-k PCs, cosine distance, offset removal, seeds | top-10-PC loop test with matched null (post hoc): significant for R5c_llama_days_time, R4_llama_counting, R6_llama_years, R8a_llama_temperature, R8b_llama_age, R7_llama_colors. Loops in 10D are not specific; only colours' values wind around theirs. Months robust to offsets and seeds |
| 6 | Steering around the holes | – | designed; simulated and LLM steering | **postponed by the author** |
| 7 | Second audit (post hoc, D8) | stored activations, colour prompts | colour RGB baseline, loop localisation, closure ratio, PCA gaps, size-matched stability, power CIs | the colour prompts' RGB values already have the hue loop (π 8.01, p = 0.001); the weekday and days_time loops lie inside one cluster; grokking's top PCs are nearly degenerate (5 Fourier frequencies); no verdict changes |
| 8 | Third audit (post hoc, D9) | stored results, synthetic test set, simulated nulls | loop sensitivity and false-loop rate per estimator; cluster-centre null on hole-free centres; centre loops in other projections | the loop test is not hole-specific: its Gaussian null flags 0.17 of hole-free synthetic clouds (spheres and caps 0.73); the cluster-centre null is undetermined at the real variance structure. Ring claims rest on the traversal (colours, residues); months downgraded to "suggestive"; no verdict changes |
| loops | Every loop, scored (post hoc, D11) | 10729 loops of 44 clouds | representative cycles; each loop's p against the cloud's Exp2 null; concept winding along the cycle; rules: significant, large, goes around once | 9 interesting loops. Months, month centres, grokked residues and colours: the concepts go around the significant loop once. The toy models' loops are polytope 4-cycles, days_time's is inside one cluster, and grokking at init is chance-level. The residues' second loop shows that winding on short cycles is not specific to one Fourier frequency |
| voids | Every void, scored (post hoc, D10) | 4759 voids of 38 clouds | representative shells and centres; each void's p against the cloud's Exp2 null; rules: significant, large, shape and meaning | 10 interesting voids. Only the toy models' voids are real by every criterion (significant, the largest, spanning the cloud, every feature a corner). Weekday and month centres and the colours hue ring wall in voids that are not significant, and a random curve has one of the largest voids |

## Datasets (from the source project)

| Dataset | Model / layer | Concept | Fitted family | Hole (Method B)? | Concept goes around? |
|---|---|---|---|---|---|
| weekdays | Llama-3.1-8B, layer 5, day token | day (cyclic) | helix | no (p = 0.094; the day centres form no loop) | around the fit's axis yes, but not specific (random-process controls also wind) |
| months | Llama-3.1-8B, layer 5, month token | month (cyclic) | helix | loop yes (p = 0.002); ring suggestive | yes in 3D, post hoc only; not in the top-10 PCs |
| residues | 1-layer transformer, W_E (weights) | a mod 113 (cyclic) | helix | yes (p = 0.001) | yes in 3D, not in the top-10 PCs |
| days with times | Llama-3.1-8B, layer 19, last token | day, time (cyclic) | ringing | only a small loop inside one day's cluster, unstable (p = 0.013) | no ring of days; days ordered linearly along the fitted curve |
| colours | Llama-3.1-8B, layer 19, last token | hue (cyclic) | cone | yes (p = 0.001), but the prompts' RGB values have it too | yes, also in the top-10 PCs |
| years, temperature, age | Llama-3.1-8B, layer 19 | ordinal | cone, ringing, clusters | no (open curves, never near the threshold) | no (ordered along a curve) |
| GPT-2 positions | GPT-2 W_pos (weights) | ordinal | sphere | no (no void either) | spiral, ordered pole to pole |
| counting | Llama-3.1-8B / Pythia, characters since newline | ordinal | ringing | no | ordered along the curve |
| 20 random walks / Gaussian processes | synthetic, ℝ⁷⁶⁸ | index (ordinal) | ringing / helix | no (0/20) | no |
| random-init controls | untrained Llama / grokking init | same prompts | clusters / polytope / blob | grokking init borderline (p = 0.046) | no |

## Glossary

- **Point cloud / top-3 PCA:** each prompt's activation is a point in a space with thousands of dimensions. We keep the 3 directions of largest variance.
- **Topology:** the properties of a shape that survive bending without tearing, such as the number of pieces, loops and enclosed voids.
- **Betti numbers (b0, b1, b2):** the counts of connected pieces, of independent loops (holes you can walk around), and of enclosed voids. Circle (1,1,0); sphere (1,0,1); torus, the doughnut surface, (1,2,1).
- **Euler characteristic χ** = b0 − b1 + b2. **Genus:** the number of handles of a closed surface, b1/2 when b2 = 1.
- **Persistent homology:** grow balls around every point and record when loops appear (birth) and fill in (death). Long-lived loops are real; short ones are noise.
- **Persistence ratio π** = death / birth. It is scale-free, so it can be compared across clouds.
- **Null model:** random Gaussian clouds that share the data's size and spread. A loop counts only if it outlives 95% of the loops found in 999 such random clouds. That rules out "a Gaussian blob", not every hole-free shape: curved sheets, caps and helices also often pass, and so do nearly closed arcs of cluster centres (third audit, D9).
- **Alpha complex / Rips complex:** two ways of turning points into a shape. Alpha is exact in 3D; Rips works in any dimension but adds spurious features.
- **Circular coordinate (θ):** an angle assigned to each point, going once around the hole. It comes from the fitted shape (θ_A) or from persistent cohomology (θ_B, DREiMac).
- **Alignment R:** how well the concepts' angles match their semantic order. R = 1 is perfect. **Winding:** how many times the semantic cycle goes around the hole; 1 means exactly once.
- **Margin ratio ρ_A:** how far the fitted shape is from changing its topology, relative to the noise. Below 1, the data cannot tell, for example, a nearly closed helix from a circle.
- **Steering:** editing an activation inside the model to change its output. **Manifold steering:** moving along a curved path instead of a straight line.

## In plain words: what was found

- **Colours** have a robust hole that hue goes around once, but the colour prompts' own RGB values already have that hole (the prompts avoid greys), so this shows that the model keeps its input's hue circle, not that it builds one.
- **Residues mod 113** have a hole the residues go around once. The top-3 view of it is unstable, because the embeddings spread their variance almost evenly over 5 Fourier frequencies, and it fails the preregistered higher-dimension check.
- **Months** have a loop through the 12 month clusters. Evenly spread hole-free arrangements did not reach its strength in simulation, but whether it is a closed ring or a nearly closed arc cannot be decided. The months go around it only in a post hoc analysis, and only in the top-3 PCs.
- **Days with times** have no ring of days: the only significant loop is small, lies inside one day's cluster, and is unstable.
- **Weekdays** are ordered around a circle on the fitted helix, but so are the indices of random smooth processes. In the top-3 PCs the 7 day centres form no loop at all; the test is also weak for 7 clusters, so a ring in other dimensions is not ruled out.
- **Ordinal concepts** (years, temperatures, ages, positions, counts) and **random controls** have no holes; they lie along open curves, which this null never flags. Because the strict tests never fired for any cyclic set either, this is weak evidence of specificity.
- **The shape fitter's "helices"** cannot be told apart from closed loops at this noise level. Months come closest to closing.
- **The topology instrument** is conservative. It is good at telling open from closed curves and caps from spheres, and weak for tori and thin loops. The loop test used on the real data is the opposite: it finds most true holes, but it also flags many hole-free shapes. So on its own, a loop is not proof of a hole.
- **Not yet tested:** whether steering *around* these loops changes the model's answers in order. That needs model runs, which are postponed.

## Reports

- [exp0_analytic.md](exp0_analytic.md)
- [coords_check.md](coords_check.md)
- [exp1_synthetic.md](exp1_synthetic.md)
- [exp2_invariants.md](exp2_invariants.md)
- [exp3_cyclic.md](exp3_cyclic.md)
- [exp4_exp5.md](exp4_exp5.md)
- [exp6_steering.md](exp6_steering.md)
- [exp7_audit.md](exp7_audit.md)
- [exp8_audit3.md](exp8_audit3.md)
- [loops.md](loops.md)
- [voids.md](voids.md)
- [findings_per_dataset.md](findings_per_dataset.md)
- [preregistration.md](preregistration.md)
- [deviations.md](deviations.md)
- [plan.md](plan.md)
- [literature-review.md](literature-review.md)
- [state-of-the-art-review.md](state-of-the-art-review.md)
