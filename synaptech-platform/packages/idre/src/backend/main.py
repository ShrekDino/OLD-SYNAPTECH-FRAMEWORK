import logging
import os
import sys
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.config import settings
from src.backend.exceptions import exception_handlers
from src.backend.middleware.auth import AuthMiddleware
from src.backend.middleware.capture_split import CaptureSplitMiddleware
from src.backend.routes import connectome, neuromorphic, telemetry, visualization
from src.backend.services.connectome_loader import ConnectomeLoader
from src.backend.services.csc_engine import _HAS_CUPY, CSCEngine
from src.backend.services.sse_streamer import SSEStreamer

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _auto_generate_data():
    data_dir = os.path.join(os.path.dirname(__file__), "../../data/flywire")
    layout_path = os.path.join(os.path.dirname(__file__), "../../data/layout.json")
    data_dir = os.path.abspath(data_dir)
    layout_path = os.path.abspath(layout_path)
    csv_path = os.path.join(data_dir, "connectome.csv")

    if os.path.exists(csv_path) and os.path.exists(layout_path):
        logger.info("Existing synthetic data found, skipping generation")
        return

    logger.info("No synthetic connectome data found — generating dataset...")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from scripts.generate_test_data import main as generate
    generate()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name}")

    if _HAS_CUPY:
        import cupy as cp
        logger.info(f"CuPy CUDA available: {cp.cuda.is_available()}")
        if cp.cuda.is_available():
            dev = cp.cuda.runtime.getDeviceProperties(0)
            name = dev["name"].decode()
            logger.info(f"GPU: {name} ({dev['totalGlobalMem'] // 1_048_576} MB VRAM)")
    else:
        logger.info("Running on CPU (SciPy + NumPy) — no GPU detected")

    engine = CSCEngine.get_instance()

    # ── Try real FlyWire first ──
    from src.backend.services.connectome_loader import load_real_flywire as _try_real

    real = _try_real()
    if real is not None:
        engine.load_from_scipy(real["matrix"])
        engine._layout_xp = np.array(real["layout_positions"], dtype=np.float64)
        engine.real_metadata = real["metadata"]
        m = real["metadata"]
        logger.info(
            f"Loaded real FlyWire: {m['total_neurons']:,} neurons, "
            f"{m['total_connections']:,} connections, "
            f"{m['total_synapses']:,} synapses ({m['source']})"
        )
    else:
        # ── Fallback: synthetic data ──
        _auto_generate_data()
        loader = ConnectomeLoader(data_path=settings.data_path)
        try:
            loader.load()
            loc = "GPU" if engine.on_gpu else "CPU"
            logger.info(f"Connectome loaded successfully on {loc}")

            layout = loader.load_layout()
            if layout is not None:
                logger.info(f"Layout loaded ({len(layout)} positions)")
        except Exception as e:
            logger.error(f"Failed to load connectome: {e}")
            raise

    yield

    logger.info("Shutting down SynapTech IDRE")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    exception_handlers=exception_handlers,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(CaptureSplitMiddleware)

app.include_router(connectome.router)
app.include_router(neuromorphic.router)
app.include_router(telemetry.router)
app.include_router(visualization.router)


@app.get("/health")
async def health():
    engine = CSCEngine.get_instance()
    return {
        "status": "ok",
        "gpu": engine.on_gpu,
        "backend": "GPU (CuPy)" if engine.on_gpu else "CPU (SciPy)",
        "connectome_loaded": engine.is_loaded,
        "sse_subscribers": SSEStreamer().subscriber_count,
    }


@app.get("/metrics")
async def metrics():
    engine = CSCEngine.get_instance()
    mem_info = {}
    if engine.on_gpu:
        import cupy as cp
        free, total = cp.cuda.runtime.memGetInfo()
        mem_info = {
            "gpu_memory_total_mb": total // 1_048_576,
            "gpu_memory_free_mb": free // 1_048_576,
            "gpu_memory_used_mb": (total - free) // 1_048_576,
        }
    return {
        **mem_info,
        "connectome_nonzeros": int(engine.matrix.nnz) if engine.is_loaded else 0,
        "backend": "gpu" if engine.on_gpu else "cpu",
        "sse_subscribers": SSEStreamer().subscriber_count,
    }
