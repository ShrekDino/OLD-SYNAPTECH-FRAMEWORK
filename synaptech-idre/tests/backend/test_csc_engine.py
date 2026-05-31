import numpy as np
import pytest
from src.backend.services.csc_engine import CSCEngine

try:
    import cupy as cp  # noqa: F401
    _HAS_CUPY = True
except ImportError:
    _HAS_CUPY = False


@pytest.fixture
def engine():
    e = CSCEngine(shape=(100, 100))
    if _HAS_CUPY:
        import cupy as cp
        xp = cp
    else:
        xp = np
    rows = xp.random.randint(0, 100, size=500).astype(xp.int32)
    cols = xp.random.randint(0, 100, size=500).astype(xp.int32)
    data = xp.random.rand(500).astype(xp.float32)
    e.load_from_coo(data, rows, cols)
    return e


@pytest.mark.skipif(not _HAS_CUPY, reason="CuPy not available")
def test_activate(engine):
    import cupy as cp
    x = cp.random.rand(100).astype(cp.float32)
    y, spikes = engine.activate(x, threshold=0.5)
    assert y.shape == (100,)
    assert spikes >= 0
    assert spikes <= 100


@pytest.mark.skipif(not _HAS_CUPY, reason="CuPy not available")
def test_subgraph(engine):
    sub, ids = engine.subgraph([0, 1, 2, 3, 4])
    assert len(sub) == 5
    assert len(sub[0]) == 5
    assert ids == [0, 1, 2, 3, 4]


@pytest.mark.skipif(not _HAS_CUPY, reason="CuPy not available")
def test_not_loaded():
    import cupy as cp
    e = CSCEngine()
    with pytest.raises(RuntimeError, match="CSC matrix not loaded"):
        e.activate(cp.zeros(100))


@pytest.mark.skipif(not _HAS_CUPY, reason="CuPy not available")
def test_wrong_shape(engine):
    import cupy as cp
    with pytest.raises(ValueError, match="does not match"):
        engine.activate(cp.zeros(50))
