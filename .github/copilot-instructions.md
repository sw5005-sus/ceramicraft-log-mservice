# Ceramicraft Log Microservice Guidelines

This is the Audit Log microservice for the Ceramicraft e-commerce platform. It provides a reliable and tamper-evident logging mechanism for merchant and customer actions.

## Context & Architecture
- gRPC: The service exposes procedures via gRPC to other microservices. Interface definitions are located in the `protos/` directory.
- Database: PostgreSQL is used as the primary datastore, interacted with via SQLAlchemy Core/ORM. 
- Tamper Evidence: This service uses a Strict Single Hash Chain mechanism. Each log entry calculates its `current_hash` using a SHA-256 hash of its content along with the `previous_hash`, ensuring that historic logs cannot be altered without breaking the chain.

## Build and Environment
- Dependency & Environment Management: This project strictly uses `uv`. Never use raw `pip` or `python` commands to manage dependencies. Always use `uv add <package>`, `uv remove <package>`, and `uv run <command>`.
- Environment Variables: Configure the environment via a local `.env` file (use `.env.example` as the template).
- Local Infrastructure: A local PostgreSQL instance can be spun up using `docker compose up -d`.

## Code Style & Conventions
- Use Python >= 3.12 features and strict type hinting.
- Database models belong in `src/ceramicraft_log_mservice/models/`.
- gRPC services and core logic will reference the generic `AuditLogEntry` model.

## Note to AI Agents
- The primary focus is currently write-only audit logging. Do not implement read/query functionality unless explicitly requested by the user.
- Consult the `skills/` directory if you need specific guidance on configuring or running `uv` and other project tooling.
