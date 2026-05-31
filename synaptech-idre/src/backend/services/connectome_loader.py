import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.backend.config import settings as global_settings
from src.backend.services.csc_engine import _HAS_CUPY, CSCEngine

if _HAS_CUPY:
    import cupy as cp
else:
    cp = None

logger = logging.getLogger(__name__)


class ConnectomeLoader:

    SUPPORTED_FORMATS = {"csv", "json", "parquet"}

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            data_path = "/data/flywire"
        self.data_path = Path(data_path)

    def _discover_file(self) -> Optional[Path]:
        for ext in self.SUPPORTED_FORMATS:
            files = sorted(self.data_path.glob(f"*.{ext}"))
            for f in files:
                if f.name == "manifest.json":
                    continue
                return f
        return None

    def load_csv(self, path: Path):
        df = pd.read_csv(path)
        required = {"source", "target", "weight"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required}")
        rows = df["source"].values.astype(np.int32)
        cols = df["target"].values.astype(np.int32)
        data = df["weight"].values.astype(np.float32)
        return rows, cols, data

    def load_json(self, path: Path):
        with open(path) as f:
            edges = json.load(f)
        if isinstance(edges, dict):
            edges = edges.get("edges", edges.get("data", []))
        rows = np.array([e["source"] for e in edges], dtype=np.int32)
        cols = np.array([e["target"] for e in edges], dtype=np.int32)
        data = np.array([e.get("weight", 1.0) for e in edges], dtype=np.float32)
        return rows, cols, data

    def load_parquet(self, path: Path):
        df = pd.read_parquet(path)
        required = {"source", "target", "weight"}
        if not required.issubset(df.columns):
            raise ValueError(f"Parquet must contain columns: {required}")
        rows = df["source"].values.astype(np.int32)
        cols = df["target"].values.astype(np.int32)
        data = df["weight"].values.astype(np.float32)
        return rows, cols, data

    def load(self, path: Optional[Path] = None) -> None:
        file_path = path or self._discover_file()
        if file_path is None:
            raise FileNotFoundError(
                f"No connectome files in {self.data_dir()}. "
                f"Place a CSV/JSON/Parquet edge-list or run `python run.py --gen-data`."
            )

        ext = file_path.suffix.lstrip(".")
        logger.info(f"Loading connectome from {file_path}")

        loader = {
            "csv": self.load_csv,
            "json": self.load_json,
            "parquet": self.load_parquet,
        }.get(ext)
        if loader is None:
            raise ValueError(f"Unsupported format: {ext}")

        rows, cols, data = loader(file_path)
        logger.info(f"Loaded {len(data)} synapses from file")

        engine = CSCEngine.get_instance()

        if engine.on_gpu and cp is not None:
            rows_t = cp.asarray(rows)
            cols_t = cp.asarray(cols)
            data_t = cp.asarray(data)
        else:
            rows_t = rows
            cols_t = cols
            data_t = data

        engine.load_from_coo(data_t, rows_t, cols_t)

    def load_layout(self) -> Optional[list]:
        layout_path = self.data_path.parent / "layout.json"
        if not layout_path.exists():
            layout_path = (
                Path(__file__).resolve().parent.parent.parent.parent / "data" / "layout.json"
            )
        if not layout_path.exists():
            logger.warning(f"No layout file found at {layout_path}")
            return None
        with open(layout_path) as f:
            layout_data = json.load(f)
        positions = layout_data["positions"]
        engine = CSCEngine.get_instance()
        xp = engine.xp
        engine._layout_xp = xp.array(positions, dtype=xp.float32)
        return positions

    def data_dir(self) -> str:
        return str(self.data_path.resolve())

    def get_metadata(self) -> dict:
        engine = CSCEngine.get_instance()
        if not engine.is_loaded:
            return {"loaded": False}
        return {
            "loaded": True,
            "shape": list(engine.shape),
            "nonzeros": int(engine.matrix.nnz),
            "backend": "gpu" if engine.on_gpu else "cpu",
        }


def load_real_flywire(config=global_settings) -> Optional[dict]:
    """Load real FlyWire connectome data from feather files.

    Returns dict with keys (matrix, layout_positions, layout_shape, metadata)
    or None if real data is not available.
    """
    real_path = Path(config.flywire_real_connections)
    root_ids_path = Path(config.flywire_root_ids)
    positions_path = Path(config.flywire_positions)

    if not real_path.exists():
        logger.info("Real FlyWire data not found — will use synthetic fallback")
        logger.info(f"  (expected: {real_path})")
        logger.info("  Run: python3 scripts/fetch_flywire_data.py")
        return None

    logger.info("Loading real FlyWire connectome from feather...")

    try:
        root_ids = np.load(str(root_ids_path))
    except FileNotFoundError:
        logger.warning(f"root_ids.npy not found at {root_ids_path} — falling back")
        return None
    n = len(root_ids)
    logger.info(f"  Root IDs loaded: {n:,} proofread neurons")

    sorted_ids = np.sort(root_ids)

    try:
        import pyarrow.feather as feather
        table = feather.read_table(str(real_path))
    except Exception as e:
        logger.warning(f"Failed to read feather file: {e} — falling back")
        return None
    df = table.to_pandas()
    logger.info(f"  Connections loaded: {len(df):,} rows from feather")

    raw_sources = np.searchsorted(sorted_ids, df["pre_pt_root_id"].values)
    raw_targets = np.searchsorted(sorted_ids, df["post_pt_root_id"].values)
    if raw_sources.max() >= n or raw_sources.min() < 0:
        logger.warning("Source root ID mapping failed — falling back")
        return None
    if raw_targets.max() >= n or raw_targets.min() < 0:
        logger.warning("Target root ID mapping failed — falling back")
        return None
    sources = raw_sources.astype(np.int32)
    targets = raw_targets.astype(np.int32)
    weights = df["syn_count"].values.astype(np.float32)

    logger.info(f"  Building CSC matrix ({n}\u00d7{n}, {len(weights)} connections)...")
    from scipy.sparse import csc_matrix
    matrix = csc_matrix((weights, (sources, targets)), shape=(n, n))

    try:
        positions = np.load(str(positions_path)).astype(np.float64)
    except FileNotFoundError:
        logger.warning(f"positions.npy not found at {positions_path} — falling back")
        return None
    logger.info(f"  Positions loaded: {positions.shape}")

    metadata = {
        "total_neurons": n,
        "total_synapses": int(weights.sum()),
        "total_connections": len(weights),
        "source": "FlyWire v783 (CC BY 4.0)",
        "doi": "10.5281/zenodo.10676866",
    }

    return {
        "matrix": matrix,
        "layout_positions": positions.tolist(),
        "layout_shape": [n, 3],
        "metadata": metadata,
        "root_ids": root_ids,
    }
