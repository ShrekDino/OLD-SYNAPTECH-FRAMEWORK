import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SpatialReasoner:
    """Wraps Cosmos-Reason2 for spatial-temporal understanding.

    Takes video frames or latent token sequences and produces
    chain-of-thought physical reasoning about spatial relationships,
    object interactions, and future state predictions.
    """

    def __init__(self, model_name: str = "nvidia/Cosmos-Reason2-2B"):
        self.model_name = model_name
        self._model = None
        self._processor = None

    def load(self, device: str = "cpu", quantize: bool = True):
        try:
            from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

            kwargs = {"device_map": device}
            if quantize and device == "cuda":
                kwargs["load_in_4bit"] = True

            self._model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_name, **kwargs
            )
            self._processor = AutoProcessor.from_pretrained(self.model_name)
            logger.info(f"Loaded Cosmos-Reason2-2B on {device}")
        except Exception as e:
            logger.warning(f"Failed to load Cosmos-Reason2: {e}")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def reason_about_scene(self, video_frames: np.ndarray, query: str) -> str:
        if not self.is_loaded:
            return "Cosmos-Reason2 not available — using fallback."
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": video_frames, "fps": 4.0},
                        {"type": "text", "text": query},
                    ],
                }
            ]
            prompt = self._processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = self._processor(
                text=prompt, videos=[video_frames], return_tensors="pt"
            ).to(self._model.device)
            output = self._model.generate(
                **inputs, max_new_tokens=512, do_sample=False
            )
            return self._processor.decode(
                output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
            )
        except Exception as e:
            logger.warning(f"Spatial reasoning failed: {e}")
            return ""

    def analyze_agent_trajectory(
        self, state_sequence: np.ndarray
    ) -> dict:
        return {
            "spatial_coherence": float(np.mean(np.abs(np.diff(state_sequence, axis=0)))),
            "state_variance": float(np.var(state_sequence)),
            "temporal_regularity": float(
                1.0 / (1.0 + np.std(np.linalg.norm(np.diff(state_sequence, axis=0), axis=1)))
            ),
        }
