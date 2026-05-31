import numpy as np

def _ellipsoid_mesh(center, rx, ry, rz, n_phi=14, n_theta=10):
    phi = np.linspace(0, 2 * np.pi, n_phi)
    theta = np.linspace(0, np.pi, n_theta)
    phi, theta = np.meshgrid(phi, theta)
    x = center[0] + rx * np.sin(theta) * np.cos(phi)
    y = center[1] + ry * np.sin(theta) * np.sin(phi)
    z = center[2] + rz * np.cos(theta)
    verts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    faces = []
    for i in range(n_theta - 1):
        for j in range(n_phi - 1):
            v0 = i * n_phi + j
            v1 = i * n_phi + j + 1
            v2 = (i + 1) * n_phi + j
            v3 = (i + 1) * n_phi + j + 1
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
    return verts, np.array(faces, dtype=np.int64)

def head_capsule():
    return _ellipsoid_mesh([0, 0, 0], 0.09, 0.08, 0.07)

def compound_eye(side):
    offset_x = 0.075
    offset_y = 0.065 if side == 'L' else -0.065
    return _ellipsoid_mesh([offset_x, offset_y, 0.01], 0.045, 0.035, 0.04)

def thorax():
    return _ellipsoid_mesh([0, 0, 0], 0.17, 0.10, 0.08)

def abdomen_tergite(n, total=5):
    t = n / (total - 1) if total > 1 else 0.5
    rx = 0.13 * (1 - 0.35 * t)
    ry = 0.09 * (1 - 0.3 * t)
    rz = 0.06 * (1 - 0.2 * t)
    z_offset = -0.18 - t * 0.28
    return _ellipsoid_mesh([0, 0, z_offset], rx, ry, rz)

def wing_mesh(side, fold=1.0):
    n_pts = 14
    theta = np.linspace(0, np.pi, n_pts)
    chord = 0.35 * (1 - 0.15 * np.cos(theta * 2))
    half_width = 0.08 * np.sin(theta) * (1 + 0.3 * np.sin(theta))
    y_off = 0.14 if side == 'L' else -0.14
    z_off = 0.03 + (1 - fold) * 0.12

    upper = np.column_stack([
        chord * np.cos(theta),
        np.full(n_pts, y_off) + half_width,
        np.full(n_pts, z_off) + 0.005 * np.sin(theta * 2),
    ])
    lower = np.column_stack([
        chord * np.cos(theta),
        np.full(n_pts, y_off) - half_width,
        np.full(n_pts, z_off) - 0.005 * np.sin(theta * 2),
    ])
    verts = np.vstack([upper, lower])
    n = n_pts
    faces = []
    for i in range(n - 1):
        faces.append([i, i + 1, i + n])
        faces.append([i + 1, i + n + 1, i + n])
    return verts, np.array(faces, dtype=np.int64)

def haltere(side):
    y_off = 0.08 if side == 'L' else -0.08
    pts = np.array([
        [0.05, y_off, -0.02],
        [-0.02, y_off, -0.01],
        [-0.06, y_off, 0.02],
    ])
    return pts

def antenna_line(side):
    y_off = 0.055 if side == 'L' else -0.055
    pts = np.array([
        [0.09, y_off, 0.04],
        [0.12, y_off, 0.06],
        [0.14, y_off, 0.07],
        [0.17, y_off, 0.09],
    ])
    return pts

def proboscis_line(extend=0.0):
    if extend < 0.01:
        return np.array([
            [0.05, 0, -0.04],
            [0.02, 0, -0.05],
        ])
    length = 0.1 * extend
    pts = np.array([
        [0.06, 0, -0.06],
        [0.06, 0, -0.06 - length * 0.3],
        [0.05, 0, -0.06 - length],
    ])
    return pts

def leg_segment_line(leg_name, coords):
    return np.array(coords)

LEG_COLORS = {
    'stance': '#44cc66',
    'swing': '#ff6644',
    'cleaning': '#4488ff',
    'feeding': '#cc8844',
}
