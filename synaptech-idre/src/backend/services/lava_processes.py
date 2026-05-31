import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)

LAVA_AVAILABLE = False
try:
    from lava.magma.core.decorator import implements, requires
    from lava.magma.core.model.py.model import PyLoihiProcessModel
    from lava.magma.core.model.py.ports import PyInPort, PyOutPort
    from lava.magma.core.model.py.type import LavaPyType
    from lava.magma.core.resources import CPU
    from lava.magma.core.sync.protocols.loihi_protocol import LoihiProtocol
    from lava.proc.lif.process import LIF
    LAVA_AVAILABLE = True
except ImportError:
    logger.warning("Lava framework not installed; using stub implementations")


if LAVA_AVAILABLE:

    @implements(proc=LIF, protocol=LoihiProtocol)
    @requires(CPU)
    class FlyWirePyLifModel(PyLoihiProcessModel):
        a_in: PyInPort = LavaPyType(PyInPort.VEC_DENSE, np.int16, precision=16)
        s_out: PyOutPort = LavaPyType(PyOutPort.VEC_DENSE, bool, precision=1)
        u: np.ndarray = LavaPyType(np.ndarray, np.int32, precision=24)
        v: np.ndarray = LavaPyType(np.ndarray, np.int32, precision=24)
        bias: np.ndarray = LavaPyType(np.ndarray, np.int16, precision=12)
        du: int = LavaPyType(int, np.uint16, precision=12)
        dv: int = LavaPyType(int, np.uint16, precision=12)
        vth: int = LavaPyType(int, int, precision=8)

        def run_spk(self):
            self.u[:] = self.u * ((2**12 - self.du) // 2**12)
            a_in_data = self.a_in.recv()
            self.u[:] += a_in_data
            self.v[:] = self.v * ((2**12 - self.dv) // 2**12) + self.u + self.bias
            s_out = self.v > self.vth
            self.v[s_out] = 0
            self.s_out.send(s_out)


@dataclass
class FlyWireNetwork:
    neuron_ids: list[int]
    weights_rows: np.ndarray
    weights_cols: np.ndarray
    weights_data: np.ndarray
    n_neurons: int
    process: object = field(init=False)
    _monitor: object = field(init=False)

    def __post_init__(self):
        if not LAVA_AVAILABLE:
            logger.warning("Lava not available; creating stub FlyWireNetwork")
            self.process = object()
            return

        from lava.proc.dense.process import Dense
        from lava.proc.lif.process import LIF
        from lava.proc.monitor.process import Monitor

        self.process = LIF(
            shape=(self.n_neurons,),
            du=100,
            dv=100,
            vth=200,
            bias=np.zeros(self.n_neurons, dtype=np.int16),
        )

        weight_matrix = np.zeros(
            (self.n_neurons, self.n_neurons), dtype=np.int16
        )
        for r, c, d in zip(self.weights_rows, self.weights_cols, self.weights_data):
            weight_matrix[r, c] = min(int(d * 64), 32767)

        self._dense = Dense(
            weights=weight_matrix,
        )

        self._dense.s_out.connect(self.process.a_in)

        self._monitor = Monitor()
        self._monitor.probe(self.process.s_out, self.n_neurons)

    def get_spikes(self) -> list[int]:
        if not LAVA_AVAILABLE:
            return []
        data = self._monitor.get_data()
        spikes = []
        for t in range(self.n_neurons):
            if t in data and data[t].any():
                spikes.append(int(t))
        return spikes
