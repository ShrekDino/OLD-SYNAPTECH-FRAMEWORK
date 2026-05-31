import logging
from typing import Optional

import numpy as np

from ..bridge import CosmosNIMClient

logger = logging.getLogger(__name__)


class CosmosFlyWorld:
    """Generates visual world states from fly motor commands and neuropil activity.

    Bridges the FlyWire Realtime Engine's 12-channel motor commands
    and 78-neuropil activation vector to Cosmos-Predict2.5 world generation.

    Uses the NIM client (local Docker or cloud) to produce RGB video
    frames that represent what the fly agent would "see" given its actions.
    """

    def __init__(
        self,
        nim_client: CosmosNIMClient,
        frame_width: int = 480,
        frame_height: int = 480,
    ):
        self.nim_client = nim_client
        self.frame_width = frame_width
        self.frame_height = frame_height
        self._last_world_state: Optional[np.ndarray] = None

    def _build_prompt(
        self, motor_commands: np.ndarray, neuropil_state: np.ndarray
    ) -> str:
        walking = np.any(motor_commands[:4] > 0.1)
        turning = motor_commands[4] - motor_commands[5]
        speed = np.mean(np.abs(motor_commands[:6]))
        activity_level = np.mean(np.abs(neuropil_state))

        direction = "forward"
        if turning > 0.3:
            direction = "turning left"
        elif turning < -0.3:
            direction = "turning right"

        prompt = (
            f"A first-person view from a small flying insect. "
            f"The insect is moving {direction} at moderate speed. "
            f"Ground texture passes below. {activity_level:.2f} neural activity level. "
            f"Natural outdoor environment with green foliage."
        )
        return prompt

    async def predict_world(
        self, motor_commands: np.ndarray, neuropil_state: np.ndarray
    ) -> Optional[np.ndarray]:
        prompt = self._build_prompt(motor_commands, neuropil_state)
        try:
            video_bytes = await self.nim_client.infer_text2world(prompt)
            self._last_world_state = np.frombuffer(video_bytes, dtype=np.uint8)
            return self._last_world_state
        except Exception as e:
            logger.warning(f"Cosmos world prediction failed: {e}")
            return None

    @property
    def last_world_state(self) -> Optional[np.ndarray]:
        return self._last_world_state
