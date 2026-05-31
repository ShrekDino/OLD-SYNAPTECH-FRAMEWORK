#!/usr/bin/env python3
"""Download the real FlyWire whole-brain connectome from Zenodo (CC BY 4.0).

Downloads:
  - proofread_root_ids_783.npy   (1.1 MB) — all 139k proofread neuron root IDs
  - proofread_connections_783.feather (852 MB) — aggregated neuron↔neuron connections
  - flywire_synapses_783.feather (9.5 GB) — all ~130M synapses with 3D positions

Pipeline:
  1. Resumable download with MD5 verification
  2. Extract per-neuron 3D positions as centroids of pre-synaptic sites
  3. Generate layout.json (same format as synthetic fallback)

Output layout path: data/layout.json  (same format as synthetic data)
Output data path:   data/flywire/     (root_ids.npy, positions.npy, *.feather)
"""

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np

ZENODO_BASE = "https://zenodo.org/records/10676866/files"

FILES = [
    {
        "name": "proofread_root_ids_783.npy",
        "path": "root_ids.npy",
        "size_gb": 0.0011,
        "md5": "e0e6c19732fd8c7a4e39a2d170105421",
    },
    {
        "name": "proofread_connections_783.feather",
        "path": "proofread_connections.feather",
        "size_gb": 0.852,
        "md5": "f48f972d262323a102aed49af1396b8a",
    },
    {
        "name": "flywire_synapses_783.feather",
        "path": "flywire_synapses.feather",
        "size_gb": 9.5,
        "md5": "f8f1b97c9d4b0ea9b4c8b287f6b99091",
    },
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "flywire"
LAYOUT_PATH = Path(__file__).resolve().parent.parent / "data" / "layout.json"


# ── helpers ──────────────────────────────────────────────────────────


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def human_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def download(url: str, dest: Path, expected_md5: str, desc: str) -> None:
    import requests

    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_suffix(".part")

    if dest.exists() and md5_file(dest) == expected_md5:
        print(f"  \u2713 {desc} \u2014 already downloaded, MD5 valid")
        return

    resume_at = 0
    if temp.exists():
        resume_at = temp.stat().st_size
        print(f"  \u21bb Resuming {desc} at {human_size(resume_at)}")

    headers = {"Range": f"bytes={resume_at}-"} if resume_at > 0 else {}
    resp = requests.get(url, stream=True, timeout=120, headers=headers)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0)) + resume_at
    mode = "ab" if resume_at > 0 else "wb"
    t0 = time.time()
    last_log = 0.0

    with open(temp, mode) as f:
        for chunk in resp.iter_content(chunk_size=8 * 1024 * 1024):
            if chunk:
                f.write(chunk)
                elapsed = time.time() - t0
                if elapsed - last_log > 5:
                    done = temp.stat().st_size
                    pct = done / total * 100 if total else 0
                    speed = done / elapsed
                    eta_sec = (total - done) / speed if speed > 0 else 0
                    eta_str = f"{eta_sec / 60:.0f}m {eta_sec % 60:.0f}s" if eta_sec > 60 else f"{eta_sec:.0f}s"
                    print(f"  {pct:5.1f}%  {human_size(done)} / {human_size(total)}  {human_size(speed)}/s  ETA {eta_str}")
                    last_log = elapsed

    print(f"  Verifying MD5...")
    if md5_file(temp) != expected_md5:
        temp.unlink()
        raise RuntimeError(f"MD5 mismatch for {desc} \u2014 file corrupted, re-run to retry")

    temp.rename(dest)
    print(f"  \u2713 {desc} \u2014 {human_size(total)}")


def extract_positions(root_ids_path: Path, synapses_path: Path, output_path: Path) -> None:
    """Stream the 9.5 GB synapse file in chunks, accumulate per-neuron centroids."""
    import pyarrow.feather as feather

    print("\nExtracting per-neuron 3D positions from ~130M synapses (this takes a few minutes)...")

    root_ids = np.load(str(root_ids_path))
    n = len(root_ids)
    root_set = set(int(x) for x in root_ids)
    id_to_idx = {int(rid): i for i, rid in enumerate(root_ids)}

    sum_pos = np.zeros((n, 3), dtype=np.float64)
    counts = np.zeros(n, dtype=np.int64)

    table = feather.read_table(str(synapses_path), memory_map=True)
    total_rows = table.num_rows
    batch_size = 200_000

    pre_id = table.column("pre_pt_root_id")
    px = table.column("pre_pt_position_x")
    py = table.column("pre_pt_position_y")
    pz = table.column("pre_pt_position_z")

    t0 = time.time()
    processed = 0

    for offset in range(0, total_rows, batch_size):
        end = min(offset + batch_size, total_rows)
        ids = pre_id.slice(offset, end - offset).to_numpy()
        xs = px.slice(offset, end - offset).to_numpy().astype(np.float64)
        ys = py.slice(offset, end - offset).to_numpy().astype(np.float64)
        zs = pz.slice(offset, end - offset).to_numpy().astype(np.float64)

        for i in range(len(ids)):
            rid = int(ids[i])
            idx = id_to_idx.get(rid)
            if idx is not None:
                sum_pos[idx, 0] += xs[i]
                sum_pos[idx, 1] += ys[i]
                sum_pos[idx, 2] += zs[i]
                counts[idx] += 1

        processed += len(ids)
        elapsed = time.time() - t0
        if elapsed > 10:
            pct = processed / total_rows * 100
            speed = processed / elapsed
            eta = max(0, (total_rows - processed) / speed)
            print(f"  {pct:5.1f}%  {processed:>12,} / {total_rows:,} synapses  {speed:>8,.0f} syn/s  ETA {eta / 60:.0f}m")
            t0 = time.time()  # reset timer to avoid log spam

    mask = counts > 0
    positions = np.zeros((n, 3), dtype=np.float32)
    positions[mask] = (sum_pos[mask] / counts[mask, np.newaxis]).astype(np.float32)

    missing = n - int(mask.sum())
    if missing:
        print(f"  \u26a0 {missing:,} neurons have zero pre-synaptic sites \u2014 using origin")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(output_path), positions)
    print(f"  \u2713 Positions saved: {output_path} ({n:,} neurons)")


def generate_layout(positions_path: Path, layout_path: Path) -> None:
    """Write layout.json in {positions, shape} format (same as synthetic)."""
    positions = np.load(str(positions_path))
    n = positions.shape[0]

    layout = {
        "positions": positions.tolist(),
        "shape": [n, 3],
    }

    layout_path.parent.mkdir(parents=True, exist_ok=True)
    with open(layout_path, "w") as f:
        json.dump(layout, f)
    print(f"  \u2713 Layout written: {layout_path} ({n:,} positions)")


# ── main ─────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("  FlyWire Whole-Brain Connectome \u2014 Data Downloader")
    print("  DOI: 10.5281/zenodo.10676866  |  License: CC BY 4.0")
    print("=" * 60)

    total_gb = sum(f["size_gb"] for f in FILES)
    _, _, free = shutil.disk_usage(DATA_DIR)
    free_gb = free / 1024**3
    if free_gb < total_gb:
        print(f"\n  \u2717 Insufficient disk: need {total_gb:.1f} GB, have {free_gb:.1f} GB at {DATA_DIR}")
        sys.exit(1)
    print(f"\n  Disk: {free_gb:.1f} GB free, need ~{total_gb:.1f} GB\n")

    # ── Step 1: download ──
    for f_info in FILES:
        url = f"{ZENODO_BASE}/{f_info['name']}?download=1"
        dest = DATA_DIR / f_info["path"]
        print(f"\n  [{f_info['name']}]  ({f_info['size_gb']:.1f} GB)")
        download(url, dest, f_info["md5"], f_info["name"])

    # ── Step 2: extract 3D positions ──
    extract_positions(
        root_ids_path=DATA_DIR / "root_ids.npy",
        synapses_path=DATA_DIR / "flywire_synapses.feather",
        output_path=DATA_DIR / "positions.npy",
    )

    # ── Step 3: generate layout.json ──
    generate_layout(
        positions_path=DATA_DIR / "positions.npy",
        layout_path=LAYOUT_PATH,
    )

    print(f"\n{'=' * 60}")
    print(f"  Done. The real FlyWire connectome is ready to load.")
    print(f"  Start the backend: PYTHONPATH=\\$PWD python -m uvicorn src.backend.main:app")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
