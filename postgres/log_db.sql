-- Ceramicraft Log Microservice - Database Initialization
-- This script runs automatically on first PostgreSQL container startup
-- (via /docker-entrypoint-initdb.d mount in docker-compose.yml).
-- It creates the audit log database. Table schema is managed by
-- SQLAlchemy (Base.metadata.create_all) in serve.py at application startup.
--
-- Append-only enforcement:
-- The audit_logs table is append-only (INSERT and SELECT only).
-- BEFORE UPDATE / BEFORE DELETE triggers that enforce this constraint are
-- installed idempotently by the application at startup (see serve.py:
-- _setup_append_only_triggers). They cannot be defined here because the
-- table itself is created by SQLAlchemy after this init script runs.

SELECT 'CREATE DATABASE log_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'log_db'
)\gexec
