import numpy as np
from dak.metabolism.szilard import SzilardEngine
from dak.metabolism.landauer import LandauerFloor


def test_szilard_ratio():
    sz = SzilardEngine(window_size=10)
    land = LandauerFloor(window_size=10)

    buffer = []
    for i in range(20):
        buffer.append({
            'cpu_percent': 50.0 + np.random.randn() * 10,
            'mem_percent': 60.0 + np.random.randn() * 5,
        })

    H_env = sz.compute_H_env(buffer)
    assert H_env > 0, f'H_env should be positive, got {H_env}'

    mu_history = [np.random.randn(4) * 0.1 for _ in range(20)]
    S_gen = land.compute_S_gen(mu_history)
    assert S_gen >= 0, f'S_gen should be non-negative, got {S_gen}'

    ratio = sz.compute_ratio(H_env, S_gen)
    assert ratio > 0, f'Szilard ratio should be positive, got {ratio}'


def test_szilard_empty_buffer():
    sz = SzilardEngine()
    assert sz.compute_H_env([]) == 1.0
    assert sz.compute_H_env([{'a': 1.0}]) == 1.0


def test_szilard_sufficient_buffer():
    sz = SzilardEngine(window_size=10)
    buffer = [{'cpu_percent': 50.0 + i} for i in range(10)]
    H_env = sz.compute_H_env(buffer)
    assert H_env > 0, f'H_env should be positive with sufficient data, got {H_env}'


def test_landauer_empty():
    land = LandauerFloor()
    assert land.compute_S_gen([]) == 0.0
    assert land.compute_S_gen([np.array([1.0])]) == 0.0


if __name__ == '__main__':
    test_szilard_ratio()
    test_szilard_empty_buffer()
    test_landauer_empty()
    print('All Szilard/Landauer tests passed.')
