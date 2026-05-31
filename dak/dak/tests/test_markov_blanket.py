import numpy as np
from dak.inference.markov_blanket import MarkovBlanket


def test_blanket_seal():
    mb = MarkovBlanket(mu=np.array([0.1, 0.2]), s={'cpu': 50}, a='write')
    assert not mb.is_sealed()
    mb.seal()
    assert mb.is_sealed()


def test_blanket_update():
    mb = MarkovBlanket()
    mb.update(mu=np.array([1.0, 2.0]), s={'temp': 70})
    assert mb.mu is not None
    assert mb.s == {'temp': 70}


if __name__ == '__main__':
    test_blanket_seal()
    test_blanket_update()
    print('All Markov blanket tests passed.')
