import numpy as np

from dak.config.settings import LEARNING_RATE, MOMENTUM, GRADIENT_CLIP_NORM


class GradientDescent:
    def __init__(self, learning_rate=LEARNING_RATE, momentum=MOMENTUM,
                 clip_norm=GRADIENT_CLIP_NORM):
        self.lr = learning_rate
        self.momentum = momentum
        self.clip_norm = clip_norm
        self.velocity = None

    def update(self, mu, gradient):
        gnorm = float(np.linalg.norm(gradient))
        if gnorm > self.clip_norm and gnorm > 1e-10:
            gradient = gradient * (self.clip_norm / gnorm)

        if self.momentum > 0:
            if self.velocity is None:
                self.velocity = np.zeros_like(mu)
            self.velocity = self.momentum * self.velocity + self.lr * gradient
            return mu - self.velocity
        else:
            return mu - self.lr * gradient

    def reset(self):
        self.velocity = None
