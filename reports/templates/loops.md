# Loops: every loop scored, the interesting ones shown (post hoc, deviation D11)

Date: 2026-11-16. Author: Libor "Burny" Burian.
- Every number is generated from `results/loops/`, `results/exp2/` and `results/exp7_audit/` by `run.py report`.
- Code: `src/neurotopo/experiments/loop_search.py` (`run.py loops`); representative cycles: `diagrams.alpha_h1_cycles`; figure: `report/figures.py` (`fig_loop_gallery`).
- No model inference and no training. Everything uses the stored clouds and the stored Exp2 nulls.

## Why

Exp2 tests only each cloud's most persistent loop, and the README's detected-loops figure shows that loop for six example clouds. This phase lists all {{loops.n_loops}} loops of the {{loops.n_clouds}} clouds and picks the ones worth showing by fixed rules, as the void search does for voids ([voids.md](voids.md)). The rules were written after the void search, so they are post hoc.

## Method

For every loop: its bar (birth, death), persistence ratio π = death / birth, and one representative cycle (the edge that creates the loop, closed by the shortest path through earlier edges; [glossary](../docs/glossary.md#representative-loop)).
- **p:** against the cloud's design-matched Exp2 null of the largest loop π. For a cloud's most persistent loop this is exactly Exp2's p (largest difference over the 44 clouds: {{loops.max_abs_p_gap_vs_exp2}}). For other loops it is conservative.
- **Size:** death − birth, how much the balls must still grow (in radius) to fill the loop once it has closed.
- **Span of the cloud:** the bounding-box diagonal of the cycle's points divided by the cloud's.
- **Concept winding:** for a cyclic concept variable, how many times the concepts' phases go around as one walks along the cycle. The residues are ordered by their Fourier frequency k, as θ_B orders them. Winding ±1 is the project's ring criterion, here read off the cycle itself instead of a circular coordinate.

**Rules:**
1. **significant:** p < 0.05. By chance about 5% of clouds have such a loop, so about 2 of 44.
2. **large:** the 5 largest loops over all clouds, by size.
3. **goes around once:** in a cloud with a cyclic concept variable, concept winding ±1 along a cycle that spans at least half the cloud; the most significant such loop per cloud, kept if p < 0.5.

## Results

{{loops.n_significant}} loops have p < 0.05, and {{loops.n_interesting}} loops pass at least one rule. Rule 2 adds {{loops.n_large_only}} loops of its own: the 5 largest loops are also significant.

![Every interesting loop](../docs/figures/fig_loop_gallery.png)

<!-- BEGIN:loops -->
<!-- END:loops -->

- **Rings: the concepts go around a significant loop once.**
  - Months and the 12 month centres: {{loops.months.1.loop_concepts}} and {{loops.monthsmeans.1.loop_concepts}} of the 12 months lie on the cycle, and they go around it once (winding {{loops.months.1.winding}} and {{loops.monthsmeans.1.winding}}).
  - Grokked residues: the {{loops.grok.1.loop_concepts}} residues on the cycle go around once (winding {{loops.grok.1.winding}}) in the order of the Fourier frequency θ_B found.
  - These are the same loops Exp2 found and Exp3 tested, here seen directly on the cycle.
- **Colours:** the hue ring is the most persistent loop of all (π = {{exp2.colors.top_pi1:2}}), {{loops.colors.1.loop_concepts}} of the {{loops.colors.1.n_concepts}} hues lie on its cycle, and they wind once ({{loops.colors.1.winding}}). It misses rule 3 only on span: its cycle spans {{loops.colors.1.extent:2}} of the cloud's bounding-box diagonal, which a few far-out points of the cloud stretch.
- **Significant, but not a ring of concepts:**
  - The toy models' loops are 4-cycles of their polytopes. With 8 features the cycle is close to a square: π = {{exp2.tmsn8.top_pi1:3}}, against 1/sin(π/4) = √2 ≈ 1.414 for a regular square.
  - Days with times: a small loop inside one day's cluster ({{loops.daystime.1.loop_concepts}} of {{loops.daystime.1.n_concepts}} days on the cycle; audit D8).
  - The random-init grokking embedding: p = {{exp2.grokinit.p_top_loop}}, about what chance gives among 44 clouds.
- **A second loop in the grokked residues** (p = {{loops.grok.1.p}} for the first, {{loops.grok.2.p}} for the second). In the order of θ_B's frequency its residues do not wind ({{loops.grok.2.winding}}). In the order of the network's five Fourier frequencies (exp7 audit: {{audit.grok.freqs}}), loop 1 winds once for frequencies {{loops.grok.loop1.wind1}} and loop 2 for {{loops.grok.loop2.wind1}}. On cycles this short ({{loops.grok.1.loop_concepts}} and {{loops.grok.2.loop_concepts}} of the 113 residues), several frequencies can give winding ±1, so the winding alone does not tell which frequency a loop belongs to.

## Limitations

- The rules are post hoc, and the per-loop p-values are not corrected over the {{loops.n_loops}} loops. The Benjamini–Hochberg correction applies to Exp2's top loops only.
- The cycle is one representative of each loop, for display; the winding depends on that choice. The preregistered traversal test (Exp3) uses the circular coordinate θ_B instead.
- A significant loop is not by itself a hole: the Gaussian null also flags many hole-free shapes (audit D9).
