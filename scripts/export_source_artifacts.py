"""Maintainer-only: export the source project's local-only artefacts for the Hugging Face dataset.

Global context: the topology pipeline must be reproducible from GitHub + Hugging Face alone. Four inputs
of the source project (shape-fitting, commit 4c5f3b6) exist only on the machine that produced them:
- raw activation matrices `data_cache/real/*.npz` (needed for null models and top-k-PC checks);
- the cached synthetic test set (39,000 clouds) and validation set (1,560 clouds);
- the source fitter's per-cloud predictions `results/main_s0/synth/per_sample.csv` (+ probs.npz, meta.json);
- the ground-truth *parameters* of every synthetic cloud, which the cache does not store. They are
  regenerated here with the source's own generator on CUDA, which reproduces the cached clouds bit-exactly
  (verified below: max |x_regenerated - x_cached| is recorded in the manifest).
Run it with the SOURCE project's interpreter (it needs torch and the source package):

    <source>/.venv/Scripts/python.exe -I scripts/export_source_artifacts.py --source-dir <source> --out data/source

Outputs go to --out (gitignored); `run.py publish-inputs` uploads them with a SHA-256 manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    """SHA-256 of a file, streamed in 1 MiB blocks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def jsonable(v):
    """Convert tensors / numpy scalars inside describe() output to plain JSON types."""
    if hasattr(v, "tolist"):
        return v.tolist()
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v


def export_cells(cells: list, out: Path, name: str) -> dict:
    """Write one ragged npz with every cloud's valid points and valid dense ground-truth samples."""
    pts, offs, gts, goffs = [], [0], [], [0]
    meta = {k: [] for k in ("family", "sigma", "n", "embed_dim", "n_bin", "noise_bin", "idx")}
    for cell in cells:
        b = cell["x"].shape[0]
        for i in range(b):
            m = cell["mask"][i].numpy().astype(bool)
            pts.append(cell["x"][i].numpy()[m])
            offs.append(offs[-1] + int(m.sum()))
            w = cell["gt_w"][i].numpy() > 0                     # padding of the dense GT has weight 0
            gts.append(cell["gt_dense"][i].numpy()[w])
            goffs.append(goffs[-1] + int(w.sum()))
            meta["family"].append(int(cell["family"][i]))
            meta["sigma"].append(float(cell["sigma"][i]))
            meta["n"].append(int(cell["n"][i]))
            meta["embed_dim"].append(int(cell["embed_dim"][i]))
            meta["n_bin"].append(int(cell["n_bin"]))
            meta["noise_bin"].append(int(cell["noise_bin"]))
            meta["idx"].append(i)
    path = out / f"{name}_cells.npz"
    np.savez_compressed(path, points=np.concatenate(pts).astype(np.float32), offsets=np.array(offs),
                        gt_points=np.concatenate(gts).astype(np.float32), gt_offsets=np.array(goffs),
                        **{k: np.array(v) for k, v in meta.items()})
    return {"clouds": len(meta["family"])}


def regenerate_params(cfg: dict, stream: str, per_cell: int, cells: list, out: Path, name: str) -> dict:
    """Re-run the source's build_test_set loop (testsets.py) with the same seed stream on CUDA, keep the
    ground-truth parameters (describe() + raw scalars) and check the regenerated clouds equal the cache."""
    import torch
    from neurogeom.data.nuisance import log_uniform
    from neurogeom.data.synth import generate_family
    from neurogeom.data.testsets import CHUNK
    from neurogeom.seeding import make_generator, stream_seed
    from neurogeom.shapes.registry import FAMILIES

    device = "cuda"
    gen = make_generator(stream_seed(cfg.get("data_seed", 0), stream), device)
    rows, max_diff, ci = [], 0.0, 0
    for bi, (lo, hi) in enumerate(cfg["eval"]["n_bins"]):
        for si, (slo, shi) in enumerate(cfg["eval"]["noise_bins"]):
            cell = cells[ci]
            ci += 1
            j = 0                                                   # running index inside the cached cell
            for fi, f in enumerate(FAMILIES):
                left = per_cell
                while left > 0:
                    c = min(CHUNK, left)
                    left -= c
                    n = int(round(float(log_uniform(1, lo, hi, gen, device))))
                    sigma = log_uniform(c, slo, shi, gen, device)
                    d = generate_family(fi, c, n, cfg["synth"], cfg["dense"], gen, device, sigma=sigma)
                    x_new = d["x"].cpu()
                    x_old = cell["x"][j:j + c, :n]
                    max_diff = max(max_diff, float((x_new - x_old).abs().max()))
                    gt = d["gt"]
                    # describe() expects canonical parameters (it is applied to canonicalised fits in the source,
                    # e.g. the polytope's vertex list is filled in by canonicalize); canonicalising only picks a
                    # representative of the shape's symmetry class, so the shape itself is unchanged.
                    gt_c = f.canonicalize(gt)
                    for i in range(c):
                        raw = {k: float(v[i]) for k, v in gt.items() if torch.is_tensor(v) and v.dim() == 1
                               and v.shape[0] == c and v.dtype.is_floating_point}
                        rows.append({"family": f.name, "describe": jsonable(f.describe(gt_c, i)), "raw": raw,
                                     "n_bin": bi, "noise_bin": si, "idx": j + i})
                    j += c
    path = out / f"{name}_gt_params.jsonl"
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return {"clouds": len(rows), "max_abs_diff_vs_cache": max_diff}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, help="source project folder that contains data_cache/")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    src = Path(args.source_dir).resolve()
    out = Path(args.out).resolve()
    (out / "real").mkdir(parents=True, exist_ok=True)
    (out / "synth").mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(src / "src"))
    import torch
    from neurogeom.config import load_config

    t0 = time.time()
    cfg = load_config("main.yaml")
    commit = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    summary = {"source_commit": commit, "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "command": "python -I scripts/export_source_artifacts.py --source-dir <source> --out data/source"}

    # 1. Raw activations (44 datasets) and the extraction status file, copied byte for byte.
    for f in sorted((src / "data_cache" / "real").glob("*.npz")) + [src / "data_cache" / "real" / "extract_status.json"]:
        shutil.copy2(f, out / "real" / f.name)
    print(f"[{time.strftime('%H:%M:%S')}] copied raw activations", flush=True)

    # 2. Fitter predictions on the synthetic test set (+ calibrated probabilities, temperature).
    for f in ("per_sample.csv", "probs.npz", "meta.json"):
        shutil.copy2(src / "results" / "main_s0" / "synth" / f, out / "synth" / f)

    # 3. Cached synthetic clouds and regenerated ground-truth parameters (test: 250 per cell, val: 10).
    for name, stream, per_cell in (("test", "test", cfg["eval"]["test_per_cell"]), ("val", "val", cfg["eval"]["val_per_cell"])):
        cache = src / "data_cache" / f"testset_{stream}_dataseed{cfg.get('data_seed', 0)}_{per_cell}.pt"
        cells = torch.load(cache, weights_only=False)
        summary[f"{name}_cells"] = export_cells(cells, out / "synth", name)
        summary[f"{name}_params"] = regenerate_params(cfg, stream, per_cell, cells, out / "synth", name)
        print(f"[{time.strftime('%H:%M:%S')}] {name}: {summary[f'{name}_params']}", flush=True)

    # 4. Manifest with SHA-256 of every exported file.
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json")
    summary["files"] = {str(p.relative_to(out)).replace("\\", "/"): {"sha256": sha256(p), "bytes": p.stat().st_size}
                        for p in files}
    summary["seconds"] = round(time.time() - t0, 1)
    with open(out / "manifest.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    print(f"[{time.strftime('%H:%M:%S')}] wrote {len(files)} files + manifest.json in {summary['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
