import logging
import os
import uuid
from typing import Optional

from src.backend.services.csc_engine import CSCEngine
from src.backend.services.lava_processes import FlyWireNetwork
from src.shared.schemas import CompileResponse, RunResponse

logger = logging.getLogger(__name__)

LAVA_AVAILABLE = False
try:
    from lava.magma.core.run_conditions import RunSteps
    from lava.magma.core.run_configs import Loihi1SimCfg, Loihi2HwCfg
    LAVA_AVAILABLE = True
except ImportError:
    logger.warning("Lava framework not installed. Neuromorphic features disabled.")


class LavaBridge:
    _instance: Optional["LavaBridge"] = None

    def __init__(self):
        self._networks: dict[str, FlyWireNetwork] = {}
        self._backend = os.environ.get("LAVA_BACKEND", "sim")
        self._inrc_enabled = os.environ.get("INRC_ENABLED", "").lower() == "true"

    @classmethod
    def get_instance(cls) -> "LavaBridge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def available(self) -> bool:
        return LAVA_AVAILABLE

    @property
    def backend(self) -> str:
        return self._backend

    def _build_run_config(self):
        if not LAVA_AVAILABLE:
            raise RuntimeError("Lava framework not installed")
        if self._backend == "loihi2" and self._inrc_enabled:
            return Loihi2HwCfg()
        return Loihi1SimCfg()

    def compile_subgraph(
        self, neuron_ids: list[int], backend: str = "sim"
    ) -> CompileResponse:
        engine = CSCEngine.get_instance()
        if not engine.is_loaded:
            raise RuntimeError("CSC matrix not loaded")

        sub_matrix = engine.matrix[neuron_ids, :][:, neuron_ids]
        weights = sub_matrix.tocoo()

        run_id = str(uuid.uuid4())
        network = FlyWireNetwork(
            neuron_ids=neuron_ids,
            weights_rows=weights.row.get(),
            weights_cols=weights.col.get(),
            weights_data=weights.data.get(),
            n_neurons=len(neuron_ids),
        )
        self._networks[run_id] = network

        logger.info(
            f"Compiled subgraph run_id={run_id} "
            f"n_neurons={len(neuron_ids)} backend={backend}"
        )
        return CompileResponse(
            run_id=run_id,
            backend=backend,
            n_neurons=len(neuron_ids),
        )

    def run(self, run_id: str, num_steps: int = 100) -> RunResponse:
        if not LAVA_AVAILABLE:
            raise RuntimeError("Lava framework not installed")

        network = self._networks.get(run_id)
        if network is None:
            raise ValueError(f"Unknown run_id: {run_id}")

        run_cfg = self._build_run_config()
        network.process.run(
            condition=RunSteps(num_steps=num_steps),
            run_cfg=run_cfg,
        )

        spikes = list(network.get_spikes())
        network.process.stop()

        logger.info(f"Run {run_id} completed: {len(spikes)} spikes in {num_steps} steps")
        return RunResponse(
            run_id=run_id,
            spikes=spikes,
            step_count=num_steps,
        )

    def cleanup(self, run_id: str) -> None:
        if run_id in self._networks:
            try:
                self._networks[run_id].process.stop()
            except Exception:
                pass
            del self._networks[run_id]

    @property
    def active_runs(self) -> list[str]:
        return list(self._networks.keys())
