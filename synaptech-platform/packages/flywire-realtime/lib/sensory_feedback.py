import numpy as np


def build_closed_loop_input(neuropil_names, sensory_state):
    I = np.zeros(len(neuropil_names))
    np_map = {n: i for i, n in enumerate(neuropil_names)}

    speed = sensory_state.get('body_velocity', 0.0)
    turn_rate = sensory_state.get('turn_rate', 0.0)
    contacts = sensory_state.get('leg_contacts', {})
    gait_phase = sensory_state.get('avg_gait_phase', 0.0)
    body_pitch = sensory_state.get('body_pitch', 0.0)
    body_roll = sensory_state.get('body_roll', 0.0)

    head_pitch = sensory_state.get('head_pitch', 0.0)
    proboscis_ext = sensory_state.get('proboscis_extend', 0.0)
    is_cleaning = sensory_state.get('is_face_cleaning', False)
    is_feeding = sensory_state.get('is_feeding', False)

    for leg_name, contact in contacts.items():
        side = leg_name[0]
        for np_name in [f'GNG_{side}', f'VPS_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] += 0.35 * float(contact)

    for side in ['L', 'R']:
        for np_name in [f'AMMC_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] = np.clip(speed * 0.6, 0.0, 1.0)

    for side in ['L', 'R']:
        sway_val = abs(body_pitch) + abs(body_roll)
        for np_name in [f'VES_{side}', f'SAD_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] = np.clip(sway_val * 0.5, 0.0, 1.0)

    if 'FB' in np_map:
        I[np_map['FB']] = np.clip(abs(turn_rate) * 0.6, 0.0, 1.0)
    if 'EB' in np_map:
        I[np_map['EB']] = np.clip(speed * 0.4, 0.0, 1.0)
    if 'PB' in np_map:
        phase_mod = 0.5 + 0.5 * np.sin(2 * np.pi * gait_phase)
        I[np_map['PB']] = np.clip(0.1 + 0.25 * phase_mod, 0.0, 1.0)

    lal_asym = turn_rate * 0.3
    if 'LAL_L' in np_map:
        I[np_map['LAL_L']] = np.clip(0.1 + lal_asym, 0.0, 1.0)
    if 'LAL_R' in np_map:
        I[np_map['LAL_R']] = np.clip(0.1 - lal_asym, 0.0, 1.0)

    for side in ['L', 'R']:
        for np_name in [f'PRW_{side}', f'EPA_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] = np.clip(
                    0.05 + 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * gait_phase + 0.3)),
                    0.0, 1.0,
                )

    feed_val = proboscis_ext * 0.4
    for side in ['L', 'R']:
        for np_name in [f'PRW_{side}', f'SAD_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] += np.clip(feed_val, 0.0, 1.0)

    head_pitch_fb = abs(head_pitch) * 0.3
    for side in ['L', 'R']:
        for np_name in [f'AMMC_{side}', f'VES_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] += np.clip(head_pitch_fb, 0.0, 1.0)

    cleaning_signal = 0.2 if is_cleaning else 0.0
    for side in ['L', 'R']:
        for np_name in [f'VPS_{side}', f'PMS_{side}']:
            if np_name in np_map:
                I[np_map[np_name]] += cleaning_signal

    if is_feeding:
        for side in ['L', 'R']:
            if f'PRW_{side}' in np_map:
                I[np_map[f'PRW_{side}']] += 0.2

    if is_cleaning:
        for side in ['L', 'R']:
            for np_name in [f'AL_{side}']:
                if np_name in np_map:
                    I[np_map[np_name]] += 0.25

    for side in ['L', 'R']:
        if f'GNG_{side}' in np_map:
            I[np_map[f'GNG_{side}']] += 0.08

    return np.clip(I, 0.0, 1.0)
