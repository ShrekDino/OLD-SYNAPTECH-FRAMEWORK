#!/usr/bin/env python3
"""
Fly Brain Neuropil Activity Visualizer

Simulates behavior-driven neural activity across ~78 neuropil regions
of the Drosophila melanogaster brain using the FlyWire connectome.

Usage:
    conda run -n flybrain python flybrain_activity.py --behavior feeding
    conda run -n flybrain python flybrain_activity.py --closed-loop -b walking_closed_loop --timesteps 400
    conda run -n flybrain python flybrain_activity.py --list-behaviors

    # Real-time 60 Hz GPU mode with live visualizer:
    conda run -n flybrain python flybrain_activity.py --closed-loop --realtime --enable-viz
"""

import argparse
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.data_loader import (
    get_available_neuropils,
    load_all_neuropil_data,
    compute_neuropil_centers_matrix,
)
from lib.projectome import compute_projectome
from lib.behaviors import BEHAVIORS, build_all_input_vectors
from lib.simulation import NeuropilSimulation
from lib.visualize import create_animation, save_figure
from lib.closed_loop import ClosedLoopSimulation
from lib.motor_viz import create_dual_figure
from lib.big_pickle import (
    get_profile_stats,
    format_profile_stats,
    generate_static_report,
    reset_profile_stats,
)
from lib.gpu_simulation import GPUClimateSimulation
from lib.realtime_engine import RealtimeEngine
from lib.runtime_logger import RuntimeLogger


def main():
    parser = argparse.ArgumentParser(
        description="Fly Brain Neuropil Activity Visualizer"
    )
    parser.add_argument(
        "--behavior", "-b",
        default="resting",
        choices=list(BEHAVIORS.keys()),
        help="Behavior mode to simulate"
    )
    parser.add_argument(
        "--timesteps", "-t",
        type=int,
        default=200,
        help="Number of simulation timesteps (default: 200)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output HTML filename (default: auto-generated)"
    )
    parser.add_argument(
        "--list-behaviors", "-l",
        action="store_true",
        help="List available behaviors and exit"
    )
    parser.add_argument(
        "--all-behaviors",
        action="store_true",
        help="Generate visualizations for all behaviors"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Recurrent connection strength (default: 0.5)"
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=0.8,
        help="Input drive strength (default: 0.8)"
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.3,
        help="Activity decay rate (default: 0.3)"
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable Big Pickle runtime profiling and print analysis report"
    )
    parser.add_argument(
        "--closed-loop", "--cl",
        action="store_true",
        help="Run in closed-loop mode: brain activity drives 3D fly body with sensory feedback"
    )
    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Run closed-loop at 60 Hz real-time (requires --closed-loop)"
    )
    parser.add_argument(
        "--enable-viz",
        action="store_true",
        help="Launch UDP visualizer bridge for live pygame window (requires --realtime)"
    )
    parser.add_argument(
        "--viz-port",
        type=int,
        default=5555,
        help="UDP port for visualizer broadcast (default: 5555)"
    )
    parser.add_argument(
        "--stimulus-port",
        type=int,
        default=5556,
        help="UDP port for stimulus input from visualizer (default: 5556)"
    )

    args = parser.parse_args()

    if args.profile:
        reset_profile_stats()

    if args.list_behaviors:
        print("\nAvailable Behaviors:")
        print("-" * 60)
        for name, b in BEHAVIORS.items():
            print(f"  {name:20s} - {b['description']}")
        print()
        sys.exit(0)

    print("=" * 60)
    print("  Fly Brain Neuropil Activity Visualizer")
    print("  Powered by FlyWire Connectome (FAFB v783)")
    print("=" * 60)

    print("\n[1/4] Loading neuropil meshes...")
    neuropil_names, meshes, centers, classifications = load_all_neuropil_data()
    print(f"  Loaded {len(neuropil_names)} neuropil meshes")

    print("\n[2/4] Computing projectome...")
    P, np_names = compute_projectome(neuropil_names)
    print(f"  Projectome: {P.shape[0]}x{P.shape[1]} matrix")

    print("\n[3/4] Running simulation...")
    input_vectors = build_all_input_vectors(neuropil_names)

    sim = NeuropilSimulation(
        P, neuropil_names,
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
    )

    if args.closed_loop:
        behavior_name = args.behavior
        if behavior_name != 'walking_closed_loop':
            print("  Note: Using walking_closed_loop for closed-loop mode")
            behavior_name = 'walking_closed_loop'

        # ── Real-time 60 Hz GPU path ──────────────────────────────
        if args.realtime:
            print(f"\n  Initializing real-time closed-loop (GPU): {behavior_name}")
            gpu_sim = GPUClimateSimulation(
                P, neuropil_names,
                alpha=args.alpha,
                beta=args.beta,
                gamma=args.gamma,
            )
            logger = RuntimeLogger(
                "NVIDIA GPU", 6.0,
                len(neuropil_names),
                np.count_nonzero(P),
            )
            engine = RealtimeEngine(
                gpu_sim, neuropil_names,
                tick_rate=60,
                device='cuda',
                enable_viz=args.enable_viz,
                viz_port=args.viz_port,
                stimulus_port=args.stimulus_port,
            )
            # Run indefinitely (Ctrl-C) when viz is active;
            # otherwise auto-stop after --timesteps ticks.
            max_ticks = None if args.enable_viz else args.timesteps
            engine.start(logger=logger, max_ticks=max_ticks)
            # engine.start() blocks until the loop exits
            return

        # ── Batch closed-loop path (unchanged) ────────────────────
        print(f"\n  Initializing closed-loop simulation: {behavior_name}")
        cl_sim = ClosedLoopSimulation(sim, neuropil_names)
        history = cl_sim.run(timesteps=args.timesteps, initial_kick_strength=0.3)

        brain_history = history['activity']
        body_states = history['body_states']
        motor_commands = history['motor_commands']

        print(f"    {args.timesteps} timesteps, "
              f"peak activity: {brain_history.max():.3f}, "
              f"mean activity: {brain_history.mean():.3f}")
        print(f"    Final position: ({body_states[-1]['pos'][0]:.2f}, "
              f"{body_states[-1]['pos'][1]:.2f})")

        print(f"\n[4/4] Creating dual visualization...")
        fig = create_dual_figure(
            neuropil_names, meshes, centers, classifications,
            brain_history, body_states, motor_commands, behavior_name,
        )

        if args.output:
            output_path = args.output
        else:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "flybrain_walking_closed.html")

        save_figure(fig, output_path)
        print(f"  Saved: {output_path}")
        print("\n✅ Done! Side-by-side brain + body visualization will open in your browser.")

    else:
        behaviors_to_run = list(BEHAVIORS.keys()) if args.all_behaviors else [args.behavior]

        for behavior_name in behaviors_to_run:
            if BEHAVIORS.get(behavior_name, {}).get('closed_loop'):
                continue

            print(f"\n  Simulating: {behavior_name}")
            input_vec = input_vectors[behavior_name]
            history = sim.run(input_vec, timesteps=args.timesteps)
            print(f"    {args.timesteps} timesteps, "
                  f"peak activity: {history.max():.3f}, "
                  f"mean activity: {history.mean():.3f}")

            print(f"\n[4/4] Creating visualization...")
            fig = create_animation(
                neuropil_names, meshes, centers, classifications,
                history, behavior_name,
            )

            if args.output:
                output_path = args.output
            else:
                output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"flybrain_{behavior_name}.html")

            save_figure(fig, output_path)
            print(f"  Saved: {output_path}")

            if not args.all_behaviors:
                print("\n✅ Done! The visualization will open in your browser.")
                print(f"   File: {output_path}")
            else:
                print(f"  ✅ {behavior_name} complete")

    if args.all_behaviors and not args.closed_loop:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        print(f"\n✅ All behaviors complete! Files saved to: {output_dir}/")
        print(f"   Files: {', '.join(f'flybrain_{b}.html' for b in behaviors_to_run)}")

    if args.profile:
        print("\n" + "=" * 60)
        print("  Big Pickle Analysis Report")
        print("=" * 60)

        print("\n  --- Runtime Profile ---")
        print(format_profile_stats())

        static = generate_static_report()

        print("\n  --- Visualization Context ---")
        vc = static["visualization_context"]
        print(f"  show_neuropil: {vc['show_neuropil']}")
        print(f"  camera_focus: {vc['camera_focus']}")
        print(f"  camera: {vc['camera_settings']['eye']}")
        print(f"  rendering: bg={vc['rendering']['background']}, "
              f"min_color={vc['rendering']['min_visibility_color']}")
        print(f"  edge_contour: {vc['rendering']['edge_contour']}")
        print(f"  axis_ranges: {vc['axis_ranges']}")

        # Compute and display actual brain bounds from loaded mesh data
        try:
            from lib.visualize import _compute_brain_bounds
            bounds = _compute_brain_bounds(neuropil_names, meshes)
            print(f"\n  --- Brain Bounding Box (data coordinates) ---")
            print(f"  x: [{bounds['x'][0]:.0f}, {bounds['x'][1]:.0f}] "
                  f"(span: {bounds['x'][1]-bounds['x'][0]:.0f})")
            print(f"  y: [{bounds['y'][0]:.0f}, {bounds['y'][1]:.0f}] "
                  f"(span: {bounds['y'][1]-bounds['y'][0]:.0f})")
            print(f"  z: [{bounds['z'][0]:.0f}, {bounds['z'][1]:.0f}] "
                  f"(span: {bounds['z'][1]-bounds['z'][0]:.0f})")
        except Exception:
            pass

        print("\n  --- Bottleneck Registry ---")
        for b in static["bottleneck_registry"]:
            print(f"  [{b['severity']:>5}] {b['component']}.{b['function']}")
            print(f"         {b['reason']}")
            print(f"         Mitigation: {b['mitigation']}")
            print()

        print("\n  --- Data Flow Quantification ---")
        dq = static["data_flow_quantification"]
        print(f"  Input:  {dq['input_throughput']['synapse_rows_ingested']}")
        print(f"  Reduction: {dq['computation_flux']['connectivity_reduction']}")
        print(f"  Compression: {dq['computation_flux']['information_compression_ratio']}")
        print(f"  Simulation: {dq['simulation_complexity']['total_for_T_timesteps']}")
        print(f"  Output: {dq['output_size']['per_behavior_html']}")


if __name__ == "__main__":
    main()
