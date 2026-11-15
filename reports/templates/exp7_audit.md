# Exp7: second independent audit (post hoc, deviation D8)

Date: 2026-11-15. Author: Libor "Burny" Burian. Every number is generated from `results/exp7_audit/` and earlier results by `run.py report`. Code: `src/neurotopo/experiments/exp7_audit.py` (`run.py audit`). No model inference and no training: everything uses stored activations, stored results, and the colour prompts' RGB values recomputed from the source's prompt builder.

## Why this audit

A second independent audit ignored earlier audits. It re-read the code, the preregistration, the deviations and the results, and recomputed key quantities from stored data.

**What it confirmed.**
- No preregistered verdict is wrong. H1-A {{exp3.H1A}}/3 and H1-B {{exp3.H1B}}/3 follow from the rules, as do H3 ({{exp3.H3.B}}), H4 ({{exp3.H4.conj_B:2}}) and H2 ({{exp3.H2.B.falsified}}).
- The design-matched nulls are implemented correctly:
  - Gaussian null: rows i.i.d. with the sample covariance, drawn through the Gram matrix;
  - cluster-centre null: concept means redrawn with their covariance, residuals kept;
  - every draw goes through the same top-k projection and normalisation as the data.
- The permutation tests, Holm and Benjamini–Hochberg are correct, and there is no leakage.

**What it found:**
1. A confounder in the strongest positive result (colours).
2. Two results described as "rings" that are loops inside a single concept's cluster (weekdays, days with times).
3. Overclaims about the months, the controls, the residues' "fragility" and the 10-dimensional winding.
4. A misdescribed power argument and a misdescribed Exp1 subset.
5. One preregistered descriptive statistic that was never reported (the closure ratio).

Each check below is post hoc and labelled as such. **No preregistered verdict changes.**

## 1. The colour loop is already in the stimuli

The source builds the 900 colour prompts from an HLS grid of 36 hues × saturation {0.4, …, 1.0} × lightness {0.25, …, 0.75} (`external/shape-fitting/src/neurogeom/realdata/llm_sets.py`, `bhalla_prompts`). Saturation ≥ 0.4 excludes the grey axis, so in RGB space the stimulus set surrounds a hole.

We ran Method B on the prompts' own RGB values (the hex-code digits), with concept = hue and the same cluster-centre null as for the activations ({{audit.rgb.m}} draws).

| cloud | top H1 π | null q95 | p | subsample stability |
|---|---|---|---|---|
| Llama-3.1-8B colour activations (Exp2) | {{exp2.colors.top_pi1:2}} | {{exp2.colors.null_q95_pi1:2}} | {{exp2.colors.p_top_loop}} | {{exp2.colors.loop_freq:2}} |
| the prompts' RGB values | {{audit.rgb.pi:2}} | {{audit.rgb.q95:2}} | {{audit.rgb.p}} | {{audit.rgb.freq:2}} |

- The 36 hue means of the RGB values have a loop of π = {{audit.rgb.means_pi:2}}.
- Their angles in PC1–PC2 wind once (winding {{audit.rgb.means_w}}, R = {{audit.rgb.means_R:2}}).
- θ_B on the RGB cloud:
  - preregistered setting: {{audit.rgb.thetaB.prereg}};
  - relaxed setting: {{audit.rgb.thetaB.relaxed}}. DREiMac's most persistent Rips class on this regular grid is not the hue loop, so the hue winding is read from the hue means instead.

**Reading.** The hue loop and its order are properties of the stimulus set. The activation loop is less persistent than the input's ({{audit.llama_over_rgb:2}} of its π). The colour result therefore shows that layer 19 of Llama-3.1-8B *preserves* the hue circle of its input. It is not evidence that the model *constructs* a cyclic hue code.

Separating the two needs model inference, which is postponed:
- a random-init Llama on the same prompts;
- colour prompts by name instead of hex code.

## 2. Where the most persistent loop lives

For prompt-template designs the loop statistic is the largest persistence ratio over **all** H1 bars, so a small loop inside one concept's cluster can win it. The check is exact:
- Below half the smallest distance between points of different concepts, the balls of different concepts are disjoint.
- So a bar that dies at or below that radius is carried by one concept's points alone.

<!-- BEGIN:audit -->
<!-- END:audit -->

- **Weekdays.** The most persistent bar [{{audit.loc.weekdays.birth:3}}, {{audit.loc.weekdays.death:3}}] dies before any two day clusters touch ({{audit.loc.weekdays.connect:3}}). It is a loop inside one cluster.
  - The 7 day centres alone have π = {{audit.loc.weekdays.means_pi:2}}; a regular 7-gon has 1/sin(π/7) ≈ 2.3.
  - The Sunday → Monday step is {{audit.loc.weekdays.lastfirst:2}}× the median step.
  - In the top-3 PCs there is no ring of days at all. The earlier text, "no stronger than the rings of randomly placed clusters", described this within-cluster loop.
- **Days with times.** The significant bar [{{audit.loc.daystime.birth:3}}, {{audit.loc.daystime.death:3}}] (p = {{exp2.daystime.p_top_loop}}, BH q = {{exp2.daystime.q_loop}}, stability {{exp2.daystime.loop_freq:2}}) dies before clusters touch ({{audit.loc.daystime.connect:3}}). It is a loop inside one day's cluster, not a ring.
  - The 7 day centres have π = {{audit.loc.daystime.means_pi:2}}.
  - The post hoc θ_B for this set (D5) is built on a different, non-significant Rips class {{audit.ph.daystime.3d.bar}}, which does not overlap the significant bar (overlap: {{audit.ph.daystime.3d.overlap}}). So "the day does not go around the loop" did not test the significant loop.
- **Months.** The bar [{{audit.loc.months.birth:2}}, {{audit.loc.months.death:2}}] runs through the clusters (they first touch at {{audit.loc.months.connect:2}}). The 12 month centres alone show the same loop (π = {{audit.loc.months.means_pi:2}}).
  - The December → January step is the largest, {{audit.loc.months.lastfirst:2}}× the median step.
  - In the power simulation at the months' top-3 variance, a ring passes the loop test in {{audit.power.k12.ring.interp_loop:2}} and a 300° arc in {{audit.power.k12.arc300.interp_loop:2}} of replicates (interpolated). So the loop test cannot call this a closed ring rather than a nearly closed arc.
- **Colours.** The loop runs through the hue clusters. The clusters overlap: they first touch at {{audit.loc.colors.connect:3}}.
- **Overlap of the relaxed-range θ_B class with the significant alpha bar** (the check of preregistration §4.6, extended to D5):
  - months {{audit.ph.months.3d.overlap}}, residues {{audit.ph.grok.3d.overlap}}, colours {{audit.ph.colors.3d.overlap}};
  - weekdays {{audit.ph.weekdays.3d.overlap}}, days_time {{audit.ph.daystime.3d.overlap}}.
  - Concepts with a constant coordinate (circular mean exactly 0) in the claimed records: months {{audit.ph.months.3d.constant}}, residues {{audit.ph.grok.3d.constant}}, colours 3D {{audit.ph.colors.3d.constant}}, colours top-10 {{audit.ph.colors.top10.constant}}.

## 3. Residues mod 113: an unstable view, not a weak circle

- The grokked W_E puts {{audit.grok.share_sum:2}} of its variance on 5 Fourier frequencies over the residues ({{audit.grok.freqs}}), {{audit.grok.share_min:2}}–{{audit.grok.share_max:2}} each. This matches the "key frequencies" of [Nanda et al. 2023](https://arxiv.org/abs/2301.05217).
- The top six PCA eigenvalue shares are therefore nearly equal: {{audit.pca.grok.l1:3}}, {{audit.pca.grok.l2:3}}, {{audit.pca.grok.l3:3}}, {{audit.pca.grok.l4:3}}, {{audit.pca.grok.l5:3}}, {{audit.pca.grok.l6:3}}. The ratio of the 3rd to the 4th is {{audit.pca.grok.gap34:2}}.
  - When eigenvalues are this close, the top-3 subspace is not stable under resampling ([Yu, Wang & Samworth 2015](https://doi.org/10.1093/biomet/asv008)).
  - So different subsamples can show different mixes of frequency planes in their top 3 PCs.
- In 10 dimensions the 5 circles combine into one closed curve with no single dominant loop.
- So the low subsample stability ({{exp2.grok.loop_freq:2}}; {{audit.stab.grok.matched:2}} against a size-matched threshold) and the failed top-10 check most likely reflect the multi-frequency code. They do not show a weak k = {{exp3.grok.thetaB.k}} circle.
- Exp2 also finds a second significant H1 bar for this set.

## 4. Controls that were never at risk

- The ordinal sets and the random walks and Gaussian processes are open curves. Their most persistent loops (π {{exp2.open.pi_min:2}}–{{exp2.open.pi_max:2}}) lie far below their Gaussian nulls' 95th percentiles ({{exp2.open.q95_min:2}}–{{exp2.open.q95_max:2}}); the smallest p is {{exp2.open.p_min:2}}.
- A matched Gaussian blob simply has more loops than a curve. "0 of 6" and "0 of 20" therefore say little about false positives on *nearly closed* curves, the relevant confound.
- The random-init networks are the informative calibration. One of 3 has p = {{exp2.grokinit.p_top_loop}}, consistent with the nominal 5%.

## 5. Ten dimensions

In the top-10 PCs (post hoc relaxed θ_B) only colours wind once:
- colours: winding {{exp3ph.colors.top10.w}};
- months {{exp3ph.months.top10.w}}, residues {{exp3ph.grok.top10.w}}, weekdays {{exp3ph.weekdays.top10.w}}, days_time {{exp3ph.daystime.top10.w}}.

"Going around once separates the cyclic concepts" was too broad: in 10D it separates 1 of 5 cyclic sets, and that one is confounded by the input (section 1).

## 6. Subsample stability against a size-matched threshold

Exp2 compared subsamples of 80% of the points with the full-size null's 95th percentile. The table in section 2 also shows the threshold recomputed at the subsample size (5 subsamples × 199 draws, the dataset's own design). The conclusions do not change:
- colours and months stay robust;
- days_time stays unstable;
- residues stay below one half.

## 7. The power argument for weekdays

The README quoted "only 15%" for the simulated cell closest to the weekdays' top-3 variance. More precisely:
- That cell has top-3 share {{audit.power.k7.ring.nearest_top3:3}}, against the real {{audit.power.k7.ring.real_top3:3}}.
- It passes in {{audit.power.k7.ring.nearest_loop:2}} of 40 replicates, with an exact 95% CI of {{audit.power.k7.ring.ci_lo:2}}–{{audit.power.k7.ring.ci_hi:2}}.
- Linear interpolation to the real share gives {{audit.power.k7.ring.interp_loop:2}}.
- The simulated within-cluster noise is isotropic in 4,096 dimensions, so the simulated clusters are much tighter in the top-3 PCs than the real weekday clusters.

Low power is real, but it does not explain the missing loop of day centres (section 2).

## 8. Exp1: the ρ_A ≥ 4 subset

The well-resolved subset (post hoc, D6) has {{exp1.well.n}} clouds from {{exp1.well.n_families}} families:
- no torus reaches ρ_A ≥ 4;
- a fraction {{exp1.well.trivial_frac:2}} are blobs, discs or paraboloids, which have infinite margin and no hole.

"Shapes whose holes stand well above the noise" was therefore wrong. The subset is "clouds far from a change of topology", and its macro average leaves out the family where the label is best.

The family label also comes from a fitter trained on the same 13-family generator, so it is scored in-distribution.

## 9. The preregistered closure ratio

Preregistration section 5 defines a descriptive closure ratio: d(last, first) / median d(c, c + 1) between concept means in the full activation space, with cosine distance. It was implemented but never reported. It is now reported in the table above.
- About 1 means the semantic cycle closes like a circle. Large values mean an open arc.
- Months: {{audit.closure.months:2}}; weekdays {{audit.closure.weekdays:2}}; days_time {{audit.closure.daystime:2}}; colours {{audit.closure.colors:2}}.
- Residues in natural order: {{audit.closure.grok:2}}. The natural order is not the representation's order, so this value says little.
- Ordinal sets in 7 bins: {{audit.closure.ordinal.min:2}}–{{audit.closure.ordinal.max:2}}. Random-process controls in 7 bins: {{audit.closure.c1.min:2}}–{{audit.closure.c1.max:2}}.
- **The ratio is a crude descriptive.**
  - Months lie below every ordinal set and every random-process control, which weakly favours a closing cycle.
  - But colours, whose loop is the clearest in the top-3 PCs, score {{audit.closure.colors:2}}, and the structureless random-init controls sit near 1 (weekdays init {{audit.closure.weekdaysinit:2}}).
  - A single last-to-first distance in thousands of dimensions does not decide closure.

## What changed in the documentation

- README, summary, per-dataset findings, the Exp1/2/3 reports and the paper now say:
  - the colour loop is inherited from the stimuli;
  - weekdays and days with times have no ring of days;
  - months have a significant loop, not necessarily a closed ring;
  - the open-curve controls were never at risk, and the random-init networks give the calibration;
  - the residues' instability comes from near-equal PCA eigenvalues;
  - 10D winding holds for colours only;
  - the power numbers come with CIs;
  - the ρ_A ≥ 4 subset is post hoc and has no tori.
- "× chance" is now "× the null's 95th percentile".
- The example figure no longer labels the days_time within-cluster loop as a ring.

## Learnings

- A maximum statistic over all bars needs localising in clustered designs. Check whether the winning bar dies before the clusters touch.
- When a stimulus set is sampled from a space with its own geometry (RGB, HLS), run the topology on the stimuli themselves before reading the activations' topology as the model's.
- Report CIs for every simulated pass rate, and interpolate rather than quote the nearest grid cell.
- A control only tests specificity if it can come near the threshold.
