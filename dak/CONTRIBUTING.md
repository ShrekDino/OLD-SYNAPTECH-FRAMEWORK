# Contributing to DAK

Contributions are welcome! This project explores the intersection of
theoretical biology, thermodynamics of computation, and active inference.

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies in a virtual environment
4. Make your changes
5. Run the test suite (`python -m pytest tests/ -v`)
6. Submit a pull request

## Development Guidelines

- Code style follows PEP 8 with a 90-character line limit
- All new features must include tests
- Mathematical formalism should be documented in docstrings with LaTeX
- Public API functions should have type annotations
- Run the integration test before submitting to verify the DQFR loop

## Adding Sensors

To add a new telemetry sensor:

1. Add the reading to `substrate/telemetry.py`'s `read_all()` method
2. Add the key and normalization range to `inference/model.py`'s `SENSOR_KEYS` and `SENSOR_RANGES`
3. Increment `N_SENSORS` in `config/settings.py` if needed

## Adding Interaction Modes

New interaction modes go in `interact/` and should:

- Import `DAK` from `dak`
- Use `run_async()` for non-blocking operation
- Stop the kernel gracefully via `dak.stop()`
- Be registered in `main.py`'s argument parser
