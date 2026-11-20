"""Traversal metrics for steering experiments: does the model's answer go around the concept cycle once?

Global context (preregistration amendment A2): for each prompt we steer the concept-token activation around a
loop by Delta = 2 pi j / K and decode the answer's phase psi(Delta) from the next-token distribution restricted
to the concept's words (argmax concept phase, or the probability-weighted circular mean for colours).
Semantically meaningful steering = psi advances with Delta and goes around exactly once:
R = max_s |mean_j exp(i (psi_j - psi_0 - s Delta_j))| (1 for perfectly linear traversal), winding of psi over
the closed sequence of steps = +-1, and the answer stays on the concept vocabulary (in-vocabulary mass).
"""

from __future__ import annotations

import numpy as np

from neurotopo.stats.circular import wrap


def decode_phase(probs: np.ndarray, phases: np.ndarray, mode: str = "argmax") -> np.ndarray:
    """Phase of the decoded answer per row of probs (rows: steps, columns: concept words)."""
    if mode == "argmax":
        return phases[np.argmax(probs, axis=-1)]
    return np.angle(probs @ np.exp(1j * phases))                        # probability-weighted circular mean


def traversal(psi: np.ndarray, deltas: np.ndarray) -> dict:
    """R (linear traversal with either orientation), its orientation, and the winding number of psi around the
    closed path of steps."""
    rel = wrap(psi - psi[0])
    r_pos = abs(np.mean(np.exp(1j * (rel - deltas))))
    r_neg = abs(np.mean(np.exp(1j * (rel + deltas))))
    steps = wrap(np.roll(psi, -1) - psi)                                 # closed: last step returns to Delta = 0
    w = int(round(steps.sum() / (2 * np.pi)))
    return {"R": float(max(r_pos, r_neg)), "orientation": 1 if r_pos >= r_neg else -1, "winding": w}


def dataset_statistic(per_prompt: list[dict]) -> dict:
    """T = mean R over prompts, fraction of prompts with |winding| = 1, mean in-vocabulary mass."""
    r = np.array([p["R"] for p in per_prompt])
    w = np.array([abs(p["winding"]) == 1 for p in per_prompt])
    m = np.array([p["vocab_mass"] for p in per_prompt])
    return {"T": float(r.mean()), "frac_wind1": float(w.mean()), "vocab_mass": float(m.mean()), "n_prompts": len(per_prompt)}


def null_pvalue(t_obs: float, t_null: np.ndarray) -> float:
    """(1 + #{T_null >= T_obs}) / (M + 1)."""
    t_null = np.asarray(t_null)
    return float((1 + np.sum(t_null >= t_obs - 1e-12)) / (t_null.size + 1))
