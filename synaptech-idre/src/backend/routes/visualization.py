from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.backend.services.sse_streamer import SSEStreamer

router = APIRouter(prefix="/api/v1/stream", tags=["visualization"])


@router.get("/pulses")
async def stream_pulses(request: Request):
    streamer = SSEStreamer()

    async def event_generator():
        async for event in streamer.subscribe():
            if await request.is_disconnected():
                break
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status")
async def stream_status():
    streamer = SSEStreamer()
    return {
        "subscribers": streamer.subscriber_count,
        "protocol": "SSE",
        "batch_size": 1000,
    }
