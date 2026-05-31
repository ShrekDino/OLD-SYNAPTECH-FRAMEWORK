import math
import signal
import time
import torch
import numpy as np

from lib.environment import DetailedFlyBody
from lib.motor_decoder import MotorDecoder, MOTOR_MAP
from lib.sensory_feedback import build_closed_loop_input
from lib.behaviors import BehaviorStateMachine
from lib.runtime_logger import RuntimeLogger
from lib.visualizer_bridge import MotorBroadcaster, StimulusReceiver

MOTOR_KEYS = sorted(MOTOR_MAP.keys())       # fixed-order columns for the logger
MOTOR_CHANNELS = len(MOTOR_KEYS)


class RealtimeEngine:
    """60 Hz wall-clock-regulated closed-loop simulation engine.

    Zero-copy philosophy
    --------------------
    - The connectome weight matrix (W^T) lives in VRAM permanently.
    - The activity vector stays on the GPU between ticks — never copied
      back to the host except for motor decoding and logging.
    - Sensory injection (N=78 floats, ~312 B) is the only host→device
      transfer per tick (non-blocking stream).
    - Motor decoding pulls *only the 12 scalar motor values* across
      device→host per tick — the full activity vector is *not* copied.
    - The activity history ring buffer is updated on the CPU side from
      a GPU→CPU copy of the activity vector (78 floats × 4 B = 312 B/tick
      = ~18 KB/s at 60 Hz — negligible bandwidth).

    Tick budget (@ 60 Hz)
    ---------------------
    Target wall time per tick:   16,667 µs
    GPU matmul + activation:        ~50 µs
    Sensory injection + copy:       ~10 µs
    Motor decode (GPU→CPU):         ~10 µs
    Body physics (CPU):             ~50 µs
    Logging (CPU ring buffer):       ~5 µs
    Safety margin:                >16,500 µs
    """

    def __init__(
        self,
        gpu_sim,
        neuropil_names: list,
        tick_rate: int = 60,
        device: str = 'cuda',
        initial_kick_strength: float = 0.3,
        baseline_current: float = 0.15,
        ambient_noise: float = 0.03,
        enable_viz: bool = False,
        viz_port: int = 5555,
        stimulus_port: int = 5556,
    ):
        self.brain = gpu_sim
        self.names = neuropil_names
        self.n = len(neuropil_names)
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.tick_interval = 1.0 / tick_rate
        self.target_tick_rate = tick_rate
        self.initial_kick_strength = initial_kick_strength
        self.baseline_current = baseline_current
        self.ambient_noise = ambient_noise

        # --- Sub-systems (all CPU-resident) ---
        self.body = DetailedFlyBody()
        self.decoder = MotorDecoder(neuropil_names)
        self.behavior_fsm = BehaviorStateMachine()

        # Pre-compute neuropil name → index map for modulation lookups
        self._np_map = {n: i for i, n in enumerate(neuropil_names)}

        # Pre-compute GPU gather indices for motor decode
        # ZERO-COPY: only the ~20 activity entries needed for motor decoding
        # are indexed on-GPU; the full 78-vector never crosses PCIe for decode.
        self._motor_gather_idxs = self._build_motor_gather_indices()

        # --- State ---
        self.brain.reset()
        self.tick_count = 0
        self.running = False
        self.feeding_modulation = 0.0

        # Logger (attached externally or created on start)
        self.logger: RuntimeLogger | None = None

        # Visualizer bridge (non-blocking UDP broadcaster)
        # ZERO-BLOCKING: push() is O(1) — JSON serialization + sendto happen
        # in a background daemon thread.
        self.broadcaster: MotorBroadcaster | None = None
        self.stimulus: StimulusReceiver | None = None
        if enable_viz:
            self.broadcaster = MotorBroadcaster(port=viz_port)
            self.stimulus = StimulusReceiver(port=stimulus_port)

        # Per-tick metrics tracked for the HUD broadcast
        self._current_firing_rate: float = 0.0
        self._current_latency_ms: float = 0.0

        # Periodic print throttling
        self._last_print_time: float = 0.0

        # SIGINT handling
        self._orig_sigint = None

    # ------------------------------------------------------------------
    # Motor gather indices (GPU-side, built once)
    # ------------------------------------------------------------------

    def _build_motor_gather_indices(self):
        gather = {}
        for name, spec in MOTOR_MAP.items():
            idxs = []
            if spec['transform'] in ('mean', 'max'):
                idxs = [self._np_map[s] for s in spec['sources'] if s in self._np_map]
            elif spec['transform'] == 'asymmetry':
                l_idxs = [self._np_map[s] for s in spec['sources_left'] if s in self._np_map]
                r_idxs = [self._np_map[s] for s in spec['sources_right'] if s in self._np_map]
                idxs = l_idxs + r_idxs
            gather[name] = torch.tensor(idxs, dtype=torch.long, device=self.device) if idxs else None
        return gather

    # ------------------------------------------------------------------
    # GPU motor decoder  (only M scalar values cross device→host)
    # ------------------------------------------------------------------

    def _decode_motor_gpu(self, activity_gpu):
        """Decode motor commands using GPU tensor ops.

        ZERO-COPY: only ``len(MOTOR_MAP)`` ≈ 12 floats cross device→host.
        """
        raw = {}
        for name, spec in MOTOR_MAP.items():
            idxs = self._motor_gather_idxs.get(name)
            if idxs is None or len(idxs) == 0:
                raw[name] = 0.0
                continue

            # Gather only the needed activity entries — O(k) where k ≤ 6
            vals = activity_gpu.index_select(0, idxs)

            if spec['transform'] == 'mean':
                val = vals.mean().item()                       # 1 scalar → CPU
            elif spec['transform'] == 'max':
                val = vals.max().item()                        # 1 scalar → CPU
            elif spec['transform'] == 'asymmetry':
                n_left = len(spec.get('sources_left', []))
                l_val = vals[:n_left].mean()
                r_val = vals[n_left:].mean()
                val = (l_val - r_val).item()                   # 1 scalar → CPU

            lo, hi = spec['range']
            if lo >= 0 or spec['transform'] != 'asymmetry':
                val = lo + np.clip(val, 0.0, 1.0) * (hi - lo)
            else:
                clipped = np.clip(val, -1.0, 1.0)
                val = lo + (clipped + 1.0) * 0.5 * (hi - lo)
            raw[name] = val

        # --- Apply smoothing & bout logic (replicates MotorDecoder.decode) ---
        raw_speed = raw.get('walking_speed', 0.0)
        raw_cleaning = raw.get('face_cleaning_drive', 0.0)
        raw_feeding = raw.get('proboscis_extension', 0.0)

        if raw_feeding > 0.4 and raw_speed < 0.1:
            self.decoder._cleaning_bout_timer = 0
        elif raw_cleaning > 0.3 and raw_speed < 0.05:
            self.decoder._cleaning_bout_timer = 60
        elif self.decoder._cleaning_bout_timer > 0:
            self.decoder._cleaning_bout_timer -= 1
            if self.decoder._cleaning_bout_timer > 0:
                raw['face_cleaning_drive'] = max(raw_cleaning, 0.4)

        DECAY = 0.92
        MIN_SPEED = 0.02
        for k in self.decoder.smoothed:
            target = raw[k]
            if k == 'walking_speed' and target < MIN_SPEED:
                target = 0.0
            self.decoder.smoothed[k] = self.decoder.smoothed[k] * DECAY + target * (1 - DECAY)

        return dict(self.decoder.smoothed)

    # ------------------------------------------------------------------
    # Behaviour modulation (replicates ClosedLoopSimulation logic)
    # ------------------------------------------------------------------

    def _apply_behavior_modulation(self, I_eff, state):
        if state == 'FEEDING':
            self.feeding_modulation = min(1.0, self.feeding_modulation + 0.005)
            for key in ['PRW_L', 'PRW_R', 'SAD_L', 'SAD_R']:
                if key in self._np_map:
                    I_eff[self._np_map[key]] += 0.3 * self.feeding_modulation
        else:
            self.feeding_modulation = max(0.0, self.feeding_modulation - 0.005)

        if state == 'FACE_CLEANING':
            for key in ['VPS_L', 'VPS_R', 'PMS_L', 'PMS_R']:
                if key in self._np_map:
                    I_eff[self._np_map[key]] += 0.25

    # ------------------------------------------------------------------
    # Virtual-arena stimulus injection (visualizer mouse → neuropils)
    # ------------------------------------------------------------------

    # Neuropil targets for directional stimulus mapping.
    # These map a world-space cursor to sensory channels in the 78-neuron
    # connectome, creating a directional "attractor" the fly steers toward.
    _STIM_VISUAL_FRONT = ["OCG", "AOTU_L", "AOTU_R", "AME_L", "AME_R"]
    _STIM_VISUAL_LEFT  = ["LO_L", "ME_L", "AL_L"]
    _STIM_VISUAL_RIGHT = ["LO_R", "ME_R", "AL_R"]
    _STIM_GUSTATORY    = ["PRW", "SAD", "GNG"]

    def _apply_stimulus_injection(self, I_eff: np.ndarray) -> np.ndarray:
        """Read the latest mouse-driven stimulus and inject current into
        targeted sensory neuropil channels.

        The stimulus is a world-space click position.  The injection maps
        the direction-from-fly and distance to specific neuropil groups:

            Front (+fwd)  →   occeli / optic-tegmentum  (OCG, AOTU)
            Left  (+left) →   left LO, ME, AL
            Right (-left) →   right LO, ME, AL
            Close range   →   gustatory / SEZ (PRW, SAD, GNG)

        All injections land in ``I_eff`` on the CPU *before* the GPU
        transfer — zero additional GPU round-trips per tick.
        """
        if self.stimulus is None:
            return I_eff
        target = self.stimulus.latest
        if target is None:
            return I_eff

        tx, ty = target
        fx = float(self.body.pos[0])
        fy = float(self.body.pos[1])
        heading = float(self.body.heading)

        dx = tx - fx
        dy = ty - fy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.001:
            return I_eff

        # Direction in the fly's body frame
        cos_h = math.cos(heading)
        sin_h = math.sin(heading)
        fwd  = ( dx * cos_h + dy * sin_h) / dist   # +1 = dead ahead
        left = (-dx * sin_h + dy * cos_h) / dist   # +1 = fly's left

        # Chase mode: constant-strength proportional steering
        np_map = self._np_map
        target_angle = math.atan2(dy, dx)
        bearing = target_angle - heading
        bearing = math.atan2(math.sin(bearing), math.cos(bearing))

        # Front visual field (always-on sensory input for chase)
        if fwd > 0.05:
            inj = fwd * 0.8
            for key in self._STIM_VISUAL_FRONT:
                if key in np_map:
                    I_eff[np_map[key]] += inj

        # Lateral visual / olfactory (left vs right)
        if left > 0.05:
            inj = left * 0.5
            for key in self._STIM_VISUAL_LEFT:
                if key in np_map:
                    I_eff[np_map[key]] += inj
        elif left < -0.05:
            inj = abs(left) * 0.5
            for key in self._STIM_VISUAL_RIGHT:
                if key in np_map:
                    I_eff[np_map[key]] += inj

        # Direct LAL steering injection — proportional bearing control
        # Strong turn even for small bearing errors; saturates at ~23°.
        if 'LAL_L' in np_map and 'LAL_R' in np_map:
            lal_inj = 1.5 * min(1.0, abs(bearing) * 2.5)
            if bearing > 0.05:
                I_eff[np_map['LAL_L']] += lal_inj
            elif bearing < -0.05:
                I_eff[np_map['LAL_R']] += lal_inj

        # Close-range gustatory / feeding
        if dist < 0.5:
            inj = (1.0 - dist / 0.5) * 0.4
            for key in self._STIM_GUSTATORY:
                if key in np_map:
                    I_eff[np_map[key]] += inj

        return I_eff

    # ------------------------------------------------------------------
    # CUDA warmup
    # ------------------------------------------------------------------

    def warmup(self, n_dummy=10):
        """Fire dummy tensors through the entire GPU pipeline to pre-compile
        all JIT kernels (sparse MM, gather, reduce, .item()) *before* the
        real-time loop.

        These ticks are invisible to the RuntimeLogger — no state in the
        body, decoder, FSM, or tick counter is affected.

        Parameters
        ----------
        n_dummy : int
            Number of warm-up steps (default 10, empirically sufficient for
            CUDA context init + PyTorch JIT + memory pre-allocation).
        """
        z = torch.zeros(self.n, device=self.device)
        self.brain.reset()
        for _ in range(n_dummy):
            a = self.brain.step(z)
            # Warm the full decode pipeline including .item() CUDA sync
            _ = self._decode_motor_gpu(a)
        # Re-initialise activity for the real loop after warm-up
        self.brain.reset()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _signal_handler(self, signum, frame):
        print("\n[SIGINT] Graceful shutdown requested — stopping tick loop...")
        self.running = False

    def start(self, logger=None, max_ticks=None, warmup=True):
        """Run the real-time loop until interrupted or *max_ticks* elapse.

        Parameters
        ----------
        logger : RuntimeLogger, optional
            If provided, metrics are recorded and dumped on exit.
        max_ticks : int, optional
            Automatically stop after this many ticks.
        warmup : bool
            Run 10 dummy CUDA ticks before the real loop to eliminate
            context-initialisation latency spikes (default True).
        """
        self.logger = logger

        # --- CUDA warm-up (eliminates first-tick latency spike) ---
        if warmup:
            t0 = time.perf_counter()
            self.warmup()
            dt = time.perf_counter() - t0
            print(f"[RealtimeEngine] CUDA warm-up complete ({dt*1000:.1f} ms)")

        # --- SIGINT registration ---
        self._orig_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.running = True
        self.tick_count = 0
        self.feeding_modulation = 0.0
        self.brain.reset()

        # --- Equalise LAL_L / LAL_R to prevent innate circular bias ---
        np_map = self._np_map
        if 'LAL_L' in np_map and 'LAL_R' in np_map:
            ll = self.brain.activity[np_map['LAL_L']].item()
            lr = self.brain.activity[np_map['LAL_R']].item()
            avg = (ll + lr) * 0.5
            self.brain.activity[np_map['LAL_L']] = avg
            self.brain.activity[np_map['LAL_R']] = avg

        print(f"[RealtimeEngine] Starting {self.target_tick_rate} Hz loop "
              f"on {self.device}")

        while self.running:
            if max_ticks is not None and self.tick_count >= max_ticks:
                self.running = False
                break
            tick_start = time.perf_counter()

            # ----------------------------------------------------------
            # 1. Body state → sensory injection (CPU)
            # ----------------------------------------------------------
            sensory = build_closed_loop_input(
                self.names, self.body.get_sensory_state(),
            )
            # ZERO-COPY: sensory is a 78-element numpy array; we transfer it
            # to the GPU inside brain.step() as a non-blocking copy.
            I_eff = sensory.copy()

            # --- Behaviour state modulation (CPU, in-place on I_eff) ---
            motor_raw = self._decode_motor_gpu(self.brain.activity)
            changed = self.behavior_fsm.update(motor_raw)
            state = self.behavior_fsm.state
            self._apply_behavior_modulation(I_eff, state)

            # --- Ramp (matches closed_loop.py: min(1.0, t/20)) ---
            ramp = min(1.0, self.tick_count / 20.0)
            I_eff = I_eff * ramp

            # --- Initial kick (first 30 ticks) ---
            if self.tick_count < 30:
                decay = 1.0 - self.tick_count / 30.0
                for key in ['GNG_L', 'GNG_R', 'VES_L', 'VES_R']:
                    if key in np_map:
                        I_eff[np_map[key]] += self.initial_kick_strength * decay

            # --- Ambient baseline current (keeps connectome from going silent) ---
            # A steady metabolic current + per-channel Gaussian noise ensures
            # spontaneous firing even when sensory feedback is near zero.
            I_eff += self.baseline_current
            I_eff += np.random.normal(0.0, self.ambient_noise, self.n).astype(np.float32)

            # --- Virtual-arena stimulus injection (mouse-driven, if active) ---
            # Maps the visualizer cursor into targeted neuropil currents.
            self._apply_stimulus_injection(I_eff)

            I_eff = np.clip(I_eff, 0.0, 1.0)

            # ----------------------------------------------------------
            # 2. GPU brain step  (all VRAM, no host round-trip)
            # ----------------------------------------------------------
            activity_gpu = self.brain.step(I_eff)

            # --- Direct GPU steering override (bypasses sigmoid compression) ---
            if self.stimulus is not None and self.stimulus.active and self.stimulus.target is not None:
                tx, ty = self.stimulus.target
                fx = float(self.body.pos[0])
                fy = float(self.body.pos[1])
                heading = float(self.body.heading)
                dx = tx - fx
                dy = ty - fy
                if math.sqrt(dx * dx + dy * dy) > 0.001:
                    target_angle = math.atan2(dy, dx)
                    bearing = target_angle - heading
                    bearing = math.atan2(math.sin(bearing), math.cos(bearing))
                    if 'LAL_L' in np_map and 'LAL_R' in np_map:
                        if bearing > 0.05:
                            activity_gpu[np_map['LAL_L']] = 1.0
                        elif bearing < -0.05:
                            activity_gpu[np_map['LAL_R']] = 1.0

            # ----------------------------------------------------------
            # 3. Motor decode (GPU → CPU, M scalars only)
            # ----------------------------------------------------------
            motor = self._decode_motor_gpu(activity_gpu)
            motor['_behavior_state'] = state

            # --- Equalise LAL_L/R on GPU to prevent asymmetric drift ---
            if 'LAL_L' in np_map and 'LAL_R' in np_map:
                l_idx = np_map['LAL_L']
                r_idx = np_map['LAL_R']
                avg = (activity_gpu[l_idx] + activity_gpu[r_idx]) * 0.5
                activity_gpu[l_idx] = avg
                activity_gpu[r_idx] = avg

            # --- Chase speed boost / stop-to-feed ---
            if self.stimulus is not None and self.stimulus.active and self.stimulus.target is not None:
                tx, ty = self.stimulus.target
                dx = tx - float(self.body.pos[0])
                dy = ty - float(self.body.pos[1])
                chase_dist = math.sqrt(dx * dx + dy * dy)
                if chase_dist > 0.3:
                    motor['walking_speed'] = min(1.0, motor['walking_speed'] * 3.0)
                else:
                    motor['walking_speed'] = 0.0
                    motor['proboscis_extension'] = 1.0

            # ----------------------------------------------------------
            # 4. Body physics (CPU)
            # ----------------------------------------------------------
            self.body.step(motor, dt=self.tick_interval)

            # ----------------------------------------------------------
            # 5. Pull activity to CPU for logging & diagnostics
            #     (78 × float32 = 312 B — negligible at 60 Hz)
            # ----------------------------------------------------------
            activity_cpu = activity_gpu.cpu().numpy().astype(np.float32)
            if self.logger is not None:
                tick_elapsed = time.perf_counter() - tick_start
                motor_arr = np.array([motor.get(k, 0.0) for k in MOTOR_KEYS],
                                     dtype=np.float32)
                self.logger.tick(activity_cpu, I_eff.astype(np.float32),
                                 motor_arr, tick_elapsed)

            # ----------------------------------------------------------
            # 6. Broadcast motor + body state + investor metrics to
            #    visualizer (non-blocking).
            #     ZERO-BLOCKING: push() is O(1) queue.put_nowait — the
            #     background daemon thread handles JSON + sendto.
            # ----------------------------------------------------------
            if self.broadcaster is not None:
                self._current_firing_rate = float(activity_cpu.mean())
                self._current_latency_ms = tick_elapsed * 1000.0
                payload = {
                    "t": self.tick_count,
                    "pos": (float(self.body.pos[0]), float(self.body.pos[1])),
                    "heading": float(self.body.heading),
                    "gait_cycle": float(self.body.gait_cycle),
                    "pose": state,
                    "firing_rate": self._current_firing_rate,
                    "latency_ms": self._current_latency_ms,
                    **{k: float(v) for k, v in motor.items()
                       if k != "_behavior_state"},
                }
                # Include current stimulus target if one is active
                if self.stimulus is not None and self.stimulus.active:
                    tx, ty = self.stimulus.target
                    payload["tx"] = float(tx)
                    payload["ty"] = float(ty)
                    payload["stimulus_active"] = 1
                self.broadcaster.push(payload)

            # ----------------------------------------------------------
            # 7. Wall-clock regulation
            # ----------------------------------------------------------
            tick_elapsed = time.perf_counter() - tick_start
            sleep_time = max(0.0, self.tick_interval - tick_elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

            self.tick_count += 1

            # Optional: print tick rate every 600 ticks
            if self.tick_count % 600 == 0:
                actual_rate = 600.0 / (time.perf_counter() - tick_start + sleep_time + 1e-9)
                print(f"  [{self.tick_count}] {actual_rate:.1f} Hz  |  "
                      f"activity: {activity_cpu.mean():.3f}  |  "
                      f"pose: {state}")

        # --- Loop exited ---
        self._cleanup()
        return self._summary()

    def stop(self):
        """Signal the loop to stop at the next tick boundary."""
        self.running = False

    # ------------------------------------------------------------------
    # Cleanup & summary
    # ------------------------------------------------------------------

    def _cleanup(self):
        signal.signal(signal.SIGINT, self._orig_sigint or signal.SIG_DFL)
        if self.broadcaster is not None:
            self.broadcaster.stop()
        if self.stimulus is not None:
            self.stimulus.stop()
        if self.logger is not None:
            self.logger.finalize()
            path = self.logger.dump()
            print(f"[RealtimeEngine] Session log saved to {path}")

    def _summary(self):
        return {
            "total_ticks": self.tick_count,
            "duration_s": time.perf_counter(),  # approximate
            "final_activity_mean": float(self.brain.activity.mean().item()),
            "final_body_pos": self.body.pos[:2].copy(),
            "final_behavior_state": self.behavior_fsm.state,
        }
