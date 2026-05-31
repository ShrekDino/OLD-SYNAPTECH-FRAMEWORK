#!/usr/bin/env python3
"""Generate synthetic FlyWire-like connectome data for local demo."""

import json
import os
import sys
import csv
import math
import random
from pathlib import Path

N_NEURONS = 130_000
N_SYNAPSES = 500_000
N_COMMUNITIES = 12
RANDOM_SEED = 42

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "flywire"
LAYOUT_PATH = Path(__file__).resolve().parent.parent / "data" / "layout.json"
CSV_PATH = DATA_DIR / "connectome.csv"


def generate_communities():
    rng = random.Random(RANDOM_SEED)
    community_names = [
        "visual", "motor", "olfactory", "auditory", "somatosensory",
        "prefrontal", "hippocampal", "thalamic", "cerebellar", "basal",
        "temporal", "parietal",
    ]
    sizes = []
    base = N_NEURONS // N_COMMUNITIES
    remainder = N_NEURONS % N_COMMUNITIES
    for i in range(N_COMMUNITIES):
        sz = base + (1 if i < remainder else 0)
        sizes.append(sz)

    communities = []
    start = 0
    for i in range(N_COMMUNITIES):
        communities.append({
            "name": community_names[i],
            "start": start,
            "end": start + sizes[i],
            "size": sizes[i],
            "center": [
                rng.uniform(-0.8, 0.8),
                rng.uniform(-0.8, 0.8),
                rng.uniform(-0.8, 0.8),
            ],
        })
        start += sizes[i]
    return communities, rng


def generate_edges(communities, rng):
    n = N_NEURONS
    edges = []
    target_total = N_SYNAPSES

    intra_prob = 0.7
    inter_prob = 0.3

    for _ in range(target_total):
        c1 = rng.randint(0, N_COMMUNITIES - 1)
        if rng.random() < intra_prob:
            c2 = c1
        else:
            c2 = rng.randint(0, N_COMMUNITIES - 1)

        src = rng.randint(communities[c1]["start"], communities[c1]["end"] - 1)
        tgt = rng.randint(communities[c2]["start"], communities[c2]["end"] - 1)
        if src == tgt:
            continue
        weight = round(rng.uniform(0.1, 1.0), 4)
        edges.append((src, tgt, weight))

    edges.sort(key=lambda x: x[0])
    return edges


def generate_layout(communities, rng):
    n = N_NEURONS
    positions = [[0.0, 0.0, 0.0] for _ in range(n)]

    hemisphere = [
        (0.6, 0.0, 0.0),
        (-0.6, 0.0, 0.0),
    ]

    for comm in communities:
        ch = hemisphere[rng.randint(0, 1)]
        cx = ch[0] + comm["center"][0] * 0.3
        cy = comm["center"][1] * 0.6
        cz = comm["center"][2] * 0.4

        radius = 0.15 + rng.random() * 0.12
        for idx in range(comm["start"], comm["end"]):
            theta = rng.random() * math.pi * 2
            phi = math.acos(2 * rng.random() - 1)
            r = radius * (0.7 + rng.random() * 0.3)
            positions[idx] = [
                cx + r * math.sin(phi) * math.cos(theta),
                cy + r * math.cos(phi),
                cz + r * math.sin(phi) * math.sin(theta),
            ]

    return positions


def write_csv(edges):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "weight"])
        for src, tgt, w in edges:
            writer.writerow([src, tgt, w])
    print(f"Wrote {len(edges)} edges to {CSV_PATH}")


def write_layout(positions):
    LAYOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LAYOUT_PATH, "w") as f:
        json.dump({"positions": positions, "shape": [N_NEURONS, 3]}, f)
    print(f"Wrote layout to {LAYOUT_PATH}")


def main():
    print("=" * 60)
    print("  SynapTech IDRE — Test Data Generator")
    print("=" * 60)

    print(f"\nGenerating {N_COMMUNITIES} brain regions for {N_NEURONS:,} neurons...")
    communities, rng = generate_communities()
    for c in communities:
        print(f"  {c['name']:16s}  neurons {c['start']:6d} – {c['end']:6d}  ({c['size']:>6d})")

    print(f"\nGenerating ~{N_SYNAPSES:,} synaptic edges...")
    edges = generate_edges(communities, rng)
    write_csv(edges)

    print(f"\nGenerating 3D layout...")
    positions = generate_layout(communities, rng)
    write_layout(positions)

    total_mb = os.path.getsize(CSV_PATH) / 1e6
    print(f"\nDone! ({total_mb:.1f} MB CSV, {len(positions):,} positions)")


if __name__ == "__main__":
    main()
