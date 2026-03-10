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
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ceramicraft_log")

GRPC_HOST = os.getenv("GRPC_HOST", "[::]")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

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
    grpc_host: str = typer.Option(GRPC_HOST, "--host", help="gRPC server host"),
    grpc_port: str = typer.Option(GRPC_PORT, "--port", help="gRPC server port"),
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
    grpc_address = f"{grpc_host}:{grpc_port}"
    server.add_insecure_port(grpc_address)

    typer.secho(f"Starting gRPC Server on {grpc_address}...", fg=typer.colors.CYAN)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    app()
