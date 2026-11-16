# Voids: every void scored, the interesting ones shown (post hoc, deviation D10)

Date: 2026-11-16. Author: Libor "Burny" Burian.
- Every number is generated from `results/voids/` and `results/exp2/` by `run.py report`.
- Code: `src/neurotopo/experiments/void_search.py` (`run.py voids`); representative shells and centres: `diagrams.alpha_h2_voids`; figures: `report/figures.py` (`fig_void_gallery`, `fig_void_life`, `fig_detected_voids`).
- No model inference and no training. Everything uses the stored clouds and the stored Exp2 nulls.

## Why

A void is an empty region walled in by a closed surface, like the inside of a hollow ball: an H2 bar of the alpha complex ([glossary](../docs/glossary.md#representative-void)). Exp2 tests only each cloud's most persistent void. This phase lists all {{voids.n_voids}} voids of the {{voids.n_clouds}} clouds that have any (of {{voids.n_clouds_total}}) and picks the ones worth showing by fixed rules, so the README's void figures do not rest on picking by eye. The rules were written after browsing the explorer, so they are post hoc.

## Method

For every void: its bar (birth, death), persistence ratio π = death / birth, representative shell (a closed surface of triangles, present at the birth radius and filled exactly at the death radius) and centre (the circumcentre of the tetrahedron that fills it; no point is closer to it than the death radius).
- **p:** (1 + the number of null clouds whose largest void π is at least this void's π) / (M + 1), against the cloud's design-matched Exp2 null. For a cloud's most persistent void this is exactly Exp2's p (largest difference over the 44 clouds: {{voids.max_abs_p_gap_vs_exp2}}). For other voids it is conservative.
- **Empty middle:** death − birth, the radius of the ball around the centre that is still uncovered when the void closes.
- **Span of the cloud:** the bounding-box diagonal of the shell's corners divided by the cloud's.
- **Concepts on the shell:** how many of the cloud's concepts have a point among the shell's corners.

**Rules:**
1. **significant:** p < 0.05. By chance about 5% of clouds have such a void, so about 2 of 44.
2. **large:** the 5 largest empty middles over all clouds.
3. **shape and meaning:** in a trained model's concept cloud, a shell spanning at least half the cloud with at least half its concepts on the corners; the most significant such void per cloud, kept if p < 0.5.

## Results

{{voids.n_significant}} voids have p < 0.05, and {{voids.n_interesting}} voids pass at least one rule.

![Every interesting void](../docs/figures/fig_void_gallery.png)

<!-- BEGIN:voids -->
<!-- END:voids -->

- **The toy models of superposition are the only clouds whose voids pass every check** (they are exploratory sets of 6–20 points).
  - Their voids are significant (they survive Benjamini–Hochberg over Exp2's 44 tests, q = {{exp2.tmsn6.q_void:3}}).
  - They are the 3 largest, the shell spans the whole cloud, and every feature (or nearly every one) is a corner.
  - The features sit on or near the corners of a polytope, and nothing lies inside it.
  - Significant means more void persistence than in Gaussian clouds of the same spread (D9). With so few points, such clouds rarely have any void at all.
- **The other significant voids are what chance and degenerate inputs give:**
  - GPT-2 positions at random init: p = {{exp2.wposinit.p_top_void}}, q = {{exp2.wposinit.q_void:2}}, back in {{exp2.wposinit.void_freq_pct}}% of subsamples;
  - the dense toy model: with only 5 points, null clouds almost never have a void at all (the null's 95th percentile of the largest void π is {{exp2.tmsdense.null_q95_pi2:3}}), so a sliver of a void with π = {{exp2.tmsdense.top_pi2:4}} gets p = {{exp2.tmsdense.p_top_void}};
  - the random-init weekdays: a tiny void inside one day's cluster.
- **Shape and meaning without significance:** the 7 weekday centres and the 12 month centres each wall in a void spanning most of the cloud, with 4 of 7 days and 7 of 12 months on its shell, but neither is significant.
- **Large without significance:**
  - The colours cloud's largest void (#{{voids.colors.rank}} of {{voids.colors.n}} by π) sits inside the hue ring, which winds around its centre once. It closes at radius {{voids.colors.birth:3}}, right after the ring is filled in ({{voids.colors.loop_death:3}}). But p = {{voids.colors.p}}.
  - A Gaussian-process control (C1_gp_3) has the 5th-largest empty middle: a thin pocket between two sheets of triangles spanning a loop of the random curve. Big, cloud-spanning voids with every concept on the shell arise in random curves too.

## The life of a void (toy model, 6 features)

![The life of a void](../docs/figures/fig_void_life.png)

The {{life.tmsn6.points}} features of this toy model sit near the corners of an octahedron.
1. At radius {{life.tmsn6.edge_r:3}} its {{life.tmsn6.s1.edges}} edges have entered and made {{life.tmsn6.loops_born}} loops.
2. Between {{life.tmsn6.faces_r:3}} and {{life.tmsn6.birth:3}} its {{life.tmsn6.s2.triangles}} faces enter. They fill all {{life.tmsn6.loops_dead_by_birth}} loops and close one void (Euler characteristic {{life.tmsn6.points}} − {{life.tmsn6.s2.edges}} + {{life.tmsn6.s2.triangles}} = 2 = 1 − 0 + 1: one piece, no loops, one void).
3. The blue ball is the part of the void the balls of radius r do not reach yet. It shrinks as r grows.
4. At {{life.tmsn6.death:3}} the inner diagonal, its triangles and the {{life.tmsn6.s4.tetrahedra}} tetrahedra enter and fill the void.

For a regular octahedron the void lives from √(2/3) ≈ 0.816 (the faces' circumradius) to 1, a persistence ratio of √(3/2) ≈ 1.225. The toy model gives π = {{exp2.tmsn6.top_pi2:3}}.

## Limitations

- The rules are post hoc, and the per-void p-values are not corrected over the {{voids.n_voids}} voids. Only the toy models' voids survive a correction (Exp2's BH over the 44 top voids).
- "Concepts on the shell" for the toy models counts equal-width bins of feature index, which carry no meaning. The features themselves are what matters there: each point is one feature.
- The shell and centre are one representative of each void, for display. The statistics never use them.
