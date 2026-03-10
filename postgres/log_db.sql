-- Ceramicraft Log Microservice - Database Initialization
-- This script runs automatically on first PostgreSQL container startup
-- (via /docker-entrypoint-initdb.d mount in docker-compose.yml).
-- It creates the audit log database. Table schema is managed by
-- SQLAlchemy (Base.metadata.create_all) in serve.py at application startup.

SELECT 'CREATE DATABASE log_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'log_db'
)\gexec
