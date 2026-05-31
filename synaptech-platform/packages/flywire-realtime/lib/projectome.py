import os
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
import pyarrow as pa
from lib.big_pickle import profiled

ZENODO_BASE = "https://zenodo.org/records/10676866/files"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

PRE_FILENAME = "per_neuron_neuropil_count_pre_783.feather"
POST_FILENAME = "per_neuron_neuropil_count_post_783.feather"
PROJ_FILENAME = "projectome_v783.npz"


def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    with open(dest_path, "wb") as f, tqdm(
        desc=os.path.basename(dest_path),
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in r.iter_content(1024 * 1024):
            f.write(chunk)
            pbar.update(len(chunk))


def ensure_data():
    pre_path = os.path.join(DATA_DIR, PRE_FILENAME)
    post_path = os.path.join(DATA_DIR, POST_FILENAME)
    if not os.path.exists(pre_path):
        url = f"{ZENODO_BASE}/{PRE_FILENAME}"
        print(f"  Downloading {PRE_FILENAME} (~17 MB)...")
        download_file(url, pre_path)
    if not os.path.exists(post_path):
        url = f"{ZENODO_BASE}/{POST_FILENAME}"
        print(f"  Downloading {POST_FILENAME} (~233 MB)...")
        download_file(url, post_path)
    return pre_path, post_path


def _dict_projectome(neuropil_names, neuropil_map, pre_agg, post_agg):
    n = len(neuropil_names)
    pre_dict = {}
    for nid, grp in pre_agg.groupby(level=0):
        total = grp["count"].sum()
        pre_dict[nid] = {
            neuropil_map.get(r["neuropil"], -1): r["count"] / total
            for _, r in grp.iterrows()
        }

    post_dict = {}
    for nid, grp in post_agg.groupby(level=0):
        total = grp["count"].sum()
        post_dict[nid] = {
            neuropil_map.get(r["neuropil"], -1): r["count"] / total
            for _, r in grp.iterrows()
        }

    common = set(pre_dict) & set(post_dict)
    P = np.zeros((n, n), dtype=np.float64)
    for nid in tqdm(common, desc="  Computing projectome"):
        pre_items = {k: v for k, v in pre_dict[nid].items() if k >= 0}
        post_items = {k: v for k, v in post_dict[nid].items() if k >= 0}
        for i, pi in pre_items.items():
            for j, qj in post_items.items():
                P[i, j] += pi * qj
    return P


@profiled("projectome_computation")
def compute_projectome(neuropil_names):
    proj_path = os.path.join(DATA_DIR, PROJ_FILENAME)
    if os.path.exists(proj_path):
        data = np.load(proj_path, allow_pickle=True)
        cached_names = data["neuropil_names"]
        if list(cached_names) == list(neuropil_names):
            print("  Using cached projectome from data/projectome_v783.npz")
            return data["matrix"], data["neuropil_names"]

    print("  Computing projectome from Zenodo data...")
    pre_path, post_path = ensure_data()

    n = len(neuropil_names)
    np_map = {name: i for i, name in enumerate(neuropil_names)}

    print("  Loading pre-synapse counts (2.8M rows)...")
    pre_df = pd.read_feather(pre_path)
    pre_id_col = "pre_pt_root_id"
    post_id_col = "post_pt_root_id"
    print(f"    Unique neurons: {pre_df[pre_id_col].nunique():,}")

    print("  Filtering post-synapse counts (43M rows, batch processing)...")
    reader = pa.ipc.RecordBatchFileReader(pa.OSFile(post_path, "rb"))
    pre_ids_set = set(pre_df[pre_id_col].unique())

    id_map = {}
    for chunk_start in tqdm(range(0, reader.num_record_batches), desc="  Reading batches"):
        batch = reader.get_record_batch(chunk_start)
        df_chunk = batch.to_pandas()
        mask = df_chunk[post_id_col].isin(pre_ids_set)
        chunk_filtered = df_chunk[mask]
        for _, row in chunk_filtered.iterrows():
            nid = row[post_id_col]
            np_name = row["neuropil"]
            cnt = row["count"]
            if nid not in id_map:
                id_map[nid] = {"post": {}, "pre": None}
            cur = id_map[nid]["post"].get(np_name, 0)
            id_map[nid]["post"][np_name] = cur + cnt

    for _, row in tqdm(pre_df.iterrows(), total=len(pre_df), desc="  Building pre dict"):
        nid = row[pre_id_col]
        if nid in id_map:
            np_name = row["neuropil"]
            cnt = row["count"]
            if id_map[nid]["pre"] is None:
                id_map[nid]["pre"] = {}
            cur = id_map[nid]["pre"].get(np_name, 0)
            id_map[nid]["pre"][np_name] = cur + cnt

    id_map = {k: v for k, v in id_map.items() if v["pre"] is not None}
    print(f"    Neurons with both pre and post: {len(id_map):,}")

    P = np.zeros((n, n), dtype=np.float64)
    for nid, data in tqdm(id_map.items(), desc="  Computing projectome"):
        pre_items = {}
        if data["pre"]:
            pre_total = sum(data["pre"].values())
            for np_name, cnt in data["pre"].items():
                if np_name in np_map:
                    pre_items[np_map[np_name]] = cnt / pre_total
        post_items = {}
        if data["post"]:
            post_total = sum(data["post"].values())
            for np_name, cnt in data["post"].items():
                if np_name in np_map:
                    post_items[np_map[np_name]] = cnt / post_total
        for i, pi in pre_items.items():
            for j, qj in post_items.items():
                P[i, j] += pi * qj

    np.savez(proj_path, matrix=P, neuropil_names=np.array(neuropil_names))
    print(f"  Projectome saved to {proj_path}")
    return P, neuropil_names
