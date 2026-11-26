"""Simulated steering (step 1 of amendment A2): would steering around a detected hole make semantic sense?

Global context: before running any model, we infer from the stored activations alone whether moving a concept
token's activation around the loop that encircles a hole would change the *represented* concept in semantic
order. The readout is a decoder trained on the other prompts' activations (cross-validated by template), so
the question is: if the model read the concept the way this decoder does, would steering around the loop
step Monday -> Tuesday -> ... -> Monday? This is a simulation under that assumption (correlational evidence),
not a causal test of the model's behaviour, which is step 2 (postponed).
- Primary decoder: nearest concept centroid in the full activation space (Euclidean).
- Secondary decoder: ridge probe to (cos phi_c, sin phi_c); used alone for grokking residues (one point each).
- On-manifold: the steered activation lies within the 95th percentile of training points' distances to their
  own concept centroid (residues: of nearest-neighbour distances among the other embeddings).
"""

from __future__ import annotations

import numpy as np

from neurotopo.steering import loops, metrics


def folds(dataset_id: str, n: int) -> np.ndarray:
    """Cross-validation group of every point (amendment A2): leave one prompt template out."""
    if "weekdays" in dataset_id and "means" not in dataset_id:
        return np.arange(n) % 7                 # offset k: row i = day i // 7, offset i % 7 + 1
    if "months" in dataset_id and "means" not in dataset_id:
        return np.arange(n) % 12
    if dataset_id == "R5c_llama_days_time":
        return np.arange(n) % 48                # time of day
    if dataset_id == "R7_llama_colors":
        return np.arange(n) % 25                # (saturation, lightness) pair
    return np.arange(n)                         # one point per value: leave one point out


class CentroidDecoder:
    """Nearest concept centroid fitted on all points outside one fold; decodes concept phases of steered points."""

    def __init__(self, x: np.ndarray, concept: np.ndarray, n_concepts: int, train: np.ndarray):
        self.c = np.full((n_concepts, x.shape[1]), np.nan)
        rad = []
        for k in range(n_concepts):
            m = train & (concept == k)
            if m.any():
                self.c[k] = x[m].mean(0)
                rad.append(np.linalg.norm(x[m] - self.c[k], axis=1))
        self.valid = np.isfinite(self.c[:, 0])
        self.radius95 = float(np.quantile(np.concatenate(rad), 0.95)) if rad else np.inf
        self.cn = (np.where(self.valid[:, None], self.c, 0) ** 2).sum(1)

    def decode(self, h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(nearest concept index, distance to it) for every row of h."""
        d2 = (h ** 2).sum(1)[:, None] - 2 * h @ np.where(self.valid[:, None], self.c, 0).T + self.cn[None]
        d2[:, ~self.valid] = np.inf
        k = np.argmin(d2, 1)
        # Direct subtraction preserves an exact zero radius for singleton training concepts.
        return k, np.linalg.norm(h - self.c[k], axis=1)


class PhaseProbe:
    """Ridge regression from activations to (cos phi, sin phi); decoded phase = atan2 (secondary decoder)."""

    def __init__(self, x: np.ndarray, phase: np.ndarray, train: np.ndarray):
        xt = x[train]
        self.mu = xt.mean(0)
        xc = xt - self.mu
        alpha = float((xc ** 2).sum(1).mean())                  # alpha = 1 x mean squared row norm (amendment A2)
        y = np.c_[np.cos(phase[train]), np.sin(phase[train])]
        # Dual ridge (N < D): W = Xc^T (Xc Xc^T + alpha I)^-1 Y
        self.w = xc.T @ np.linalg.solve(xc @ xc.T + alpha * np.eye(len(xc)), y - y.mean(0))
        self.b = y.mean(0)

    def decode(self, h: np.ndarray) -> np.ndarray:
        o = (h - self.mu) @ self.w + self.b
        return np.arctan2(o[:, 1], o[:, 0])


def steer_displacements(loop: loops.Loop, z_i: np.ndarray, basis: np.ndarray, deltas: np.ndarray) -> np.ndarray:
    """(K, D) displacements gamma(phi + Delta) - gamma(phi) mapped to the full space for one prompt."""
    phi = loop.param(z_i[None])[0]
    return (loop(phi + deltas) - loop(np.array([phi]))) @ basis.T


def build_decoders(x: np.ndarray, concept: np.ndarray, phase: np.ndarray, groups: np.ndarray,
                   probe: bool = False) -> dict:
    """One (centroid decoder, optional phase probe) per cross-validation fold, fitted without that fold."""
    n = len(phase)
    out = {}
    for g in np.unique(groups):
        train = groups != g
        out[g] = (CentroidDecoder(x, concept, n, train), PhaseProbe(x, phase[concept], train) if probe else None)
    return out


def evaluate(loop_for, x: np.ndarray, z: np.ndarray, basis: np.ndarray, phase: np.ndarray, groups: np.ndarray,
             deltas: np.ndarray, decoders: dict, prompts: np.ndarray | None = None) -> dict:
    """Per-prompt traversal under one loop. loop_for(i) returns the loop for prompt i (loop A is per prompt);
    the decoders of the prompt's own (held-out) fold read the steered activations."""
    per = []
    idx = np.arange(len(x)) if prompts is None else prompts
    for i in idx:
        dec, pr = decoders[groups[i]]
        h = x[i] + steer_displacements(loop_for(i), z[i], basis, deltas)
        k, dist = dec.decode(h)
        rec = {"prompt": int(i), **metrics.traversal(phase[k], deltas), "vocab_mass": float(np.mean(dist <= dec.radius95))}
        if pr is not None:
            rec["probe"] = metrics.traversal(pr.decode(h), deltas)
        per.append(rec)
    return {"per_prompt": per, **metrics.dataset_statistic(per)}
