import json
import queue
import socket
import threading
import time
from typing import Any


class MotorBroadcaster:
    """Non-blocking UDP broadcaster for real-time motor and body-state data.

    Architecture
    ------------
    Main thread (the engine's tick loop) → ``push()`` (O(1), no I/O)
        → internal ``queue.Queue`` (maxsize=64, drops oldest on overflow)
            → daemon sender thread → ``json.dumps`` + ``socket.sendto``

    The engine tick loop **never** blocks on serialization or network I/O.
    If the visualizer is not running the ``sendto`` silently fails (UDP is
    connectionless); if it is too slow the queue drops frames gracefully.

    Wire format
    -----------
    Compact JSON dict, one per tick:
        {
            "t": <tick_count>,
            "pos": [x, y],
            "heading": float,
            "gait_cycle": float,
            "pose": str,
            "walking_speed": float,
            "turning_rate": float,
            "wing_amplitude": float,
            "proboscis_extension": float,
            "face_cleaning_drive": float,
            "gait_energy": float,
            "head_pitch": float,
            "head_yaw": float,
            "abdomen_bend": float,
            "body_height": float,
        }
    """

    def __init__(self, port: int = 5555, host: str = "127.0.0.1"):
        self._queue: queue.Queue[dict[str, Any] | None] = queue.Queue(maxsize=64)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._addr = (host, port)
        self._running = True
        self._thread = threading.Thread(target=self._sender_loop, daemon=True, name="viz-bridge")
        self._thread.start()

    # ------------------------------------------------------------------
    # Public API  (called from the engine tick loop)
    # ------------------------------------------------------------------

    def push(self, data: dict[str, Any]) -> None:
        """Enqueue a payload for broadcast.

        O(1) — no serialization, no I/O.  Drops the frame silently if the
        sender queue is full (visualizer too slow or not running).
        """
        try:
            self._queue.put_nowait(data)
        except queue.Full:
            pass

    def stop(self) -> None:
        """Shut down the sender thread and close the socket."""
        self._running = False
        self._queue.put_nowait(None)  # unblock sender
        self._thread.join(timeout=1.0)
        try:
            self._sock.close()
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Sender thread  (background, handles all I/O)
    # ------------------------------------------------------------------

    def _sender_loop(self) -> None:
        while self._running:
            try:
                data = self._queue.get(timeout=0.05)
                if data is None:
                    break
                msg = json.dumps(data, default=_json_default, ensure_ascii=False).encode("utf-8")
                self._sock.sendto(msg, self._addr)
            except queue.Empty:
                continue
            except (OSError, ConnectionResetError, ConnectionRefusedError):
                pass  # visualizer not listening


# ---------------------------------------------------------------------------
# Reverse channel: stimulus receiver (visualizer → engine)
# ---------------------------------------------------------------------------

class StimulusReceiver:
    """Non-blocking UDP listener for mouse-driven stimulus coordinates.

    The visualizer sends normalized (x, y) world coordinates of the user's
    cursor position.  This class runs a daemon thread that listens on a
    separate UDP port and exposes the latest target via a property, with
    no locks — the target tuple is updated atomically by CPython's GIL.

    Wire format (visualizer → engine, port 5556):
        {"tx": float, "ty": float, "active": 1|0}
    """

    def __init__(self, port: int = 5556, host: str = "127.0.0.1"):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 ** 20)
        self._sock.bind((host, port))
        self._sock.settimeout(0.05)
        self._running = True
        # Atomically-updated target (GIL-protected on CPython)
        self.target: tuple[float, float] | None = None
        self.active: bool = False
        self._thread = threading.Thread(target=self._listen, daemon=True,
                                        name="stimulus-listener")
        self._thread.start()

    @property
    def latest(self) -> tuple[float, float] | None:
        """Latest stimulus world coordinates, or *None* if inactive."""
        return self.target if self.active else None

    def _listen(self) -> None:
        while self._running:
            try:
                data, _ = self._sock.recvfrom(1024)
                msg = json.loads(data.decode("utf-8"))
                self.target = (float(msg["tx"]), float(msg["ty"]))
                self.active = msg.get("active", 0) > 0
            except socket.timeout:
                continue
            except (json.JSONDecodeError, KeyError, OSError):
                pass

    def stop(self) -> None:
        self._running = False
        self._sock.close()


def _json_default(obj: Any) -> Any:
    """Convert numpy types to native Python for JSON serialization."""
    import numpy as np
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
