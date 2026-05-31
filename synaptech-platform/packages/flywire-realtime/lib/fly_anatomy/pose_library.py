import numpy as np

ZERO_POSE = {
    'head': {'pitch': 0.0, 'yaw': 0.0},
    'proboscis': {'extend': 0.0},
    'abdomen': {'bend': 0.0},
    'wings': {'fold': 1.0, 'flutter': 0.0},
    'L1_leg': {'coxa': 0.0, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.1},
    'R1_leg': {'coxa': 0.0, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.1},
    'L2_leg': {'coxa': 0.0, 'femur': -0.2, 'tibia': 0.5, 'tarsus': 0.1},
    'R2_leg': {'coxa': 0.0, 'femur': -0.2, 'tibia': 0.5, 'tarsus': 0.1},
    'L3_leg': {'coxa': 0.0, 'femur': -0.3, 'tibia': 0.6, 'tarsus': 0.1},
    'R3_leg': {'coxa': 0.0, 'femur': -0.3, 'tibia': 0.6, 'tarsus': 0.1},
}

STANDING = {
    'head': {'pitch': 0.0, 'yaw': 0.0},
    'proboscis': {'extend': 0.0},
    'abdomen': {'bend': 0.0},
    'wings': {'fold': 1.0, 'flutter': 0.0},
    'L1_leg': {'coxa': 0.15, 'femur': -0.2, 'tibia': 0.5, 'tarsus': 0.05},
    'R1_leg': {'coxa': -0.15, 'femur': -0.2, 'tibia': 0.5, 'tarsus': 0.05},
    'L2_leg': {'coxa': 0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'R2_leg': {'coxa': -0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'L3_leg': {'coxa': 0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
    'R3_leg': {'coxa': -0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
}

FEEDING = {
    'head': {'pitch': -0.35, 'yaw': 0.0},
    'proboscis': {'extend': 1.0},
    'abdomen': {'bend': 0.0},
    'wings': {'fold': 1.0, 'flutter': 0.0},
    'L1_leg': {'coxa': 0.2, 'femur': -0.1, 'tibia': 0.35, 'tarsus': 0.15},
    'R1_leg': {'coxa': -0.2, 'femur': -0.1, 'tibia': 0.35, 'tarsus': 0.15},
    'L2_leg': {'coxa': 0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'R2_leg': {'coxa': -0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'L3_leg': {'coxa': 0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
    'R3_leg': {'coxa': -0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
}

FACE_CLEANING = {
    'head': {'pitch': -0.2, 'yaw': 0.0},
    'proboscis': {'extend': 0.0},
    'abdomen': {'bend': 0.02},
    'wings': {'fold': 1.0, 'flutter': 0.0},
    'L1_leg': {'coxa': 0.65, 'femur': 0.55, 'tibia': -0.75, 'tarsus': 0.3},
    'R1_leg': {'coxa': -0.65, 'femur': 0.55, 'tibia': -0.75, 'tarsus': 0.3},
    'L2_leg': {'coxa': 0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'R2_leg': {'coxa': -0.1, 'femur': -0.15, 'tibia': 0.45, 'tarsus': 0.05},
    'L3_leg': {'coxa': 0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
    'R3_leg': {'coxa': -0.2, 'femur': -0.25, 'tibia': 0.55, 'tarsus': 0.05},
}

STARTLE = {
    'head': {'pitch': 0.05, 'yaw': 0.0},
    'proboscis': {'extend': 0.0},
    'abdomen': {'bend': -0.08},
    'wings': {'fold': 0.2, 'flutter': 0.0},
    'L1_leg': {'coxa': 0.1, 'femur': -0.35, 'tibia': 0.7, 'tarsus': 0.1},
    'R1_leg': {'coxa': -0.1, 'femur': -0.35, 'tibia': 0.7, 'tarsus': 0.1},
    'L2_leg': {'coxa': 0.05, 'femur': -0.3, 'tibia': 0.65, 'tarsus': 0.1},
    'R2_leg': {'coxa': -0.05, 'femur': -0.3, 'tibia': 0.65, 'tarsus': 0.1},
    'L3_leg': {'coxa': 0.15, 'femur': -0.4, 'tibia': 0.7, 'tarsus': 0.1},
    'R3_leg': {'coxa': -0.15, 'femur': -0.4, 'tibia': 0.7, 'tarsus': 0.1},
}

POSE_BOOK = {
    'zero': ZERO_POSE,
    'standing': STANDING,
    'feeding': FEEDING,
    'face_cleaning': FACE_CLEANING,
    'startle': STARTLE,
}

class PoseBlender:
    def __init__(self):
        self.current = {}
        for part, joints in ZERO_POSE.items():
            self.current[part] = dict(joints)

    def blend_to(self, target_pose, rate=0.08):
        for part, joints in target_pose.items():
            if part not in self.current:
                self.current[part] = {}
            for joint, val in joints.items():
                old = self.current[part].get(joint, 0.0)
                self.current[part][joint] = old + (val - old) * rate

    def get(self, part, joint, default=0.0):
        return self.current.get(part, {}).get(joint, default)

    def set_pose(self, pose_name, rate=0.08):
        if pose_name in POSE_BOOK:
            self.blend_to(POSE_BOOK[pose_name], rate)

    def get_full_state(self):
        return dict(self.current)
