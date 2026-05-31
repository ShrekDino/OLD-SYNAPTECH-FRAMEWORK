from dak.temporal.dqfr import DQFR, Phase


def test_initial_phase():
    dqfr = DQFR()
    assert dqfr.phase == Phase.SAMPLING
    assert dqfr.time_in_phase == 0.0


def test_transition():
    dqfr = DQFR(drift_duration=1.0, sampling_duration=1.0)
    assert dqfr.phase == Phase.SAMPLING

    for _ in range(12):
        dqfr.tick(0.1)

    assert dqfr.should_transition() == True
    dqfr.transition(Phase.DRIFT)
    assert dqfr.phase == Phase.DRIFT
    assert dqfr.time_in_phase == 0.0


def test_utility():
    dqfr = DQFR()
    u = dqfr.compute_utility(10.0, 5.0)
    assert u > 0
    u2 = dqfr.compute_utility(5.0, 10.0)
    assert u2 < u


if __name__ == '__main__':
    test_initial_phase()
    test_transition()
    test_utility()
    print('All DQFR tests passed.')
