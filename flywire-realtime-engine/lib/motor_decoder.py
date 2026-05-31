import numpy as np

MOTOR_MAP = {
    'walking_speed': {
        'sources': ['GNG_L', 'GNG_R', 'VES_L', 'VES_R'],
        'transform': 'mean',
        'range': [0.0, 1.0],
    },
    'turning_rate': {
        'sources_left': ['LAL_L'],
        'sources_right': ['LAL_R'],
        'transform': 'asymmetry',
        'range': [-1.0, 1.0],
    },
    'body_height': {
        'sources': ['SAD_L', 'SAD_R', 'PRW_L', 'PRW_R'],
        'transform': 'mean',
        'range': [0.14, 0.22],
    },
    'gait_energy': {
        'sources': ['GNG_L', 'GNG_R', 'VES_L', 'VES_R', 'VPS_L', 'VPS_R'],
        'transform': 'max',
        'range': [0.0, 1.0],
    },
    'wing_amplitude': {
        'sources': ['PMS_L', 'PMS_R'],
        'transform': 'mean',
        'range': [0.0, 0.3],
    },
    'head_pitch': {
        'sources': ['SAD_L', 'SAD_R', 'PRW_L', 'PRW_R'],
        'transform': 'mean',
        'range': [-0.4, 0.05],
    },
    'head_yaw': {
        'sources_left': ['LAL_L'],
        'sources_right': ['LAL_R'],
        'transform': 'asymmetry',
        'range': [-0.4, 0.4],
    },
    'proboscis_extension': {
        'sources': ['PRW_L', 'PRW_R', 'SAD_L', 'SAD_R'],
        'transform': 'max',
        'range': [0.0, 1.0],
    },
    'face_cleaning_drive': {
        'sources': ['VPS_L', 'VPS_R', 'PMS_L', 'PMS_R'],
        'transform': 'mean',
        'range': [0.0, 1.0],
    },
    'abdomen_bend': {
        'sources': ['EPA_L', 'EPA_R', 'GOR_L', 'GOR_R'],
        'transform': 'mean',
        'range': [0.0, 0.3],
    },
}

DECAY = 0.92
MIN_SPEED = 0.02


class MotorDecoder:
    def __init__(self, neuropil_names):
        self.np_map = {n: i for i, n in enumerate(neuropil_names)}
        self.smoothed = {k: 0.0 for k in MOTOR_MAP}
        self._cleaning_bout_timer = 0

    def decode(self, activity):
        raw = {}
        for name, spec in MOTOR_MAP.items():
            if spec['transform'] == 'mean':
                idxs = [self.np_map[s] for s in spec['sources'] if s in self.np_map]
                val = np.mean([activity[i] for i in idxs]) if idxs else 0.0
            elif spec['transform'] == 'max':
                idxs = [self.np_map[s] for s in spec['sources'] if s in self.np_map]
                val = max([activity[i] for i in idxs]) if idxs else 0.0
            elif spec['transform'] == 'asymmetry':
                l_idxs = [self.np_map[s] for s in spec['sources_left'] if s in self.np_map]
                r_idxs = [self.np_map[s] for s in spec['sources_right'] if s in self.np_map]
                l_val = np.mean([activity[i] for i in l_idxs]) if l_idxs else 0.0
                r_val = np.mean([activity[i] for i in r_idxs]) if r_idxs else 0.0
                val = l_val - r_val
            lo, hi = spec['range']
            if lo >= 0 or spec['transform'] != 'asymmetry':
                val = lo + np.clip(val, 0.0, 1.0) * (hi - lo)
            else:
                clipped = np.clip(val, -1.0, 1.0)
                val = lo + (clipped + 1.0) * 0.5 * (hi - lo)
            raw[name] = val

        raw_speed = raw.get('walking_speed', 0.0)
        raw_cleaning = raw.get('face_cleaning_drive', 0.0)
        raw_feeding = raw.get('proboscis_extension', 0.0)

        if raw_feeding > 0.4 and raw_speed < 0.1:
            self._cleaning_bout_timer = 0
        elif raw_cleaning > 0.3 and raw_speed < 0.05:
            self._cleaning_bout_timer = 60
        elif self._cleaning_bout_timer > 0:
            self._cleaning_bout_timer -= 1
            if self._cleaning_bout_timer > 0:
                raw['face_cleaning_drive'] = max(raw_cleaning, 0.4)

        for k in self.smoothed:
            target = raw[k]
            if k == 'walking_speed' and target < MIN_SPEED:
                target = 0.0
            self.smoothed[k] = self.smoothed[k] * DECAY + target * (1 - DECAY)

        return dict(self.smoothed)
