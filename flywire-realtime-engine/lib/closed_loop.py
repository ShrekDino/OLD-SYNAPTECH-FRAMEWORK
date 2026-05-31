import numpy as np
from lib.environment import DetailedFlyBody
from lib.motor_decoder import MotorDecoder
from lib.sensory_feedback import build_closed_loop_input
from lib.behaviors import BehaviorStateMachine
from lib.big_pickle import profiled


class ClosedLoopSimulation:
    def __init__(self, brain, neuropil_names):
        self.brain = brain
        self.names = neuropil_names
        self.n = len(neuropil_names)
        self.body = DetailedFlyBody()
        self.decoder = MotorDecoder(neuropil_names)
        self.behavior_fsm = BehaviorStateMachine()

    @profiled("closed_loop_run")
    def run(self, timesteps=400, initial_kick_strength=0.3):
        history = {
            'activity': np.zeros((timesteps, self.n), dtype=np.float64),
            'motor_commands': [],
            'body_states': [],
            'sensory_inputs': np.zeros((timesteps, self.n), dtype=np.float64),
        }

        activity = np.random.uniform(0, 0.02, self.n)

        np_map = {n: i for i, n in enumerate(self.names)}

        for key in ['GNG_L', 'GNG_R', 'VES_L', 'VES_R']:
            if key in np_map:
                activity[np_map[key]] = 0.3

        feeding_modulation = 0.0

        for t in range(timesteps):
            motor = self.decoder.decode(activity)
            self.body.step(motor, dt=0.04)

            changed = self.behavior_fsm.update(motor)
            state = self.behavior_fsm.state

            sensory = build_closed_loop_input(self.names, self.body.get_sensory_state())

            ramp = min(1.0, t / 20.0)
            I_eff = sensory * ramp

            if state == 'FEEDING':
                feeding_modulation = min(1.0, feeding_modulation + 0.005)
                for key in ['PRW_L', 'PRW_R', 'SAD_L', 'SAD_R']:
                    if key in np_map:
                        I_eff[np_map[key]] += 0.3 * feeding_modulation
            else:
                feeding_modulation = max(0.0, feeding_modulation - 0.005)

            if state == 'FACE_CLEANING':
                for key in ['VPS_L', 'VPS_R', 'PMS_L', 'PMS_R']:
                    if key in np_map:
                        I_eff[np_map[key]] += 0.25

            if t < 30:
                decay = 1.0 - t / 30.0
                for key in ['GNG_L', 'GNG_R', 'VES_L', 'VES_R']:
                    if key in np_map:
                        I_eff[np_map[key]] += initial_kick_strength * decay

            activity = self.brain.step(activity, I_eff)
            activity = np.clip(
                activity + np.random.uniform(-0.008, 0.008, self.n),
                0.0, 1.0,
            )

            motor['_behavior_state'] = state
            history['activity'][t] = activity
            history['motor_commands'].append(dict(motor))
            history['body_states'].append(self.body.get_state())
            history['sensory_inputs'][t] = sensory

        return history
