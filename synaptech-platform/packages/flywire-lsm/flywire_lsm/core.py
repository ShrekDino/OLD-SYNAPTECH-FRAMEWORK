import time

import numpy as np

from flywire_lsm.config import (
    A_TO_B_SCALE,
    A_TO_B_SPARSITY,
    B_TO_A_SCALE,
    B_TO_A_SPARSITY,
    DEFAULT_SEED,
    EXC_RATIO,
    LEAK_RATE_A,
    LEAK_RATE_B,
    MAX_DELAY,
    N_A,
    N_B,
    NOISE_STD,
    SENSORY_GAIN,
    SPARSITY,
    SPECTRAL_RADIUS_A,
    SPECTRAL_RADIUS_B,
)
from flywire_lsm.logging import get_logger

_LOG = get_logger()


class ConnectomeGraph:
    def __init__(
        self,
        n_neurons: int,
        sparsity: float,
        exc_ratio: float,
        rng: np.random.Generator | None = None,
        n_pre: int | None = None,
    ) -> None:
        t0 = time.perf_counter()
        self.n = n_neurons
        self.n_pre = n_pre if n_pre is not None else n_neurons

        if rng is None:
            rng = np.random.default_rng(DEFAULT_SEED)

        is_square = (self.n_pre == self.n)
        if is_square:
            n_possible = n_neurons * (n_neurons - 1)
        else:
            n_possible = self.n_pre * self.n

        n_edges = int(n_possible * sparsity)
        n_edges = max(n_edges, 1)

        tag = "square" if is_square else f"rect({self.n_pre}->{self.n})"
        _LOG.info(
            "[INIT] ConnectomeGraph: %s N=%d sparsity=%.3f target_NNZ=%d",
            tag, n_neurons, sparsity, n_edges,
        )

        if is_square:
            all_pairs = [
                (i, j) for i in range(self.n_pre)
                for j in range(n_neurons) if i != j
            ]
        else:
            all_pairs = [
                (i, j) for i in range(self.n_pre) for j in range(n_neurons)
            ]

        chosen = rng.choice(len(all_pairs), size=n_edges, replace=False)

        n_exc = int(n_edges * exc_ratio)
        n_inh = n_edges - n_exc
        exc_w = rng.uniform(0.1, 1.0, size=n_exc).tolist()
        inh_w = rng.uniform(-1.0, -0.1, size=n_inh).tolist()
        all_w = exc_w + inh_w
        rng.shuffle(all_w)
        all_d = rng.integers(1, MAX_DELAY + 1, size=n_edges).tolist()

        edges: list[tuple[int, int, float, int]] = []
        for idx, sel in enumerate(chosen):
            s, t = all_pairs[sel]
            edges.append((s, t, all_w[idx], all_d[idx]))

        edges.sort(key=lambda x: x[1])

        self.colptr = np.zeros(n_neurons + 1, dtype=np.int64)
        self.rows = np.zeros(n_edges, dtype=np.int64)
        self.data = np.zeros(n_edges, dtype=np.float64)
        self.delays = np.zeros(n_edges, dtype=np.int64)

        for ei, (src, dst, w, d) in enumerate(edges):
            self.rows[ei] = src
            self.data[ei] = w
            self.delays[ei] = d

        cnt = 0
        for dst in range(n_neurons):
            c = sum(1 for e in edges if e[1] == dst)
            cnt += c
            self.colptr[dst + 1] = cnt

        self.col_idx = np.zeros(n_edges, dtype=np.int64)
        for col in range(n_neurons):
            self.col_idx[self.colptr[col]:self.colptr[col + 1]] = col

        self.nnz = n_edges
        self.density = n_edges / n_possible if n_possible > 0 else 0.0
        self.n_exc = n_exc
        self.n_inh = n_inh
        self.mean_weight = float(np.mean(self.data))
        self.std_weight = float(np.std(self.data))

        dt = time.perf_counter() - t0
        mem_kb = (
            self.colptr.nbytes + self.rows.nbytes
            + self.data.nbytes + self.delays.nbytes
        ) / 1024

        _LOG.info("[INIT] Graph built in %.3f ms", dt * 1000)
        _LOG.info(
            "[GRAPH] NNZ=%d density=%.6f  E=%d(%.1f%%) I=%d(%.1f%%)",
            self.nnz, self.density,
            self.n_exc, self.n_exc / self.nnz * 100,
            self.n_inh, self.n_inh / self.nnz * 100,
        )
        _LOG.info("[GRAPH] Weights: mu=%.4f sigma=%.4f", self.mean_weight, self.std_weight)
        _LOG.info("[GRAPH] Memory: ~%.2f KB", mem_kb)

    def apply_spectral_normalization(self, target_radius: float) -> None:
        if self.n_pre != self.n:
            _LOG.info("[GRAPH] Rectangular graph -- skipping spectral norm")
            return

        _LOG.info("[GRAPH] Computing spectral radius of %dx%d weight matrix ...", self.n, self.n)
        W_dense = np.zeros((self.n, self.n), dtype=np.float64)
        for i in range(self.n):
            row_start = self.colptr[i]
            row_end = self.colptr[i + 1]
            if row_start < row_end:
                W_dense[self.rows[row_start:row_end], i] = self.data[row_start:row_end]

        ev = np.linalg.eigvals(W_dense)
        orig_rho = float(np.max(np.abs(ev)))
        scale = target_radius / orig_rho if orig_rho > 0 else 1.0
        self.data *= scale
        new_rho = orig_rho * scale

        _LOG.info(
            "[GRAPH] Spectral radius: %.4f -> %.4f (scale=%.4f, target=%.4f)",
            orig_rho, new_rho, scale, target_radius,
        )

    def matvec_delayed(self, delay_buffer: list[np.ndarray]) -> np.ndarray:
        out = np.zeros(self.n, dtype=np.float64)
        depth_limit = min(len(delay_buffer), MAX_DELAY)
        for depth in range(depth_limit):
            mask = self.delays == (depth + 1)
            if not np.any(mask):
                continue
            contrib = self.data[mask] * delay_buffer[depth][self.rows[mask]]
            out += np.bincount(self.col_idx[mask], weights=contrib, minlength=self.n)
        return out


class HierarchicalReservoir:
    def __init__(
        self,
        sensory_gain: float = SENSORY_GAIN,
        noise_std: float = NOISE_STD,
        max_delay: int = MAX_DELAY,
        rng: np.random.Generator | None = None,
    ) -> None:
        t0 = time.perf_counter()
        self.rng = rng if rng is not None else np.random.default_rng(DEFAULT_SEED)
        self.n_a = N_A
        self.n_b = N_B
        self.sensory_gain = sensory_gain
        self.noise_std = noise_std
        self.delay_depth = max_delay

        def _make_square(n, sp, er, sr, label):
            g = ConnectomeGraph(n, sp, er, rng=self.rng)
            g.apply_spectral_normalization(sr)
            _LOG.info("[INIT] Module %s  N=%d rho=%.2f alpha=%.2f", label, n, sr,
                      LEAK_RATE_A if label == 'A' else LEAK_RATE_B)
            return g

        def _make_rect(pre_n, post_n, sp, er, scale, label):
            g = ConnectomeGraph(post_n, sp, er, rng=self.rng, n_pre=pre_n)
            g.data *= scale
            _LOG.info("[INIT] Projection %s  %d->%d sparsity=%.4f scale=%.2f",
                      label, pre_n, post_n, sp, scale)
            return g

        self.graph_AA = _make_square(N_A, SPARSITY, EXC_RATIO, SPECTRAL_RADIUS_A, "A")
        self.graph_BB = _make_square(N_B, SPARSITY, EXC_RATIO, SPECTRAL_RADIUS_B, "B")
        self.graph_AB = _make_rect(N_A, N_B, A_TO_B_SPARSITY, EXC_RATIO, A_TO_B_SCALE, "A->B")
        self.graph_BA = _make_rect(N_B, N_A, B_TO_A_SPARSITY, EXC_RATIO, B_TO_A_SCALE, "B->A")

        self.v_A = np.zeros(N_A, dtype=np.float64)
        self.a_A = np.zeros(N_A, dtype=np.float64)
        self.v_B = np.zeros(N_B, dtype=np.float64)
        self.a_B = np.zeros(N_B, dtype=np.float64)

        self.delay_A: list[np.ndarray] = [
            np.zeros(N_A, dtype=np.float64) for _ in range(self.delay_depth)
        ]
        self.delay_B: list[np.ndarray] = [
            np.zeros(N_B, dtype=np.float64) for _ in range(self.delay_depth)
        ]

        self.step_count = 0

        dt = time.perf_counter() - t0
        _LOG.info("[INIT] HierarchicalReservoir: A=%d(alpha=%.2f,rho=%.2f) "
                  "B=%d(alpha=%.2f,rho=%.2f) A->B->A init=%.3f ms",
                  N_A, LEAK_RATE_A, SPECTRAL_RADIUS_A,
                  N_B, LEAK_RATE_B, SPECTRAL_RADIUS_B,
                  dt * 1000)

    def step(self, I_inj: np.ndarray, log: bool = True) -> tuple[np.ndarray, np.ndarray]:
        t_start = time.perf_counter()

        I_inj_A = I_inj[:N_A]
        I_inj_B = I_inj[N_A:]

        I_syn_AA = self.graph_AA.matvec_delayed(self.delay_A)
        I_syn_BA = self.graph_BA.matvec_delayed(self.delay_B)
        I_syn_A = I_syn_AA + I_syn_BA

        noise_A = self.rng.normal(0.0, self.noise_std, size=N_A)
        drive_A = I_syn_A + self.sensory_gain * I_inj_A + noise_A
        self.v_A = (1.0 - LEAK_RATE_A) * self.v_A + LEAK_RATE_A * np.tanh(drive_A)
        self.a_A = self.v_A.copy()

        I_syn_BB = self.graph_BB.matvec_delayed(self.delay_B)
        I_syn_AB = self.graph_AB.matvec_delayed(self.delay_A)
        I_syn_B = I_syn_BB + I_syn_AB

        noise_B = self.rng.normal(0.0, self.noise_std, size=N_B)
        drive_B = I_syn_B + self.sensory_gain * I_inj_B + noise_B
        self.v_B = (1.0 - LEAK_RATE_B) * self.v_B + LEAK_RATE_B * np.tanh(drive_B)
        self.a_B = self.v_B.copy()

        for k in range(self.delay_depth - 1, 0, -1):
            self.delay_A[k] = self.delay_A[k - 1]
            self.delay_B[k] = self.delay_B[k - 1]
        self.delay_A[0] = self.a_A.copy()
        self.delay_B[0] = self.a_B.copy()

        t_elapsed = time.perf_counter() - t_start

        if log:
            _LOG.info(
                "[STEP] t=%4d | "
                "V_A mu=%.4f sigma=%.4f [%.4f, %.4f] | "
                "V_B mu=%.4f sigma=%.4f [%.4f, %.4f] | "
                "I_syn mu=%.4f | I_inj NZ=%d | dt=%.4f ms",
                self.step_count,
                float(np.mean(self.v_A)), float(np.std(self.v_A)),
                float(np.min(self.v_A)), float(np.max(self.v_A)),
                float(np.mean(self.v_B)), float(np.std(self.v_B)),
                float(np.min(self.v_B)), float(np.max(self.v_B)),
                float(np.mean(I_syn_A)) + float(np.mean(I_syn_B)),
                int(np.count_nonzero(I_inj)),
                t_elapsed * 1000,
            )

        self.step_count += 1
        return self.a_A, self.a_B

    def get_state(self) -> np.ndarray:
        return np.concatenate([self.a_A, self.a_B])

    def reset(self) -> None:
        self.v_A.fill(0.0)
        self.a_A.fill(0.0)
        self.v_B.fill(0.0)
        self.a_B.fill(0.0)
        for k in range(self.delay_depth):
            self.delay_A[k].fill(0.0)
            self.delay_B[k].fill(0.0)
        self.step_count = 0
        _LOG.info("[RESET] Reservoir state reset")
