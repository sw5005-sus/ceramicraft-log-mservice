from collections.abc import Generator
from unittest.mock import MagicMock

import grpc
import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from ceramicraft_log_mservice.models.audit_log import Base
from ceramicraft_log_mservice.service import AuditLogService


def _setup_append_only_triggers(bind_engine: Engine) -> None:
    """Install append-only triggers on audit_logs (mirrors serve.py logic)."""
    with bind_engine.connect() as conn:
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION prevent_audit_log_mutation()
            RETURNS TRIGGER LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'audit_logs is append-only: % operations are not permitted', TG_OP;
            END;
            $$
        """))
        conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_no_update_audit_logs ON audit_logs
        """))
        conn.execute(text("""
            CREATE TRIGGER trg_no_update_audit_logs
            BEFORE UPDATE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation()
        """))
        conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_no_delete_audit_logs ON audit_logs
        """))
        conn.execute(text("""
            CREATE TRIGGER trg_no_delete_audit_logs
            BEFORE DELETE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation()
        """))
        conn.commit()


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    with PostgresContainer("postgres:16-alpine") as pg:
        url = pg.get_connection_url().replace("psycopg2", "psycopg")
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        _setup_append_only_triggers(engine)
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
    # TRUNCATE bypasses row-level triggers, so it is safe to use here for test cleanup.
    with db_engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE audit_logs"))
        conn.commit()


@pytest.fixture
def svc(
    session_factory: sessionmaker[Session],
) -> AuditLogService:
    return AuditLogService(session_factory=session_factory)


@pytest.fixture
def ctx() -> MagicMock:
    return MagicMock(spec=grpc.ServicerContext)
