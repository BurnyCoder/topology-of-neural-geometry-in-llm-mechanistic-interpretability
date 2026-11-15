# Where the labelled points sit on their fitted shapes (exploratory, deviation D4)

Date: 2026-11-15. Code: `src/neurotopo/experiments/coords_check.py`. Results: `results/coords/`. No model is run: only the stored clouds and the source fits are used.

## Question

The author asked: project the original labelled points onto the fitted shape, and check whether the concept values are ordered along it.

## Method

- **Intrinsic coordinates of every point:**
  - helix: curve parameter t, azimuth and axial position;
  - ringing and line curves: parameter s;
  - cone: azimuth and height s;
  - sphere: azimuth and polar height z;
  - clusters and polytope: nearest centroid or vertex.
- **Statistics:**
  - angular coordinates: circular alignment with the semantic phases (concept means, permutation p, winding);
  - linear coordinates: Spearman ρ with the value (ordinal sets, per point) or with the concept index (cyclic sets, per concept mean; exact permutation p for n ≤ 8);
  - assignments: NMI and ARI with the concepts.
- **Variables implicit in the source's row order and labels:** the prompt offset "k days from" for weekdays and months, and saturation and lightness for colours.
- **Post hoc:** the harmonic content (R² of 1st, 2nd and 3rd Fourier harmonics) of the axial position of the cyclic helix fits.

## Results

- **Weekdays** (helix):
  - the days sit around the axis in cyclic order (R = {{coords.weekdays.azimuth.day_of_week.R:3}}, exact p = {{coords.weekdays.azimuth.day_of_week.p}}, winding {{coords.weekdays.azimuth.day_of_week.winding}});
  - curve parameter t vs day: ρ = {{coords.weekdays.curve_parameter_t.day_of_week.rho:2}} (p = {{coords.weekdays.curve_parameter_t.day_of_week.p:2}});
  - axial position vs offset k: ρ = {{coords.weekdays.axial_position.offset_k.rho:2}}.
- **Months** (helix):
  - around the axis: R = {{coords.months.azimuth.month.R:3}}, winding {{coords.months.azimuth.month.winding}};
  - t vs month: ρ = {{coords.months.curve_parameter_t.month.rho:2}};
  - axial position vs offset: ρ = {{coords.months.axial_position.offset_k.rho:2}};
  - post hoc, axial harmonics: R² = {{coords.months.harmonic.h1:2}} / {{coords.months.harmonic.h2:2}} / {{coords.months.harmonic.h3:2}} for h = 1 / 2 / 3. Weekdays: {{coords.weekdays.harmonic.h1:2}} / {{coords.weekdays.harmonic.h2:2}} / {{coords.weekdays.harmonic.h3:2}}.
- **Residues** (helix): around the axis at k = {{exp3.grok.thetaB.k}}, R = {{coords.grok.azimuth.residue_(max_over_k).R:3}}.
- **Days with times** (ringing curve): days are ordered *along* the open curve (ρ = {{coords.daystime.curve_parameter_s.day_of_week.rho:2}}, p = {{coords.daystime.curve_parameter_s.day_of_week.p}}); time of day also (ρ = {{coords.daystime.curve_parameter_s.time_of_day.rho:2}}).
- **Colours** (cone): hue goes around the axis (R = {{coords.colors.azimuth.hue.R:3}}, winding {{coords.colors.azimuth.hue.winding}}). Height follows lightness (ρ = {{coords.colors.height_s.lightness.rho:2}}) more than saturation (ρ = {{coords.colors.height_s.saturation.rho:2}}).
- **Ordinal sets:**
  - counting: ρ = {{coords.counting.curve_parameter_s.value.rho:3}} along the curve;
  - temperature: {{coords.temperature.curve_parameter_s.value.rho:3}};
  - GPT-2 positions: polar height {{coords.wpos.polar_height_z.value.rho:3}}; the azimuth winds twice (a spiral on the fitted sphere);
  - years (cone): height {{coords.years.height_s.value.rho:2}}, no winding;
  - age (clusters): NMI with 7 age bins {{coords.age.nearest_centroid/vertex.value_in_7_bins.NMI:2}}.

<!-- BEGIN:coords -->
<!-- END:coords -->

## Interpretation

- **The helices of the cyclic concepts are circles around their axis.**
  - The concept order is on the azimuth.
  - The axial direction is neither the concept order nor the prompt offset.
  - For months, the axial position is a second harmonic of the month angle. That is the signature of a closed, saddle-shaped loop (cos φ, sin φ, cos 2φ), like a tennis-ball seam, which the helix family can only approximate.
- **Ordinal concepts lie along open curves.** For counts and temperature this is a PCA horseshoe; for GPT-2 positions it is a spiral.
- **Days with times** (Llama layer 19, last token) represent the day linearly along an open curve. Monday and Sunday are at opposite ends.

## Learnings

- The analysis was added at the author's request instead of simulated steering. It answers "does it make semantic sense on the fit?" without running any model.
- The harmonic analysis is post hoc. It was prompted by the non-monotone axial means.
