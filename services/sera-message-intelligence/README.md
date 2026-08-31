# Sera Message Intelligence

Local-first multi-IM message ingest and intelligence service for Sera OPC OS.

P0 deliberately starts with the Message Core before any WeChat-native integration. Platform-specific collectors are adapters; they must never leak native SDK/database details into the core.

## P0 scope

- Canonical `MessageEventV1`
- FastAPI ingest endpoint
- PostgreSQL message store
- External-ID + deterministic fingerprint deduplication
- Collector protocol abstraction
- Fake collector smoke test
- Versioned SQL bootstrap migration
- Tests for idempotent ingestion

## Run locally

```bash
docker compose up -d postgres
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export SMI_DATABASE_URL='postgresql+psycopg://smi:smi@localhost:5432/smi'
uvicorn sera_message_intelligence.main:app --reload
```

In another terminal:

```bash
python scripts/fake_collector.py
```

Expected first result: `inserted=true`. Re-running the same fake collector payload should return `inserted=false`.

## Design rule

Collectors may fail, change, or be replaced. Stored messages, reports, search, and intelligence pipelines must continue to work without knowing how a platform was collected.

See `docs/` for the P0 contracts and roadmap.
