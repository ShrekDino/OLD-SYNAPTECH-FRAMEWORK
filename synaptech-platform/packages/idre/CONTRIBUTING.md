# Contributing to SynapTech IDRE

Thank you for your interest in the Integrated Data Representation Engine. This project is at the intersection of connectomics, neuromorphic computing, and open science.

## Getting Started

1. **Clone and set up** — see `README.md` for environment setup (Python 3.13, Node 22.x)
2. **Activate the venv**: `source .venv/bin/activate`
3. **Set PYTHONPATH**: `export PYTHONPATH=$PWD` (required for all backend commands)
4. **Start the backend**: `python3 -m uvicorn src.backend.main:app --reload --port 8000`
5. **Start the frontend**: `cd src/frontend && npm run dev`

## Development Workflow

- **Branch from `main`** for every change. Use descriptive names: `fix/sse-heartbeat`, `feat/lsm-engine`, `docs/api-ref`
- **Open a draft PR** early to signal intent and get feedback
- **Run checks before requesting review**:
  ```bash
  # Backend
  cd $PROJECT_ROOT
  ruff check src/
  PYTHONPATH=$PWD python3 -m pytest tests/

  # Frontend
  cd src/frontend
  npx tsc --noEmit
  npm run lint
  ```
- **Keep PRs focused** — one logical change per PR. Large features (e.g., LSM engine, Cloud Loihi) should be broken into stacked PRs.

## Code Standards

### Python
- **Type hints** required on all public functions and methods
- **Line length**: 120 characters
- **Formatting** via `ruff` (matching `pyproject.toml` config)
- **Imports**: stdlib → third-party → project (`src.`), one blank line between groups
- **Singletons**: `CSCEngine`, `SSEStreamer`, etc. use `get_instance()` — never instantiate directly

### TypeScript / React
- **TypeScript strict mode** enabled — avoid `any` unless absolutely necessary
- **Functional components** with hooks (no class components)
- **Three.js** patterns: prefer `useMemo` for geometry/positions, `useFrame` for per-frame updates, refs for imperative handles
- **GLSL shaders** should remain as separate `.glsl` files imported via raw string

## Testing

- **Backend**: `pytest` with `pytest-asyncio`. Tests for services in `tests/backend/`
- **Frontend**: (planned) Vitest + React Testing Library
- **New features** must include tests. Bug fixes should include a regression test.

## Pull Request Process

1. Ensure all CI checks pass (ruff, pytest, tsc, lint)
2. Update `DEVELOPMENT_NOTES.md` if the change affects per-file completeness or roadmap status
3. Request review from at least one maintainer
4. Squash-merge into `main` with a descriptive commit message

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and inclusive.

## Roadmap

See `DEVELOPMENT_NOTES.md` for the phased engineering roadmap (P0–P7). If you'd like to pick up a planned item, open an issue or comment on an existing one to signal intent.
