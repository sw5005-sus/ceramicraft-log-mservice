import logging
import os
import sys
from concurrent import futures

import dotenv
import dttb
import grpc
import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ceramicraft_log_mservice.models.audit_log import Base
from ceramicraft_log_mservice.pb import audit_log_pb2_grpc
from ceramicraft_log_mservice.service import AuditLogService

# Apply dttb tracebacks for timestamps on exceptions
dttb.apply()

# Load environment variables
dotenv.load_dotenv()

# Build connection string from environment or use sensible defaults
LOG_MSERVICE_DB_USERNAME = os.getenv("LOG_MSERVICE_DB_USERNAME", "user")
LOG_MSERVICE_DB_PASSWORD = os.getenv("LOG_MSERVICE_DB_PASSWORD", "password")
LOG_MSERVICE_DB_HOST = os.getenv("LOG_MSERVICE_DB_HOST", "localhost")
LOG_MSERVICE_DB_PORT = os.getenv("LOG_MSERVICE_DB_PORT", "5432")
LOG_MSERVICE_DB_NAME = os.getenv("LOG_MSERVICE_DB_NAME", "ceramicraft_log")

LOG_MSERVICE_GRPC_HOST = os.getenv("LOG_MSERVICE_GRPC_HOST", "[::]")
LOG_MSERVICE_GRPC_PORT = os.getenv("LOG_MSERVICE_GRPC_PORT", "50051")

DATABASE_URL = f"postgresql+psycopg://{LOG_MSERVICE_DB_USERNAME}:{LOG_MSERVICE_DB_PASSWORD}@{LOG_MSERVICE_DB_HOST}:{LOG_MSERVICE_DB_PORT}/{LOG_MSERVICE_DB_NAME}"

# Engine setup
engine = create_engine(DATABASE_URL)

app = typer.Typer(help="Ceramicraft Audit Log Microservice CLI")


@app.command()
def reset_db() -> None:
    """Reset the database schema (drop all and recreate)."""
    typer.echo("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    typer.echo("Creating tables...")
    Base.metadata.create_all(bind=engine)
    typer.secho("Database reset successfully.", fg=typer.colors.GREEN)


@app.command()
def start(
    LOG_MSERVICE_GRPC_HOST: str = typer.Option(
        LOG_MSERVICE_GRPC_HOST, "--host", help="gRPC server host"
    ),
    LOG_MSERVICE_GRPC_PORT: str = typer.Option(
        LOG_MSERVICE_GRPC_PORT, "--port", help="gRPC server port"
    ),
) -> None:
    """Start the gRPC server."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Initialize DB schema
    Base.metadata.create_all(bind=engine)

    # Start gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Inject SessionLocal directly into our LogService handler
    audit_log_pb2_grpc.add_AuditLogServiceServicer_to_server(
        AuditLogService(session_factory=SessionLocal), server
    )
    grpc_address = f"{LOG_MSERVICE_GRPC_HOST}:{LOG_MSERVICE_GRPC_PORT}"
    server.add_insecure_port(grpc_address)

    typer.secho(f"Starting gRPC Server on {grpc_address}...", fg=typer.colors.CYAN)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    app()
