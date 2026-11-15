"""Compare two results/ folders file by file (clean-room replication check).

Global context: the replication test clones the repository, moves the committed results/ aside, runs
`run.py all` from scratch (inputs from Hugging Face only) and compares the new results/ with the committed ones.
JSON and CSV files are compared numerically (relative tolerance 1e-6, absolute 1e-9); env.json files, which
record machine and commit details, are skipped. Usage:

    uv run python scripts/compare_results.py results_committed results [results/replication.json]
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

RTOL, ATOL = 1e-6, 1e-9


def same(a, b, path="") -> list[str]:
    """Recursive comparison of JSON values; returns a list of differing paths."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = [f"{path}/{k}: missing" for k in set(a) ^ set(b)]
        for k in set(a) & set(b):
            out += same(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in same(x, y, f"{path}[{i}]")]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if math.isclose(float(a), float(b), rel_tol=RTOL, abs_tol=ATOL):
            return []
        return [f"{path}: {a} vs {b}"]
    return [] if a == b else [f"{path}: {a!r} vs {b!r}"]


def compare_csv(pa: Path, pb: Path) -> list[str]:
    a, b = pd.read_csv(pa, low_memory=False), pd.read_csv(pb, low_memory=False)
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return [f"shape/columns {a.shape} vs {b.shape}"]
    out = []
    for c in a.columns:
        x, y = a[c], b[c]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            ok = np.isclose(x.to_numpy(float), y.to_numpy(float), rtol=RTOL, atol=ATOL, equal_nan=True)
            if not ok.all():
                out.append(f"column {c}: {int((~ok).sum())} rows differ")
        elif not (x.fillna("").astype(str) == y.fillna("").astype(str)).all():   # missing == missing
            out.append(f"column {c}: text differs")
    return out


def main(a: str, b: str, out: str | None = None) -> int:
    ra, rb = Path(a), Path(b)
    files = sorted(p.relative_to(ra) for p in ra.rglob("*") if p.is_file() and p.name not in ("env.json", "replication.json"))
    bad = 0
    for rel in files:
        pa, pb = ra / rel, rb / rel
        if not pb.exists():
            print(f"MISSING {rel}")
            bad += 1
            continue
        if rel.suffix == ".json":
            diffs = same(json.loads(pa.read_text(encoding="utf-8")), json.loads(pb.read_text(encoding="utf-8")))
        elif rel.name.endswith(".json.gz"):          # gzip headers contain a timestamp: compare the content
            import gzip
            diffs = same(json.loads(gzip.open(pa).read()), json.loads(gzip.open(pb).read()))
        elif rel.suffix in (".csv", ".gz") and ".csv" in rel.name:
            diffs = compare_csv(pa, pb)
        elif rel.suffix in (".npy", ".npz"):
            za, zb = np.load(pa), np.load(pb)
            arrs = [(za, zb)] if rel.suffix == ".npy" else [(za[k], zb[k]) for k in za.files]
            diffs = [] if all(np.allclose(x, y, rtol=RTOL, atol=ATOL, equal_nan=True) for x, y in arrs) else ["arrays differ"]
        else:
            diffs = [] if pa.read_bytes() == pb.read_bytes() else ["bytes differ"]
        if diffs:
            bad += 1
            print(f"DIFF {rel}: {len(diffs)} differences, e.g. {diffs[:3]}")
    print(f"{len(files) - bad}/{len(files)} files identical within tolerance")
    if out:
        Path(out).write_text(json.dumps({"files": len(files), "identical": len(files) - bad, "rtol": RTOL, "atol": ATOL,
                                         "date": time.strftime("%Y-%m-%d")}, indent=1), encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
