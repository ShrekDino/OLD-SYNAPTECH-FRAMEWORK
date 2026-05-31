import numpy as np
from fafbseg import flywire
from lib.big_pickle import profiled

NEUROPIL_GROUPS = {
    'optic': ['LA', 'ME', 'LO', 'LOP', 'AME', 'AOTU'],
    'sensory_olfactory': ['AL'],
    'sensory_auditory': ['AMMC'],
    'sensory_visual': ['OC'],
    'central_mushroom_body': ['MB_', 'CA'],
    'central_complex': ['FB', 'EB', 'PB', 'NO', 'BU'],
    'central_lateral_complex': ['LAL', 'GAL'],
    'central_superior': ['SLP', 'SIP', 'SMP'],
    'central_inferior': ['CL', 'CRE', 'ATL', 'IB'],
    'central_ventrolateral': ['AVLP', 'PVLP', 'IVLP', 'PLP', 'LH'],
    'central_ventromedial': ['SAD', 'VES', 'EPA', 'GOR', 'PRW', 'PS'],
    'motor_sez': ['GNG'],
    'motor_gnathal': ['VPS', 'PMS'],
}

def get_available_neuropils():
    neuropils = flywire.get_neuropil_volumes(None)
    return sorted([str(n) for n in neuropils])

def classify_neuropil(name):
    base = name.split('_')[0].upper() if '_' in name else name.upper()
    hemi = name.split('_')[1] if '_' in name and len(name.split('_')) > 1 else ''
    for group, prefixes in NEUROPIL_GROUPS.items():
        for prefix in prefixes:
            if name.upper().startswith(prefix):
                side = 'left' if hemi == 'L' else 'right' if hemi == 'R' else 'unpaired'
                return group, side
    return 'other', ''

def load_neuropil_mesh(name):
    vol = flywire.get_neuropil_volumes(name)
    verts = np.asarray(vol.vertices, dtype=np.float64)
    faces = np.asarray(vol.faces, dtype=np.int64)
    center = verts.mean(axis=0)
    return verts, faces, center

@profiled("mesh_loader")
def load_all_neuropil_data(names=None):
    if names is None:
        names = get_available_neuropils()
    meshes = {}
    centers = {}
    classifications = {}
    for name in names:
        try:
            verts, faces, center = load_neuropil_mesh(name)
            meshes[name] = (verts, faces)
            centers[name] = center
            group, side = classify_neuropil(name)
            classifications[name] = {'group': group, 'side': side}
        except Exception as e:
            print(f"  Warning: could not load {name}: {e}")
    neuropil_names = sorted(meshes.keys())
    return neuropil_names, meshes, centers, classifications

def compute_neuropil_centers_matrix(neuropil_names, centers):
    return np.array([centers[n] for n in neuropil_names])
