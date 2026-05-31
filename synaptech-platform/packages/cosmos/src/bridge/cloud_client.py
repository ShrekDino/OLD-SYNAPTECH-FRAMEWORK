import asyncio
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class CosmosCloudClient:
    """Client for NVIDIA Cosmos cloud API (NVIDIA API Catalog).

    Uses NGC API key for authentication. Falls back gracefully
    when local GPU is unavailable.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.nvcf.nvidia.com/v2/nvcf",
        timeout: int = 600,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )

    async def text2world(
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
            f"{self.base_url}/exec", json=payload
        ) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
