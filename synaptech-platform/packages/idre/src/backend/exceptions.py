from fastapi import Request
from fastapi.responses import JSONResponse


class IDREError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class ConnectomeNotLoadedError(IDREError):
    def __init__(self):
        super().__init__(503, "Connectome not loaded. Activate the connectome first.")


class LavaNotAvailableError(IDREError):
    def __init__(self):
        super().__init__(
            503, "Lava-NC runtime not available. Install lava-nc or use simulation mode."
        )


class InvalidRunIDError(IDREError):
    def __init__(self, run_id: str):
        super().__init__(404, f"Run ID '{run_id}' not found or expired.")


class GPUNotAvailableError(IDREError):
    def __init__(self):
        super().__init__(503, "GPU (CUDA) not available. This operation requires a GPU.")


async def idre_exception_handler(request: Request, exc: IDREError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


exception_handlers = {IDREError: idre_exception_handler}
