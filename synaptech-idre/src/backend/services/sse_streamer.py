import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import AsyncGenerator

from src.shared.constants import SSE_BATCH_SIZE, SSE_HEARTBEAT_SECS
from src.shared.schemas import PulseBatch

logger = logging.getLogger(__name__)


@dataclass
class PulseEvent:
    neuron_id: int
    voltage: float
    spike: bool


class SSEStreamer:
    def __init__(self, batch_size: int = SSE_BATCH_SIZE, heartbeat_secs: int = SSE_HEARTBEAT_SECS):
        self._queue: asyncio.Queue[list[PulseEvent]] = asyncio.Queue(maxsize=1024)
        self._subscribers: set[asyncio.Queue] = set()
        self._batch_size = batch_size
        self._heartbeat_secs = heartbeat_secs
        self._buffer: list[PulseEvent] = []
        self._lock = asyncio.Lock()

    def publish(self, events: list[PulseEvent]) -> None:
        self._buffer.extend(events)
        if len(self._buffer) >= self._batch_size:
            batch = self._buffer[: self._batch_size]
            self._buffer[:] = self._buffer[self._batch_size:]
            for sub in self._subscribers:
                try:
                    sub.put_nowait(batch)
                except asyncio.QueueFull:
                    pass

    async def flush(self) -> None:
        async with self._lock:
            if self._buffer:
                batch = self._buffer[:]
                self._buffer.clear()
                for sub in self._subscribers:
                    try:
                        sub.put_nowait(batch)
                    except asyncio.QueueFull:
                        pass

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[list[PulseEvent]] = asyncio.Queue(maxsize=256)
        self._subscribers.add(queue)
        logger.info(f"SSE subscriber connected. Total: {len(self._subscribers)}")

        try:
            while True:
                try:
                    batch = await asyncio.wait_for(
                        queue.get(), timeout=self._heartbeat_secs
                    )
                    pulse_batch = PulseBatch(
                        neuron_ids=[e.neuron_id for e in batch],
                        voltages=[e.voltage for e in batch],
                        spikes=[e.spike for e in batch],
                        ts=time.time(),
                    )
                    frame = {
                        "batch": pulse_batch.model_dump(mode="json"),
                        "ts": time.time(),
                    }
                    yield f"data: {json.dumps(frame)}\n\n"
                except asyncio.TimeoutError:
                    yield f": heartbeat {time.time()}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self._subscribers.discard(queue)
            logger.info(f"SSE subscriber disconnected. Total: {len(self._subscribers)}")

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)
