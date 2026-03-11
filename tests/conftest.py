from collections.abc import Generator
from unittest.mock import MagicMock

import grpc
import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from ceramicraft_log_mservice.models.audit_log import Base
from ceramicraft_log_mservice.service import AuditLogService


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    with PostgresContainer("postgres:16-alpine") as pg:
        url = pg.get_connection_url().replace("psycopg2", "psycopg")
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        yield engine
        engine.dispose()


@pytest.fixture(scope="session")
def session_factory(
    db_engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture(autouse=True)
def clear_db(
    db_engine: Engine,
) -> Generator[None, None, None]:
    yield
    with db_engine.connect() as conn:
        conn.execute(text("DELETE FROM audit_logs"))
        conn.commit()


@pytest.fixture
def svc(
    session_factory: sessionmaker[Session],
) -> AuditLogService:
    return AuditLogService(session_factory=session_factory)


@pytest.fixture
def ctx() -> MagicMock:
    return MagicMock(spec=grpc.ServicerContext)
