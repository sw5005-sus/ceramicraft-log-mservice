# Ceramicraft Log Microservice Guidelines

Audit Log microservice for the Ceramicraft e-commerce platform (course project). Provides tamper-evident logging for merchant/customer actions via gRPC.

## Architecture

- gRPC service: `AuditLogService` in `src/ceramicraft_log_mservice/service.py`, implements 3 RPCs:
  - `RecordAuditLog` — write a new log entry (primary use case)
  - `QueryAuditLogs` — query with filters (actor_id, service, role, time range, pagination)
  - `VerifyAuditLogChain` — verify hash chain integrity over a time range
- Proto definitions: `protos/audit_log.proto`; generated pb files in `src/ceramicraft_log_mservice/pb/` (do not edit manually, regenerate with buf)
- DB model: `AuditLogEntry` ORM in `src/ceramicraft_log_mservice/models/audit_log.py`, table `audit_logs`
  - Fields: `id` (UUID str), `service`, `actor_id` (bigint), `role`, `description`, `occurred_at`, `created_at`, `previous_hash`, `current_hash`
- Hash chain: SHA-256 of `service|actor_id|role|description|occurred_at|created_at|previous_hash`; genesis `previous_hash = "0"*64`
- Entry point: `serve.py` — Typer CLI with `start` (launch gRPC server, default port `50051`) and `reset_db` commands

## Build & Environment

- Package manager: `uv` exclusively. Use `uv add`, `uv remove`, `uv run`. Never raw `pip`/`python`.
- Env vars (`.env` file): `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `LOG_MSERVICE_GRPC_HOST`, `LOG_MSERVICE_GRPC_PORT`; DB name hardcoded as `log_db`
- Local infra: `docker compose up -d` for PostgreSQL

## Code Conventions

- Python >= 3.12, strict type hints throughout
- Models in `src/ceramicraft_log_mservice/models/`; service logic in `service.py`
- SQLAlchemy ORM (not Core); session injected via `session_factory` into `AuditLogService`

## Skills Available

`uv`, `ruff`, `ty`, `dttb` — read the relevant skill file in `.github/skills/` before using these tools.
