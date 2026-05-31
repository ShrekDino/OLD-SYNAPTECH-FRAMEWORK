import pytest
from src.backend.services.sse_streamer import SSEStreamer, PulseEvent


@pytest.mark.asyncio
async def test_sse_publish_subscribe():
    streamer = SSEStreamer(batch_size=2)

    events = [
        PulseEvent(neuron_id=0, voltage=0.8, spike=True),
        PulseEvent(neuron_id=1, voltage=0.3, spike=False),
        PulseEvent(neuron_id=2, voltage=0.9, spike=True),
    ]

    collected = []

    async def subscriber():
        async for frame in streamer.subscribe():
            collected.append(frame)
            if len(collected) >= 2:
                break

    import asyncio
    task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.05)

    streamer.publish(events)
    streamer.publish(events)
    await asyncio.sleep(0.05)
    task.cancel()

    assert len(collected) >= 1
    assert "data:" in collected[0]


@pytest.mark.asyncio
async def test_heartbeat():
    streamer = SSEStreamer(heartbeat_secs=2)
    collected = []

    async def subscriber():
        async for frame in streamer.subscribe():
            collected.append(frame)

    import asyncio
    task = asyncio.create_task(subscriber())

    # Wait for heartbeat to be emitted (with margin)
    await asyncio.sleep(2.5)

    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, TimeoutError):
        pass

    assert any("heartbeat" in f for f in collected)
