# Exp2: persistent-homology invariants of the 44 real clouds (Method B)

Date: 2026-11-15. Code: `src/neurotopo/experiments/exp2_invariants.py`, `realdata.py`. Results: `results/exp2/`, with nulls cached in `results/nulls/`.

## Method

- **Alpha diagrams** (H0–H2, radius units) of each source-identical, RMS-normalised top-3 PCA cloud. The recomputed clouds match the source's stored points to better than 1e-3 of their scale.
- **Significance:** the maximum persistence ratio π = death/birth is compared with 999 draws of a design-matched null.
  - Cluster-centre null for prompt-template designs: weekdays, months, days_time, colours (concept = hue), and the random-init weekday and month controls.
  - Full-dimensional matched-covariance Gaussian for everything else.
  - Every null draw passes through the same top-3 PCA normalisation.
- **Descriptive extras:**
  - universal-null counts for alpha (A = ½) and Rips (A = 1);
  - b0 by the tuned single-linkage rule;
  - Betti numbers and χ at the characteristic scale r_c;
  - genus, reported only for closed surfaces;
  - stability: the fraction of 200 subsamples of 80% (source seeds) whose top π exceeds the full cloud's null threshold.

## Results

- **{{exp2.n_loop}} clouds have a significant loop and {{exp2.n_void}} a significant void.** The loops:
  - colours: π = {{exp2.colors.top_pi1:2}} vs {{exp2.colors.null_q95_pi1:2}}, p = {{exp2.colors.p_top_loop}}, stable in {{exp2.colors.loop_freq:2}} of subsamples;
  - grokked residues: {{exp2.grok.top_pi1:2}} vs {{exp2.grok.null_q95_pi1:2}}, p = {{exp2.grok.p_top_loop}}, stability {{exp2.grok.loop_freq:2}};
  - months: {{exp2.months.top_pi1:2}} vs {{exp2.months.null_q95_pi1:2}}, p = {{exp2.months.p_top_loop}}, stability {{exp2.months.loop_freq:2}};
  - month means: p = {{exp2.monthsmeans.p_top_loop}};
  - days with times: {{exp2.daystime.top_pi1:2}} vs {{exp2.daystime.null_q95_pi1:2}}, p = {{exp2.daystime.p_top_loop}}, stability {{exp2.daystime.loop_freq:2}};
  - the grokking model at initialisation (p = {{exp2.grokinit.p_top_loop}}, borderline);
  - the toy-model clouds of superposition (5–8 points).
- **Weekdays have no significant loop** (π = {{exp2.weekdays.top_pi1:2}} vs {{exp2.weekdays.null_q95_pi1:2}}, p = {{exp2.weekdays.p_top_loop}}).
- **No ordinal concept has a loop** ({{exp2.ordinal_loops}}/6), and neither do the 20 random-process controls ({{exp2.c1_loops}}/20; max π {{exp2.c1_pi_max:2}}).
- **GPT-2 W_pos:** fitted as a closed sphere (Method A void), but there is no significant void in the data (H2 π = {{exp2.wpos.top_pi2:2}}). The positions trace a spiral curve, not a surface.
- **Agreement between Method A and Method B (b1, b2):** {{exp2.agree:3}}.

<!-- BEGIN:exp2 -->
<!-- END:exp2 -->

![gallery](../docs/figures/fig_real_gallery.png)

## Interpretation

- Topology detects loops exactly where the concept is cyclic: hue, residues mod 113, months, and day-of-week in the days_time set. It detects none for ordinal concepts or random controls.
- **Weekdays are the exception.** The 7 tight prompt clusters do not form a loop more persistent than random arrangements of 7 clusters with the same spread. At 7 clusters the maximum possible ratio is 1/sin(π/7) ≈ 2.3, so the power is inherently limited.
- **Caveats:** two random-init or toy controls cross the 5% line, consistent with the nominal error rate over this many tests. The days_time loop is unstable under subsampling.

## Learnings

- The cluster-centre null matters. With a plain Gaussian null, any arrangement of tight clusters would look "loopy".
- Stability under subsampling separates robust loops (colours 1.0, months 0.9) from fragile ones (days_time 0.03).
