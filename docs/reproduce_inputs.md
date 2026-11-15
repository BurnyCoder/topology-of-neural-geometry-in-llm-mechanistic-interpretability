# Reproducing the pipeline inputs from scratch

The normal route needs no GPU and no local files beyond a GitHub clone. `uv run python run.py fetch` downloads `inputs/` of the Hugging Face dataset [BurnyCoder/topology-of-neural-geometry](https://huggingface.co/datasets/BurnyCoder/topology-of-neural-geometry) at the revision pinned in `configs/base.yaml`, and checks every file against `inputs/manifest.json` (SHA-256).

This page explains how those inputs were produced, so they can be regenerated from public sources.

## What the inputs are

| File | Produced by | In the source repo's git? |
|---|---|---|
| `real/<id>.npz` (44 raw activation / weight matrices) | source `run.py extract-real` (GPT-2, Llama-3.1-8B in bf16, Pythia-410m, the grokking model, toy models) | no (`data_cache/` is gitignored) |
| `synth/test_cells.npz`, `synth/val_cells.npz` | source `build_test_set` (seed streams `test` and `val`, `data_seed` 0) | no |
| `synth/*_gt_params.jsonl` | `scripts/export_source_artifacts.py`, re-running the source generator on CUDA | no; regenerated |
| `synth/per_sample.csv`, `probs.npz`, `meta.json` | source `run.py eval-synth` with the checkpoint [BurnyCoder/neurogeom-shape-fitter-main-s0](https://huggingface.co/BurnyCoder/neurogeom-shape-fitter-main-s0) | no |
| viz JSON, `real_results.json` | source `run.py eval-real` | **yes** (read from the submodule) |

## Steps (needs an NVIDIA GPU and access to the gated meta-llama/Llama-3.1-8B)

```bash
git clone --recursive https://github.com/BurnyCoder/topology-of-neural-geometry-in-llm-mechanistic-interpretability.git
```

```bash
cd topology-of-neural-geometry-in-llm-mechanistic-interpretability/external/shape-fitting && uv sync
```

Download the source checkpoint into `checkpoints/main_s0/final.pt`:

```bash
uv run hf download BurnyCoder/neurogeom-shape-fitter-main-s0 final.pt --local-dir checkpoints/main_s0
```

Re-run the source phases that produce the inputs (several GPU hours; see the source README):

```bash
uv run python run.py extract-real eval-synth --config main.yaml
```

Export the inputs from the topology repository's root, using the source venv's interpreter:

```bash
cd ../.. && external/shape-fitting/.venv/Scripts/python.exe -I scripts/export_source_artifacts.py --source-dir external/shape-fitting --out data/source
```

**Expected results:**
- The regenerated synthetic clouds equal the cached ones bit for bit on CUDA. The manifest records `max_abs_diff_vs_cache = 0.0` for the 39,000 test and 1,560 validation clouds.
- The CPU random generator differs from the CUDA one, so regeneration must run on CUDA.
- Raw activations re-extracted on other hardware can differ in the last bits (bf16 kernels). Compare them with the published files by value, not by hash.
