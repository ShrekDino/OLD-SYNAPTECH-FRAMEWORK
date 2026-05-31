from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import scipy.sparse
    from numpy import ndarray
    from scipy.sparse import csc_matrix

logger = logging.getLogger(__name__)

_HAS_CUPY = False
try:
    import cupy as _cupy
    _HAS_CUPY = _cupy.cuda.is_available()
    if _HAS_CUPY:
        try:
            _cupy.cuda.runtime.memGetInfo()
            logger.info("CuPy detected — using GPU-accelerated sparse matrices")
        except Exception:
            _HAS_CUPY = False
            logger.warning(
                "CuPy installed but CUDA unavailable — falling back to CPU"
            )
    else:
        logger.warning(
            "No CUDA device found — falling back to CPU"
        )
except ImportError:
    logger.info("CuPy not found — falling back to CPU (SciPy + NumPy)")

if _HAS_CUPY:
    from cupyx.scipy.sparse import csc_matrix as _csc_cupy


def _get_array_module():
    if _HAS_CUPY:
        return _cupy
    import numpy
    return numpy


def _get_sparse_module():
    if _HAS_CUPY:
        import cupyx.scipy.sparse
        return cupyx.scipy.sparse
    import scipy.sparse
    return scipy.sparse


class CSCEngine:
    _instance: Optional["CSCEngine"] = None

    def __init__(self, shape: tuple[int, int] = (130_000, 130_000)):
        self.shape = shape
        self._matrix: Optional["csc_matrix"] = None
        self._layout_xp: Optional["ndarray"] = None
        self.xp = _get_array_module()
        self.sparse = _get_sparse_module()
        self._on_gpu = _HAS_CUPY

    @property
    def on_gpu(self) -> bool:
        return self._on_gpu

    @classmethod
    def get_instance(cls) -> "CSCEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_from_coo(self, data: "ndarray", rows: "ndarray", cols: "ndarray") -> None:
        xp = self.xp
        data = xp.asarray(data, dtype=xp.float32)
        rows = xp.asarray(rows, dtype=xp.int32)
        cols = xp.asarray(cols, dtype=xp.int32)

        if self._on_gpu:
            self._matrix = self.sparse.csc_matrix(
                (data, (rows, cols)), shape=self.shape, dtype=xp.float32
            )
        else:
            import scipy.sparse
            data_np = data  # already numpy if CPU
            rows_np = rows
            cols_np = cols
            self._matrix = scipy.sparse.csc_matrix(
                (data_np, (rows_np, cols_np)), shape=self.shape, dtype=xp.float32
            )

        loc = "GPU" if self._on_gpu else "CPU"
        logger.info(
            f"CSC matrix loaded on {loc}: {self._matrix.shape}, "
            f"{self._matrix.nnz} non-zeros, "
            f"density={self._matrix.nnz / (self.shape[0] * self.shape[1]):.8f}"
        )

    def load_from_scipy(self, sp_mat: "scipy.sparse.csc_matrix") -> None:
        self.shape = sp_mat.shape
        if self._on_gpu:
            data = _cupy.asarray(sp_mat.data)
            indices = _cupy.asarray(sp_mat.indices)
            indptr = _cupy.asarray(sp_mat.indptr)
            self._matrix = _csc_cupy(
                (data, indices, indptr), shape=sp_mat.shape
            )
        else:
            self._matrix = sp_mat
        logger.info(f"Matrix loaded from scipy: {self._matrix.shape}, {self._matrix.nnz} nnz")

    @property
    def matrix(self):
        if self._matrix is None:
            raise RuntimeError("CSC matrix not loaded. Call load_from_coo first.")
        return self._matrix

    @property
    def is_loaded(self) -> bool:
        return self._matrix is not None

    def activate(
        self, input_vector: "ndarray", threshold: float = 0.5,
        phenotype: Optional[str] = None,
    ) -> tuple["ndarray", int]:
        if self._matrix is None:
            raise RuntimeError("CSC matrix not loaded")
        xp = self.xp
        if hasattr(input_vector, 'shape') and input_vector.shape[0] != self.shape[0]:
            raise ValueError(
                f"Input vector length {input_vector.shape[0]} "
                f"does not match matrix dimension {self.shape[0]}"
            )
        vec = xp.asarray(input_vector, dtype=xp.float32)

        # Apply phenotypic modulation
        if phenotype:
            try:
                with open("/home/cinni/PitchDeck/SynapTech_IDRE/data/phenotype_map.json", "r") as f:
                    phenotypes = json.load(f)
                if phenotype in phenotypes:
                    mod = phenotypes[phenotype]
                    vec = vec * mod["dopamine_modulation"]
                    threshold += mod["threshold_offset"]
            except Exception as e:
                logger.error(f"Error applying phenotype {phenotype}: {e}")

        output = self._matrix @ vec
        if self._on_gpu:
            spike_count = int(xp.sum(output > threshold).get())
        else:
            spike_count = int(xp.sum(output > threshold))
        return output, spike_count

    def subgraph(self, neuron_ids: list[int]) -> tuple[list[list[float]], list[int]]:
        xp = self.xp
        ids = xp.array(neuron_ids, dtype=xp.int32)
        sub = self._matrix[ids, :][:, ids]
        if self._on_gpu:
            dense = sub.toarray().get()
        else:
            dense = sub.toarray()
        return dense.tolist(), neuron_ids

    def compute_layout(self, iterations: int = 50) -> "ndarray":
        if self._matrix is None:
            raise RuntimeError("CSC matrix not loaded")
        xp = self.xp

        n = self.shape[0]
        rng = xp.random.RandomState(42) if not self._on_gpu else xp.random
        positions = rng.randn(n, 3).astype(xp.float32)
        norms = xp.linalg.norm(positions, axis=1, keepdims=True) + 1e-8
        positions /= norms

        for i in range(iterations):
            coo = self._matrix.tocoo()
            row = xp.array(coo.row, dtype=xp.int32)
            col = xp.array(coo.col, dtype=xp.int32)

            diff = positions[row] - positions[col]
            dist = xp.linalg.norm(diff, axis=1, keepdims=True) + 1e-8
            attraction = -0.005 * diff / dist

            repulsion = xp.zeros_like(positions)
            sample_n = min(5000, n)
            if self._on_gpu:
                sample = xp.random.randint(0, n, size=sample_n)
            else:
                sample = xp.random.RandomState(i).randint(0, n, size=sample_n)
            dr = positions[sample].reshape(-1, 1, 3) - positions.reshape(1, -1, 3)
            dr_dist = xp.linalg.norm(dr, axis=2, keepdims=True) + 1e-8
            repulsion[sample] += xp.sum(0.05 * dr / dr_dist ** 2, axis=1)

            positions += attraction + repulsion
            n2 = xp.linalg.norm(positions, axis=1, keepdims=True) + 1e-8
            positions /= n2

            if i % 10 == 0:
                logger.info(f"Layout iteration {i}/{iterations}")

        self._layout_xp = positions
        logger.info(f"Layout computed: {positions.shape}")
        return positions

    def get_layout(self) -> Optional["ndarray"]:
        return self._layout_xp

    def layout_to_list(self) -> list[list[float]]:
        if self._layout_xp is None:
            return []
        if self._on_gpu:
            return self._layout_xp.get().tolist()
        return self._layout_xp.tolist()
