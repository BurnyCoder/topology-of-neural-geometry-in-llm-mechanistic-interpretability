"""An interrupted synthetic replay can resume without changing the order or the measurements."""
from joblib import delayed
import pytest


def test_resume_verifies_indices_and_recomputes_incomplete_shards(tmp_path):
    from neurotopo.experiments.exp1_batches import measured_rows
    calls = []
    def task(i):
        calls.append(i)
        if i==2 and calls.count(i)==1:
            raise RuntimeError("interrupted")
        return {"value":i*i}
    with pytest.raises(RuntimeError):
        measured_rows(tmp_path, "sample", [0,1,2], lambda i:delayed(task)(i), 2, workers=1)
    rows = measured_rows(tmp_path, "sample", [0,1,2], lambda i:delayed(task)(i), 2, workers=1)
    assert rows == [{"value":0},{"value":1},{"value":4}]
    assert calls == [0,1,2,2]
    with pytest.raises(ValueError,match="indices"):
        measured_rows(tmp_path, "sample", [1,0,2], lambda i:delayed(task)(i), 2, workers=1)
