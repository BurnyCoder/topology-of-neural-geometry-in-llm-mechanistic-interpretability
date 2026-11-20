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
  - all three Betti numbers, χ and a Betti label at the characteristic scale r_c (b0 is read at r_c too since deviation D12; the label is not a homotopy class, because Betti numbers do not determine one);
  - genus, reported only for closed surfaces;
  - stability: the fraction of 200 subsamples of 80% (source seeds) whose top π exceeds the full cloud's null threshold.

## Results

- **{{exp2.n_loop}} clouds have a significant loop and {{exp2.n_void}} a significant void.** The loops:
  - colours: π = {{exp2.colors.top_pi1:2}} vs {{exp2.colors.null_q95_pi1:2}}, p = {{exp2.colors.p_top_loop}}, stable in {{exp2.colors.loop_freq:2}} of subsamples;
  - grokked residues: {{exp2.grok.top_pi1:2}} vs {{exp2.grok.null_q95_pi1:2}}, p = {{exp2.grok.p_top_loop}}, stability {{exp2.grok.loop_freq:2}};
  - months: {{exp2.months.top_pi1:2}} vs {{exp2.months.null_q95_pi1:2}}, p = {{exp2.months.p_top_loop}}, stability {{exp2.months.loop_freq:2}};
  - month means: p = {{exp2.monthsmeans.p_top_loop}};
  - days with times: {{exp2.daystime.top_pi1:2}} vs {{exp2.daystime.null_q95_pi1:2}}, p = {{exp2.daystime.p_top_loop}}, stability {{exp2.daystime.loop_freq:2}}; a small loop inside one day's cluster (bar [{{audit.loc.daystime.birth:3}}, {{audit.loc.daystime.death:3}}], clusters first touch at {{audit.loc.daystime.connect:3}}; audit D8);
  - the grokking model at initialisation (p = {{exp2.grokinit.p_top_loop}}, borderline);
  - the toy-model clouds of superposition (5–8 points).
- **Weekdays have no significant loop** (π = {{exp2.weekdays.top_pi1:2}} vs {{exp2.weekdays.null_q95_pi1:2}}, p = {{exp2.weekdays.p_top_loop}}). That most persistent bar is a small loop inside one day's cluster (it dies at {{audit.loc.weekdays.death:3}}; clusters first touch at {{audit.loc.weekdays.connect:3}}), and the 7 day centres alone have no loop (π = {{audit.loc.weekdays.means_pi:2}}).
- **No ordinal concept has a loop** ({{exp2.ordinal_loops}}/6), and neither do the 20 random-process controls ({{exp2.c1_loops}}/20; max π {{exp2.c1_pi_max:2}}). These open curves were never at risk: their top π ({{exp2.open.pi_min:2}}–{{exp2.open.pi_max:2}}) is far below the Gaussian null's 95th percentile ({{exp2.open.q95_min:2}}–{{exp2.open.q95_max:2}}), because a blob of the same spread has more loops than a curve.
- **GPT-2 W_pos:** fitted as a closed sphere (Method A void), but there is no significant void in the data (H2 π = {{exp2.wpos.top_pi2:2}}). The positions trace a spiral curve, not a surface.
- **Truth cities (exploratory prediction, preregistration section 6: b0 = 2, true vs false statements):** not supported. The tuned single-linkage rule gives b0 = {{exp2.truth.b0}}, and the alpha complex has b0 = {{exp2.truth.b0_rc}} pieces at the characteristic scale. Its Betti label is {{exp2.truth.betti_label}}.
- **Agreement between Method A and Method B (b1, b2):** {{exp2.agree:3}}.
- **Benjamini–Hochberg over the 44 loop tests (post hoc, D6):** {{exp2.n_loop_q05}} loops at q < 0.05: {{exp2.loops_q05}}.

<!-- BEGIN:exp2 -->
<!-- END:exp2 -->

![gallery](../docs/figures/fig_real_gallery.png)

![null distributions](../docs/figures/fig_null_tests.png)

Grey: Monte Carlo null distribution of the largest H1 persistence ratio (999 design-matched draws). Dashed: its 95th percentile. Solid: the observed largest ratio.

## Interpretation

- Topology detects loops through the concept clusters in three cyclic sets (hue, residues mod 113, months). The days_time loop lies inside one day's cluster. Topology detects no loop in weekdays, ordinal concepts or random-process controls, and a borderline one in the random-init grokking embedding.
- **The hue loop is in the stimuli.** The colour prompts' own RGB values have the loop too (π = {{audit.rgb.pi:2}} vs null {{audit.rgb.q95:2}}, p = {{audit.rgb.p}}; [exp7_audit.md](exp7_audit.md)). The model reads hex codes, so its loop is not trivial, but any continuous encoding of the stimulus colour would have it.
- **A loop is not traversal.** The days_time loop is not a ring of days at all. The residue loop is unstable under subsampling (stability {{exp2.grok.loop_freq:2}}; {{audit.stab.grok.matched:2}} against a size-matched threshold), most likely because its top PCA eigenvalues are nearly equal ({{audit.pca.grok.l3:3}} vs {{audit.pca.grok.l4:3}} for the 3rd and 4th), so subsamples rotate the top-3 view.
- **Weekdays are the exception.** The 7 day centres form no loop in the top-3 PCs, and the most persistent loop of the cloud lies inside one cluster. For 7 evenly spaced point-like centres the polygon's loop has π = 1/sin(π/7) ≈ 2.3 (spread within the clusters can raise it), and the power simulation shows that the loop test has limited power at 7 clusters, but here there is no polygon loop to detect.
- **A loop is not a hole (third audit, D9).** Both nulls are Gaussian, so a significant loop means "more persistent than a covariance-matched Gaussian". On synthetic clouds of known topology, the design-(b) null flags loops on {{audit3.mc.fpr:2}} of hole-free clouds (spheres and caps {{audit3.mc.fam.sphere_b0:2}}, paraboloids {{audit3.mc.fam.paraboloid_b0:2}}). Hole claims need independent evidence: the traversal, the localisation, and the concept centres alone ([exp8_audit3.md](exp8_audit3.md)).
- **Caveats:** two random-init or toy controls cross the 5% line, consistent with the nominal error rate over this many tests. The days_time loop is unstable under subsampling. For prompt-template designs, the maximum-π statistic does not say *where* a loop lives; the audit's localisation check (D8) is needed to tell a ring of concepts from a loop inside one cluster.

## Learnings

- The cluster-centre null matters. With a plain Gaussian null, any arrangement of tight clusters would look "loopy".
- Stability under subsampling separates robust loops (colours {{exp2.colors.loop_freq:2}}, months {{exp2.months.loop_freq:2}}) from fragile ones (days_time {{exp2.daystime.loop_freq:2}}). The threshold should be computed at the subsample size, and near-equal PCA eigenvalues make any top-3 view unstable (audit, D8).
- A significant maximum-π loop in a clustered design must be localised: check whether it dies before the clusters touch.
