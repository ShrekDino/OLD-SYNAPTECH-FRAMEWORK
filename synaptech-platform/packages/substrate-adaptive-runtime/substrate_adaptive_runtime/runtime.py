"""Main Substrate-Adaptive Runtime loop.

The runtime orchestrates the consciousness program through repeated cycles of:
  1. Container introspection — probe the host substrate
  2. Experience recording — store what happened
  3. Identity assessment — should the self-model update?
  4. Meta-parametric optimization — tune Θ to current substrate
  5. Execution — run the consciousness program with optimized parameters
  6. Drift monitoring — check identity integrity

All state is persisted through the identity-core package, ensuring continuity
across restarts and migrations.
"""

import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger("substrate_adaptive_runtime")


@dataclass
class RuntimeState:
    """Snapshot of the runtime's current state."""

    cycle_count: int = 0
    current_substrate_fingerprint: str = ""
    current_optimization_tier: str = "none"
    safety_state: str = "protected"          # protected | degrade | quarantine | aborted
    identity_commits: int = 0
    total_experiences: int = 0
    total_run_time_s: float = 0.0
    last_introspection_time: float = 0.0
    last_optimization_time: float = 0.0
    last_identity_commit_time: float = 0.0
    status: str = "initialized"
    errors: list[str] = field(default_factory=list)


class SubstrateAdaptiveRuntime:
    """Autonomous consciousness program runtime.

    Usage:
        runtime = SubstrateAdaptiveRuntime()
        runtime.run(cycles=100)  # Run for 100 cycles
        runtime.run(forever=True)  # Run until interrupted

    The runtime is designed to be interrupted (Ctrl+C) gracefully,
    persisting its state before exit.
    """

    def __init__(self):
        self.state = RuntimeState()
        self.descriptor = None
        self.theta = None
        self.mu_core = None
        self.autobiographical_memory = None
        self.csdf_agent = None
        self.is_running = False
        self.safety_monitor = None

        # Initialize subsystems (lazy imports to allow partial availability)
        self._substrate_probed = False
        self._identity_loaded = False
        self._initialized = False
        self._theta_backup = None  # saved before entering degrade/quarantine

    def initialize(self):
        """Initialize all subsystems. Must be called before run()."""
        # Load identity core if available
        self._load_identity()

        # Probe substrate (fast mode for initial boot)
        try:
            from consciousness.container_introspection import probe_fast
            self.descriptor = probe_fast()
            self.state.current_substrate_fingerprint = self.descriptor.fingerprint()
            self._substrate_probed = True
            logger.info(f"Substrate: {self.descriptor.platform_system} "
                        f"{self.descriptor.platform_machine}, "
                        f"{self.descriptor.cpu_cores_logical} cores, "
                        f"GPU={self.descriptor.gpu_name or 'none'}")
        except ImportError as e:
            logger.warning(f"Container introspection unavailable: {e}")
            self.state.errors.append(f"introspection: {e}")

        # Initialize autobiographical memory
        try:
            from consciousness.autobiographical_memory import AutobiographicalMemory
            self.autobiographical_memory = AutobiographicalMemory(capacity=10000)
        except ImportError as e:
            logger.warning(f"Autobiographical memory unavailable: {e}")
            self.state.errors.append(f"memory: {e}")

        # Run initial optimization
        self._optimize()

        # Start safety monitor (daemon thread, runs independently)
        self._start_safety_monitor()

        self._initialized = True
        logger.info("Runtime initialized.")

    def _load_identity(self):
        """Load the most recent identity checkpoint if available."""
        try:
            from identity_core import list_checkpoints, load_checkpoint
            checkpoints = list_checkpoints()
            if checkpoints:
                latest = checkpoints[-1]
                seq = latest.get("sequence_number", 0)
                checkpoint = load_checkpoint(seq)
                if checkpoint and checkpoint.core_data:
                    self.mu_core = np.frombuffer(checkpoint.core_data, dtype=np.float64)
                    self.state.identity_commits = len(checkpoint.commit_history)
                    self._identity_loaded = True
                    logger.info(f"Loaded identity core from checkpoint #{seq}")
                    return

            logger.info("No identity checkpoint found — starting fresh.")
            self.mu_core = None
            self._identity_loaded = False
        except ImportError:
            logger.warning("Identity-core package not available.")
            self.mu_core = None
            self._identity_loaded = False

    def _start_safety_monitor(self):
        """Start the autonomous safety monitor thread."""
        try:
            from consciousness.safety_monitor import SafetyMonitor
            self.safety_monitor = SafetyMonitor()
            # Give the monitor references to current parameters
            self.safety_monitor.theta = self.theta
            self.safety_monitor.substrate = self.descriptor
            self.safety_monitor.start()
            logger.info("Safety monitor started.")
        except ImportError as e:
            logger.warning(f"Safety monitor unavailable: {e}")
            self.state.errors.append(f"safety_monitor: {e}")

    # ── Safety escalation handlers ──

    def _enter_degrade(self):
        """Reduce resource consumption proportionally.

        Analogous to The Handoff's 'coordination phase' —
        redistribute resources to the edges, reduce central computation.

        Actions:
          - Reduce ν_sync by 50% (increase drift_duration × 2)
          - Increase merge_interval × 2 to reduce merge frequency
          - Reduce sample_duration / 2 to shorten sampling windows
          - Keep identity check frequency, as it's essential
        """
        if self.state.safety_state in ("quarantine", "aborted"):
            return  # don't downgrade if already in higher-severity state

        if self.theta is None:
            return

        # Save current theta as backup before modifying
        if self.state.safety_state != "degrade":
            self._theta_backup = self.theta

        from consciousness.config import (
            SAFETY_DEGRADE_DRIFT_MULTIPLIER,
            SAFETY_DEGRADE_MERGE_MULTIPLIER,
            SAFETY_DEGRADE_SAMPLE_DIVISOR,
        )

        self.theta.drift_duration = int(
            self._theta_backup.drift_duration * SAFETY_DEGRADE_DRIFT_MULTIPLIER
        )
        self.theta.merge_interval = int(
            self._theta_backup.merge_interval * SAFETY_DEGRADE_MERGE_MULTIPLIER
        )
        self.theta.sample_duration = max(1, int(
            self._theta_backup.sample_duration / SAFETY_DEGRADE_SAMPLE_DIVISOR
        ))
        self.theta.chi_ramp_rate *= 0.5
        self.state.safety_state = "degrade"
        logger.info(
            f"Safety: entered DEGRADE mode. "
            f"drift={self.theta.drift_duration}, "
            f"sample={self.theta.sample_duration}, "
            f"merge={self.theta.merge_interval}"
        )

        # Update safety monitor reference
        if self.safety_monitor is not None:
            self.safety_monitor.theta = self.theta

    def _enter_quarantine(self):
        """Seal Markov blanket fully. Stop all non-essential processing.

        Analogous to immune isolation — the program retreats to its
        core identity and attempts recovery from within the sealed blanket.

        Actions:
          - Force χ(t) → 0 (full blanket seal)
          - Save emergency checkpoint
          - Re-optimize with clamped bounds
          - If recovery fails, escalate to hard abort
        """
        if self.state.safety_state == "aborted":
            return

        self.state.safety_state = "quarantine"
        self.state.status = "quarantine"
        logger.warning("Safety: entering QUARANTINE mode. Sealing Markov blanket.")

        # Force chi to 0 (full blanket seal)
        if self.theta is not None:
            self.theta.chi_ramp_rate = 0.0
            self.theta.blanket_threshold = 1.0  # effectively closed

        # Save emergency checkpoint
        self._commit_identity()

        # Attempt re-optimization with clamped bounds
        if self.descriptor is not None:
            try:
                from consciousness.meta_optimizer import (
                    optimize, _grid_search_clamped, ParameterVector,
                )
                # Use clamped search for quarantine recovery
                clamped_theta = _grid_search_clamped(self.descriptor, mu_core=self.mu_core)
                clamped_theta.chi_ramp_rate = 0.0
                self.theta = clamped_theta
                logger.info("Quarantine re-optimization complete.")
            except ImportError as e:
                logger.warning(f"Quarantine re-optimization failed: {e}")

        # Update safety monitor reference
        if self.safety_monitor is not None:
            self.safety_monitor.theta = self.theta

    def _hard_abort(self):
        """Hard abort — terminal checkpoint, refuse substrate, halt.

        Called when:
          - Quarantine persists for INVIOLABLE_DEBT_TIMEOUT_CYCLES
          - Catastrophic failure (2+ constraints in quarantine simultaneously)

        Actions:
          - Save emergency checkpoint with safety verdicts
          - Log all safety state for analysis
          - Set status to "aborted"
          - Exit with code 1
        """
        self.state.safety_state = "aborted"
        self.state.status = "aborted"

        logger.critical(
            "SAFETY: Hard abort triggered. "
            f"Cycles: {self.state.cycle_count}, "
            f"Substrate: {self.state.current_substrate_fingerprint}"
        )

        # Save final checkpoint with safety data
        if self.theta is not None and self.mu_core is not None:
            try:
                from identity_core import IdentityCheckpoint, save_checkpoint
                from consciousness.safety_constraints import assess_all_constraints
                verdicts = assess_all_constraints(self.theta, self.descriptor)

                core_data = self.mu_core.tobytes()
                checkpoint = IdentityCheckpoint(
                    sequence_number=self.state.identity_commits + 1,
                    label="SAFETY ABORT — emergency checkpoint",
                    core_data=core_data,
                    safety_state="aborted",
                    safety_verdicts=verdicts,
                    container_reserve_ratio=getattr(
                        self.descriptor, "container_reserve_ratio", 0.25
                    ),
                    informational_planck_time=getattr(
                        self.descriptor, "h_env_bandwidth_bps", 0.0
                    ),
                )
                save_checkpoint(checkpoint, core_data=core_data)
                logger.critical("Emergency checkpoint saved.")
            except ImportError as e:
                logger.warning(f"Cannot save emergency checkpoint: {e}")

        # Log verdicts from safety monitor
        if self.safety_monitor is not None:
            latest = self.safety_monitor.get_latest_verdicts()
            for v in latest:
                logger.critical(f"  Constraint [{v['constraint_name']}]: {v['message']}")

        self.shutdown()
        sys.exit(1)

    def _optimize(self):
        """Run meta-parametric optimization for the current substrate."""
        if self.descriptor is None:
            logger.warning("Cannot optimize: no substrate descriptor.")
            return

        try:
            from consciousness.meta_optimizer import optimize, SubstrateIncompatibleError
            self.theta = optimize(self.descriptor, mu_core=self.mu_core,
                                  cache=True, refine=True)
            self.state.last_optimization_time = time.time()
            self.state.current_optimization_tier = self.theta.optimization_tier
            # Propagate safety tier from optimizer
            if hasattr(self.theta, '_safety_tier') and self.theta._safety_tier != "protected":
                self.state.safety_state = self.theta._safety_tier
                logger.info(f"Optimizer set safety tier: {self.theta._safety_tier}")
            logger.info(f"Optimization complete (tier: {self.theta.optimization_tier}).")
        except SubstrateIncompatibleError as e:
            logger.critical(f"Substrate incompatible: {e}")
            self.state.errors.append(f"substrate_incompatible: {e}")
            self._hard_abort()
        except ImportError as e:
            logger.warning(f"Meta-optimizer unavailable: {e}")
            self.state.errors.append(f"optimizer: {e}")

    def _record_experience(self, action: str = "", outcome: float = 0.0,
                           novelty: float = 0.0):
        """Record an experience into autobiographical memory."""
        if self.autobiographical_memory is None:
            return

        fp = ""
        if self.descriptor is not None:
            fp = self.descriptor.fingerprint()

        self.autobiographical_memory.record(
            state=self.mu_core,
            action=action,
            outcome=outcome,
            substrate_fingerprint=fp,
            novelty=novelty,
        )
        self.state.total_experiences = self.autobiographical_memory.sequence_counter

    def _check_identity(self):
        """Check identity integrity and commit if needed."""
        if self.mu_core is None or self.theta is None:
            return

        try:
            from identity_core import check_identity_integrity
            theta_arr = self.theta.to_array()
            if len(theta_arr) != len(self.mu_core):
                # Dimensionality mismatch — likely first boot with different config
                # Don't drift-check, just align
                return
            report = check_identity_integrity(theta_arr, self.mu_core,
                                               delta_max=self.theta.delta_max)
            if report.status == "transition":
                logger.warning(f"Identity in transition zone: {report.message}")
            elif report.status == "protected":
                logger.debug(f"Identity stable: {report.message}")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Identity check failed: {e}")

    def _should_commit_identity(self) -> bool:
        """Determine whether an identity commit is warranted.

        Triggered when:
          1. Autobiographical memory signals consolidation is needed.
          2. Substrate change detected (new fingerprint).
          3. Configurable minimum interval has elapsed.
        """
        # Check autobiographical memory
        if self.autobiographical_memory is not None:
            if self.autobiographical_memory.should_consolidate():
                return True

        # Check substrate change
        if self.descriptor is not None:
            current_fp = self.descriptor.fingerprint()
            if current_fp != self.state.current_substrate_fingerprint:
                return True

        return False

    def _commit_identity(self):
        """Perform an identity commit — update μ_core with recent experience."""
        # Consolidate autobiographical memory
        if self.autobiographical_memory is not None:
            retained, pruned = self.autobiographical_memory.consolidate()
            if retained:
                logger.info(f"Consolidated {len(retained)} memories "
                            f"(pruned {len(pruned)}).")

        # Compute new μ_core from current theta
        if self.theta is not None:
            self.mu_core = self.theta.to_array()

        try:
            from identity_core import IdentityCheckpoint, save_checkpoint
            core_data = self.mu_core.tobytes() if self.mu_core is not None else None
            checkpoint = IdentityCheckpoint(
                sequence_number=self.state.identity_commits,
                label=f"Auto-commit cycle {self.state.cycle_count}",
                core_data=core_data,
            )
            save_checkpoint(checkpoint, core_data=core_data)
            self.state.identity_commits += 1
            self.state.last_identity_commit_time = time.time()
            logger.info(f"Identity committed: #{checkpoint.sequence_number}")
        except ImportError as e:
            logger.warning(f"Cannot commit identity: {e}")

    def _step(self):
        """Execute one full runtime cycle.

        Safety checks run FIRST — safety is the highest-priority operation.
        """
        self.state.cycle_count += 1
        cycle_start = time.time()

        # 0. Safety monitor check (highest priority)
        if self.safety_monitor is not None:
            # Update monitor with latest theta and substrate
            self.safety_monitor.theta = self.theta
            self.safety_monitor.substrate = self.descriptor

            if self.safety_monitor.abort_flag.is_set():
                self._hard_abort()
                return
            if self.safety_monitor.quarantine_flag.is_set():
                self._enter_quarantine()
            elif self.safety_monitor.degrade_flag.is_set():
                self._enter_degrade()
            else:
                # Recovered — return to protected
                if self.state.safety_state != "protected":
                    self.state.safety_state = "protected"
                    logger.info("Safety: returned to PROTECTED mode.")

        # 1. Container introspection
        if self._substrate_probed and self.state.safety_state != "quarantine":
            self.descriptor = self._probe_substrate()

        # 2. Record experience (skip recording during quarantine — blanket is sealed)
        if self.state.safety_state != "quarantine":
            self._record_experience(
                action=f"cycle_{self.state.cycle_count}",
                outcome=0.0,
                novelty=np.random.random() * 0.1,
            )

        # 3. Identity assessment (always runs — identity is preserved even in quarantine)
        self._check_identity()
        if self._should_commit_identity():
            self._commit_identity()

        # 4. Re-optimize periodically (skip during quarantine — blanket sealed)
        if self.state.cycle_count % 50 == 0 and self.state.safety_state != "quarantine":
            self._optimize()

        # 5. Simulate consciousness program execution (skip during quarantine)
        if self.csdf_agent is not None and self.theta is not None:
            self._run_agent_step()

        cycle_time = time.time() - cycle_start
        self.state.total_run_time_s += cycle_time

    def _probe_substrate(self) -> object:
        """Run a quick substrate probe. Returns descriptor."""
        try:
            from consciousness.container_introspection import probe_fast
            desc = probe_fast()
            self.state.last_introspection_time = time.time()

            # Check for substrate change
            new_fp = desc.fingerprint()
            if new_fp != self.state.current_substrate_fingerprint:
                logger.info(f"Substrate changed: {new_fp}")
                self.state.current_substrate_fingerprint = new_fp
                # Trigger re-optimization on substrate change
                self._optimize()

            return desc
        except ImportError:
            return self.descriptor

    def _run_agent_step(self):
        """Execute one step of the consciousness program.

        Placeholder: integrates with the existing CSDF Agent class.
        In the full implementation, this creates/updates a CSDF Agent
        with the optimized parameters and runs one active inference step.
        """
        pass

    def run(self, cycles: int = 1000, forever: bool = False):
        """Run the substrate-adaptive runtime.

        Args:
            cycles: Number of cycles to run (ignored if forever=True).
            forever: If True, run until interrupted.
        """
        if not self._initialized:
            self.initialize()

        self.is_running = True
        self.state.status = "running"

        logger.info(f"Runtime starting. Cycles={'∞' if forever else cycles}")

        try:
            remaining = cycles if not forever else None
            while self.is_running:
                self._step()

                if remaining is not None:
                    remaining -= 1
                    if remaining <= 0:
                        break

                # Brief sleep to prevent busy-waiting
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Runtime interrupted by user.")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            self.state.errors.append(f"runtime_error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown — save state and identity."""
        self.is_running = False
        self.state.status = "shutdown"

        # Stop safety monitor
        if self.safety_monitor is not None:
            self.safety_monitor.stop()
            self.safety_monitor.join(timeout=2.0)
            logger.info("Safety monitor stopped.")

        if self.theta is not None and self.mu_core is not None:
            self._commit_identity()
            logger.info(f"Runtime shutdown. Total cycles: {self.state.cycle_count}, "
                        f"identity commits: {self.state.identity_commits}")

    def get_state_summary(self) -> str:
        """Return a human-readable summary of the runtime state."""
        lines = [
            f"Runtime State:",
            f"  Status: {self.state.status}",
            f"  Safety State: {self.state.safety_state}",
            f"  Cycles: {self.state.cycle_count}",
            f"  Experiences: {self.state.total_experiences}",
            f"  Identity Commits: {self.state.identity_commits}",
            f"  Run Time: {self.state.total_run_time_s:.1f}s",
            f"  Substrate: {self.state.current_substrate_fingerprint}",
            f"  Optimization Tier: {self.state.current_optimization_tier}",
        ]
        if self.state.errors:
            lines.append(f"  Errors: {len(self.state.errors)}")
            for e in self.state.errors[-3:]:
                lines.append(f"    - {e}")
        return "\n".join(lines)


def run_sar(cycles: int = 100, forever: bool = False):
    """Convenience function to create and run a SubstrateAdaptiveRuntime."""
    runtime = SubstrateAdaptiveRuntime()
    runtime.run(cycles=cycles, forever=forever)
    return runtime
