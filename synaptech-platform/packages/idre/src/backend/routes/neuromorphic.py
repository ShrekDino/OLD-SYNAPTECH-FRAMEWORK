from fastapi import APIRouter, HTTPException

from src.backend.services.lava_bridge import LavaBridge
from src.shared.schemas import CompileRequest, CompileResponse, RunRequest, RunResponse

router = APIRouter(prefix="/api/v1/loihi", tags=["neuromorphic"])


@router.get("/status")
async def loihi_status():
    bridge = LavaBridge.get_instance()
    return {
        "available": bridge.available,
        "backend": bridge.backend,
        "active_runs": bridge.active_runs,
    }


@router.post("/compile", response_model=CompileResponse)
async def compile_subgraph(body: CompileRequest):
    bridge = LavaBridge.get_instance()
    if not bridge.available:
        raise HTTPException(
            status_code=503,
            detail="Lava framework not available. Install lava-nc to enable.",
        )

    if len(body.neuron_ids) > 10_000:
        raise HTTPException(
            status_code=400,
            detail="Subgraph compilation limited to 10,000 neurons",
        )

    try:
        result = bridge.compile_subgraph(
            neuron_ids=body.neuron_ids,
            backend=body.backend,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=RunResponse)
async def run_simulation(body: RunRequest):
    bridge = LavaBridge.get_instance()
    if not bridge.available:
        raise HTTPException(
            status_code=503,
            detail="Lava framework not available",
        )

    if body.num_steps > 1_000_000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1,000,000 simulation steps",
        )

    try:
        result = bridge.run(run_id=body.run_id, num_steps=body.num_steps)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/{run_id}")
async def cleanup_run(run_id: str):
    bridge = LavaBridge.get_instance()
    bridge.cleanup(run_id)
    return {"status": "cleaned", "run_id": run_id}
