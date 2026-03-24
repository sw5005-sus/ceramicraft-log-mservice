# CeramiCraft Log Microservice

Audit log microservice for the CeramiCraft e-commerce system. It provides a gRPC API for recording, querying, and verifying tamper-evident audit logs across all services.

## Features

- **gRPC API**: Record audit log entries, query logs with rich filtering, and verify the integrity of the log chain.
- **Tamper-evident**: Each log entry is chained via SHA-256 hash, making any modification detectable.
- **Append-only**: Database-level triggers prevent UPDATE and DELETE operations on the audit log table.
- **Health endpoint**: Minimal HTTP server (`GET /log-ms/v1/ping`) for Kubernetes liveness/readiness probes.
- **Asynchronous-ready**: Built with Python 3.12 and synchronous SQLAlchemy backed by PostgreSQL.
- **Containerized**: Dockerfile and docker-compose setup for easy deployment.

## Tech Stack

- Python 3.12, `uv`
- `grpc` (synchronous)
- PostgreSQL, SQLAlchemy (sync), `psycopg`
- `typer` for CLI commands
- `pytest`, `testcontainers` for testing
