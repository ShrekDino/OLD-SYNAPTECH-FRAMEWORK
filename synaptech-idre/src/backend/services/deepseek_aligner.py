import json
import logging
import os
from typing import Optional

import httpx

from src.shared.constants import DEEPSEEK_MODEL
from src.shared.schemas import AlignmentRequest, AlignmentResponse, Edge

logger = logging.getLogger(__name__)


class DeepSeekAligner:
    _instance: Optional["DeepSeekAligner"] = None

    def __init__(self, api_key: str, model: str = DEEPSEEK_MODEL):
        self._api_key = api_key
        self._model = model
        self._base_url = "https://api.deepseek.com/v1"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=300.0,
        )

    @classmethod
    def from_env(cls) -> "DeepSeekAligner":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY environment variable required")
        return cls(api_key=api_key)

    @classmethod
    def get_instance(cls) -> "DeepSeekAligner":
        if cls._instance is None:
            cls._instance = cls.from_env()
        return cls._instance

    def _build_prompt(self, request: AlignmentRequest) -> str:
        edge_list_str = json.dumps(
            [e.model_dump() for e in request.edge_list[:500_000]],
            separators=(",", ":"),
        )
        prompt = f"""You are a connectome alignment system for EM datasets.

Source dataset: {request.source_dataset}
Target dataset: {request.target_dataset}

Edge list format: [{{"source": int, "target": int, "weight": float}}, ...]

Task:
1. Identify corresponding neurons between source and target datasets using connectivity patterns.
2. Produce an ID mapping (source_id -> target_id) for all neurons.
3. Remap the edge list using the aligned IDs.

Return valid JSON with fields:
- "id_mapping": dict[int, int]
- "confidence": float between 0 and 1
- "aligned_edges": list of [source_aligned, target_aligned, weight]

Edge list ({len(request.edge_list)} edges):
{edge_list_str[:950_000]}
"""
        return prompt

    async def align(self, request: AlignmentRequest) -> AlignmentResponse:
        prompt = self._build_prompt(request)

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": "Output connectome alignment as valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 8192,
            "temperature": 0.0,
        }

        logger.info(
            f"Sending alignment prompt ({len(prompt)} chars) to DeepSeek-V4"
        )

        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception as e:
            logger.error(f"DeepSeek alignment failed: {e}")
            return AlignmentResponse(
                aligned_edges=[],
                id_mapping={},
                confidence=0.0,
            )

        id_mapping = {int(k): int(v) for k, v in parsed.get("id_mapping", {}).items()}
        aligned_edges = [
            Edge(source=e[0], target=e[1], weight=e[2])
            for e in parsed.get("aligned_edges", [])
        ]

        logger.info(
            f"Alignment complete: {len(id_mapping)} mappings, "
            f"{len(aligned_edges)} aligned edges, "
            f"confidence={parsed.get('confidence', 0):.3f}"
        )

        return AlignmentResponse(
            aligned_edges=aligned_edges,
            id_mapping=id_mapping,
            confidence=parsed.get("confidence", 0.0),
        )

    async def close(self) -> None:
        await self._client.aclose()
