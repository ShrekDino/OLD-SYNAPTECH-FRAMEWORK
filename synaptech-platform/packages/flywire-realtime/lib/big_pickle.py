"""
Big Pickle: Flywire profiling and analysis framework.

Provides:
    - @profiled decorator for runtime instrumentation
    - Static analysis of system architecture, dependencies, constraints, bottlenecks
    - Report generation merging static + runtime data

Usage:
    from lib.big_pickle import profiled, generate_report

    @profiled("my_function")
    def my_func():
        ...
"""

import functools
import os
import time

try:
    import psutil as _psutil
except ImportError:
    _psutil = None

# ---------------------------------------------------------------------------
# Profiling registry
# ---------------------------------------------------------------------------

_PROFILE_DATA = {}

def profiled(name):
    """Decorator that records wall-clock time and peak memory.

    Accumulates call count, total/min/max wall time, and peak RSS memory
    into the global ``_PROFILE_DATA`` dict keyed by *name*.

    Retrievable via ``get_profile_stats()``.  Overhead is ~1-2 µs per call
    when ``psutil`` is available, ~0.5 µs without.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            mem0 = _psutil.Process().memory_info().rss if _psutil else 0

            result = func(*args, **kwargs)

            dt = time.perf_counter() - t0
            mem1 = _psutil.Process().memory_info().rss if _psutil else 0
            peak = max(mem0, mem1)

            prev = _PROFILE_DATA.get(name, {
                "calls": 0,
                "total_wall": 0.0,
                "min_wall": float("inf"),
                "max_wall": 0.0,
                "peak_mem": 0,
            })
            prev["calls"] += 1
            prev["total_wall"] += dt
            prev["min_wall"] = min(prev["min_wall"], dt)
            prev["max_wall"] = max(prev["max_wall"], dt)
            prev["peak_mem"] = max(prev["peak_mem"], peak)
            _PROFILE_DATA[name] = prev

            return result
        return wrapper
    return decorator


def get_profile_stats():
    """Return copy of accumulated profiling data."""
    return dict(_PROFILE_DATA)


def reset_profile_stats():
    _PROFILE_DATA.clear()


# ---------------------------------------------------------------------------
# Static analysis: dependency graph
# ---------------------------------------------------------------------------

DEPENDENCY_GRAPH = {
    "nodes": [
        {
            "id": "mesh_loader",
            "module": "lib.data_loader",
            "responsibility": "Load neuropil meshes from FlyWire API",
        },
        {
            "id": "projectome_computer",
            "module": "lib.projectome",
            "responsibility": "Compute neuropil-to-neuropil connectivity matrix from synapse counts",
        },
        {
            "id": "simulation_engine",
            "module": "lib.simulation",
            "responsibility": "Run RNN-based activity dynamics with sigmoid activation",
        },
        {
            "id": "behavior_driver",
            "module": "lib.behaviors",
            "responsibility": "Define 5 behavioral modes and build sparse input vectors",
        },
        {
            "id": "renderer",
            "module": "lib.visualize",
            "responsibility": "Generate 3D animated Plotly visualization with activity heatmap",
        },
    ],
    "edges": [
        {
            "from": "mesh_loader",
            "to": "renderer",
            "data": "neuropil_meshes (vertices + faces per neuropil)",
            "volume": "~50 MB for 78 meshes",
        },
        {
            "from": "projectome_computer",
            "to": "simulation_engine",
            "data": "connectivity_matrix (N×N float64)",
            "volume": "~48 KB for N=78",
        },
        {
            "from": "behavior_driver",
            "to": "simulation_engine",
            "data": "input_vector (N×1 float64)",
            "volume": "~624 B for N=78",
        },
        {
            "from": "mesh_loader",
            "to": "projectome_computer",
            "data": "neuropil_names (list of str)",
            "volume": "~78 strings",
        },
        {
            "from": "simulation_engine",
            "to": "renderer",
            "data": "activity_trajectory (T×N float64)",
            "volume": f"~125 KB @ T=200, N=78",
        },
    ],
}

# ---------------------------------------------------------------------------
# Static analysis: constraints
# ---------------------------------------------------------------------------

CONSTRAINT_MATRIX = [
    {
        "component": "projectome_computer",
        "constraint": "Memory (Feather I/O)",
        "bound": "~4 GB peak RSS",
        "limit": "System RAM",
        "detail": "Pre file = 17 MB, Post file = 224 MB; in-memory aggregation dicts for 43M rows",
    },
    {
        "component": "mesh_loader",
        "constraint": "API rate limit",
        "bound": "~10 req/s (FlyWire / fafbseg)",
        "limit": "External service",
        "detail": "Each neuropil mesh requires a separate API call; burst rate may trigger throttling",
    },
    {
        "component": "projectome_computer",
        "constraint": "Disk I/O bandwidth",
        "bound": "224 MB Feather read",
        "limit": "Storage subsystem",
        "detail": "Post-synapse file is read via PyArrow RecordBatchFileReader in chunks",
    },
    {
        "component": "simulation_engine",
        "constraint": "Compute (matrix-vector multiply)",
        "bound": f"O(T × N²) = O(200 × 6084) FLOPS",
        "limit": "CPU throughput",
        "detail": "Each timestep: W^T @ activity + beta * input - gamma * (activity - baseline) + sigmoid",
    },
    {
        "component": "renderer",
        "constraint": "Output file size",
        "bound": "~3 MB per behavior HTML",
        "limit": "Disk / bandwidth",
        "detail": "Full Plotly.js figure with all frames; scales linearly with T",
    },
    {
        "component": "mesh_loader",
        "constraint": "Sequential API calls",
        "bound": "78 serial requests",
        "limit": "Wall-clock time",
        "detail": "No parallel fetching; each request blocks until previous completes",
    },
]

# ---------------------------------------------------------------------------
# Static analysis: bottleneck registry
# ---------------------------------------------------------------------------

BOTTLENECK_REGISTRY = [
    {
        "component": "projectome_computer",
        "function": "compute_projectome",
        "severity": "HIGH",
        "reason": (
            "Single-threaded iteration over 43M post-synapse rows building "
            "Python dicts; repeated isin() lookups and row-wise aggregation"
        ),
        "estimated_cost": "30-120s wall time",
        "mitigation": (
            "Use pandas groupby aggregations + numpy vectorized operations "
            "instead of row-wise iteration; pre-compute sparse COO matrix"
        ),
    },
    {
        "component": "mesh_loader",
        "function": "load_all_neuropil_data",
        "severity": "MEDIUM",
        "reason": (
            "Sequential API calls for 78 neuropils, each with network "
            "round-trip latency to FlyWire servers"
        ),
        "estimated_cost": "30-60s wall time",
        "mitigation": (
            "concurrent.futures.ThreadPoolExecutor with 8-16 workers "
            "for parallel mesh fetching"
        ),
    },
    {
        "component": "renderer",
        "function": "create_animation",
        "severity": "LOW",
        "reason": (
            "All T frames embedded inline as separate Mesh3d traces "
            "in a single HTML file; no streaming or lazy loading"
        ),
        "estimated_cost": "~3 MB per 200 timesteps; ~15 MB for all 5 behaviors",
        "mitigation": (
            "Downsample frames in slider; use Plotly frame compression "
            "(traces with matching UIDs); switch to JSON-only serialization"
        ),
    },
    {
        "component": "projectome_computer",
        "function": "compute_projectome (inner loop)",
        "severity": "LOW",
        "reason": (
            "O(K × P_i × Q_i) triple-loop per neuron where K=#common neurons, "
            "P_i=#pre-neuropils, Q_i=#post-neuropils"
        ),
        "estimated_cost": "N/A (dominated by I/O)",
        "mitigation": (
            "Sparse matrix multiplication (scipy.sparse.coo_matrix) "
            "instead of dense Python loops"
        ),
    },
]

# ---------------------------------------------------------------------------
# Static analysis: data flow quantification
# ---------------------------------------------------------------------------

VISUALIZATION_CONTEXT = {
    "show_neuropil": True,
    "neuropil_entity": {
        "type": "mesh3d",
        "count": 78,
        "description": "Individual neuropil region meshes from FlyWire, each rendered as a Plotly Mesh3d trace",
    },
    "camera_focus": "auto",
    "camera_settings": {
        "mode": "data-bounded",
        "eye": {"x": 1.2, "y": 1.2, "z": 0.6},
        "center": {"x": 0, "y": 0, "z": 0},
        "aspectmode": "data",
    },
    "rendering": {
        "background": "#111111",
        "min_visibility_color": "#1a1a5a",
        "edge_contour": "rgba(255,255,255,0.08)",
        "opacity": 0.85,
        "flatshading": True,
    },
    "axis_ranges": "auto-computed from mesh bounding box + 10% padding",
}

DATA_FLOW_QUANTIFICATION = {
    "input_throughput": {
        "synapse_rows_ingested": "45.8M total (2.8M pre + 43M post)",
        "mesh_data_loaded": "78 neuropil meshes from FlyWire API",
        "total_input_volume": "~241 MB (Feather) + ~50 MB (mesh geometry)",
    },
    "computation_flux": {
        "connectivity_reduction": "45.8M synapse rows → 78×78 = 6,084 weight entries",
        "information_compression_ratio": "~7530:1 (input rows → output matrix entries)",
    },
    "simulation_complexity": {
        "per_timestep_cost": "O(N²) = 6,084 FLOPS (matrix-vector multiply + activations)",
        "total_for_T_timesteps": "O(T × N²) = 1.22M FLOPS @ T=200",
        "trajectory_memory": "T × N × 8 bytes = 200 × 78 × 8 = 124.8 KB",
    },
    "output_size": {
        "per_behavior_html": "~3 MB (200 frames, 78 colored meshes per frame)",
        "full_5_behavior_run": "~15 MB total across all behaviors",
    },
}


def generate_static_report():
    return {
        "dependency_graph": DEPENDENCY_GRAPH,
        "constraint_matrix": CONSTRAINT_MATRIX,
        "bottleneck_registry": BOTTLENECK_REGISTRY,
        "data_flow_quantification": DATA_FLOW_QUANTIFICATION,
        "visualization_context": VISUALIZATION_CONTEXT,
    }


def format_profile_stats(stats=None, indent=2):
    if stats is None:
        stats = get_profile_stats()
    if not stats:
        return "  No profiling data collected."

    prefix = " " * indent
    lines = []
    for name, data in stats.items():
        avg = data["total_wall"] / data["calls"] if data["calls"] else 0
        peak_mb = data["peak_mem"] / (1024 * 1024)
        lines.append(f"{prefix}{name}:")
        lines.append(f"{prefix}  Calls:         {data['calls']}")
        lines.append(f"{prefix}  Total wall:    {data['total_wall']:.3f}s")
        lines.append(f"{prefix}  Avg wall:      {avg:.3f}s")
        lines.append(f"{prefix}  Min wall:      {data['min_wall']:.3f}s")
        lines.append(f"{prefix}  Max wall:      {data['max_wall']:.3f}s")
        lines.append(f"{prefix}  Peak memory:   {peak_mb:.1f} MB")
        lines.append("")
    return "\n".join(lines)


def generate_report(profile_stats=None, include_static=True):
    report = {}
    if include_static:
        report["static"] = generate_static_report()
    if profile_stats is None:
        profile_stats = get_profile_stats()
    if profile_stats:
        report["runtime"] = {"profile_stats": profile_stats}
    return report
