# Exp3: do semantically cyclic concepts travel around a hole? (H1–H4; post hoc D5)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp3_cyclic.py`, `exp3_posthoc.py`, `alignment.py`. Results: `results/exp3/`. Inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115)).

## Preregistered tests

- **H1-A** (Method A): the fitted shape has a resolvable hole, and θ_A alignment passes (Holm) with winding ±1.
- **H1-B** (Method B):
  - (a) a significant alpha loop;
  - (b) θ_B (DREiMac, `standard_range=True`) alignment, Holm-corrected over 6 tests;
  - (c) |winding| = 1;
  - (d) the same in the top-10 PCs.
- **H2:** the conjunctions fail on the 6 ordinal sets (7 and 12 bins), the 3 random-init controls and the 20 random-process controls.
- **H3:** days_time, day phase.
- **H4:** balanced accuracy of three criteria for separating cyclic from ordinal sets.

## Results

- **H1-A: {{exp3.H1A}}/3.** All three primary fits are helices.
- **H1-B: {{exp3.H1B}}/3.**
  - Weekdays: (a) {{exp3.weekdays.B.a_loop}}.
  - Months: (a) {{exp3.months.B.a_loop}}, but (b)–(d) {{exp3.months.B.b_align}}. DREiMac built no coordinate, because the Rips class's death is less than twice its birth.
  - Residues: (a) {{exp3.grok.B.a_loop}}, (b) {{exp3.grok.B.b_align}} (Holm p = {{exp3.grok.B.holm}}), (c) {{exp3.grok.B.c_wind1}}, (d) {{exp3.grok.B.d_top10}}.
- **H2:** Method A {{exp3.H2.A.falsified}}, Method B {{exp3.H2.B.falsified}}. Ordinal sets passing: {{exp3.H2.B.ordinal}}/6. Init controls: {{exp3.H2.B.init}}/3. Random-process controls: {{exp3.H2.B.c1}}/20.
- **H3:** Method A {{exp3.H3.A}}, Method B {{exp3.H3.B}}.
- **H4:** balanced accuracy {{exp3.H4.hole_only_A:2}} (hole only, Method A), {{exp3.H4.conj_A:2}} (conjunction A), {{exp3.H4.conj_B:2}} (conjunction B). No criterion identified any cyclic set under the strict conjunctions.
- **Exploratory, colours:** a loop with hue alignment R = {{exp3.colors.thetaB.R:3}}, winding {{exp3.colors.thetaB.w}}.

## Post hoc (deviation D5): θ_B with `standard_range=False`

This changes no verdict.
- **Months:** 3D R = {{exp3ph.months.3d.R:2}} (p = {{exp3ph.months.3d.p}}), winding {{exp3ph.months.3d.w}}; top-10 R = {{exp3ph.months.top10.R:2}}, winding {{exp3ph.months.top10.w}}.
- **Residues:** 3D R = {{exp3ph.grok.3d.R:2}}, winding {{exp3ph.grok.3d.w}}; top-10 R = {{exp3ph.grok.top10.R:2}}, winding {{exp3ph.grok.top10.w}}.
- **Colours:** 3D R = {{exp3ph.colors.3d.R:2}}, winding {{exp3ph.colors.3d.w}}; top-10 R = {{exp3ph.colors.top10.R:2}}, winding {{exp3ph.colors.top10.w}}.
- **Weekdays:** 3D R = {{exp3ph.weekdays.3d.R:2}}, winding {{exp3ph.weekdays.3d.w}}.
- **Days with times (day):** 3D R = {{exp3ph.daystime.3d.R:2}}, winding {{exp3ph.daystime.3d.w}}. Its Rips class {{audit.ph.daystime.3d.bar}} does not overlap the significant alpha bar (overlap: {{audit.ph.daystime.3d.overlap}}; audit D8), so this coordinate does not describe the significant loop, which lies inside one day's cluster.
- **Overlap of the relaxed-range class with the significant alpha bar (audit D8):** months {{audit.ph.months.3d.overlap}}, residues {{audit.ph.grok.3d.overlap}}, colours {{audit.ph.colors.3d.overlap}}, weekdays {{audit.ph.weekdays.3d.overlap}}, days_time {{audit.ph.daystime.3d.overlap}}.
- **Month means (12 points):** 3D R = {{exp3ph.monthsmeans.3d.R:2}}, winding {{exp3ph.monthsmeans.3d.w}}; top-10 winding {{exp3ph.monthsmeans.top10.w}}.
- **Non-cyclic records with |winding| = 1** (ordinal sets and random-process controls, 3D and top-10): {{exp3ph.noncyclic_wind1}}.

<!-- BEGIN:exp3 -->
<!-- END:exp3 -->

![travel around the hole](../docs/figures/fig_traversal.png)

Each dot is one concept, placed at the circular mean of its points' hole angle and coloured by its position in the semantic cycle. Chords join consecutive concepts. Going round once in order gives a single non-crossing polygon (winding ±1).

## Interpretation

- **The strict preregistered answer is negative.** No primary cyclic set passes all conditions.
  - The residues come closest, failing only the top-10-PC check.
  - Months fail at the coordinate-construction step, not at the alignment.
  - Weekdays fail at the loop step: the 7 day centres form no loop, and the cloud's most persistent loop lies inside one day's cluster (audit D8).
- **Specificity holds, but it is weakly informative.**
  - No ordinal or control set passes any conjunction.
  - Sensitivity is zero, though: H4 balanced accuracy is 0.5 for every criterion.
  - The ordinal and random-process controls are open curves, whose loop statistics never approach the null threshold, so they barely exercise the test. The random-init networks are the informative calibration (1 of 3 below 0.05; with 3 controls this says little, since at least one of 3 falls below 0.05 with probability 0.14 under the null).
- **Post hoc,** the semantic order goes around the loop once in 3D for colours, residues and months. Days_time has no ring of days to go around. Only colours keep a winding loop in the top-10 PCs, so in 10 dimensions winding separates 1 of 5 cyclic sets from the ordinal sets, not the cyclic concepts as a group.
- **The colour result is confounded by the input.** The colour prompts' RGB values already have the hue loop, and hue winds once around it (audit D8). The colour traversal therefore shows that the model preserves the input's hue circle.
- **The alignment R and its permutation p measure ordering, not looping.** For example, nearly constant coordinates of random-process controls give small p with tiny R. Only winding ±1 carries the cyclic claim. The cyclic-order check was fixed to require a single winding (D6).
- **DREiMac class vs alpha bar overlap** (preregistration §4.6): colours {{exp3.colors.overlap}}, residues {{exp3.grok.overlap}}.

## Learnings

- **DREiMac's `standard_range` matters for clustered designs.** A loop of 12 tight clusters can be significant yet have a Rips death/birth ratio below 2. A preregistration should state what happens in that case; here it counted as a failure (D3).
- **The top-10-PC check is demanding.** Grokked embeddings carry several Fourier frequencies, so in 10 dimensions the single top-3 circle is no longer the dominant loop.
