import os
from datetime import datetime, timedelta, timezone

import dotenv
import grpc

from ceramicraft_log_mservice.pb import audit_log_pb2, audit_log_pb2_grpc

dotenv.load_dotenv()

LOG_MSERVICE_GRPC_PORT = os.getenv("LOG_MSERVICE_GRPC_PORT", "50051")
_env_host = os.getenv("LOG_MSERVICE_GRPC_HOST", "localhost")
LOG_MSERVICE_GRPC_HOST = "localhost" if "[::]" == _env_host else _env_host


def main() -> None:
    grpc_target = f"{LOG_MSERVICE_GRPC_HOST}:{LOG_MSERVICE_GRPC_PORT}"
    print(f"Connecting to {grpc_target}...")

    with grpc.insecure_channel(grpc_target) as channel:
        stub = audit_log_pb2_grpc.AuditLogServiceStub(channel)

        # Timestamps for test records
        now = datetime.now(timezone.utc)
        t_old = (now - timedelta(days=3)).isoformat()  # 3 days ago
        t_mid = (now - timedelta(days=1)).isoformat()  # 1 day ago
        t_recent = now.isoformat()  # now

        # Test record 1 — occurred 3 days ago
        response = stub.RecordAuditLog(
            audit_log_pb2.RecordAuditLogRequest(
                service="product-service",
                actor_id=101,
                role="MERCHANT",
                description="Merchant 101 updated product stock",
                occurred_at=t_old,
            )
        )
        print(f"Record 1 success: {response.success}, event_id: {response.event_id}")

        # Test record 2 — occurred 1 day ago
        response2 = stub.RecordAuditLog(
            audit_log_pb2.RecordAuditLogRequest(
                service="order-service",
                actor_id=202,
                role="CUSTOMER",
                description="Customer 202 completed payment",
                occurred_at=t_mid,
            )
        )
        print(f"Record 2 success: {response2.success}, event_id: {response2.event_id}")

        # Test record 3 — occurred just now
        response3 = stub.RecordAuditLog(
            audit_log_pb2.RecordAuditLogRequest(
                service="product-service",
                actor_id=303,
                role="SYSTEM",
                description="System recalculated inventory",
                occurred_at=t_recent,
            )
        )
        print(f"Record 3 success: {response3.success}, event_id: {response3.event_id}")

        # Test query
        print("-" * 40)
        print("Testing QueryAuditLogs:")
        query_response = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=10, offset=0)
        )
        print(f"Total count: {query_response.total_count}")
        for log in query_response.logs:
            print(
                f"[{log.occurred_at}](rcv {log.created_at}) ID: {log.id}, Service: {log.service}, Actor: {log.actor_id}, Role: {log.role}, Desc: {log.description}"
            )
            print(
                f"    PrevHash: {log.previous_hash[:16]}... CurrHash: {log.current_hash[:16]}..."
            )

        # Test query by actor_id
        print("-" * 40)
        print("Testing QueryAuditLogs with actor_id=101:")
        query_response_actor = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(actor_id=101, limit=10)
        )
        print(f"Total count for actor 101: {query_response_actor.total_count}")
        for log in query_response_actor.logs:
            print(
                f"[{log.occurred_at}](rcv {log.created_at}) ID: {log.id}, Service: {log.service}, Actor: {log.actor_id}, Desc: {log.description}"
            )

        # Test query by service
        print("-" * 40)
        print("Testing QueryAuditLogs with service=order-service:")
        query_response_service = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(service="order-service", limit=10)
        )
        print(f"Total count for order-service: {query_response_service.total_count}")
        for log in query_response_service.logs:
            print(
                f"[{log.occurred_at}](rcv {log.created_at}) ID: {log.id}, Service: {log.service}, Actor: {log.actor_id}, Desc: {log.description}"
            )

        # Test query by occurred_at range — only records that occurred within the last 2 days
        print("-" * 40)
        print("Testing QueryAuditLogs with occurred_at_start (last 2 days):")
        two_days_ago = (now - timedelta(days=2)).isoformat()
        query_response_occ = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(
                occurred_at_start=two_days_ago,
                limit=10,
            )
        )
        print(
            f"Total count (occurred in last 2 days): {query_response_occ.total_count}"
        )
        for log in query_response_occ.logs:
            print(
                f"[occurred {log.occurred_at}] ID: {log.id}, Service: {log.service}, Actor: {log.actor_id}"
            )

        # Test query by occurred_at range — only records that occurred more than 2 days ago
        print("-" * 40)
        print("Testing QueryAuditLogs with occurred_at_end (older than 2 days):")
        query_response_occ_old = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(
                occurred_at_end=two_days_ago,
                limit=10,
            )
        )
        print(
            f"Total count (occurred > 2 days ago): {query_response_occ_old.total_count}"
        )
        for log in query_response_occ_old.logs:
            print(
                f"[occurred {log.occurred_at}] ID: {log.id}, Service: {log.service}, Actor: {log.actor_id}"
            )

        # Test validation
        print("-" * 40)
        print("Testing VerifyAuditLogChain:")
        verify_response = stub.VerifyAuditLogChain(
            audit_log_pb2.VerifyAuditLogChainRequest()
        )
        print(f"Is valid? {verify_response.is_valid}")
        print(f"Message: {verify_response.message}")
        if not verify_response.is_valid:
            print(f"Failed Log ID: {verify_response.failed_log_id}")


if __name__ == "__main__":
    main()
