import time
import numpy as np
from dak import DAK


def test_dak_boot():
    dak = DAK(fresh=True)
    assert dak.state.read().shape == (64,)
    assert dak.F == 0.0
    assert dak.tick_count == 0


def test_dak_step():
    dak = DAK(fresh=True)
    mu_before = dak.state.read().copy()
    F_before = dak.F

    dak._step()

    assert dak.tick_count == 1
    assert dak.F >= 0
    assert dak.H_env >= 0
    assert dak.S_gen >= 0
    assert dak.szilard_ratio > 0

    mu_after = dak.state.read()
    diff = np.linalg.norm(mu_after - mu_before)
    assert diff > 0 or abs(dak.F - F_before) < 1e-6

    dak.state.cleanup()


def test_dak_dqfr_cycle():
    from dak.temporal.dqfr import Phase

    dak = DAK(fresh=True)
    t = dak.run_async()
    timeout = 5.0
    start = time.time()
    while dak.tick_count < 3 and time.time() - start < timeout:
        time.sleep(0.1)
    assert dak.tick_count >= 3, f'Expected >=3 ticks, got {dak.tick_count}'
    assert dak.dqfr.phase == Phase.SAMPLING
    assert dak.F > 0, f'F should be positive, got {dak.F}'
    assert dak.szilard_ratio > 0, f'szilard_ratio should be >0, got {dak.szilard_ratio}'
    dak.stop()
    t.join(timeout=2)
    dak.state.cleanup()


def test_dak_checkpoint():
    import os
    from dak.config.settings import CHECKPOINT_PATH

    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)

    dak = DAK(fresh=True)
    mu_orig = dak.state.read().copy()
    dak.state.save_checkpoint()
    assert os.path.exists(CHECKPOINT_PATH)
    dak.state.cleanup()

    dak2 = DAK(fresh=True)
    dak2.state.load_checkpoint()
    mu_after = dak2.state.read()
    assert np.allclose(mu_orig, mu_after), 'Loaded checkpoint should match saved state'
    dak2.state.cleanup()


if __name__ == '__main__':
    test_dak_boot()
    test_dak_step()
    test_dak_dqfr_cycle()
    test_dak_checkpoint()
    print('All integration tests passed.')
