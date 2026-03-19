# TouchMap test suite

All tests for the project live under this directory.

## Backend (Python / pytest)

- **Unit tests** – `backend/unit/`
  - `domain/` – domain models (panel map, task models)
  - `services/` – application services (explore, graphs, intent, locate, panelmap, task planning)
- **Integration tests** – `backend/integration/` – API and scan pipeline

### How to run

**From repo root (recommended):**

```bash
pytest
```

Requires root `pytest.ini` (or `pyproject.toml`) with `testpaths = tests/backend` and `pythonpath = backend`.

**From backend directory:**

```bash
cd backend
pytest ../tests/backend
```

Or with `backend/pytest.ini` pointing at `../tests/backend`:

```bash
cd backend
pytest
```

Shared fixtures and `app` import path are configured in `tests/backend/conftest.py`.

## Frontend

The frontend currently has no tests. If you add them later (e.g. Jest or Vitest), they can live under `tests/frontend/` and be run from the `frontend/` directory with the frontend test runner.
