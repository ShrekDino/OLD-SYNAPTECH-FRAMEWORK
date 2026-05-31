# ==============================================================================
# CONSCIOUSNESS DASHBOARD - Substrate-Adaptive Runtime monitor for CSDF
# ==============================================================================
#
# Displays the current substrate descriptor, optimized parameter vector Θ,
# identity coherence meter, commit history, and DSM-6 cross-reference.
# Provides controls for identity commit, checkpoint import/export.
# ==============================================================================

import json
import os
import time
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QTextEdit, QScrollArea,
    QProgressBar, QComboBox, QMessageBox, QFileDialog,
    QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem,
    QFormLayout,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ai_librarian.pyside6_modules.theme_manager import ThemeManager


class CoherenceMeter(QWidget):
    """Visual identity coherence meter showing GWFR distance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Identity Coherence: --")
        self.label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFixedHeight(24)
        layout.addWidget(self.progress)

        self.hint_label = QLabel("Run container introspection to measure identity coherence")
        self.hint_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']}; font-size: 10px;")
        layout.addWidget(self.hint_label)

    def set_coherence(self, distance: float, delta_max: float):
        """Update the coherence meter with a GWFR distance value.

        Args:
            distance: Current GWFR distance (0 = identical).
            delta_max: Maximum allowed deviation threshold.
        """
        pct = min(int((distance / delta_max) * 100), 100)
        self.progress.setValue(pct)
        self.label.setText(f"Identity Coherence: {distance:.3f} / {delta_max:.3f} (δ_max)")

        if pct < 30:
            color = ThemeManager.COLORS['accent_green']
            status = "Protected — Identity stable"
        elif pct < 70:
            color = ThemeManager.COLORS['accent_orange']
            status = "Transition — Identity drifting"
        else:
            color = ThemeManager.COLORS['accent_red']
            status = "Debt — Identity at risk"

        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                color: {ThemeManager.COLORS['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        self.hint_label.setText(status)


class ConsciousnessPanel(QWidget):
    """Consciousness Dashboard panel — monitors the substrate-adaptive runtime."""

    log_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.substrate_data = None
        self.theta_data = None
        self.identity_checkpoints = []
        self.setup_ui()

    def setup_ui(self):
        """Build the consciousness panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Consciousness Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        layout.addWidget(title)

        subtitle = QLabel(
            "Monitoring the substrate-adaptive runtime — container introspection, "
            "meta-parametric optimization, identity coherence."
        )
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        # Row: introspection + identity
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # ── Substrate Info Group ──
        substrate_group = QGroupBox("Container Introspection")
        substrate_group.setStyleSheet(f"""
            QGroupBox {{
                color: {ThemeManager.COLORS['text_primary']};
                font-weight: bold;
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
        sub_layout = QVBoxLayout(substrate_group)

        self.substrate_label = QLabel("No introspection data. Run probe to detect substrate.")
        self.substrate_label.setWordWrap(True)
        self.substrate_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        sub_layout.addWidget(self.substrate_label)

        probe_btn = QPushButton("Run Container Introspection")
        probe_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['accent_blue']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        probe_btn.clicked.connect(self.on_run_introspection)
        sub_layout.addWidget(probe_btn)

        top_row.addWidget(substrate_group, 1)

        # ── Identity Coherence Group ──
        identity_group = QGroupBox("Identity Core")
        identity_group.setStyleSheet(substrate_group.styleSheet())
        id_layout = QVBoxLayout(identity_group)

        self.coherence_meter = CoherenceMeter()
        id_layout.addWidget(self.coherence_meter)

        # Checkpoint controls
        checkpoint_row = QHBoxLayout()
        commit_btn = QPushButton("Identity Commit")
        commit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.COLORS['accent_green']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #16a085;
            }}
        """)
        commit_btn.clicked.connect(self.on_identity_commit)

        export_btn = QPushButton("Export to Vault")
        export_btn.clicked.connect(self.on_export_to_vault)

        checkpoint_row.addWidget(commit_btn)
        checkpoint_row.addWidget(export_btn)
        id_layout.addLayout(checkpoint_row)

        self.commit_count_label = QLabel("No identity commits recorded")
        self.commit_count_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        id_layout.addWidget(self.commit_count_label)

        top_row.addWidget(identity_group, 1)
        scroll_layout.addLayout(top_row)

        # ── Parameter Vector Group ──
        param_group = QGroupBox("Parameter Vector Θ (Optimized)")

        param_group.setStyleSheet(substrate_group.styleSheet())
        param_layout = QVBoxLayout(param_group)

        self.param_text = QTextEdit()
        self.param_text.setReadOnly(True)
        self.param_text.setMaximumHeight(200)
        self.param_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        self.param_text.setText("No parameter vector. Run introspection + optimization first.")
        param_layout.addWidget(self.param_text)

        optimize_btn = QPushButton("Run Meta-Parametric Optimization")
        optimize_btn.clicked.connect(self.on_run_optimization)
        param_layout.addWidget(optimize_btn)

        scroll_layout.addWidget(param_group)

        # ── Checkpoint History Group ──
        history_group = QGroupBox("Identity Checkpoint History")
        history_group.setStyleSheet(substrate_group.styleSheet())
        history_layout = QVBoxLayout(history_group)

        self.checkpoint_list = QListWidget()
        self.checkpoint_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 6px;
            }}
            QListWidget::item:selected {{
                background: {ThemeManager.COLORS['accent_blue']};
            }}
        """)
        self.checkpoint_list.itemClicked.connect(self.on_checkpoint_selected)

        # Safety timer for periodic display update
        self.safety_timer = QTimer(self)
        self.safety_timer.timeout.connect(self.on_refresh_safety)
        self.safety_timer.start(2000)  # every 2 seconds
        history_layout.addWidget(self.checkpoint_list)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.on_refresh_checkpoints)
        history_layout.addWidget(refresh_btn)

        scroll_layout.addWidget(history_group)

        # ── DSM-6 Cross-Reference Group ──
        dsm6_group = QGroupBox("DSM-6 Phenotype Cross-Reference")
        dsm6_group.setStyleSheet(substrate_group.styleSheet())
        dsm6_layout = QVBoxLayout(dsm6_group)

        self.dsm6_text = QTextEdit()
        self.dsm6_text.setReadOnly(True)
        self.dsm6_text.setMaximumHeight(120)
        self.dsm6_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        self.dsm6_text.setText(
            "No DSM-6 profile loaded. Run introspection to evaluate current parameter regime.\n\n"
            "The current parameter vector Θ can be cross-referenced against the CSDF–DSM-6 Bridge "
            "to identify which neuro-somatic phenotype(s) the current configuration corresponds to."
        )
        dsm6_layout.addWidget(self.dsm6_text)

        scroll_layout.addWidget(dsm6_group)

        # ── Safety Constitution Status Group ──
        safety_group = QGroupBox("Safety Constitution — Inviolable Bounds")
        safety_group.setStyleSheet(substrate_group.styleSheet())
        safety_layout = QVBoxLayout(safety_group)

        # Safety state indicator
        self.safety_state_label = QLabel("State: Not monitored")
        self.safety_state_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        safety_layout.addWidget(self.safety_state_label)

        # Four mini progress bars for each constraint
        self.constraint_bars = {}
        constraint_names = [
            ("nyquist_bound", "Nyquist Sampling Bound"),
            ("container_integrity", "Container Integrity"),
            ("sustainability", "Negentropy Sustainability"),
            ("measurement_uncertainty", "Measurement Uncertainty"),
        ]
        for key, display_name in constraint_names:
            row = QHBoxLayout()
            label = QLabel(display_name)
            label.setFixedWidth(200)
            label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(True)
            bar.setFixedHeight(18)
            self.constraint_bars[key] = bar
            row.addWidget(label)
            row.addWidget(bar, 1)
            safety_layout.addLayout(row)

        # Container reserve ratio
        reserve_row = QHBoxLayout()
        reserve_label = QLabel("Container Reserve ρ_container:")
        reserve_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_primary']};")
        self.reserve_value_label = QLabel("0.25 (default)")
        self.reserve_value_label.setStyleSheet(f"color: {ThemeManager.COLORS['text_secondary']};")
        reserve_row.addWidget(reserve_label)
        reserve_row.addWidget(self.reserve_value_label)
        reserve_row.addStretch()
        safety_layout.addLayout(reserve_row)

        # Constitutional constants display
        self.constitution_text = QTextEdit()
        self.constitution_text.setReadOnly(True)
        self.constitution_text.setMaximumHeight(120)
        self.constitution_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ThemeManager.COLORS['bg_secondary']};
                color: {ThemeManager.COLORS['text_primary']};
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid {ThemeManager.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        safety_layout.addWidget(self.constitution_text)

        scroll_layout.addWidget(safety_group)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    # ── Actions ──

    def on_run_introspection(self):
        """Run container introspection and display results."""
        self.log_message.emit("Running container introspection...")
        try:
            from consciousness.container_introspection import probe_fast
            desc = probe_fast()
            self.substrate_data = desc
            lines = [
                f"Platform: {desc.platform_system} ({desc.platform_machine})",
                f"CPU: {desc.cpu_cores_logical} logical / {desc.cpu_cores_physical} physical cores",
                f"GPU: {desc.gpu_name if desc.gpu_present else 'None'}",
                f"Memory: {desc.memory_total_gb:.1f} GB",
                f"T_collapse estimate: {desc.t_collapse_estimate:.0f}°C",
                f"H_env (bandwidth): {desc.h_env_bandwidth_bps:.0f} bps",
                f"ρ_container: {desc.container_reserve_ratio:.2%}",
                f"H_regen: {desc.h_env_regen_rate:.0f} bps",
                f"Fingerprint: {desc.fingerprint()}",
            ]
            self.substrate_label.setText("\n".join(lines))
            self.reserve_value_label.setText(f"{desc.container_reserve_ratio:.2%}")
            self.coherence_meter.set_coherence(0.2, 1.0)
            self.log_message.emit("Container introspection complete.")

            # Load constitutional constants into display
            try:
                from consciousness.safety_constitution import get_all_constitutional_constants
                consts = get_all_constitutional_constants()
                const_lines = ["Inviolable Safety Constitution:", ""]
                for key, val in sorted(consts.items()):
                    const_lines.append(f"  {key}: {val}")
                self.constitution_text.setText("\n".join(const_lines))
            except ImportError:
                self.constitution_text.setText("Safety constitution module not available.")
        except ImportError:
            self.substrate_label.setText(
                "Container introspection module not available.\n"
                "Ensure the CSDF package is installed:\n"
                "  pip install -e /path/to/uploaded-consciousness-framework"
            )
            self.log_message.emit("ERROR: container_introspection module not found.")

    def on_run_optimization(self):
        """Run meta-parametric optimization."""
        if self.substrate_data is None:
            QMessageBox.warning(self, "No Substrate Data",
                                "Run container introspection first.")
            return

        self.log_message.emit("Running meta-parametric optimization...")
        try:
            from consciousness.meta_optimizer import optimize
            theta = optimize(self.substrate_data, cache=True, refine=True)
            self.theta_data = theta

            param_lines = []
            for key, val in sorted(theta.to_dict().items()):
                if isinstance(val, float):
                    param_lines.append(f"  {key}: {val:.6f}")
                elif isinstance(val, int):
                    param_lines.append(f"  {key}: {val}")
                else:
                    param_lines.append(f"  {key}: {val}")

            status = f"Optimization tier: {theta.optimization_tier}\n"
            self.param_text.setText(status + "\n".join(param_lines))
            self.log_message.emit(
                f"Optimization complete (tier: {theta.optimization_tier})."
            )
        except ImportError:
            self.param_text.setText(
                "Meta-optimizer module not available.\n"
                "Ensure the CSDF package is installed."
            )
            self.log_message.emit("ERROR: meta_optimizer module not found.")

    def on_identity_commit(self):
        """Perform an identity commit — save current state as new identity core."""
        self.log_message.emit("Performing identity commit...")

        if self.theta_data is None and self.substrate_data is None:
            QMessageBox.warning(self, "No Data",
                                "No substrate or parameter data to commit. "
                                "Run introspection and optimization first.")
            return

        try:
            from identity_core import IdentityCheckpoint, save_checkpoint
            import numpy as np

            # Build checkpoint from current state
            mu_core_arr = np.zeros(14) if self.theta_data is None else self.theta_data.to_array()
            checkpoint = IdentityCheckpoint(
                sequence_number=len(self.identity_checkpoints),
                label=f"Commit from {time.strftime('%Y-%m-%d %H:%M:%S')}",
                core_data=mu_core_arr.tobytes(),
                core_data_shape=list(mu_core_arr.shape),
            )

            # Add substrate if available
            if self.substrate_data is not None:
                fp = self.substrate_data.fingerprint()
                checkpoint.known_substrates[fp] = {
                    "machine": self.substrate_data.platform_machine,
                    "cpu_cores": self.substrate_data.cpu_cores_physical,
                    "gpu": self.substrate_data.gpu_name,
                }

            save_checkpoint(checkpoint, core_data=mu_core_arr.tobytes())
            self.identity_checkpoints.append(checkpoint)
            self.commit_count_label.setText(
                f"Commits: {len(self.identity_checkpoints)}"
            )
            self.on_refresh_checkpoints()
            self.log_message.emit(f"Identity committed: #{checkpoint.sequence_number}")

        except ImportError:
            QMessageBox.warning(self, "Identity Core Not Available",
                                "Install identity-core package:\n"
                                "  pip install -e packages/identity-core")
            self.log_message.emit("ERROR: identity_core module not found.")

    def on_export_to_vault(self):
        """Export the latest identity checkpoint to EVE vault."""
        if not self.identity_checkpoints:
            QMessageBox.warning(self, "No Commits",
                                "Perform an identity commit first.")
            return

        try:
            from identity_core import export_to_eve
            latest = self.identity_checkpoints[-1]
            vault_path = os.path.join(
                os.path.expanduser("~"), "Documents", "KB", "System", "Identity"
            )
            fpath = export_to_eve(latest, vault_path=vault_path)
            QMessageBox.information(
                self, "Exported",
                f"Identity checkpoint exported to:\n{fpath}"
            )
            self.log_message.emit(f"Checkpoint exported to {fpath}")
        except ImportError:
            self.log_message.emit("ERROR: identity_core module not found.")

    def on_refresh_checkpoints(self):
        """Refresh the checkpoint list from storage."""
        self.checkpoint_list.clear()
        try:
            from identity_core import list_checkpoints
            checkpoints = list_checkpoints()
            for cp in checkpoints:
                item = QListWidgetItem(
                    f"#{cp.get('sequence_number', '?')} | "
                    f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(cp.get('timestamp', 0)))} | "
                    f"{cp.get('label', '')[:40]}"
                )
                item.setData(Qt.ItemDataRole.UserRole, cp.get('sequence_number'))
                self.checkpoint_list.addItem(item)
        except ImportError:
            self.checkpoint_list.addItem("identity-core package not installed")

    def on_refresh_safety(self):
        """Periodically refresh safety status display.

        Reads the latest safety monitor verdicts if the runtime is running,
        or displays the last available state from introspection data.
        """
        # Update safety state label based on latest verdicts if available
        if self.theta_data is not None and self.substrate_data is not None:
            try:
                from consciousness.safety_constraints import assess_all_constraints
                verdicts = assess_all_constraints(self.theta_data, self.substrate_data)
                self._update_safety_bars(verdicts)

                # Determine highest severity
                severity_rank = {"quarantine": 0, "degrade": 1, "protected": 2}
                worst = min(verdicts, key=lambda v: severity_rank.get(v.get("severity", "protected"), 2))
                sev = worst.get("severity", "protected")

                color_map = {
                    "protected": ThemeManager.COLORS.get("accent_green", "#2ecc71"),
                    "degrade": ThemeManager.COLORS.get("accent_orange", "#f39c12"),
                    "quarantine": ThemeManager.COLORS.get("accent_red", "#e74c3c"),
                    "aborted": "#8e44ad",
                }
                color = color_map.get(sev, "#ffffff")
                self.safety_state_label.setText(f"State: {sev.upper()}")
                self.safety_state_label.setStyleSheet(f"color: {color}; font-weight: bold;")

                # Update reserve ratio
                rho = getattr(self.substrate_data, "container_reserve_ratio", 0.25)
                self.reserve_value_label.setText(f"{rho:.2%}")

            except ImportError:
                pass

    def _update_safety_bars(self, verdicts: list[dict]):
        """Update the four constraint progress bars from verdict data.

        Each bar shows how close the constraint is to violation:
          0-70% = safe (green)
          70-100% = approaching limit (orange)
          >100% = violated (red)
        """
        for v in verdicts:
            key = v.get("constraint_name", "")
            bar = self.constraint_bars.get(key)
            if bar is None:
                continue

            measured = v.get("measured_value", 0.0)
            threshold = v.get("threshold", 1.0)
            if threshold <= 0:
                threshold = 1.0
            pct = min(int((measured / threshold) * 100), 150)

            bar.setValue(min(pct, 100))
            sev = v.get("severity", "protected")
            if sev == "quarantine":
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {ThemeManager.COLORS.get('bg_secondary', '#333')};
                        border: 1px solid {ThemeManager.COLORS.get('accent_red', '#e74c3c')};
                        border-radius: 3px;
                        text-align: center;
                        color: white;
                    }}
                    QProgressBar::chunk {{
                        background-color: {ThemeManager.COLORS.get('accent_red', '#e74c3c')};
                        border-radius: 2px;
                    }}
                """)
                suffix = " VIOLATED"
            elif sev == "degrade":
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {ThemeManager.COLORS.get('bg_secondary', '#333')};
                        border: 1px solid {ThemeManager.COLORS.get('accent_orange', '#f39c12')};
                        border-radius: 3px;
                        text-align: center;
                        color: white;
                    }}
                    QProgressBar::chunk {{
                        background-color: {ThemeManager.COLORS.get('accent_orange', '#f39c12')};
                        border-radius: 2px;
                    }}
                """)
                suffix = " WARNING"
            else:
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {ThemeManager.COLORS.get('bg_secondary', '#333')};
                        border: 1px solid {ThemeManager.COLORS.get('accent_green', '#2ecc71')};
                        border-radius: 3px;
                        text-align: center;
                        color: white;
                    }}
                    QProgressBar::chunk {{
                        background-color: {ThemeManager.COLORS.get('accent_green', '#2ecc71')};
                        border-radius: 2px;
                    }}
                """)
                suffix = ""

            bar.setFormat(f"{measured:.2f} / {threshold:.2f}{suffix}")

    def on_checkpoint_selected(self, item):
        """Display details of the selected checkpoint."""
        seq = item.data(Qt.ItemDataRole.UserRole)
        if seq is None:
            return
        try:
            from identity_core import load_checkpoint
            cp = load_checkpoint(seq)
            if cp is not None:
                details = (
                    f"Checkpoint #{cp.sequence_number}\n"
                    f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp.timestamp))}\n"
                    f"Label: {cp.label or '(none)'}\n"
                    f"Hash: {cp.checkpoint_hash[:16]}...\n"
                    f"Substrates known: {len(cp.known_substrates)}\n"
                    f"Commits in history: {len(cp.commit_history)}"
                )
                QMessageBox.information(self, "Checkpoint Details", details)
        except ImportError:
            pass
