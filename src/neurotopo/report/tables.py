"""Markdown table helpers and generated report fragments (every number is read from results/).

Global context: README, reports and paper only contain numbers that a script wrote from results files
(`run.py report`). This module formats tables and writes fragments to reports/generated/*.md.
"""

from __future__ import annotations

import math

import pandas as pd

from neurotopo import config


def fmt(v, nd: int = 3) -> str:
    """Compact number formatting for tables (inf/nan as text, small p-values in scientific notation)."""
    if isinstance(v, str) or v is None:
        return "-" if v is None else v
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if math.isnan(v):
            return "-"
        if math.isinf(v):
            return "inf"
        if v != 0 and abs(v) < 10 ** -nd and nd >= 3:     # small p-values: scientific notation
            return f"{v:.1e}"
        return f"{v:.{nd}f}"
    return str(v)


def md_table(df: pd.DataFrame, nd: int = 3) -> str:
    """DataFrame -> GitHub markdown table."""
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(fmt(r[c], nd) for c in cols) + " |")
    return "\n".join(lines)


def write_generated(name: str, text: str) -> None:
    p = config.ROOT / "reports" / "generated"
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{name}.md").write_text(text.strip() + "\n", encoding="utf-8", newline=chr(10))


def addendum() -> str:
    """Preregistration addendum A1 values: validation-tuned rules and the power simulation summary."""
    from neurotopo.experiments.common import read_json
    res = config.path("results")
    t = read_json(res / "power" / "val_tuning.json")
    so = pd.DataFrame(read_json(res / "power" / "real_second_order.json"))
    ps = pd.read_csv(res / "power" / "power_summary.csv")
    ps = ps.rename(columns={"fb": "between fraction", "loop": "(a) loop", "align": "(b) align p<0.05/6",
                            "wind1": "(c) |w|=1", "all": "(a)-(c)"})
    txt = [
        "Validation-tuned values (validation stream only, 1,560 clouds; results/power/val_tuning.json):",
        "",
        f"- b0 rule: tau = {fmt(t['b0_tau'], 1)}, min_frac = {fmt(t['b0_minfrac'], 2)} "
        f"(exact-b0 accuracy on {t['n_val_resolvable']} resolvable validation clouds: {fmt(t['b0_val_accuracy'])}).",
        f"- Fixed-pi baseline: pi0_1 = {fmt(t['pi0_1'], 1)}, pi0_2 = {fmt(t['pi0_2'], 1)} "
        f"(validation macro exact accuracy {fmt(t['pi_val_macro_accuracy'])}).",
        "- Family-implied baseline map (family -> modal exact Betti vector): "
        + ", ".join(f"{k} {tuple(v)}" for k, v in t["family_map"].items()) + ".",
        "",
        "Second-order statistics of the real sets used to place the simulation grid (no topology computed):",
        "",
        md_table(so),
        "",
        "Power / false-positive rates of H1-B conditions (a)-(c) (40 replicates per cell, M = 199 null draws; "
        "results/power/power_summary.csv):",
        "",
        md_table(ps),
    ]
    return "\n".join(txt)
