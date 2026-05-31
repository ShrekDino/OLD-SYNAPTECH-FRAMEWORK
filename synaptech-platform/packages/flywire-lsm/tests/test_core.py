import numpy as np

from flywire_lsm.config import MAX_DELAY, N_A, N_B, N_NEURONS
from flywire_lsm.core import ConnectomeGraph, HierarchicalReservoir


class TestConnectomeGraph:
    def test_square_construction(self):
        g = ConnectomeGraph(100, 0.1, 0.8, rng=np.random.default_rng(42))
        assert g.n == 100
        assert g.n_pre == 100
        assert g.nnz > 0
        assert g.density > 0
        assert g.n_exc + g.n_inh == g.nnz

    def test_rectangular_construction(self):
        g = ConnectomeGraph(50, 0.1, 0.8, rng=np.random.default_rng(42), n_pre=30)
        assert g.n == 50
        assert g.n_pre == 30
        assert g.nnz > 0

    def test_spectral_normalization(self):
        g = ConnectomeGraph(50, 0.3, 0.8, rng=np.random.default_rng(42))
        g.apply_spectral_normalization(0.95)
        W_dense = np.zeros((50, 50))
        for i in range(50):
            row_start = g.colptr[i]
            row_end = g.colptr[i + 1]
            if row_start < row_end:
                W_dense[g.rows[row_start:row_end], i] = g.data[row_start:row_end]
        ev = np.linalg.eigvals(W_dense)
        rho = float(np.max(np.abs(ev)))
        assert abs(rho - 0.95) < 0.05

    def test_matvec_delayed_square(self):
        g = ConnectomeGraph(20, 0.5, 0.8, rng=np.random.default_rng(42))
        g.apply_spectral_normalization(0.9)
        delay_buf = [np.ones(20, dtype=np.float64) for _ in range(MAX_DELAY)]
        out = g.matvec_delayed(delay_buf)
        assert out.shape == (20,)
        assert not np.all(out == 0)

    def test_rectangular_skips_spectral_norm(self):
        g = ConnectomeGraph(50, 0.1, 0.8, rng=np.random.default_rng(42), n_pre=30)
        before = g.data.copy()
        g.apply_spectral_normalization(0.95)
        np.testing.assert_array_equal(before, g.data)


class TestHierarchicalReservoir:
    def test_initialization(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        assert hr.n_a == N_A
        assert hr.n_b == N_B
        assert hr.step_count == 0
        assert hr.graph_AA.n == N_A
        assert hr.graph_BB.n == N_B

    def test_step_updates_state(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        inj = np.zeros(N_NEURONS, dtype=np.float64)
        inj[0] = 1.0
        a_A, a_B = hr.step(inj, log=False)
        assert a_A.shape == (N_A,)
        assert a_B.shape == (N_B,)
        assert hr.step_count == 1
        assert not np.all(hr.v_A == 0)
        assert not np.all(hr.v_B == 0)

    def test_get_state(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        state = hr.get_state()
        assert state.shape == (N_NEURONS,)
        assert np.all(state == 0)

    def test_reset(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        inj = np.zeros(N_NEURONS, dtype=np.float64)
        inj[0] = 1.0
        hr.step(inj, log=False)
        assert hr.step_count == 1
        hr.reset()
        assert hr.step_count == 0
        assert np.all(hr.v_A == 0)
        assert np.all(hr.v_B == 0)
        assert np.all(hr.get_state() == 0)

    def test_multiple_steps(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        inj = np.zeros(N_NEURONS, dtype=np.float64)
        for i in range(10):
            inj[i % 79] = 1.0
            hr.step(inj, log=False)
            inj.fill(0)
        assert hr.step_count == 10

    def test_delay_buffer_effect(self):
        hr = HierarchicalReservoir(rng=np.random.default_rng(42))
        inj = np.zeros(N_NEURONS, dtype=np.float64)
        inj[0] = 1.0
        state_after_1 = hr.get_state().copy()
        hr.step(inj, log=False)
        state_after_2 = hr.get_state().copy()
        assert not np.array_equal(state_after_1, state_after_2)
