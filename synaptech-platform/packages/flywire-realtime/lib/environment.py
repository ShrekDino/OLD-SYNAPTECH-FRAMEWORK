import numpy as np
from lib.fly_anatomy.skeleton import FlySkeleton, LEG_NAMES

GROUND_FRICTION = 0.7
TURN_DAMPING = 3.0


class DetailedFlyBody:
    def __init__(self):
        self.skeleton = FlySkeleton()
        self.pos = np.array([0.0, 0.0, 0.16], dtype=np.float64)
        self.heading = 0.0
        self.velocity = np.zeros(2, dtype=np.float64)
        self.turn_rate = 0.0
        self.gait_cycle = 0.0
        self._path = [np.array([0.0, 0.0])]
        self._active_pose = 'standing'
        self._pose_blend_rate = 0.08
        self._head_pitch = 0.0
        self._head_yaw = 0.0
        self._proboscis_extend = 0.0
        self._abdomen_bend = 0.0
        self._wing_fold = 1.0
        self._wing_flutter = 0.0

    def step(self, motor_cmds, dt=0.04):
        speed = float(motor_cmds.get('walking_speed', 0.0))
        turn = float(motor_cmds.get('turning_rate', 0.0))
        gait_energy = float(motor_cmds.get('gait_energy', 0.0))
        head_pitch = float(motor_cmds.get('head_pitch', 0.0))
        head_yaw = float(motor_cmds.get('head_yaw', 0.0))
        proboscis_ext = float(motor_cmds.get('proboscis_extension', 0.0))
        cleaning_drive = float(motor_cmds.get('face_cleaning_drive', 0.0))
        abdomen_bend = float(motor_cmds.get('abdomen_bend', 0.0))
        wing_amp = float(motor_cmds.get('wing_amplitude', 0.0))

        if speed < 0.01:
            gait_energy = 0.0

        self.gait_cycle = (self.gait_cycle + dt * 1.2 * (0.3 + 0.7 * gait_energy)) % 1.0

        turn_eff = turn * 1.5 * max(0.3, speed)
        self.turn_rate += (turn_eff - self.turn_rate) * dt * TURN_DAMPING
        self.heading += self.turn_rate * dt

        self.skeleton.heading = self.heading
        self.skeleton.pos = self.pos
        self.skeleton.gait_cycle = self.gait_cycle

        fwd_vel = speed * 0.6 * np.array([
            np.cos(self.heading),
            np.sin(self.heading),
        ])
        lat_vel = np.array([
            -np.sin(self.heading),
            np.cos(self.heading),
        ]) * self.turn_rate * 0.1

        self.velocity = self.velocity * 0.9 + (fwd_vel + lat_vel) * 0.1
        self.pos[:2] += self.velocity * dt * 2.0

        height_osci = 0.015 * np.sin(2 * np.pi * self.gait_cycle * 2)
        target_z = 0.16 + height_osci
        self.pos[2] += (target_z - self.pos[2]) * 0.1

        self._head_pitch += (head_pitch - self._head_pitch) * 0.1
        self._head_yaw += (head_yaw - self._head_yaw) * 0.1
        self._proboscis_extend += (proboscis_ext - self._proboscis_extend) * 0.08
        self._abdomen_bend += (abdomen_bend - self._abdomen_bend) * 0.06
        self._wing_fold += ((1.0 - wing_amp * 0.3) - self._wing_fold) * 0.04
        self._wing_flutter = wing_amp * 0.1 * np.sin(2 * np.pi * self.gait_cycle * 4)

        self._select_pose(speed, proboscis_ext, cleaning_drive)

        pose = self.skeleton.blender.get_full_state()
        pose['head']['pitch'] = self._head_pitch
        pose['head']['yaw'] = self._head_yaw
        pose['proboscis']['extend'] = self._proboscis_extend
        pose['abdomen']['bend'] = self._abdomen_bend
        pose['wings']['fold'] = self._wing_fold
        pose['wings']['flutter'] = self._wing_flutter

        if speed > 0.05:
            self.skeleton.apply_gait(speed, self.gait_cycle)

        for name in LEG_NAMES:
            leg_p = pose.get(f'{name}_leg', {})
            for joint, val in leg_p.items():
                key = f'{name}_leg'
                if key not in pose:
                    pose[key] = {}
                pose[key][joint] = val

        self.skeleton.blender.current = pose

        self._path.append(self.pos[:2].copy())
        if len(self._path) > 100:
            self._path.pop(0)

    def _select_pose(self, speed, proboscis_ext, cleaning_drive):
        if cleaning_drive > 0.3 and speed < 0.08:
            self._active_pose = 'face_cleaning'
            self._pose_blend_rate = 0.06
        elif proboscis_ext > 0.4 and speed < 0.12:
            self._active_pose = 'feeding'
            self._pose_blend_rate = 0.04
        elif speed > 0.08:
            self._active_pose = 'standing'
            self._pose_blend_rate = 0.08
        else:
            self._active_pose = 'standing'
            self._pose_blend_rate = 0.06

    def get_state(self):
        return {
            'pos': self.pos.copy(),
            'heading': self.heading,
            'velocity': self.velocity.copy(),
            'turn_rate': self.turn_rate,
            'gait_cycle': self.gait_cycle,
            'active_pose': self._active_pose,
            'head_pitch': self._head_pitch,
            'head_yaw': self._head_yaw,
            'proboscis_extend': self._proboscis_extend,
            'abdomen_bend': self._abdomen_bend,
            'wing_fold': self._wing_fold,
            'leg_joints': self.skeleton.get_leg_joints(),
            'leg_contacts': self.skeleton.get_contacts(),
            'skeleton_items': self.skeleton.evaluate(),
            'path': [p.copy() for p in self._path],
        }

    def get_sensory_state(self):
        speed = float(np.linalg.norm(self.velocity))
        contacts = self.skeleton.get_contacts()
        num_contact = sum(1 for c in contacts.values() if c)
        body_pitch = 0.015 * np.sin(2 * np.pi * self.gait_cycle * 2)
        body_roll = 0.008 * np.sin(2 * np.pi * self.gait_cycle * 2 + 0.5)

        is_cleaning = self._active_pose == 'face_cleaning'
        is_feeding = self._active_pose == 'feeding'

        return {
            'body_velocity': speed,
            'turn_rate': self.turn_rate,
            'heading': self.heading,
            'leg_contacts': contacts,
            'num_leg_contacts': num_contact,
            'body_pitch': body_pitch,
            'body_roll': body_roll,
            'avg_gait_phase': self.gait_cycle,
            'body_height': self.pos[2],
            'head_pitch': self._head_pitch,
            'head_yaw': self._head_yaw,
            'proboscis_extend': self._proboscis_extend,
            'is_face_cleaning': is_cleaning,
            'is_feeding': is_feeding,
        }
