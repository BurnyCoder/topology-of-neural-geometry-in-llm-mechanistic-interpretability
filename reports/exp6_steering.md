# Exp6: steering around topologically detected holes (primary hypothesis H6, postponed)

Date: 2026-11-15. Status: **designed and preregistered (amendment A2), not run.** The author postponed both steps. No model inference has been performed in this project.

## Hypothesis (amendment A2)

Whenever topology detects a hole in a concept cloud, moving the concept token's activation around the loop that encircles the hole makes the answer go around the concept's semantic cycle exactly once. This is inspired by manifold steering ([Wurgaft et al. 2026](https://arxiv.org/abs/2605.05115); [Goodfire](https://www.goodfire.com/research/manifold-steering)).

## Registered design and unmeasured outcomes

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

## Eligibility and implementation review on 26 November 2026

None of the registered steering readouts has observations. A detected loop determines eligibility for the conditional comparison. Continuity, circular-coordinate availability, semantic traversal in a projection, and a response to an intervention each require separate measurements. Ordinal datasets can have persistent loops. [Every model and control](../results/science/h6_datasets.csv) · [Projection evidence](../results/science/dataset_assessment.csv)

The explorer uses 24 display bins. The H6 protocol specifies twice the number of concepts, capped at 72. The unrun residue implementations now use that rule, include the initialization embedding in the simulated control set, and compare model and random paths on the same single prompt for each residue. An unavailable coordinate produces a missing endpoint. These changes have no effect on a published steering result. [Preregistered amendment A2](preregistration.md) · [Simulated implementation](../src/neurotopo/experiments/exp6_sim.py) · [Model implementation](../src/neurotopo/experiments/exp6_steering.py)

The registered simulated on-manifold threshold is the 95th percentile of training rows' distances to their own concept centroid. For one embedding per residue, each training centroid equals its training row and this radius is zero. The historical code used a positive nearest-neighbour radius, a different endpoint. A looser future criterion would require a dated amendment. The modular model's output vocabulary consists entirely of residues, making its in-vocabulary mass one by construction. The empirical winding and random-loop comparisons remain unmeasured. [Centroid rule](../src/neurotopo/steering/offline.py) · [Model output layer](../src/neurotopo/steering/models.py)
