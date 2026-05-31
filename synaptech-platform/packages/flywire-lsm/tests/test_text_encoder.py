import numpy as np

from flywire_lsm.config import CHAR_TO_IDX, N_NEURONS, VOCAB_SIZE
from flywire_lsm.text_encoder import TextEncoder


class TestTextEncoder:
    def test_initialization(self):
        enc = TextEncoder(N_NEURONS)
        assert enc.n_neurons == N_NEURONS
        assert len(enc.sensory_nodes) == VOCAB_SIZE

    def test_encode_valid_char(self):
        enc = TextEncoder(N_NEURONS)
        result = enc.encode('a')
        assert result.shape == (N_NEURONS,)
        assert result[0] == 1.0
        assert np.sum(result) == 1.0

    def test_encode_uppercase(self):
        enc = TextEncoder(N_NEURONS)
        result = enc.encode('A')
        idx = CHAR_TO_IDX['A']
        assert result[idx] == 1.0

    def test_encode_digit(self):
        enc = TextEncoder(N_NEURONS)
        result = enc.encode('3')
        idx = CHAR_TO_IDX['3']
        assert result[idx] == 1.0

    def test_encode_invalid_char(self):
        enc = TextEncoder(N_NEURONS)
        result = enc.encode('\t')
        assert np.all(result == 0)

    def test_encode_with_strength(self):
        enc = TextEncoder(N_NEURONS)
        result = enc.encode('b', strength=0.5)
        assert result[1] == 0.5

    def test_custom_sensory_nodes(self):
        enc = TextEncoder(N_NEURONS, sensory_nodes=[100, 101, 102])
        result = enc.encode('a')
        assert result[100] == 1.0
        assert np.sum(result) == 1.0
