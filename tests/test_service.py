import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from sqlalchemy import Engine, text

from ceramicraft_log_mservice.pb import audit_log_pb2
from ceramicraft_log_mservice.service import AuditLogService

NOW = datetime.now(timezone.utc)
T_THREE_DAYS_AGO = (NOW - timedelta(days=3)).isoformat()
T_ONE_DAY_AGO = (NOW - timedelta(days=1)).isoformat()
T_TWO_DAYS_AGO = (NOW - timedelta(days=2)).isoformat()


def _record(
    svc: AuditLogService,
    ctx: MagicMock,
    *,
    service: str = "test-service",
    actor_id: int = 1,
    role: str = "SYSTEM",
    description: str = "test action",
    occurred_at: str | None = None,
) -> audit_log_pb2.RecordAuditLogResponse:
    return svc.RecordAuditLog(
        audit_log_pb2.RecordAuditLogRequest(
            service=service,
            actor_id=actor_id,
            role=role,
            description=description,
            occurred_at=occurred_at or NOW.isoformat(),
        ),
        ctx,
    )


class TestRecordAuditLog:
    def test_success(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        resp = _record(svc, ctx)
        assert resp.success is True
        assert resp.event_id != ""

    def test_event_id_is_valid_uuid(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        resp = _record(svc, ctx)
        uuid.UUID(resp.event_id)  # raises ValueError if invalid

    def test_genesis_entry_has_zero_prev_hash(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx)
        query_resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=1),
            ctx,
        )
        assert query_resp.logs[0].previous_hash == "0" * 64


class TestQueryAuditLogs:
    def test_empty_db(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=10),
            ctx,
        )
        assert resp.total_count == 0
        assert len(resp.logs) == 0

    def test_returns_all_logs(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, actor_id=1)
        _record(svc, ctx, actor_id=2)

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=10),
            ctx,
        )
        assert resp.total_count == 2
        assert len(resp.logs) == 2

    def test_filter_by_actor_id(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, actor_id=101)
        _record(svc, ctx, actor_id=202)

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(actor_id=101, limit=10),
            ctx,
        )
        assert resp.total_count == 1
        assert resp.logs[0].actor_id == 101

    def test_filter_by_service(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, service="order-service")
        _record(svc, ctx, service="product-service")

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(service="order-service", limit=10),
            ctx,
        )
        assert resp.total_count == 1
        assert resp.logs[0].service == "order-service"

    def test_filter_by_role(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, role="MERCHANT")
        _record(svc, ctx, role="CUSTOMER")

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(role="MERCHANT", limit=10),
            ctx,
        )
        assert resp.total_count == 1
        assert resp.logs[0].role == "MERCHANT"

    def test_filter_by_occurred_at_start(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, occurred_at=T_THREE_DAYS_AGO)
        _record(svc, ctx, occurred_at=T_ONE_DAY_AGO)

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(
                occurred_at_start=T_TWO_DAYS_AGO, limit=10
            ),
            ctx,
        )
        assert resp.total_count == 1
        assert resp.logs[0].occurred_at.startswith(T_ONE_DAY_AGO[:10])

    def test_filter_by_occurred_at_end(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        _record(svc, ctx, occurred_at=T_THREE_DAYS_AGO)
        _record(svc, ctx, occurred_at=T_ONE_DAY_AGO)

        resp = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(
                occurred_at_end=T_TWO_DAYS_AGO, limit=10
            ),
            ctx,
        )
        assert resp.total_count == 1
        assert resp.logs[0].occurred_at.startswith(T_THREE_DAYS_AGO[:10])

    def test_pagination(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        for i in range(5):
            _record(svc, ctx, actor_id=i)

        page = svc.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=2, offset=0),
            ctx,
        )
        assert len(page.logs) == 2
        assert page.total_count == 5


class TestVerifyAuditLogChain:
    def test_empty_chain_is_valid(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        resp = svc.VerifyAuditLogChain(
            audit_log_pb2.VerifyAuditLogChainRequest(),
            ctx,
        )
        assert resp.is_valid is True

    def test_valid_chain(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
    ) -> None:
        for i in range(3):
            _record(svc, ctx, actor_id=i)

        resp = svc.VerifyAuditLogChain(
            audit_log_pb2.VerifyAuditLogChainRequest(),
            ctx,
        )
        assert resp.is_valid is True
        assert "3" in resp.message

    def test_tampered_data_is_detected(
        self,
        svc: AuditLogService,
        ctx: MagicMock,
        db_engine: Engine,
    ) -> None:
        _record(svc, ctx)

        with db_engine.connect() as conn:
            conn.execute(text("UPDATE audit_logs SET description = 'TAMPERED'"))
            conn.commit()

        resp = svc.VerifyAuditLogChain(
            audit_log_pb2.VerifyAuditLogChainRequest(),
            ctx,
        )
        assert resp.is_valid is False
        assert resp.failed_log_id != ""
