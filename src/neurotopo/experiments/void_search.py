"""`run.py voids`: every void of every cloud, scored, and the interesting ones picked by fixed rules (post hoc).

Global context: Exp2 tests only each cloud's most persistent void (H2 bar) against the design-matched Monte Carlo null.
This phase lists all voids of the 44 alpha complexes (diagrams.alpha_h2_voids: bar, representative shell, centre)
and scores each for significance, size, shape and meaning, so the README's void figures can show the interesting ones
by rule rather than by eye. It was written after browsing the explorer, so the rules are post hoc (deviation D10):

- **significant:** p < 0.05, where p = (1 + #{null clouds whose largest void pi >= this void's pi}) / (M + 1)
  against the cloud's own null (realdata.null, the Exp2 null). For the top void this is Exp2's p; for any other void it
  is conservative (compared with the null's largest void). By chance, 5% of clouds have such a void.
- **large:** among the LARGE_N largest empty middles (death - birth: the radius of the ball around the void's centre
  that is still uncovered when the void closes) of all clouds.
- **shape and meaning:** in a trained model's concept cloud (ids R*, not the R3 toy models), a shell whose corners span
  at least SHAPE of the cloud (bounding-box diagonal ratio) and cover at least MEANING of its concepts
  (source.concepts); the most significant such void per cloud, kept if p < SHAPE_P.

Outputs: results/voids/all_voids.csv (one row per void), results/voids/summary.json (rules, counts, the interesting
voids with their reasons) and env.json. No model inference: stored clouds and stored nulls only.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from neurotopo import config
from neurotopo.data import source
from neurotopo.experiments import realdata
from neurotopo.experiments.common import env_record, out_dir, write_json
from neurotopo.tda import diagrams

log = logging.getLogger(__name__)
LARGE_N, SHAPE, MEANING, SHAPE_P = 5, 0.5, 0.5, 0.5


def mc_p(null: np.ndarray, pi: float) -> float:
    """Monte Carlo p of one bar's persistence ratio pi against a null of the largest pi per null cloud:
    (1 + #{null >= pi}) / (M + 1). Shared with experiments/loop_search.py."""
    return float((1 + np.sum(null >= pi)) / (len(null) + 1))


def cloud_voids(d: str, seed: int) -> pd.DataFrame:
    """One row per void of cloud d, ranked by pi (k = 1 is the most persistent; stable sort, as examples.replay)."""
    c = realdata.cloud(d)
    y = c["y"]
    bars, shells, centres = diagrams.alpha_h2_voids(y)
    if not len(bars):
        return pd.DataFrame()
    pi = bars[:, 1] / bars[:, 0]
    null = realdata.null(d, seed)[:, 1]                                 # largest void pi in each of the M null clouds
    try:
        con = source.concepts(d, c["labels"])
        idx, n_con = con.index, len(con.names)
    except ValueError:                                                  # no concept structure (none of the 44 today)
        idx, n_con = None, 0
    diag = np.linalg.norm(np.ptp(y, axis=0))
    rows = []
    for rank, i in enumerate(np.argsort(-pi, kind="stable"), start=1):
        v = np.unique(shells[i])                                        # the shell's corners
        rows.append({"id": d, "N": len(y), "k": rank, "birth": bars[i, 0], "death": bars[i, 1],
                     "empty": bars[i, 1] - bars[i, 0], "pi": pi[i],
                     "p": mc_p(null, pi[i]),
                     "faces": len(shells[i]), "corners": len(v), "extent": np.linalg.norm(np.ptp(y[v], axis=0)) / diag,
                     "shell_concepts": len(np.unique(idx[v])) if idx is not None else 0, "n_concepts": n_con,
                     "cx": centres[i, 0], "cy": centres[i, 1], "cz": centres[i, 2]})
    return pd.DataFrame(rows)


def interesting(df: pd.DataFrame) -> pd.DataFrame:
    """The voids picked by the three rules (module docstring), one row each, with the rules that picked it."""
    reasons: dict[tuple[str, int], list[str]] = {}
    for _, r in df[df["p"] < 0.05].iterrows():
        reasons.setdefault((r["id"], r["k"]), []).append("significant")
    for _, r in df.nlargest(LARGE_N, "empty").iterrows():
        reasons.setdefault((r["id"], r["k"]), []).append("large")
    trained = df["id"].str.startswith("R") & ~df["id"].str.startswith("R3_")
    sm = df[trained & (df["extent"] >= SHAPE) & (df["shell_concepts"] >= MEANING * df["n_concepts"])]
    for _, r in sm.sort_values(["p", "k"]).groupby("id").head(1).iterrows():
        if r["p"] < SHAPE_P:
            reasons.setdefault((r["id"], r["k"]), []).append("shape and meaning")
    out = df.set_index(["id", "k"]).loc[list(reasons)].reset_index()
    out["reasons"] = [", ".join(reasons[(i, k)]) for i, k in zip(out["id"], out["k"])]
    return out.sort_values(["p", "empty"], ascending=[True, False]).reset_index(drop=True)


def run() -> None:
    seed = config.load()["seed"]
    out = out_dir("voids")
    env_record("voids")
    df = pd.concat([cloud_voids(d, seed) for d in source.dataset_ids()], ignore_index=True)
    df.to_csv(out / "all_voids.csv", index=False)
    inv = pd.read_csv(config.path("results") / "exp2" / "invariants.csv").set_index("id")
    top = df[df["k"] == 1].set_index("id")
    gap = float(np.abs(top["p"] - inv.loc[top.index, "p_top_void"]).max())   # top void: must equal Exp2's p
    pick = interesting(df)
    write_json(out / "summary.json", {
        "rules": {"significant": "p < 0.05", "large": f"top {LARGE_N} by death - birth",
                  "shape_and_meaning": f"trained concept clouds, extent >= {SHAPE}, concepts >= {MEANING}, "
                                       f"best p per cloud, p < {SHAPE_P}"},
        "n_voids": int(len(df)), "n_clouds": int(df["id"].nunique()), "n_clouds_total": len(source.dataset_ids()),
        "n_significant": int((df["p"] < 0.05).sum()), "max_abs_p_gap_vs_exp2": gap,
        "interesting": pick.to_dict(orient="records")})
    log.info("%d voids in %d clouds; %d interesting (%s); top-void p vs Exp2: max gap %.2g", len(df), df["id"].nunique(),
             len(pick), ", ".join(f"{i}#{k}" for i, k in zip(pick["id"], pick["k"])), gap)
