
from fastapi import APIRouter, HTTPException

from src.shared.schemas import TelemetryQuery, TelemetryQueryResult

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


def _get_pinecone():
    from src.backend.services.pinecone_client import PineconeClient
    if not PineconeClient.available():
        return None
    try:
        return PineconeClient.get_instance()
    except Exception:
        return None


@router.get("/status")
async def telemetry_status():
    pc = _get_pinecone()
    if pc is None:
        return {"available": False, "index": None}
    return {"available": True}


@router.post("/query", response_model=TelemetryQueryResult)
async def query_telemetry(body: TelemetryQuery):
    pc = _get_pinecone()
    if pc is None:
        raise HTTPException(status_code=503, detail="Pinecone unavailable")

    if not body.similar_operation:
        return TelemetryQueryResult(results=[], count=0)

    try:
        results = pc.query_similar(
            operation=body.similar_operation,
            top_k=body.top_k,
        )
        return TelemetryQueryResult(results=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
