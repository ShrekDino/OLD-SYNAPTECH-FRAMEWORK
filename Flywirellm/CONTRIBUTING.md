# Contributing

Thanks for your interest in FlyWire Connectome!

## Development Setup

```bash
git clone https://github.com/anomalyco/Flywirellm.git
cd Flywirellm

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e .[dev]
```

## Code Style

This project uses [ruff](https://docs.astrodocs.ai/ruff/) for linting and formatting:

```bash
# Check for issues
make lint

# Auto-fix what you can
ruff check --fix .
```

## Running Tests

```bash
# Full test suite with coverage
make test

# Run a specific test file
python -m pytest tests/test_core.py -v
```

## Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run `make test && make lint` — all checks must pass
5. Commit with a clear message
6. Push and open a PR

## Project Structure

```
flywire_lsm/     — Core Python package
scripts/         — CLI tools
frontend/        — Web frontend (single HTML file)
tests/           — Pytest suite
docs/            — Documentation
data/            — Persisted state
```

## Adding Features

- **New hyperparameters**: add to `flywire_lsm/config.py` — this is the single source of truth
- **New endpoint**: add to `flywire_lsm/server.py`
- **New visualizer feature**: edit `frontend/index.html`
- **Tests**: add to `tests/` — every new function should have a corresponding test

## Questions?

Open an issue at https://github.com/anomalyco/Flywirellm/issues
