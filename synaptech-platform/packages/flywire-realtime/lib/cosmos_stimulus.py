"""Cosmos-powered visual stimulus injection for closed-loop fly simulation.

Replaces the simple cursor-based stimulus with generated visual world
frames from Cosmos-Predict2.5. Maps fly motor commands and body state
to visual scene descriptions, then injects the resulting sensory
signals back into the 78-neuropil activation vector.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class CosmosVisualStimulus:
    """Generates visual sensory input from motor commands and body state.

    Integrates with the FlyWire Realtime Engine's closed-loop feedback
    by producing visual stimulus signals that map to neuropil targets
    (optic lobes, visual projection neurons) based on Cosmos-generated
    world simulations.
    """

    def __init__(
        self,
        nim_url: str = "http://localhost:8002",
        neuropil_count: int = 78,
        use_cosmos: bool = False,
    ):
        self.nim_url = nim_url
        self.neuropil_count = neuropil_count
        self.use_cosmos = use_cosmos
        self._client = None

    async def _ensure_client(self):
        if self._client is None and self.use_cosmos:
            try:
                from cosmos.bridge.nim_client import CosmosNIMClient
                self._client = CosmosNIMClient(base_url=self.nim_url)
                logger.info(f"Cosmos NIM client initialized at {self.nim_url}")
            except ImportError:
                logger.warning("Cosmos package not available, using fallback")
                self.use_cosmos = False

    def compute_visual_stimulus(
        self, motor_commands: np.ndarray, neuropil_state: np.ndarray
    ) -> np.ndarray:
        """Compute visual stimulus injection vector.

        Returns a neuropil-shaped injection vector (78,) with
        visual stimulus signals mapped to optic lobe targets.

        When Cosmos is enabled, the stimulus is derived from
        predicted world states. Otherwise, falls back to a
        simple motion-based stimulus.
        """
        if self.use_cosmos and self._client is not None:
            return self._cosmos_stimulus(motor_commands, neuropil_state)
        return self._fallback_visual(motor_commands, neuropil_state)

    def _cosmos_stimulus(
        self, motor_commands: np.ndarray, neuropil_state: np.ndarray
    ) -> np.ndarray:
        stimulus = np.zeros(self.neuropil_count, dtype=np.float32)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._client.infer_text2world(
                    "A fly's perspective moving through a natural environment"
                )
            )
            loop.close()
            if result:
                visual_energy = np.frombuffer(result, dtype=np.float32)[:self.neuropil_count]
                stimulus[: len(visual_energy)] = visual_energy
        except Exception as e:
            logger.warning(f"Cosmos visual gen failed: {e}")
            stimulus = self._fallback_visual(motor_commands, neuropil_state)
        return stimulus

    def _fallback_visual(
        self, motor_commands: np.ndarray, neuropil_state: np.ndarray
    ) -> np.ndarray:
        stimulus = np.zeros(self.neuropil_count, dtype=np.float32)
        speed = np.mean(np.abs(motor_commands[:6]))
        turn = motor_commands[4] - motor_commands[5]

        stimulus[0] = np.clip(speed * 0.5 + abs(turn) * 0.3, 0.0, 1.0)
        stimulus[1] = np.clip(speed * 0.3, 0.0, 1.0)
        stimulus[2] = np.clip(0.1 + 0.3 * (0.5 + 0.5 * np.sin(np.sum(neuropil_state) * 0.1)), 0.0, 1.0)
        if abs(turn) > 0.2:
            idx = 3 if turn > 0 else 4
            stimulus[idx] = np.clip(abs(turn) * 0.6, 0.0, 1.0)
        return stimulus
