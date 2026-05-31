import numpy as np

BEHAVIORS = {
    'resting': {
        'label': 'Resting',
        'description': 'Low spontaneous baseline activity across all neuropils',
        'input_strength': 0.05,
        'targets': None,
    },
    'feeding': {
        'label': 'Feeding',
        'description': 'Gustatory input activates SEZ (GNG, SAD, PRW) and gnathal motor neuropils',
        'input_strength': 0.9,
        'targets': {
            'primary': ['GNG_L', 'GNG_R', 'SAD_L', 'SAD_R', 'PRW_L', 'PRW_R'],
            'secondary': ['VPS_L', 'VPS_R', 'PMS_L', 'PMS_R'],
        },
    },
    'walking': {
        'label': 'Walking',
        'description': 'Descending neuron targets activate leg motor circuits',
        'input_strength': 0.85,
        'targets': {
            'primary': ['GNG_L', 'GNG_R', 'VES_L', 'VES_R', 'SAD_L', 'SAD_R'],
            'secondary': ['PRW_L', 'PRW_R', 'EPA_L', 'EPA_R', 'GOR_L', 'GOR_R'],
        },
    },
    'startle': {
        'label': 'Startle / Escape',
        'description': 'Visual stimulus activates optic lobe giant fiber escape circuit',
        'input_strength': 1.0,
        'targets': {
            'primary': ['LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'ME_L', 'ME_R', 'AOTU_L', 'AOTU_R'],
            'secondary': ['GNG_L', 'GNG_R', 'SAD_L', 'SAD_R'],
        },
    },
    'olfactory_search': {
        'label': 'Olfactory Search',
        'description': 'Antennal lobe activates mushroom body learning and memory circuit',
        'input_strength': 0.8,
        'targets': {
            'primary': ['AL_L', 'AL_R', 'MB_CA_L', 'MB_CA_R', 'MB_M_L', 'MB_M_R', 'MB_VL_L', 'MB_VL_R'],
            'secondary': ['LH_L', 'LH_R', 'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R'],
        },
    },
    'walking_closed_loop': {
        'label': 'Walking (Closed-Loop)',
        'description': 'Brain→body→sensory closed-loop walking using FlyWire connectome',
        'closed_loop': True,
        'input_strength': 0.3,
        'targets': {
            'primary': ['GNG_L', 'GNG_R', 'VES_L', 'VES_R', 'SAD_L', 'SAD_R'],
            'secondary': ['VPS_L', 'VPS_R', 'PRW_L', 'PRW_R'],
        },
    },
}

def build_input_vector(neuropil_names, behavior_name):
    np_map = {n: i for i, n in enumerate(neuropil_names)}
    behavior = BEHAVIORS.get(behavior_name, BEHAVIORS['resting'])
    strength = behavior['input_strength']
    I = np.zeros(len(neuropil_names))

    if behavior['targets'] is None:
        I[:] = np.random.uniform(0, strength, len(neuropil_names))
        return I

    for tier, weight in [('primary', 1.0), ('secondary', 0.4)]:
        targets = behavior['targets'].get(tier, [])
        for t in targets:
            if t in np_map:
                I[np_map[t]] = strength * weight
            parts = t.split('_')
            base, hemi = parts[0], parts[1] if len(parts) > 1 else ''
            if hemi:
                other = f"{base}_{'R' if hemi == 'L' else 'L'}"
                if other in np_map:
                    I[np_map[other]] = strength * weight * 0.6

    return I

def build_all_input_vectors(neuropil_names):
    return {
        name: build_input_vector(neuropil_names, name)
        for name in BEHAVIORS
    }


class BehaviorStateMachine:
    STATES = ['RESTING', 'WALKING', 'FEEDING', 'FACE_CLEANING', 'STARTLE']

    def __init__(self):
        self.state = 'RESTING'
        self.timer = 0
        self.cleaning_bout = 0
        self.feeding_timer = 0

    def update(self, motor_cmds, dt=0.04):
        speed = motor_cmds.get('walking_speed', 0.0)
        proboscis_ext = motor_cmds.get('proboscis_extension', 0.0)
        cleaning_drive = motor_cmds.get('face_cleaning_drive', 0.0)

        self.timer += 1
        prev = self.state

        if self.cleaning_bout > 0:
            self.cleaning_bout -= 1
            self.state = 'FACE_CLEANING'
        elif cleaning_drive > 0.3 and speed < 0.08:
            self.state = 'FACE_CLEANING'
            self.cleaning_bout = 40
        elif proboscis_ext > 0.4 and speed < 0.12:
            self.state = 'FEEDING'
            self.feeding_timer = self.timer
        elif speed > 0.08:
            self.state = 'WALKING'
        else:
            self.state = 'RESTING'

        return self.state != prev
