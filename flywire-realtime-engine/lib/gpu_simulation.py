import torch
import numpy as np
from scipy import sparse as sp


class GPUClimateSimulation:
    """Stateful GPU-accelerated connectome simulation.

    Zero-copy philosophy:
      - Weight matrix W^T lives permanently in VRAM as a sparse COO tensor.
      - Activity vector is allocated on GPU in reset() and never leaves VRAM
        between ticks.
      - Sensory input (N=78 floats) is the only host→device transfer per tick
        (~312 bytes via non_blocking stream).
      - Motor values are decoded on GPU; only ~12 scalar outputs cross
        device→host per tick.
    """

    def __init__(
        self, projectome, neuropil_names,
        alpha=0.6, beta=0.9, gamma=0.3, noise=0.03,
        diagonal_self=0.15, device='cuda',
    ):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.n = len(neuropil_names)
        self.names = neuropil_names
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.noise = noise

        # --- Build weight matrix (matches NeuropilSimulation logic exactly) ---
        W = projectome.copy().astype(np.float64)
        np.fill_diagonal(W, 0.0)
        row_sums = W.sum(axis=1)
        row_sums = np.where(row_sums == 0, 1.0, row_sums)
        W = W / row_sums[:, np.newaxis]
        W = W * alpha
        np.fill_diagonal(W, diagonal_self)

        # Transpose so tick uses: sparse_mm(W_T, activity)
        # ZERO-COPY: this tensor lives in VRAM for the entire run.
        W_T = np.ascontiguousarray(W.T)
        coo = sp.coo_matrix(W_T)
        idx = torch.from_numpy(np.vstack([coo.row, coo.col])).long()
        vals = torch.from_numpy(coo.data.astype(np.float32))
        shape = torch.Size([self.n, self.n])
        self.W_T = torch.sparse_coo_tensor(
            idx, vals, shape, device=self.device,
        ).coalesce()

        # Pre-allocate activity (filled on first reset)
        # ZERO-COPY: this tensor remains GPU-resident between ticks.
        self.activity = None

        # Pre-allocate GPU noise buffer (re-used each tick to reduce alloc churn)
        self._noise_buf = torch.empty(self.n, device=self.device)

    def reset(self, seed=None):
        """(Re)initialise activity on GPU.  No host-device copy occurs."""
        if seed is not None:
            torch.manual_seed(seed)
        self.activity = torch.rand(self.n, device=self.device, dtype=torch.float32) * 0.03

    def step(self, input_vec):
        """Single GPU tick — all operations resident on device.

        Parameters
        ----------
        input_vec : np.ndarray | torch.Tensor
            Sensory input vector, shape (N,).
            If numpy, a single non-blocking host→device copy occurs (~312 B).

        Returns
        -------
        torch.Tensor
            Next activity vector, shape (N,), GPU-resident.
        """
        if self.activity is None:
            self.reset()

        # ZERO-COPY: sensory injection is a tiny (78,) host→device push
        if isinstance(input_vec, torch.Tensor):
            I = input_vec.to(self.device, non_blocking=True)
        else:
            I = torch.from_numpy(input_vec).float().to(self.device, non_blocking=True)

        # --- GPU compute path (all VRAM, no host round-trip) ---
        recurrent = torch.sparse.mm(self.W_T, self.activity.unsqueeze(-1)).squeeze(-1)
        baseline = 0.05

        self._noise_buf.uniform_(0.0, self.noise)

        a_next = torch.sigmoid(
            recurrent
            + self.beta * I
            - self.gamma * (self.activity - baseline)
            + self._noise_buf
        )
        a_next = torch.clamp(a_next, 0.0, 1.0)
        self.activity = a_next
        return self.activity

    @property
    def nan_detected(self):
        """Check for NaN propagation in the current activity vector (O(N))."""
        return bool(torch.any(torch.isnan(self.activity)).item())
