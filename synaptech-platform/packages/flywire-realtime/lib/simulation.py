import numpy as np
from lib.big_pickle import profiled

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

class NeuropilSimulation:
    def __init__(self, projectome, neuropil_names, alpha=0.6, beta=0.9, gamma=0.3, noise=0.03, diagonal_self=0.2):
        self.n = len(neuropil_names)
        self.names = neuropil_names
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.noise = noise

        W = projectome.copy()
        np.fill_diagonal(W, 0)
        row_sums = W.sum(axis=1)
        row_sums = np.where(row_sums == 0, 1, row_sums)
        self.W = W / row_sums[:, np.newaxis]
        self.W = self.W * alpha
        np.fill_diagonal(self.W, 0.15)

    def step(self, activity, input_vec):
        recurrent = self.W.T @ activity
        baseline = 0.05
        noise = np.random.uniform(0, self.noise, self.n)
        a_next = sigmoid(
            recurrent +
            self.beta * input_vec -
            self.gamma * (activity - baseline) +
            noise
        )
        a_next = np.clip(a_next, 0.0, 1.0)
        return a_next

    @profiled("simulation_run")
    def run(self, input_vec, timesteps=200):
        activity = np.random.uniform(0, 0.03, self.n)
        history = np.zeros((timesteps, self.n))

        for t in range(timesteps):
            ramp = min(1.0, t / 15.0)
            I_eff = input_vec * ramp
            band = 0.02 * np.sin(2 * np.pi * t / 30)
            activity = self.step(activity, I_eff + band)
            activity = np.clip(activity + np.random.uniform(-0.01, 0.01, self.n), 0.0, 1.0)
            history[t] = activity

        return history

    def run_multiple_behaviors(self, input_vectors, timesteps_per_behavior=200):
        results = {}
        for name, input_vec in input_vectors.items():
            history = self.run(input_vec, timesteps=timesteps_per_behavior)
            results[name] = history
        return results

    def compute_global_activity(self, history):
        return history.mean(axis=1)
