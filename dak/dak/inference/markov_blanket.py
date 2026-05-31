from dataclasses import dataclass, field
from typing import Any


@dataclass
class MarkovBlanket:
    mu: Any = None
    s: Any = None
    a: Any = None
    eta: Any = None

    def seal(self):
        self.s = None
        self.a = None

    def update(self, mu=None, s=None, a=None, eta=None):
        if mu is not None:
            self.mu = mu
        if s is not None:
            self.s = s
        if a is not None:
            self.a = a
        if eta is not None:
            self.eta = eta

    def is_sealed(self):
        return self.s is None and self.a is None
