import numpy as np
from .body_parts import (
    head_capsule, compound_eye, thorax, abdomen_tergite,
    wing_mesh, haltere, antenna_line, proboscis_line,
)
from .pose_library import PoseBlender

LEG_NAMES = ['L1', 'R1', 'L2', 'R2', 'L3', 'R3']

LEG_ATTACH = {
    'L1': np.array([0.14, 0.09, -0.02]),
    'R1': np.array([0.14, -0.09, -0.02]),
    'L2': np.array([0.0, 0.10, -0.02]),
    'R2': np.array([0.0, -0.10, -0.02]),
    'L3': np.array([-0.14, 0.09, -0.02]),
    'R3': np.array([-0.14, -0.09, -0.02]),
}

SEGMENT_LENGTHS = {
    'coxa': 0.04, 'femur': 0.09, 'tibia': 0.07, 'tarsus': 0.06,
}

TRIPOD_A = {'L1', 'R2', 'L3'}
TRIPOD_B = {'R1', 'L2', 'R3'}


class FlySkeleton:
    def __init__(self):
        self.blender = PoseBlender()
        self.heading = 0.0
        self.pos = np.zeros(3)
        self.gait_cycle = 0.0
        self.leg_contacts = {name: True for name in LEG_NAMES}
        self.leg_tip_positions = {}
        self._cache = {}

    def set_pose(self, pose_name, rate=0.08):
        self.blender.set_pose(pose_name, rate)

    def blend_to(self, target_pose, rate=0.08):
        self.blender.blend_to(target_pose, rate)

    def apply_gait(self, speed, gait_cycle):
        for name in LEG_NAMES:
            is_a = name in TRIPOD_A
            offset = 0.0 if is_a else 0.5
            phase = (gait_cycle + offset) % 1.0
            in_swing = phase >= 0.5
            sw = (phase - 0.5) / 0.5 if in_swing else 0.0
            fwd = 0.06 * speed * np.cos(2 * np.pi * phase)
            lift = 0.05 * np.sin(np.pi * sw) if in_swing else 0.0

            pose_val = self.blender.get(f'{name}_leg', 'tibia', 0.5)
            base_tibia = pose_val
            gait_mod = fwd * 0.3
            self.blender.current[f'{name}_leg']['tibia'] = base_tibia + gait_mod

            contact = not in_swing and speed > 0.01
            self.leg_contacts[name] = contact

    def evaluate(self):
        pose = self.blender.get_full_state()
        items = []

        head_pitch = pose.get('head', {}).get('pitch', 0.0)
        head_yaw = pose.get('head', {}).get('yaw', 0.0)
        proboscis_ext = pose.get('proboscis', {}).get('extend', 0.0)
        abdomen_bend = pose.get('abdomen', {}).get('bend', 0.0)
        wing_fold = pose.get('wings', {}).get('fold', 1.0)
        wing_flutter = pose.get('wings', {}).get('flutter', 0.0)

        c, s = np.cos(self.heading), np.sin(self.heading)

        def world(offset):
            x = offset[0] * c - offset[1] * s + self.pos[0]
            y = offset[0] * s + offset[1] * c + self.pos[1]
            z = offset[2] + self.pos[2]
            return np.array([x, y, z])

        def head_rotate(offset, pitch, yaw):
            cp, sp = np.cos(pitch), np.sin(pitch)
            cy, sy = np.cos(yaw), np.sin(yaw)
            x = offset[0] * cy - offset[1] * sy
            y = offset[0] * sy * cp + offset[1] * cy * cp + offset[2] * sp
            z = -offset[0] * sy * sp - offset[1] * cy * sp + offset[2] * cp
            return np.array([x, y, z])

        thorax_center = world([0, 0, 0.02])
        head_offset_body = np.array([0.17, 0, 0.04])
        head_center_local = head_rotate(head_offset_body, head_pitch, head_yaw)
        head_center = world(head_center_local)

        v, f = thorax()
        items.append({'type': 'mesh', 'verts': v + thorax_center, 'faces': f, 'color': '#5588aa'})

        v, f = head_capsule()
        items.append({'type': 'mesh', 'verts': v + head_center, 'faces': f, 'color': '#88bbcc'})

        for side, y_sign in [('L', 1), ('R', -1)]:
            eye_v, eye_f = compound_eye(side)
            eye_center = head_center + np.array([0.02, y_sign * 0.01, 0.0])
            items.append({'type': 'mesh', 'verts': eye_v + eye_center, 'faces': eye_f, 'color': '#cc4422'})

            ant = antenna_line(side)
            ant_world = np.array([world(head_rotate(a, head_pitch, head_yaw)) for a in ant])
            items.append({'type': 'line', 'points': ant_world, 'color': '#ddaa88', 'width': 2})

        prob = proboscis_line(proboscis_ext)
        prob_world = np.array([world(head_rotate(p, head_pitch, head_yaw) + head_offset_body) for p in prob])
        if len(prob) > 1:
            items.append({'type': 'line', 'points': prob_world, 'color': '#dd8855', 'width': 3})

        for n in range(5):
            v, f = abdomen_tergite(n, 5)
            bend_angle = abdomen_bend * (n / 4)
            offset = np.array([0, 0, 0])
            terg_world = world(offset)
            items.append({'type': 'mesh', 'verts': v + terg_world, 'faces': f,
                          'color': f'#{40+n*4:x}{60+n*3:x}{80-n*3:x}'})

        for side, y_sign in [('L', 1), ('R', -1)]:
            wv, wf = wing_mesh(side, wing_fold + wing_flutter * 0.05)
            wing_center = world(np.array([0.02, y_sign * 0.08, 0.02]))
            items.append({'type': 'mesh', 'verts': wv + wing_center, 'faces': wf,
                          'color': 'rgba(200,220,240,0.4)'})

            ht = haltere(side)
            ht_world = world(ht[0])
            items.append({'type': 'line', 'points': np.array([world(p) for p in ht]), 'color': '#aa8866', 'width': 2})

        for name in LEG_NAMES:
            self._build_leg(name, pose, items)

        return items

    def _build_leg(self, name, pose, items):
        attach = LEG_ATTACH[name]
        c, s = np.cos(self.heading), np.sin(self.heading)

        def world(offset):
            x = offset[0] * c - offset[1] * s + self.pos[0]
            y = offset[0] * s + offset[1] * c + self.pos[1]
            z = offset[2] + self.pos[2]
            return np.array([x, y, z])

        leg_pose = pose.get(f'{name}_leg', {})
        coxa_a = leg_pose.get('coxa', 0.0)
        femur_a = leg_pose.get('femur', -0.2)
        tibia_a = leg_pose.get('tibia', 0.5)
        tarsus_a = leg_pose.get('tarsus', 0.1)

        y_sign = 1 if name.startswith('L') else -1

        coxa_end = attach + np.array([0, y_sign * 0.02 * np.sin(coxa_a), -SEGMENT_LENGTHS['coxa']])
        femur_end = coxa_end + np.array([
            SEGMENT_LENGTHS['femur'] * np.sin(femur_a),
            y_sign * SEGMENT_LENGTHS['femur'] * 0.1,
            -SEGMENT_LENGTHS['femur'] * np.cos(femur_a),
        ])
        tibia_end = femur_end + np.array([
            -SEGMENT_LENGTHS['tibia'] * np.sin(tibia_a) * 0.3,
            0,
            -SEGMENT_LENGTHS['tibia'] * np.cos(tibia_a),
        ])
        tarsus_end = tibia_end + np.array([
            SEGMENT_LENGTHS['tarsus'] * 0.2,
            0,
            -SEGMENT_LENGTHS['tarsus'] * 0.9,
        ])

        pts_local = np.array([attach, coxa_end, femur_end, tibia_end, tarsus_end])
        pts_world = np.array([world(p) for p in pts_local])

        contact = self.leg_contacts.get(name, True)
        speed = abs(self.gait_cycle - 0.5) * 2 if hasattr(self, 'gait_cycle') else 0

        is_front = name in ('L1', 'R1')
        is_cleaning = is_front and abs(femur_a) > 0.3 and abs(tibia_a) > 0.6
        is_feeding = is_front and abs(femur_a) < 0.15

        if is_cleaning:
            color = '#4488ff'
        elif is_feeding:
            color = '#cc8844'
        elif contact:
            color = '#44cc66'
        else:
            color = '#ff6644'

        items.append({'type': 'leg', 'points': pts_world, 'color': color, 'width': 4, 'name': name})

    def get_leg_joints(self):
        joints = {}
        for name in LEG_NAMES:
            attach = LEG_ATTACH[name]
            c, s = np.cos(self.heading), np.sin(self.heading)
            def world(offset):
                x = offset[0] * c - offset[1] * s + self.pos[0]
                y = offset[0] * s + offset[1] * c + self.pos[1]
                z = offset[2] + self.pos[2]
                return np.array([x, y, z])
            joints[name] = {
                'hip': world(attach),
                'knee': world(attach + np.array([0.03, 0, -0.08])),
                'foot': world(attach + np.array([0, 0, -0.18])),
            }
        return joints

    def get_contacts(self):
        return dict(self.leg_contacts)
