"""Resume the deterministic per-cloud calculations after a native worker or OS interruption.

The full benchmark still evaluates every requested row. A batch becomes visible only after all its
workers return. Joblib documents reuse of worker pools and n_jobs at https://joblib.readthedocs.io/en/stable/parallel.html.
"""
import gzip
import hashlib
import json
import logging
import os
from pathlib import Path
import tempfile

from joblib import Parallel, cpu_count

from neurotopo import config

log = logging.getLogger(__name__)


def worker_count():
    """Limit simultaneous native persistence calculations on memory-constrained machines."""
    return min(4, cpu_count())


def checkpoint_folder(tuning):
    """Fingerprint measurements by inputs, parameters, implementation and locked library versions."""
    root = config.ROOT
    state = hashlib.sha256(json.dumps(tuning, sort_keys=True).encode())
    sources = root/"src/neurotopo"
    for p in (config.path("inputs")/"manifest.json", root/"configs/base.yaml", root/"uv.lock",
              Path(__file__), sources/"experiments/exp1_synthetic.py", sources/"data/synthetic.py",
              sources/"geometry/pca.py", *sorted((sources/"tda").glob("*.py"))):
        state.update(hashlib.sha256(p.read_bytes()).digest())
    return root/"data/replay/exp1"/state.hexdigest()


def measured_rows(folder, phase, indices, task, batch_size, workers=None):
    """Accumulate ordered rows; reuse only complete JSON batches with the same sample indices."""
    folder = folder/phase
    folder.mkdir(parents=True,exist_ok=True)
    records = []
    with Parallel(n_jobs=workers or worker_count(),batch_size="auto") as pool:
        for start in range(0,len(indices),batch_size):
            ids = [int(i) for i in indices[start:start+batch_size]]
            target = folder/f"{start:06d}.json.gz"
            if target.is_file():
                with gzip.open(target,"rt",encoding="utf-8") as handle:
                    content = json.load(handle)
                if content["ids"]!=ids or len(content["rows"])!=len(ids):
                    raise ValueError(f"{target}: checkpoint indices or length differ")
                rows = content["rows"]
            else:
                rows = pool(task(i) for i in ids)
                with tempfile.NamedTemporaryFile(dir=folder,suffix=".partial",delete=False) as raw:
                    temporary = Path(raw.name)
                try:
                    with gzip.open(temporary,"wt",encoding="utf-8",compresslevel=2) as handle:
                        json.dump({"ids":ids,"rows":rows},handle,separators=(",",":"),allow_nan=False)
                    os.replace(temporary,target)
                finally:
                    temporary.unlink(missing_ok=True)
            records.extend(rows)
            log.info("Exp1 %s: %d/%d clouds",phase,len(records),len(indices))
    return records
