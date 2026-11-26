# Exp6: steering around topologically detected holes (primary hypothesis H6, postponed)

Date: 2026-11-15. Status: **designed and preregistered (amendment A2), not run.** The author postponed both steps. No model inference has been performed in this project.

## Hypothesis (amendment A2)

Whenever topology detects a hole in a concept cloud, moving the concept token's activation around the loop that encircles the hole makes the answer go around the concept's semantic cycle exactly once. This is inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); [Goodfire](https://www.goodfire.com/research/manifold-steering)).

## Design (code ready)

- **Loops:**
  - B: fit-free, the θ_B-binned periodic cubic spline (`steering/loops.py`);
  - A: the fitted axis circle;
  - linear chord path through concept centroids;
  - random loops of the same radius in random planes of the top-10 PC space.
- **Displacement:** h(Δ) = h + (γ(φ + Δ) − γ(φ)) · basisᵀ.
- **Step 1, simulated steering** (`steering/offline.py`, `experiments/exp6_sim.py`): cross-validated nearest-centroid decoders and phase probes trained on the other prompts' stored activations. Postponed by the author, deviation D4.
- **Step 2, model steering** (`steering/models.py`, `tasks.py`, `experiments/exp6_steering.py`):
  - a forward hook on hidden_states[layer] of meta-llama/Llama-3.1-8B in bf16;
  - readouts over day, month and colour words;
  - the grokked modular-addition model, retrained with the source's recipe.
- **Decision per dataset:** p < 0.05 against random loops, |winding| = 1 for ≥ 50% of prompts, and on-manifold or in-vocabulary mass ≥ 0.5.

## What the topology predicts (from Exp2, Exp3 and the coordinates check)

- **Candidates with a detected hole that the concept travels around (3D):** colours (also in the top-10 PCs), residues mod 113, and months (post hoc).
- **Weekdays:** no detected hole in the top-3 PCs, although the days are ordered around the fitted helix's axis. Steering around an assumed circle could still work, but topology would not have found that circle.
- **Ordinal concepts and controls:** no hole, so steering around a loop has nothing semantic to follow.
