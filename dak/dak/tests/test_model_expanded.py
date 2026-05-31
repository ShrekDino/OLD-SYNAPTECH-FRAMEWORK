import numpy as np
from dak.inference.model import GenerativeModel, SENSOR_KEYS


def test_sensor_keys():
    assert len(SENSOR_KEYS) == 15
    assert 'cpu_percent' in SENSOR_KEYS
    assert 'mem_percent' in SENSOR_KEYS
    assert 'uptime' in SENSOR_KEYS


def test_model_handles_sensors():
    model = GenerativeModel(mu_dim=64, n_sensors=15)
    mu = np.random.randn(64).astype(np.float64) * 0.1

    sensors = {
        'cpu_percent': 50.0,
        'mem_percent': 60.0,
        'disk_read_mb': 100.0,
        'uptime': 3600.0,
    }

    arr = model.sensors_to_array(sensors)
    assert arr.shape == (15,)
    assert arr[0] == 0.5  # cpu_percent normalized


def test_prediction():
    model = GenerativeModel(mu_dim=64, n_sensors=15)
    mu = np.random.randn(64).astype(np.float64) * 0.1

    sensors = {
        'cpu_percent': 50.0,
        'mem_percent': 60.0,
        'load_1min': 1.0,
    }

    s_pred = model.predict(mu)
    s = model.sensors_to_array(sensors)
    assert s_pred.shape == (15,)
    assert s.shape == (15,)

    prediction_error = s - s_pred
    F = float(np.sum(prediction_error ** 2))
    assert F >= 0
