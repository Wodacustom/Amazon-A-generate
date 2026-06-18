# Amazon A+ Agent MVP

This repository now uses a clean backend MVP built around FastAPI, LangGraph,
PostgreSQL with pgvector, Redis, and RustFS-compatible S3 storage.

## Backend

Key API routes:

- `GET /api/health`
- `POST /api/files`
- `POST /api/products`
- `POST /api/agent/runs`
- `GET /api/agent/runs/{run_id}`
- `GET /api/search?query=...`

Local checks:

```powershell
uv pip install -r backend\requirements.txt
pytest -p no:cacheprovider backend\tests
docker compose -f docker\docker-compose.yml config
```

Docker startup:

```powershell
docker compose -f docker\docker-compose.yml up --build
```

The backend container runs Alembic on startup. The initial migration enables
the `vector` extension and creates the MVP tables.
