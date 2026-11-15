"""Shared helpers for experiment phases: results folders, JSON with numpy types, environment record.

Global context: every experiment writes machine-readable results to results/<exp>/ (read later by
`run.py report`, which generates every table, figure and number in README, reports and paper), plus an
env.json recording package versions and the git commits, for reproducibility.
"""

from __future__ import annotations

import json
import platform
import subprocess
from importlib.metadata import version
from pathlib import Path

import numpy as np

from neurotopo import config


def out_dir(exp: str) -> Path:
    """results/<exp>/, created on demand."""
    p = config.path("results") / exp
    p.mkdir(parents=True, exist_ok=True)
    return p


def _default(o):
    """JSON encoder fallback for numpy scalars/arrays; non-finite floats become strings."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return _finite(float(o))
    if isinstance(o, np.ndarray):
        return [_default(x) if not isinstance(x, (list, dict)) else x for x in o.tolist()]
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


def _finite(x: float):
    return x if np.isfinite(x) else ("inf" if x > 0 else "-inf" if x < 0 else "nan")


def _clean(o):
    """Recursively replace non-finite floats (JSON has no inf/nan) and numpy types."""
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float):
        return _finite(o)
    if isinstance(o, (np.floating, np.integer, np.bool_, np.ndarray)):
        return _clean(_default(o))
    return o


def write_json(path: Path, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_clean(obj), f, indent=1)


def read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def env_record(exp: str) -> None:
    """results/<exp>/env.json: python, platform, key package versions, this repo's and the submodule's commits."""
    def git(*args):
        return subprocess.run(["git", "-C", str(config.ROOT), *args], capture_output=True, text=True).stdout.strip()
    pk = {p: version(p) for p in ("numpy", "scipy", "scikit-learn", "gudhi", "ripser", "persim", "dreimac", "pandas")}
    write_json(out_dir(exp) / "env.json", {"python": platform.python_version(), "platform": platform.platform(),
                                           "packages": pk, "commit": git("rev-parse", "HEAD"),
                                           "dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
                                           "submodule": git("-C", "external/shape-fitting", "rev-parse", "HEAD"),
                                           "hf_revision": config.load()["hf"]["revision"]})
