"""Hugging Face Hub I/O: fetch the pipeline inputs (pinned revision, SHA-256 checked) and publish them.

Global context: the analysis must be reproducible by anyone with GitHub + Hugging Face access only
(reports/plan.md, "Reproducibility"). The source project's local-only artefacts (raw activations, cached
synthetic clouds, regenerated ground-truth parameters, fitter predictions) are exported once by
scripts/export_source_artifacts.py and uploaded to the dataset repo under `inputs/`; `run.py fetch`
downloads exactly that revision and verifies every file against the manifest's SHA-256.
API: huggingface_hub HfApi.upload_folder / snapshot_download
(https://huggingface.co/docs/huggingface_hub/guides/upload, .../guides/download).
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

from neurotopo import config

log = logging.getLogger(__name__)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify(folder: Path) -> int:
    """Check every file listed in folder/manifest.json against its SHA-256; returns the number checked."""
    with open(folder / "manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    bad = [name for name, meta in manifest["files"].items() if _sha256(folder / name) != meta["sha256"]]
    if bad:
        raise RuntimeError(f"SHA-256 mismatch for {len(bad)} input files, e.g. {bad[:3]}")
    return len(manifest["files"])


def fetch() -> Path:
    """Download inputs/ of the pinned dataset revision into paths.inputs and verify the hashes."""
    cfg = config.load()
    target = config.path("inputs")                          # data/hf/inputs
    if (target / "manifest.json").exists():
        try:
            n = verify(target)
            log.info("inputs already present and verified (%d files) in %s", n, target)
            return target
        except (RuntimeError, FileNotFoundError) as exc:
            log.warning("re-downloading inputs: %s", exc)
    snapshot_download(repo_id=cfg["hf"]["dataset"], repo_type="dataset", revision=cfg["hf"]["revision"],
                      allow_patterns=["inputs/*", "inputs/**/*"], local_dir=str(target.parent))
    n = verify(target)
    log.info("fetched and verified %d input files from %s@%s", n, cfg["hf"]["dataset"], cfg["hf"]["revision"])
    return target


DATASET_CARD = """---
license: mit
tags:
- interpretability
- topological-data-analysis
- persistent-homology
- neural-geometry
pretty_name: Topology of neural geometry - inputs and results
---

# Topology of neural geometry: inputs and results

Data for [topology-of-neural-geometry-in-llm-mechanistic-interpretability](https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability):
exact topology of fitted shapes and persistent homology of top-3-PCA activation clouds, and a test of whether
semantically cyclic concepts (weekdays, months, residues mod 113) travel around a hole.

## `inputs/` (exported once from the source project, commit `{commit}`)

Source project: [shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability](https://github.com/BurnyCoder/shape-fitting-in-neural-geometry-in-llm-mechanistic-interpretability)
([model](https://huggingface.co/BurnyCoder/neurogeom-shape-fitter-main-s0)). Exported with
`scripts/export_source_artifacts.py`; every file's SHA-256 is in `inputs/manifest.json`.

- `real/<id>.npz`: raw activation (or weight) matrices `X` (N x D), `labels`, `meta` (JSON) for the 44 datasets
  (GPT-2, Llama-3.1-8B, Pythia-410m, a grokked modular-addition transformer, toy models of superposition,
  random-init and ordinal-process controls).
- `synth/test_cells.npz`, `synth/val_cells.npz`: the source's fixed synthetic test set (39,000 clouds) and
  validation stream (1,560 clouds), ragged (`points`, `offsets`, dense ground truth `gt_points`, `gt_offsets`,
  `family`, `sigma`, `n`, `embed_dim`, `n_bin`, `noise_bin`, `idx`).
- `synth/*_gt_params.jsonl`: ground-truth shape parameters per synthetic cloud (source `describe()` format,
  normalised frame), regenerated on CUDA with the source generator; the regenerated clouds equal the cached
  ones exactly (max |difference| = {diff}).
- `synth/per_sample.csv`, `synth/probs.npz`, `synth/meta.json`: the source fitter's predictions per test cloud.

## Licences

Code of both projects: MIT. Activations derived from Llama-3.1-8B are subject to the
[Llama 3.1 Community License](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE);
GPT-2 (MIT), Pythia (Apache-2.0).
"""


def publish_inputs(staging: Path) -> str:
    """Upload a staged export folder to inputs/ of the dataset repo; returns the new commit SHA."""
    cfg = config.load()
    repo = cfg["hf"]["dataset"]
    api = HfApi()
    api.create_repo(repo, repo_type="dataset", private=False, exist_ok=True)
    with open(staging / "manifest.json", encoding="utf-8") as f:
        man = json.load(f)
    card = DATASET_CARD.format(commit=man["source_commit"][:7], diff=man["test_params"]["max_abs_diff_vs_cache"])
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md", repo_id=repo, repo_type="dataset",
                    commit_message="Dataset card")
    info = api.upload_folder(folder_path=str(staging), path_in_repo="inputs", repo_id=repo, repo_type="dataset",
                             commit_message=f"Inputs exported from shape-fitting {man['source_commit'][:7]}")
    try:
        api.add_collection_item(cfg["hf"]["collection"], item_id=repo, item_type="dataset", exists_ok=True)
    except Exception as exc:                                  # the collection may be missing or renamed
        log.warning("could not add %s to collection %s: %s", repo, cfg["hf"]["collection"], exc)
    log.info("uploaded inputs to %s at commit %s", repo, info.oid)
    return info.oid
