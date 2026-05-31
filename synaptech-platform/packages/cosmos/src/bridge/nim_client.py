import asyncio
import base64
import json
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class CosmosNIMClient:
    """Async HTTP client for NVIDIA NIM for Cosmos WFM.

    Supports Cosmos-Predict1, Predict2.5, Transfer2.5, and Tokenizer
    deployed as Docker NIM containers with Triton Inference Server.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def health(self) -> dict:
        await self._ensure_session()
        async with self.session.get(f"{self.base_url}/v1/health/ready") as resp:
            return await resp.json()

    async def infer_text2world(
        self, prompt: str, resolution: str = "480", num_frames: int = 121
    ) -> bytes:
        await self._ensure_session()
        payload = {
            "prompt": prompt,
            "resolution": resolution,
            "frames_count": num_frames,
            "frames_per_sec": 24,
        }
        async with self.session.post(
            f"{self.base_url}/v1/infer", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def infer_video2world(
        self, video_bytes: bytes, prompt: str = "", resolution: str = "480"
    ) -> bytes:
        await self._ensure_session()
        video_b64 = base64.b64encode(video_bytes).decode("utf-8")
        payload = {
            "prompt": prompt,
            "video": video_b64,
            "resolution": resolution,
        }
        async with self.session.post(
            f"{self.base_url}/v1/infer", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def metadata(self) -> dict:
        await self._ensure_session()
        async with self.session.get(f"{self.base_url}/v1/metadata") as resp:
            return await resp.json()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def __del__(self):
        if self.session and not self.session.closed:
            try:
                asyncio.create_task(self.close())
            except RuntimeError:
                pass
