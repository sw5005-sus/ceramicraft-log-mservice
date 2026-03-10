import logging
import os
import sys
from concurrent import futures

import dotenv
import dttb
import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ceramicraft_log_mservice.models.audit_log import Base
from ceramicraft_log_mservice.pb import audit_log_pb2_grpc
from ceramicraft_log_mservice.service import AuditLogService

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

# Engine & Session local setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def serve() -> None:
    # Initialize DB schema
    init_db()

    # Start gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Inject SessionLocal directly into our LogService handler
    audit_log_pb2_grpc.add_AuditLogServiceServicer_to_server(
        AuditLogService(session_factory=SessionLocal), server
    )
    grpc_address = f"{GRPC_HOST}:{GRPC_PORT}"
    server.add_insecure_port(grpc_address)

    print(f"Starting gRPC Server on {grpc_address}...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    serve()
