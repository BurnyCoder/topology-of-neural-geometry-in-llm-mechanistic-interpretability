"""`run.py loops`: every loop of every cloud, scored, and the interesting ones picked by fixed rules (post hoc, D11).

Global context: Exp2 tests only each cloud's most persistent loop (H1 bar) against the design-matched Monte Carlo
null, and the README's detected-loops figure shows that loop for six example clouds. This phase lists all loops of
the 44 alpha complexes (diagrams.alpha_h1_cycles: bar and one representative cycle of vertices) and scores each, as
experiments/void_search.py does for voids. Written after the void search, so the rules are post hoc:

- **significant:** p < 0.05 against the cloud's own Exp2 null of the largest loop pi (void_search.mc_p). For the top
  loop this is Exp2's p; for any other loop it is conservative. By chance, 5% of clouds have such a loop.
- **large:** among the LARGE_N largest loops over all clouds by death - birth (how much the balls must grow, in
  radius, to fill the loop once it has closed).
- **goes around once:** in a cloud whose concept variable is cyclic (source.concepts; residues ordered by their
  Fourier frequency k), the concepts' phases wind exactly once around the loop's representative cycle (the
  project's ring criterion, here read off the cycle itself rather than a circular coordinate) and the cycle spans at
  least SHAPE of the cloud; the most significant such loop per cloud, kept if p < AROUND_P.

Outputs: results/loops/all_loops.csv (one row per loop), results/loops/summary.json (rules, counts, the interesting
loops with their reasons and cycles) and env.json. No model inference: stored clouds and stored nulls only.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import env_record, out_dir, read_json, write_json
from neurotopo.experiments.void_search import mc_p
from neurotopo.tda import diagrams

log = logging.getLogger(__name__)
LARGE_N, SHAPE, AROUND_P = 5, 0.5, 0.5


def winding(phase: np.ndarray) -> int:
    """Times a closed sequence of angles goes around the circle: the sum of its steps, each wrapped to [-pi, pi),
    divided by 2 pi (the last step closes the cycle)."""
    step = np.diff(np.r_[phase, phase[:1]])
    return int(round(np.sum((step + np.pi) % (2 * np.pi) - np.pi) / (2 * np.pi)))


def cloud_loops(d: str, seed: int) -> tuple[pd.DataFrame, list[np.ndarray]]:
    """One row per loop of cloud d, ranked by pi (k = 1 is the most persistent; stable sort, as examples.replay), and
    the representative cycles in the same order."""
    from neurotopo.report.examples import concept_positions               # residues: by k * r mod 113 (exp3 theta_B)
    c = realdata.cloud(d)
    y = c["y"]
    bars, cycles = diagrams.alpha_h1_cycles(y)
    if not len(bars):
        return pd.DataFrame(), []
    pi = bars[:, 1] / bars[:, 0]
    null = realdata.null(d, seed)[:, 0]                                 # largest loop pi in each of the M null clouds
    try:
        con = source.concepts(d, c["labels"])
        idx, n_con, cyclic = con.index, len(con.names), bool(con.cyclic)
        phase = 2 * np.pi * concept_positions(d, c["labels"])
    except ValueError:                                                  # no concept structure (none of the 44 today)
        idx, n_con, cyclic, phase = None, 0, False, None
    diag = np.linalg.norm(np.ptp(y, axis=0))
    rows, order = [], np.argsort(-pi, kind="stable")
    for rank, i in enumerate(order, start=1):
        v = cycles[i]
        rows.append({"id": d, "N": len(y), "k": rank, "birth": bars[i, 0], "death": bars[i, 1],
                     "size": bars[i, 1] - bars[i, 0], "pi": pi[i], "p": mc_p(null, pi[i]), "length": len(v),
                     "extent": np.linalg.norm(np.ptp(y[v], axis=0)) / diag,
                     "loop_concepts": len(np.unique(idx[v])) if idx is not None else 0, "n_concepts": n_con,
                     "cyclic": cyclic, "winding": winding(phase[v]) if cyclic else 0})
    return pd.DataFrame(rows), [cycles[i] for i in order]


def interesting(df: pd.DataFrame) -> pd.DataFrame:
    """The loops picked by the three rules (module docstring), one row each, with the rules that picked it."""
    reasons: dict[tuple[str, int], list[str]] = {}
    for _, r in df[df["p"] < 0.05].iterrows():
        reasons.setdefault((r["id"], r["k"]), []).append("significant")
    for _, r in df.nlargest(LARGE_N, "size").iterrows():
        reasons.setdefault((r["id"], r["k"]), []).append("large")
    around = df[df["cyclic"] & (df["winding"].abs() == 1) & (df["extent"] >= SHAPE)]
    for _, r in around.sort_values(["p", "k"]).groupby("id").head(1).iterrows():
        if r["p"] < AROUND_P:
            reasons.setdefault((r["id"], r["k"]), []).append("goes around once")
    out = df.set_index(["id", "k"]).loc[list(reasons)].reset_index()
    out["reasons"] = [", ".join(reasons[(i, k)]) for i, k in zip(out["id"], out["k"])]
    return out.sort_values(["p", "size"], ascending=[True, False]).reset_index(drop=True)


def run() -> None:
    seed = config.load()["seed"]
    out = out_dir("loops")
    env_record("loops")
    tables, cycles = [], {}
    for d in source.dataset_ids():
        t, cyc = cloud_loops(d, seed)
        tables.append(t)
        cycles[d] = cyc
    df = pd.concat(tables, ignore_index=True)
    df.to_csv(out / "all_loops.csv", index=False, float_format="%.6g")
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    top = df[df["k"] == 1].set_index("id")
    gap = float(np.abs(top["p"] - inv.loc[top.index, "p_top_loop"]).max())   # top loop: must equal Exp2's p
    pick = interesting(df)
    pick["cycle"] = [cycles[i][k - 1].tolist() for i, k in zip(pick["id"], pick["k"])]
    # Residues: on a short cycle several of the network's Fourier frequencies (exp7 audit) can give winding +-1.
    freqs = [int(f) for f in read_json(config.path("results") / "exp7_audit" / "summary.json")["grok_fourier"]
             ["top_frequencies"][:5]]
    res = np.array([int(s) for s in realdata.cloud("R2_grokking_WE")["labels"]])
    grok = {f"loop {k}": {str(f): winding(2 * np.pi * f * res[np.array(c)] / 113) for f in freqs}
            for i, k, c in zip(pick["id"], pick["k"], pick["cycle"]) if i == "R2_grokking_WE"}
    write_json(out / "summary.json", {
        "rules": {"significant": "p < 0.05", "large": f"top {LARGE_N} by death - birth",
                  "goes_around_once": f"cyclic concept clouds, concept winding = +-1 along the cycle, extent >= {SHAPE}, "
                                      f"best p per cloud, p < {AROUND_P}"},
        "n_loops": int(len(df)), "n_clouds": int(df["id"].nunique()), "n_clouds_total": len(source.dataset_ids()),
        "n_significant": int((df["p"] < 0.05).sum()), "max_abs_p_gap_vs_exp2": gap,
        "grok_winding_by_frequency": grok, "interesting": pick.to_dict(orient="records")})
    log.info("%d loops in %d clouds; %d interesting (%s); top-loop p vs Exp2: max gap %.2g", len(df), df["id"].nunique(),
             len(pick), ", ".join(f"{i}#{k}" for i, k in zip(pick["id"], pick["k"])), gap)
