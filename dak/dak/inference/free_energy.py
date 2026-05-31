import numpy as np

from dak.config.settings import SIGMA2_LIK, SIGMA2_PRIOR


class FreeEnergy:
    def __init__(self, model, sigma2_lik=SIGMA2_LIK, sigma2_prior=SIGMA2_PRIOR):
        self.model = model
        self.sigma2_lik = sigma2_lik
        self.sigma2_prior = sigma2_prior

    def compute(self, mu, sensors):
        s_pred = self.model.predict(mu)
        s = self.model.sensors_to_array(sensors)

        n = min(len(s), len(s_pred))
        prediction_error = s[:n] - s_pred[:n]

        F_pred = 0.5 * float(np.sum(prediction_error ** 2)) / self.sigma2_lik
        F_reg = 0.5 * float(np.sum(mu ** 2)) / self.sigma2_prior
        F = F_pred + F_reg

        gradient = self.model.compute_gradient(mu, prediction_error, self.sigma2_lik)
        gradient += mu / self.sigma2_prior

        delta = float(np.mean(prediction_error ** 2))

        return F, gradient, delta
