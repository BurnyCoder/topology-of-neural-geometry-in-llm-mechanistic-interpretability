"""Entry point: run the pipeline phases in order (`uv run python run.py <phase> [<phase> ...]`).

Global context: each phase is one imported function from `neurotopo`; this file only wires them together.
`all` = fetch -> exp0 -> coords -> power -> power2 -> exp1 -> exp1outliers -> exp2 -> exp3 -> exp3posthoc -> exp4
-> exp5 -> report -> site, needs no GPU and no local files beyond the GitHub clone (inputs come from the pinned
Hugging Face dataset revision). exp6sim / exp6 (steering) are postponed and not part of `all`.
`publish-inputs` is maintainer-only (uploads the export of scripts/export_source_artifacts.py).
"""

from __future__ import annotations

import argparse
import importlib
from pathlib import Path

from neurotopo import config, log

# phase name -> (module, function); modules are imported lazily so `fetch` works before anything else.
PHASES = {
    "fetch": ("neurotopo.data.hub", "fetch"),
    "exp0": ("neurotopo.experiments.exp0_analytic", "run"),
    "coords": ("neurotopo.experiments.coords_check", "run"),
    "power": ("neurotopo.experiments.power", "run"),
    "power2": ("neurotopo.experiments.power", "run_v2"),
    "exp1": ("neurotopo.experiments.exp1_synthetic", "run"),
    "exp1outliers": ("neurotopo.experiments.exp1_synthetic", "outlier_check"),
    "exp2": ("neurotopo.experiments.exp2_invariants", "run"),
    "exp3": ("neurotopo.experiments.exp3_cyclic", "run"),
    "exp3posthoc": ("neurotopo.experiments.exp3_posthoc", "run"),
    "exp4": ("neurotopo.experiments.exp4_similarity", "run"),
    "exp5": ("neurotopo.experiments.exp5_robustness", "run"),
    "exp6sim": ("neurotopo.experiments.exp6_sim", "run"),
    "exp6": ("neurotopo.experiments.exp6_steering", "run"),
    "report": ("neurotopo.report.build", "run"),
    "site": ("neurotopo.report.site", "run"),
    "publish": ("neurotopo.report.publish", "run"),
}
ALL = ["fetch", "exp0", "coords", "power", "power2", "exp1", "exp1outliers", "exp2", "exp3", "exp3posthoc", "exp4", "exp5", "report", "site"]   # exp6sim / exp6: postponed


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phases", nargs="+", help=f"phases: {', '.join(PHASES)}, all, publish-inputs")
    ap.add_argument("--staging", default="data/source", help="export folder for publish-inputs")
    args = ap.parse_args(argv)
    phases = [p for ph in args.phases for p in (ALL if ph == "all" else [ph])]
    for ph in phases:
        log.setup(ph)
        if ph == "publish-inputs":
            from neurotopo.data.hub import publish_inputs
            sha = publish_inputs(config.ROOT / Path(args.staging))
            print(f"uploaded inputs; set hf.revision: {sha} in configs/base.yaml")
            continue
        module, fn = PHASES[ph]
        getattr(importlib.import_module(module), fn)()


if __name__ == "__main__":
    main()
