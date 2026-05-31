import numpy as np
from dak.inference.model import GenerativeModel
from dak.inference.free_energy import FreeEnergy


def test_free_energy_computation():
    model = GenerativeModel(mu_dim=4, n_sensors=3)
    fe = FreeEnergy(model, sigma2_lik=0.5, sigma2_prior=2.0)

    mu = np.array([0.1, -0.2, 0.3, -0.1], dtype=np.float64)
    sensors = {'cpu_percent': 50.0, 'mem_percent': 60.0, 'load_1min': 1.0}

    F, grad, delta = fe.compute(mu, sensors)

    assert F > 0, f'Free energy should be positive, got {F}'
    assert grad.shape == mu.shape, f'Gradient shape {grad.shape} != {mu.shape}'
    assert delta >= 0, f'Delta should be non-negative, got {delta}'


def test_free_energy_zero_prediction_error():
    model = GenerativeModel(mu_dim=2, n_sensors=2)
    fe = FreeEnergy(model, sigma2_lik=1.0, sigma2_prior=1.0)

    mu = np.array([0.1, -0.1], dtype=np.float64)
    s_pred = model.predict(mu)
    sensors = {
        'cpu_percent': float(s_pred[0] * 100.0),
        'cpu_freq': float(s_pred[1] * 5000.0),
    }

    F, grad, delta = fe.compute(mu, sensors)

    assert F > 0, f'F should be positive from regularization, got {F}'
    assert delta < 1e-3, f'Prediction error should be near zero, got {delta}'


def test_gradient_descent_reduces_F():
    model = GenerativeModel(mu_dim=4, n_sensors=3)
    fe = FreeEnergy(model)
    from dak.inference.gradient_descent import GradientDescent
    gd = GradientDescent(learning_rate=0.5)

    mu = np.array([0.5, -0.5, 0.5, -0.5], dtype=np.float64)
    sensors = {'cpu_percent': 50.0, 'mem_percent': 60.0, 'load_1min': 1.0}

    F0, grad, _ = fe.compute(mu, sensors)
    for _ in range(20):
        F, grad, _ = fe.compute(mu, sensors)
        mu = gd.update(mu, grad)

    F_final, _, _ = fe.compute(mu, sensors)
    assert F_final < F0, f'F should decrease: {F0} -> {F_final}'


if __name__ == '__main__':
    test_free_energy_computation()
    test_free_energy_zero_prediction_error()
    test_gradient_descent_reduces_F()
    print('All free energy tests passed.')
