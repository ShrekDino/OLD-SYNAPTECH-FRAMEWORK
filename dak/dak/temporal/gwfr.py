import numpy as np


class GWFR:
    def __init__(self):
        pass

    def wasserstein_distance(self, dist1, dist2):
        arr1 = np.asarray(dist1)
        arr2 = np.asarray(dist2)
        if arr1.ndim == 0 or arr2.ndim == 0:
            return 0.0
        if arr1.ndim > 1:
            d1 = np.linalg.norm(arr1, axis=1)
        else:
            d1 = arr1.flatten()
        if arr2.ndim > 1:
            d2 = np.linalg.norm(arr2, axis=1)
        else:
            d2 = arr2.flatten()
        if len(d1) == 0 or len(d2) == 0:
            return 0.0
        d1.sort()
        d2.sort()
        n = min(len(d1), len(d2))
        return float(np.mean(np.abs(d1[:n] - d2[:n])))

    def reconcile(self, mu_history):
        if len(mu_history) < 2:
            if len(mu_history) == 1:
                return 0.0, mu_history[0]
            return 0.0, None
        w_dist = self.wasserstein_distance(
            np.array(mu_history[-2]), np.array(mu_history[-1])
        )
        barycenter = 0.5 * np.array(mu_history[-2]) + 0.5 * np.array(mu_history[-1])
        return w_dist, barycenter
