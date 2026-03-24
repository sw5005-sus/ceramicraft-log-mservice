import logging
import sys
from concurrent import futures

import dttb
import grpc
import typer
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from ceramicraft_log_mservice.config import get_settings
from ceramicraft_log_mservice.health import start_health_server
from ceramicraft_log_mservice.models.audit_log import Base
from ceramicraft_log_mservice.pb import audit_log_pb2_grpc
from ceramicraft_log_mservice.service import AuditLogService

# Apply dttb tracebacks for timestamps on exceptions
dttb.apply()

app = typer.Typer(help="Ceramicraft Audit Log Microservice CLI")


def _setup_append_only_triggers(bind_engine: Engine) -> None:
    """
    Install database-level triggers that prevent UPDATE and DELETE on audit_logs.
    The table is append-only: only INSERT and SELECT are permitted.
    This function is idempotent and safe to call on every startup.
    """
    with bind_engine.connect() as conn:
        conn.execute(
            text("""
            CREATE OR REPLACE FUNCTION prevent_audit_log_mutation()
            RETURNS TRIGGER LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'audit_logs is append-only: % operations are not permitted', TG_OP;
            END;
            $$
        """)
        )
        conn.execute(
            text("""
            DROP TRIGGER IF EXISTS trg_no_update_audit_logs ON audit_logs
        """)
        )
        conn.execute(
            text("""
            CREATE TRIGGER trg_no_update_audit_logs
            BEFORE UPDATE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation()
        """)
        )
        conn.execute(
            text("""
            DROP TRIGGER IF EXISTS trg_no_delete_audit_logs ON audit_logs
        """)
        )
        conn.execute(
            text("""
            CREATE TRIGGER trg_no_delete_audit_logs
            BEFORE DELETE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation()
        """)
        )
        conn.commit()


@app.command()
def reset_db() -> None:
    """Reset the database schema (drop all and recreate)."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    typer.echo("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    typer.echo("Creating tables...")
    Base.metadata.create_all(bind=engine)
    _setup_append_only_triggers(engine)
    typer.secho("Database reset successfully.", fg=typer.colors.GREEN)


@app.command()
def start() -> None:
    """Start the gRPC server."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    settings = get_settings()

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Initialize DB schema
    Base.metadata.create_all(bind=engine)

    # Enforce append-only constraint via database triggers
    _setup_append_only_triggers(engine)

    # Start gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audit_log_pb2_grpc.add_AuditLogServiceServicer_to_server(
        AuditLogService(session_factory=SessionLocal), server
    )
    grpc_address = (
        f"{settings.LOG_MSERVICE_GRPC_HOST}:{settings.LOG_MSERVICE_GRPC_PORT}"
    )
    server.add_insecure_port(grpc_address)

    typer.secho(f"Starting gRPC server on {grpc_address}...", fg=typer.colors.CYAN)
    server.start()

    # Start health-check HTTP server for Kubernetes probes
    start_health_server(port=settings.LOG_MSERVICE_HTTP_PORT)
    typer.secho(
        f"Health HTTP server listening on 0.0.0.0:{settings.LOG_MSERVICE_HTTP_PORT}",
        fg=typer.colors.CYAN,
    )

    server.wait_for_termination()


if __name__ == "__main__":
    app()
