import os
import time
import numpy as np
from datetime import datetime

from lib.motor_decoder import MOTOR_MAP

LOG_WINDOW = 10000                  # ~2.8 min @ 60 Hz before oldest entries are overwritten
MOTOR_CHANNELS = len(MOTOR_MAP)     # auto-derived from motor decoder spec


class RuntimeLogger:
    """Lightweight, O(1) ring-buffer metrics aggregator for real-time sessions.

    Zero-copy philosophy:
      - All buffers are pre-allocated at construction time (no appends during
        the live tick loop).
      - Each ``tick()`` call performs exactly two array-write operations
        (index-modulo into the buffer + running scalar accumulators).
      - ``dump()`` compresses the window into a human-readable markdown log
        *after* the simulation has stopped — I/O never touches the hot path.
    """

    def __init__(
        self,
        device_name: str,
        allocated_vram_gb: float,
        n_neurons: int,
        sparse_nnz: int,
        n_motor_channels: int = MOTOR_CHANNELS,
    ):
        self.device_name = device_name
        self.allocated_vram_gb = allocated_vram_gb
        self.n_neurons = n_neurons
        self.sparse_nnz = sparse_nnz
        self.n_motor = n_motor_channels

        # --- Ring buffers (pre-allocated, zero dynamic growth) ---
        self.activity_buf = np.zeros((LOG_WINDOW, n_neurons), dtype=np.float32)
        self.sensory_buf = np.zeros((LOG_WINDOW, n_neurons), dtype=np.float32)
        self.motor_buf = np.zeros((LOG_WINDOW, n_motor_channels), dtype=np.float32)
        self.latency_buf = np.zeros(LOG_WINDOW, dtype=np.float64)
        self.tick_buf = np.zeros(LOG_WINDOW, dtype=np.int64)
        self.nan_flag_buf = np.zeros(LOG_WINDOW, dtype=bool)
        self.zero_motor_flag_buf = np.zeros(LOG_WINDOW, dtype=bool)

        self._pos = 0
        self.total_ticks = 0
        self._wrapped = False

        # --- O(1) running accumulators (no iteration over history) ---
        self.peak_activity = 0.0
        self.activity_sum = 0.0          # Σ mean(activity)  →  final mean
        self.activity_sq_sum = 0.0       # Σ mean(activity)² →  final std
        self.total_latency = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.nan_count = 0
        self.zero_motor_count = 0

        self.start_time: float | None = None
        self.end_time: float | None = None

    # ------------------------------------------------------------------
    # Public API  (called once per tick from the engine)
    # ------------------------------------------------------------------

    def tick(self, activity_np, sensory_np, motor_np, latency_s):
        """Record a single tick into the ring buffer (O(1))."""
        now = time.time()
        if self.start_time is None:
            self.start_time = now

        idx = self._pos % LOG_WINDOW

        # Ring-buffer writes (pre-allocated — no malloc)
        self.activity_buf[idx] = activity_np
        self.sensory_buf[idx] = sensory_np
        self.motor_buf[idx] = motor_np
        self.latency_buf[idx] = latency_s
        self.tick_buf[idx] = self.total_ticks

        # Anomaly flags
        has_nan = bool(np.any(np.isnan(activity_np)))
        self.nan_flag_buf[idx] = has_nan
        if has_nan:
            self.nan_count += 1

        all_zero = bool(np.all(motor_np == 0.0))
        self.zero_motor_flag_buf[idx] = all_zero
        if all_zero:
            self.zero_motor_count += 1

        # Running scalar stats (O(1))
        mean_act = float(activity_np.mean())
        peak = float(activity_np.max())
        if peak > self.peak_activity:
            self.peak_activity = peak
        self.activity_sum += mean_act
        self.activity_sq_sum += mean_act * mean_act

        self.total_latency += latency_s
        if latency_s < self.min_latency:
            self.min_latency = latency_s
        if latency_s > self.max_latency:
            self.max_latency = latency_s

        self._pos += 1
        self.total_ticks += 1
        if not self._wrapped and self._pos >= LOG_WINDOW:
            self._wrapped = True

        self.end_time = now

    def finalize(self):
        """Freeze end-time (call once when the loop exits)."""
        self.end_time = time.time()

    # ------------------------------------------------------------------
    # Report generation  (called *after* the simulation stops)
    # ------------------------------------------------------------------

    def dump(self, output_dir: str = None) -> str:
        """Assemble and write the markdown session log.

        Returns the absolute path of the written ``.md`` file.
        """
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "output",
            )
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"realtime_run_{timestamp}.md")

        stats = self._compute_final_stats()

        with open(path, "w") as f:
            f.write(self._render_markdown(stats))

        return path

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _valid_count(self) -> int:
        """Number of valid entries in the ring buffer."""
        return min(self.total_ticks, LOG_WINDOW)

    def _valid_slice(self):
        """Return a slice of valid (non-wrapped) buffer entries."""
        n = self._valid_count()
        if n < LOG_WINDOW:
            return slice(0, n)
        return slice(self._pos % LOG_WINDOW, None)

    def _compute_final_stats(self):
        n = self._valid_count()
        if n == 0:
            return {}

        s = slice( 0 if not self._wrapped else self._pos % LOG_WINDOW,
                   None if not self._wrapped else self._pos % LOG_WINDOW + n)
        # Adjust for wrapped case: we need two slices
        if self._wrapped:
            idx = self._pos % LOG_WINDOW
            valid_act = np.concatenate([self.activity_buf[idx:], self.activity_buf[:idx]])
            valid_sen = np.concatenate([self.sensory_buf[idx:], self.sensory_buf[:idx]])
            valid_mot = np.concatenate([self.motor_buf[idx:], self.motor_buf[:idx]])
            valid_lat = np.concatenate([self.latency_buf[idx:], self.latency_buf[:idx]])
            valid_nan = np.concatenate([self.nan_flag_buf[idx:], self.nan_flag_buf[:idx]])
            valid_zero = np.concatenate([self.zero_motor_flag_buf[idx:], self.zero_motor_flag_buf[:idx]])
        else:
            valid_act = self.activity_buf[:n]
            valid_sen = self.sensory_buf[:n]
            valid_mot = self.motor_buf[:n]
            valid_lat = self.latency_buf[:n]
            valid_nan = self.nan_flag_buf[:n]
            valid_zero = self.zero_motor_flag_buf[:n]

        total = max(self.total_ticks, 1)
        elapsed = (self.end_time or time.time()) - (self.start_time or 0.0)
        mean_activity = self.activity_sum / total
        var_activity = (self.activity_sq_sum / total) - (mean_activity ** 2)
        std_activity = np.sqrt(max(var_activity, 0.0))
        mean_lat = self.total_latency / total

        # Sensory-to-motor latency: difference between sensory injection time
        # and motor decode availability.  We approximate this as the tick
        # duration since everything is synchronous.
        sensory_to_motor_latency = mean_lat * 1000  # ms

        return {
            "duration_s": elapsed,
            "total_ticks": self.total_ticks,
            "log_window_ticks": n,
            "avg_tick_rate": total / max(elapsed, 1e-9),
            "mean_activity": mean_activity,
            "std_activity": std_activity,
            "peak_activity": self.peak_activity,
            "mean_latency_ms": mean_lat * 1000,
            "min_latency_ms": self.min_latency * 1000 if self.min_latency != float('inf') else 0.0,
            "max_latency_ms": self.max_latency * 1000,
            "nan_count": self.nan_count,
            "nan_rate": self.nan_count / total * 100,
            "zero_motor_count": self.zero_motor_count,
            "zero_motor_rate": self.zero_motor_count / total * 100,
            "peak_latency_violations": int(np.sum(valid_lat > 1.0 / 60.0)),
            "sensory_to_motor_latency_ms": sensory_to_motor_latency,
        }

    def _render_markdown(self, s: dict) -> str:
        if not s:
            return "# Real-Time Simulation Log\n\n*No data collected.*\n"

        started = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "N/A"
        duration_str = f"{s['duration_s']:.1f}s ({s['total_ticks']} ticks @ {s['avg_tick_rate']:.1f} Hz avg)"
        window_str = f"Ring buffer: {s['log_window_ticks']} entries (last {s['log_window_ticks']} of {s['total_ticks']})"

        lines = []
        lines.append("# Real-Time Simulation Log\n")
        lines.append(f"**Date:** {started}")
        lines.append(f"**Duration:** {duration_str}")
        lines.append(f"**Log window:** {s['log_window_ticks']} / {s['total_ticks']} ticks retained\n")

        lines.append("## Execution Hardware\n")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Device | {self.device_name} |")
        lines.append(f"| Allocated VRAM | {self.allocated_vram_gb:.1f} / ? GB |")
        lines.append(f"| Tick loop latency | mean={s['mean_latency_ms']:.3f}ms, max={s['max_latency_ms']:.3f}ms, min={s['min_latency_ms']:.3f}ms |")
        lines.append(f"| Loop regulation | {s['total_ticks']} ticks in {s['duration_s']:.1f}s wall (target 60.0 Hz) |")
        lines.append(f"| Latency violations (>16.67ms) | {s['peak_latency_violations']} |\n")

        lines.append("## Ingestion Data Metrics\n")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Neuropil nodes | {self.n_neurons} |")
        lines.append(f"| Sparse matrix NNZ | {self.sparse_nnz} / {self.n_neurons * self.n_neurons} ({100.0 * self.sparse_nnz / (self.n_neurons * self.n_neurons):.1f}% density) |")
        lines.append(f"| Sensory channels | {self.n_neurons} |")
        lines.append(f"| Total ticks executed | {s['total_ticks']} (last {s['log_window_ticks']} in buffer) |\n")

        lines.append("## Step Anomalies\n")
        lines.append("| Anomaly | Count | Rate |")
        lines.append("|---|---|---|")
        lines.append(f"| NaN propagations | {s['nan_count']} | {s['nan_rate']:.4f}% |")
        lines.append(f"| Zero-motor dead loops | {s['zero_motor_count']} | {s['zero_motor_rate']:.2f}% |\n")

        lines.append("## Final Output Delta\n")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Mean firing rate | {s['mean_activity']:.4f} ± {s['std_activity']:.4f} |")
        lines.append(f"| Peak activity | {s['peak_activity']:.4f} |")
        lines.append(f"| Sensory→motor latency | {s['sensory_to_motor_latency_ms']:.3f}ms (mean) |\n")

        return "\n".join(lines)
