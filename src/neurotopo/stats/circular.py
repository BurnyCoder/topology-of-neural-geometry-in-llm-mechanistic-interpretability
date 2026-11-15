"""Travel-around-the-hole statistics, shared by Method A (fitted-shape coordinate) and Method B (cohomology).

Global context: inspired by manifold steering (Wurgaft et al. 2026, arXiv:2605.05115), which moves activations
along a fitted day-of-week manifold and finds the output stepping Monday -> Tuesday -> ..., we ask the
observational, topological question: given a circle-valued coordinate theta that goes once around a hole,
do the concepts (days, months, residues) sit around it in their semantic cyclic order, going around exactly
once? (reports/preregistration.md, section 5). Statistics:
- concept circular means (aggregate first, so prompt templates are not pseudo-replicates);
- alignment R = max_s |mean_c exp(i(theta_c - s phi_c))| with a permutation null over concept labels;
- winding number of the semantic cycle in theta; exact cyclic-order test p = 2/(n-1)!;
- closure ratio of the semantic cycle in the full activation space (descriptive).
"""

from __future__ import annotations

import itertools
import math

import numpy as np
from scipy.spatial.distance import cdist


def wrap(a: np.ndarray) -> np.ndarray:
    """Wrap angles to (-pi, pi]."""
    return np.angle(np.exp(1j * np.asarray(a, dtype=np.float64)))


def concept_means(theta: np.ndarray, idx: np.ndarray, n: int) -> np.ndarray:
    """Circular mean arg(sum_{i in c} e^{i theta_i}) of each concept c = 0..n-1 (NaN if a concept is empty)."""
    z = np.zeros(n, dtype=complex)
    np.add.at(z, np.asarray(idx), np.exp(1j * np.asarray(theta, dtype=np.float64)))
    out = np.angle(z)
    out[np.abs(z) == 0] = np.nan
    return out


def alignment(theta_c: np.ndarray, phase: np.ndarray) -> tuple[float, int]:
    """R = max over orientation s in {+1, -1} of |mean_c exp(i (theta_c - s phi_c))|; returns (R, s).
    Invariant to the arbitrary origin (rotation) and orientation (reflection) of theta."""
    ok = np.isfinite(theta_c)
    th, ph = theta_c[ok], phase[ok]
    rp = abs(np.mean(np.exp(1j * (th - ph))))
    rm = abs(np.mean(np.exp(1j * (th + ph))))
    return (float(rp), 1) if rp >= rm else (float(rm), -1)


def _alignment_matrix(theta_c: np.ndarray, phases: np.ndarray) -> np.ndarray:
    """Vectorised alignment R for many phase assignments (rows of `phases`)."""
    e = np.exp(1j * theta_c)[None, :]
    rp = np.abs((e * np.exp(-1j * phases)).mean(1))
    rm = np.abs((e * np.exp(1j * phases)).mean(1))
    return np.maximum(rp, rm)


def permutation_pvalue(theta_c: np.ndarray, phase: np.ndarray, exact_max_n: int = 7, mc: int = 99999,
                       rng: np.random.Generator | None = None) -> float:
    """p-value of R against reassigning the phases among concepts.

    n <= exact_max_n: exact over all n! assignments (the observed assignment is one of them).
    Otherwise Monte Carlo: p = (1 + #{R_perm >= R_obs}) / (mc + 1) (Phipson & Smyth 2010, doi:10.2202/1544-6115.1585).
    """
    ok = np.isfinite(theta_c)
    th, ph = np.asarray(theta_c)[ok], np.asarray(phase)[ok]
    r_obs = alignment(th, ph)[0]
    n = th.size
    if n <= exact_max_n:
        perms = np.array(list(itertools.permutations(range(n))))
        r = _alignment_matrix(th, ph[perms])
        return float(np.mean(r >= r_obs - 1e-12))
    rng = rng or np.random.default_rng(0)
    count, done, batch = 0, 0, 10000
    while done < mc:
        b = min(batch, mc - done)
        perms = np.argsort(rng.random((b, n)), axis=1)            # b uniform random permutations
        count += int((_alignment_matrix(th, ph[perms]) >= r_obs - 1e-12).sum())
        done += b
    return (1.0 + count) / (mc + 1.0)


def max_over_frequency(theta: np.ndarray, a: np.ndarray, modulus: int, kmax: int) -> tuple[float, int, int]:
    """Grokking residues: max over Fourier frequency k in 1..kmax of R(theta, 2 pi k a / modulus); (R, k, s)."""
    best = (-1.0, 0, 1)
    for k in range(1, kmax + 1):
        r, s = alignment(theta, 2 * np.pi * k * np.asarray(a) / modulus)
        if r > best[0]:
            best = (r, k, s)
    return best


def max_over_frequency_pvalue(theta: np.ndarray, a: np.ndarray, modulus: int, kmax: int, mc: int,
                              rng: np.random.Generator) -> float:
    """Max-statistic permutation p-value: residues are permuted and the max over k recomputed each time."""
    a = np.asarray(a)
    r_obs = max_over_frequency(theta, a, modulus, kmax)[0]
    ks = np.arange(1, kmax + 1)[:, None]
    e = np.exp(1j * np.asarray(theta))[None, :]
    count, done = 0, 0
    while done < mc:
        b = min(500, mc - done)
        for _ in range(b):
            ph = 2 * np.pi * ks * rng.permutation(a)[None, :] / modulus     # (kmax, n) phases for permuted labels
            r = np.maximum(np.abs((e * np.exp(-1j * ph)).mean(1)), np.abs((e * np.exp(1j * ph)).mean(1)))
            count += int(r.max() >= r_obs - 1e-12)
        done += b
    return (1.0 + count) / (mc + 1.0)


def winding(theta_c: np.ndarray) -> int:
    """Winding number of the closed semantic cycle c = 0, 1, ..., n-1, 0 in the coordinate theta:
    w = (1 / 2 pi) sum_c wrap(theta_{c+1} - theta_c). Empty concepts (NaN) are skipped."""
    th = np.asarray(theta_c, dtype=np.float64)
    th = th[np.isfinite(th)]
    if th.size < 2:
        return 0
    steps = wrap(np.roll(th, -1) - th)
    return int(round(steps.sum() / (2 * np.pi)))


def cyclic_order_matches(theta_c: np.ndarray) -> bool:
    """True if the circular order of the concept means equals the semantic cycle 0..n-1 up to rotation and
    reflection (every step goes the same way around and the cycle winds exactly once)."""
    th = np.asarray(theta_c, dtype=np.float64)
    if not np.all(np.isfinite(th)):
        return False
    order = np.argsort(wrap(th))                     # concepts sorted by angle around the circle
    n = order.size
    d = (np.roll(order, -1) - order) % n             # successive concept differences around the circle
    return bool(np.all(d == 1) or np.all(d == n - 1))


def cyclic_order_p(n: int) -> float:
    """Probability that a random labelling reproduces the cyclic order up to rotation/reflection: 2n / n!."""
    return 2.0 / math.factorial(n - 1)


def closure_ratio(means: np.ndarray, metric: str = "cosine") -> float:
    """d(last, first) / median_c d(c, c+1) between concept means in the full space (descriptive): about 1 when
    the semantic cycle closes like a circle; large for an open arc or a helix whose ends are far apart."""
    m = np.asarray(means, dtype=np.float64)
    d = cdist(m, m, metric=metric)
    steps = np.array([d[c, c + 1] for c in range(len(m) - 1)])
    return float(d[-1, 0] / np.median(steps))
