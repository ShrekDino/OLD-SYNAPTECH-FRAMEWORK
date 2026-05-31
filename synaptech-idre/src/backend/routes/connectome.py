import time

from fastapi import APIRouter, HTTPException

from src.backend.services.csc_engine import _HAS_CUPY, CSCEngine
from src.backend.services.sse_streamer import PulseEvent, SSEStreamer
from src.shared.schemas import (
    ActivationInput,
    ActivationResult,
    ConnectomeMetadata,
    SubgraphRequest,
    SubgraphResponse,
)

router = APIRouter(prefix="/api/v1/connectome", tags=["connectome"])

if _HAS_CUPY:
    pass
else:
    pass


@router.get("/metadata", response_model=ConnectomeMetadata)
async def get_metadata():
    engine = CSCEngine.get_instance()
    if not engine.is_loaded:
        return ConnectomeMetadata(n_neurons=130_000, n_synapses=0)
    metadata = getattr(engine, "real_metadata", {})
    return ConnectomeMetadata(
        n_neurons=metadata.get("total_neurons", engine.shape[0]),
        n_synapses=int(engine.matrix.nnz),
        source=metadata.get("source", "FlyWire"),
        version=metadata.get("doi", "v1.0"),
    )


@router.post("/activate", response_model=ActivationResult)
async def activate(body: ActivationInput):
    engine = CSCEngine.get_instance()
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Connectome not loaded")

    t0 = time.time()
    xp = engine.xp
    input_arr = xp.array(body.input_vector, dtype=xp.float32)
    output, spike_count = engine.activate(input_arr, body.threshold)
    latency = (time.time() - t0) * 1000

    if engine.on_gpu:
        output_list = output.get().tolist()
    else:
        output_list = output.tolist()

    streamer = SSEStreamer()
    events = [
        PulseEvent(
            neuron_id=int(i),
            voltage=float(output[i]),
            spike=bool(output[i] > body.threshold),
        )
        for i in range(0, len(output), max(1, len(output) // 1000))
    ]
    streamer.publish(events)

    return ActivationResult(
        output_vector=output_list,
        spike_count=int(spike_count),
        latency_ms=latency,
    )


@router.post("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(body: SubgraphRequest):
    engine = CSCEngine.get_instance()
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Connectome not loaded")

    if len(body.neuron_ids) > 10_000:
        raise HTTPException(
            status_code=400,
            detail="Subgraph request limited to 10,000 neurons",
        )

    adjacency, neuron_ids = engine.subgraph(body.neuron_ids)
    return SubgraphResponse(adjacency=adjacency, neuron_ids=neuron_ids)


@router.get("/layout")
async def get_layout():
    engine = CSCEngine.get_instance()
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Connectome not loaded")

    layout = engine.get_layout()
    if layout is None:
        raise HTTPException(status_code=404, detail="Layout not computed")

    if engine.on_gpu:
        positions = layout.get().tolist()
    else:
        positions = layout.tolist()

    metadata = getattr(engine, "real_metadata", {
        "total_neurons": engine.shape[0],
        "total_synapses": int(engine.matrix.nnz),
        "source": "synthetic",
    })

    return {
        "positions": positions,
        "shape": list(layout.shape),
        "metadata": metadata,
    }


@router.get("/status")
async def connectome_status():
    engine = CSCEngine.get_instance()
    streamer = SSEStreamer()
    metadata = getattr(engine, "real_metadata", {})
    return {
        "loaded": engine.is_loaded,
        "shape": list(engine.shape) if engine.is_loaded else None,
        "nonzeros": int(engine.matrix.nnz) if engine.is_loaded else 0,
        "subscribers": streamer.subscriber_count,
        "backend": "gpu" if engine.on_gpu else "cpu",
        "source": metadata.get("source", "synthetic"),
        "total_neurons": metadata.get("total_neurons", engine.shape[0] if engine.is_loaded else 0),
        "total_synapses": metadata.get("total_synapses", 0),
        "doi": metadata.get("doi", None),
    }
