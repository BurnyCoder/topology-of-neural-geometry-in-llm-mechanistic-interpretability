# Summary of all experiments

Date: 2026-11-15. Author: Libor "Burny" Burian. Every number below is generated from `results/` by `run.py report`.

## The question in plain words

Language models seem to store some concepts on loops: days of the week, months, colours on a colour wheel, numbers modulo 113 in a model trained on modular arithmetic. If a concept really lives on a loop, there is a **hole** in the middle that you can walk around. Walking around it should step through the concept in order (Monday, Tuesday, …, Sunday, back to Monday). That would make "steering around the hole" a meaningful way to control the model.

We checked, without running any model, whether the activation clouds really have such holes, and whether the concepts go around them in order.

## Experiments overview

| Exp | What | Data | Method | Main result |
|---|---|---|---|---|
| 0 | Exact topology of the fitted shapes | 44 real fits, 40,560 synthetic ground-truth shapes | closed-form Betti numbers, margin ratio, point coordinates on the fit | cyclic sets are fitted as helices (no hole); whether they are open or closed is unresolvable (ρ_A ≈ {{exp0.weekdays.rho:2}}); concepts sit around the helix axis in order, but so do the indices of {{exp0.gp_wind1}} of {{exp0.gp_helix_n}} random-process helix controls |
| coords | Where labelled points sit on the fit | 44 real fits | intrinsic coordinates; Spearman, circular alignment, NMI | months lie on a closed saddle loop (2nd harmonic R² {{coords.months.harmonic.h2:2}}, post hoc); ordinal concepts lie along open curves |
| power | Tuning and power | validation stream; simulated rings, arcs and random sets | Monte Carlo | preregistered simulation misspecified (rings trivially detected, D6). Corrected simulation (post hoc): the loop test detects weekday-like rings in {{power2.weekdays.loop:2}}, month-like in {{power2.months.loop:2}}, residue-like in {{power2.grok.loop:2}} of replicates; the full conjunction passes cluster rings in ≤ {{power2.months.ring_all_max:2}} |
| 1 | Are the persistent-homology estimators right? | 39,000 synthetic clouds, exact topology | alpha and Rips persistence, universal and Monte Carlo nulls, baselines | preregistered estimator {{exp1.P.acc:2}} vs fixed threshold {{exp1.Ba.acc:2}} vs family label {{exp1.Bb.acc:2}}; on well-resolved clouds P {{exp1.well.P.acc:2}} vs family label {{exp1.well.Bb.acc:2}}; persistence beats the label for open/closed arcs and caps/spheres |
| 2 | Holes in the real clouds | 44 real clouds | alpha persistence + design-matched null (999 draws) | loops in colours, residues, months, days_time (unstable) and, borderline, the random-init grokking embedding; none in weekdays, ordinal concepts or random-process controls; after BH over 44 tests: {{exp2.loops_q05}} |
| 3 | Do cyclic concepts go around the hole? | cyclic, ordinal and control sets | DREiMac circular coordinate, permutation tests, winding | preregistered H1-A {{exp3.H1A}}/3, H1-B {{exp3.H1B}}/3, H4 balanced accuracy {{exp3.H4.conj_B:2}}; specificity {{exp3.H2.B.falsified}} but weakly informative; post hoc, months, residues and colours wind once in 3D, days_time does not |
| 4 | Topological similarity | 44 clouds + templates | bottleneck distance on significant bars | uninformative (dominated by absolute scale) |
| 5 | Robustness | key sets | top-k PCs, cosine distance, offset removal, seeds | top-10-PC loop test with matched null (post hoc): significant for {{exp5.top10.sig_ids}}. Loops in 10D are not specific; only colours' values wind around theirs. Months robust to offsets and seeds |
| 6 | Steering around the holes | – | designed; simulated and LLM steering | **postponed by the author** |

## Datasets (from the source project)

| Dataset | Model / layer | Concept | Fitted family | Hole (Method B)? | Concept goes around? |
|---|---|---|---|---|---|
| weekdays | Llama-3.1-8B, layer 5, day token | day (cyclic) | {{exp0.weekdays.family}} | no (p = {{exp2.weekdays.p_top_loop}}) | around the fit's axis yes, but not specific (random-process controls also wind); no detected hole (low power) |
| months | Llama-3.1-8B, layer 5, month token | month (cyclic) | {{exp0.months.family}} | yes (p = {{exp2.months.p_top_loop}}) | yes in 3D, post hoc only; not in the top-10 PCs |
| residues | 1-layer transformer, W_E (weights) | a mod 113 (cyclic) | {{exp0.grok.family}} | yes (p = {{exp2.grok.p_top_loop}}) | yes in 3D, not in the top-10 PCs |
| days with times | Llama-3.1-8B, layer 19, last token | day, time (cyclic) | {{exp0.daystime.family}} | yes, unstable (p = {{exp2.daystime.p_top_loop}}) | no: the day does not go around the loop; days ordered linearly along the fitted curve |
| colours | Llama-3.1-8B, layer 19, last token | hue (cyclic) | {{exp0.colors.family}} | yes (p = {{exp2.colors.p_top_loop}}) | yes, also in the top-10 PCs |
| years, temperature, age | Llama-3.1-8B, layer 19 | ordinal | {{exp0.years.family}}, {{exp0.temperature.family}}, {{exp0.age.family}} | no | no (ordered along a curve) |
| GPT-2 positions | GPT-2 W_pos (weights) | ordinal | {{exp0.wpos.family}} | no (no void either) | spiral, ordered pole to pole |
| counting | Llama-3.1-8B / Pythia, characters since newline | ordinal | {{exp0.counting.family}} | no | ordered along the curve |
| 20 random walks / Gaussian processes | synthetic, ℝ⁷⁶⁸ | index (ordinal) | ringing / helix | no ({{exp2.c1_loops}}/20) | no |
| random-init controls | untrained Llama / grokking init | same prompts | clusters / polytope / blob | grokking init borderline (p = {{exp2.grokinit.p_top_loop}}) | no |

## Glossary

- **Point cloud / top-3 PCA:** each prompt's activation is a point in a space with thousands of dimensions. We keep the 3 directions of largest variance.
- **Topology:** the properties of a shape that survive bending without tearing, such as the number of pieces, loops and enclosed voids.
- **Betti numbers (b0, b1, b2):** the counts of connected pieces, of independent loops (holes you can walk around), and of enclosed voids. Circle (1,1,0); sphere (1,0,1); torus, the doughnut surface, (1,2,1).
- **Euler characteristic χ** = b0 − b1 + b2. **Genus:** the number of handles of a closed surface, b1/2 when b2 = 1.
- **Persistent homology:** grow balls around every point and record when loops appear (birth) and fill in (death). Long-lived loops are real; short ones are noise.
- **Persistence ratio π** = death / birth. It is scale-free, so it can be compared across clouds.
- **Null model:** random clouds that share the data's size and spread but have no structure. A loop counts only if it outlives 95% of the loops found in 999 such random clouds.
- **Alpha complex / Rips complex:** two ways of turning points into a shape. Alpha is exact in 3D; Rips works in any dimension but adds spurious features.
- **Circular coordinate (θ):** an angle assigned to each point, going once around the hole. It comes from the fitted shape (θ_A) or from persistent cohomology (θ_B, DREiMac).
- **Alignment R:** how well the concepts' angles match their semantic order. R = 1 is perfect. **Winding:** how many times the semantic cycle goes around the hole; 1 means exactly once.
- **Margin ratio ρ_A:** how far the fitted shape is from changing its topology, relative to the noise. Below 1, the data cannot tell, for example, a nearly closed helix from a circle.
- **Steering:** editing an activation inside the model to change its output. **Manifold steering:** moving along a curved path instead of a straight line.

## In plain words: what was found

- **Colours** have a robust hole that hue goes around once. **Residues mod 113** have a hole the residues go around once, but it is fragile under subsampling and fails the preregistered higher-dimension check.
- **Months** have a hole. The months go around it only in a post hoc analysis, and only in the top-3 PCs.
- **Days with times** have an unstable loop that the day does not go around.
- **Weekdays** are ordered around a circle on the fitted helix, but so are the indices of random smooth processes. A hole is not detectable with 7 prompt clusters; the corrected power simulation suggests the test is weak there.
- **Ordinal concepts** (years, temperatures, ages, positions, counts) and **random controls** have no holes; they lie along open curves. Because the strict tests never fired for any cyclic set either, this is weak evidence of specificity.
- **The shape fitter's "helices"** cannot be told apart from closed loops at this noise level. Months come closest to closing.
- **The topology instrument** is conservative. It is good at telling open from closed curves and caps from spheres, and weak for tori and thin loops.
- **Not yet tested:** whether steering *around* these loops changes the model's answers in order. That needs model runs, which are postponed.

## Reports

- [exp0_analytic.md](exp0_analytic.md)
- [coords_check.md](coords_check.md)
- [exp1_synthetic.md](exp1_synthetic.md)
- [exp2_invariants.md](exp2_invariants.md)
- [exp3_cyclic.md](exp3_cyclic.md)
- [exp4_exp5.md](exp4_exp5.md)
- [exp6_steering.md](exp6_steering.md)
- [preregistration.md](preregistration.md)
- [deviations.md](deviations.md)
- [plan.md](plan.md)
- [literature-review.md](literature-review.md)
- [state-of-the-art-review.md](state-of-the-art-review.md)
