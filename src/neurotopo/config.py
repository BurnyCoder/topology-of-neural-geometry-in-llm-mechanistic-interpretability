"""Configuration: repository root, YAML settings and .env overrides.

Global context: every phase of `run.py` reads its settings from `configs/base.yaml` (analysis parameters,
most of them fixed by the preregistration) and resolves paths relative to the repository root, so the
pipeline behaves identically on any machine that cloned the repository and ran `run.py fetch`.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]          # src/neurotopo/config.py -> repository root


@lru_cache(maxsize=1)
def load() -> dict:
    """Load configs/base.yaml once; environment variables from .env override the HF dataset name."""
    load_dotenv(ROOT / ".env")                      # optional; absent on a fresh clone, which is fine
    with open(ROOT / "configs" / "base.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["hf"]["dataset"] = os.environ.get("NEUROTOPO_HF_DATASET", cfg["hf"]["dataset"])
    return cfg


def path(key: str) -> Path:
    """Absolute path of a configured folder (paths.<key>), created on demand for outputs."""
    p = ROOT / load()["paths"][key]
    if key in ("results", "figures", "logs", "inputs"):
        p.mkdir(parents=True, exist_ok=True)
    return p


def source_run_dir() -> Path:
    """The source project's run folder inside the git submodule (viz JSON, real_results.json)."""
    cfg = load()
    return ROOT / cfg["paths"]["submodule"] / cfg["paths"]["source_run"]
