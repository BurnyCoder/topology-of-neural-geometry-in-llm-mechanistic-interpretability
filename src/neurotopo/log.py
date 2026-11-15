"""Timestamped logging to the terminal and to logs/<phase>_<timestamp>.log.

Global context: every `run.py` phase writes a full, timestamped log so each number in the reports can be
traced back to the run that produced it.
"""

from __future__ import annotations

import logging
import time

from neurotopo import config


def setup(phase: str) -> logging.Logger:
    """Configure the root logger once per phase: INFO to stderr and to a new timestamped file."""
    stamp = time.strftime("%Y%m%dT%H%M%S")
    path = config.path("logs") / f"{phase}_{stamp}.log"
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):
        root.removeHandler(h)
    for h in (logging.StreamHandler(), logging.FileHandler(path, encoding="utf-8")):
        h.setFormatter(fmt)
        root.addHandler(h)
    logging.getLogger("numba").setLevel(logging.WARNING)       # DREiMac's numba is very chatty at INFO
    root.info("phase %s, log file %s", phase, path)
    return root
