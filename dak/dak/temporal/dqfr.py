from enum import Enum

from dak.config.settings import DRIFT_DURATION, SAMPLING_DURATION, TICK_INTERVAL


class Phase(Enum):
    DRIFT = 'DRIFT'
    SAMPLING = 'SAMPLING'


class DQFR:
    def __init__(self, drift_duration=DRIFT_DURATION, sampling_duration=SAMPLING_DURATION):
        self.drift_duration = drift_duration
        self.sampling_duration = sampling_duration
        self.phase = Phase.SAMPLING
        self.time_in_phase = 0.0
        self.utility = 1.0

    def tick(self, dt=TICK_INTERVAL):
        self.time_in_phase += dt

    def should_transition(self):
        if self.phase == Phase.SAMPLING:
            return self.time_in_phase >= self.sampling_duration
        return self.time_in_phase >= self.drift_duration

    def transition(self, new_phase):
        self.phase = new_phase
        self.time_in_phase = 0.0

    def compute_utility(self, F_before, F_after):
        reduction = F_before - F_after
        self.utility = 0.9 * self.utility + 0.1 * max(0.0, reduction)
        return self.utility
