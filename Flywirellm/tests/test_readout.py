import numpy as np

from flywire_lsm.config import VOCAB_SIZE
from flywire_lsm.readout import LinearReadout


class TestLinearReadout:
    def test_initialization(self):
        ro = LinearReadout(500, VOCAB_SIZE)
        assert ro.W.shape == (VOCAB_SIZE, 500)
        assert ro.b.shape == (VOCAB_SIZE,)
        assert not ro.trained

    def test_predict_before_training(self):
        ro = LinearReadout(500, VOCAB_SIZE)
        logits = ro.predict(np.random.randn(500))
        assert logits.shape == (VOCAB_SIZE,)

    def test_train_ridge_simple(self):
        ro = LinearReadout(10, 3, rng=np.random.default_rng(42))
        X = np.random.randn(100, 10)
        Y = np.zeros((100, 3))
        Y[np.arange(100), np.random.randint(0, 3, 100)] = 1.0
        acc = ro.train_ridge(X, Y)
        assert ro.trained
        assert acc >= 0.0

    def test_perfect_fit(self):
        ro = LinearReadout(5, 2, rng=np.random.default_rng(42))
        rng = np.random.default_rng(99)
        X = rng.standard_normal((50, 5))
        W_true = rng.standard_normal((2, 5))
        b_true = rng.standard_normal(2)
        logits = X @ W_true.T + b_true
        Y = np.zeros((50, 2))
        Y[np.arange(50), np.argmax(logits, axis=1)] = 1.0
        acc = ro.train_ridge(X, Y, alpha=0.0)
        assert acc == 1.0

    def test_decode(self):
        ro = LinearReadout(500, VOCAB_SIZE)
        logits = np.zeros(VOCAB_SIZE)
        logits[10] = 5.0
        char, idx = ro.decode(logits)
        assert idx == 10
        assert isinstance(char, str)

    def test_train_alpha_regularization(self):
        ro = LinearReadout(20, 5, rng=np.random.default_rng(42))
        X = np.random.randn(30, 20)
        Y = np.zeros((30, 5))
        Y[np.arange(30), np.random.randint(0, 5, 30)] = 1.0
        acc_no_reg = ro.train_ridge(X, Y, alpha=0.0)
        acc_reg = ro.train_ridge(X, Y, alpha=1.0)
        assert isinstance(acc_no_reg, float)
        assert isinstance(acc_reg, float)
