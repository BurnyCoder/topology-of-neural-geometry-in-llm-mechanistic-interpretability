# Findings per dataset

Date: 2026-11-15. Every number is generated from `results/` (`run.py report`). Compact overview: the README's evaluation tables; methods: [docs/methodology.md](../docs/methodology.md).


Here "hole" means a significant H1 loop under the design-matched Monte Carlo null (999 draws), and "goes around" means winding exactly once in the loop's circle-valued coordinate. The alignment R and its permutation p measure *ordering*; only winding ±1 carries the cyclic claim.

- **Colours (exploratory set):**
  - Hole: π = {{exp2.colors.top_pi1:2}} vs null 95th percentile {{exp2.colors.null_q95_pi1:2}}, p = {{exp2.colors.p_top_loop}}, Benjamini–Hochberg q = {{exp2.colors.q_loop}}, stable in {{exp2.colors.loop_freq:2}} of subsamples.
  - Hue goes around it once, in θ_B (R = {{exp3.colors.thetaB.R:2}}, winding {{exp3.colors.thetaB.w}}) and on the fitted cone (R = {{exp0.colors.theta.R:2}}, winding {{exp0.colors.theta.w}}).
  - In the top-10 PCs the loop stays significant (Rips π = {{exp5.top10.colors.pi:2}} vs {{exp5.top10.colors.q95:2}}, p = {{exp5.top10.colors.p}}), and hue still winds once there, post hoc (R = {{exp3ph.colors.top10.R:2}}, winding {{exp3ph.colors.top10.w}}).
- **Grokked residues mod 113:**
  - Hole: π = {{exp2.grok.top_pi1:2}} vs {{exp2.grok.null_q95_pi1:2}}, p = {{exp2.grok.p_top_loop}}, but stable in only {{exp2.grok.loop_freq:2}} of subsamples.
  - The residues go around it once at Fourier frequency {{exp3.grok.thetaB.k}} (Holm p = {{exp3.grok.B.holm}}, winding {{exp3.grok.thetaB.w}}).
  - The preregistered top-10-PC check fails (top-10 null p = {{exp5.top10.grok.p}}).
- **Months:**
  - Hole: π = {{exp2.months.top_pi1:2}} vs {{exp2.months.null_q95_pi1:2}}, p = {{exp2.months.p_top_loop}}.
  - The preregistered circular-coordinate setting built no coordinate. Only post hoc (relaxed setting) do the months go around the loop once in 3D (R = {{exp3ph.months.3d.R:2}}, winding {{exp3ph.months.3d.w}}). They do not in the top-10 PCs (winding {{exp3ph.months.top10.w}}; top-10 null p = {{exp5.top10.months.p}}).
  - On the fitted helix the two ends nearly meet (closure gap {{exp0.months.azimuth.gap:2}} radii). Post hoc, the axial position follows the 2nd Fourier harmonic (R² = {{coords.months.harmonic.h2:2}} vs {{coords.months.harmonic.h1:2}} for the 1st), as a closed saddle-shaped loop would.
- **Days with times** (day phase, exploratory):
  - There is a loop (p = {{exp2.daystime.p_top_loop}}), but it is unstable (stable in {{exp2.daystime.loop_freq:2}} of subsamples).
  - **The day does not go around it**, even post hoc (R = {{exp3ph.daystime.3d.R:2}}, winding {{exp3ph.daystime.3d.w}}). On the fitted curve the days lie in linear order (ρ = {{coords.daystime.curve_parameter_s.day_of_week.rho:2}}).
- **Weekdays:**
  - **No detectable hole** (π = {{exp2.weekdays.top_pi1:2}} vs {{exp2.weekdays.null_q95_pi1:2}}, p = {{exp2.weekdays.p_top_loop}}).
  - The test has little power here (corrected power simulation: a true weekday-like ring passes the loop test in {{power2.weekdays.loop:2}} of replicates; [fig_power](../docs/figures/fig_power.png)).
  - The days are ordered around the fitted helix's axis (exact p = {{exp0.weekdays.azimuth.p}}, winding {{exp0.weekdays.azimuth.w}}). **This is not specific:** {{exp0.gp_wind1}} of {{exp0.gp_helix_n}} smooth random-process controls fitted as helices wind too, and their closure gaps ({{exp0.gp_gap_min:2}}–{{exp0.gp_gap_max:2}}) include the weekdays' {{exp0.weekdays.azimuth.gap:2}}.
- **Ordinal concepts and controls:**
  - Ordinal values do not wind around the top-10 loops. Only {{exp3ph.noncyclic_wind1_ids}} has a single winding record among all non-cyclic sets.
  - After Benjamini–Hochberg over all 44 loop tests, {{exp2.n_loop_q05}} loops remain at q < 0.05: {{exp2.loops_q05}}.
  - Ordinal concepts lie in order along open curves: counts ρ = {{coords.counting.curve_parameter_s.value.rho:3}}, temperature {{coords.temperature.curve_parameter_s.value.rho:3}}. GPT-2 positions run from pole to pole of their fitted sphere ({{coords.wpos.polar_height_z.value.rho:3}}) as a spiral curve.
  - Truth cities: the exploratory prediction of two components (true vs false statements) is not supported (b0 = {{exp2.truth.b0}}).
