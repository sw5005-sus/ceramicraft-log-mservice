import grpc

from ceramicraft_log_mservice.pb import audit_log_pb2, audit_log_pb2_grpc


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = audit_log_pb2_grpc.AuditLogServiceStub(channel)

        # Test record 1
        response = stub.RecordAuditLog(
            audit_log_pb2.RecordAuditLogRequest(
                actor_id=101,
                role=audit_log_pb2.MERCHANT,
                description="Merchant 101 updated product stock",
            )
        )
        print(f"Record 1 success: {response.success}, event_id: {response.event_id}")

        # Test record 2
        response2 = stub.RecordAuditLog(
            audit_log_pb2.RecordAuditLogRequest(
                actor_id=202,
                role=audit_log_pb2.CUSTOMER,
                description="Customer 202 completed payment",
            )
        )
        print(f"Record 2 success: {response2.success}, event_id: {response2.event_id}")

        # Test query
        print("-" * 40)
        print("Testing QueryAuditLogs:")
        query_response = stub.QueryAuditLogs(
            audit_log_pb2.QueryAuditLogsRequest(limit=10, offset=0)
        )
        print(f"Total count: {query_response.total_count}")
        for log in query_response.logs:
            print(
                f"[{log.created_at}] ID: {log.id}, Actor: {log.actor_id}, Role: {audit_log_pb2.Role.Name(log.role)}, Desc: {log.description}"
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
                f"[{log.created_at}] ID: {log.id}, Actor: {log.actor_id}, Desc: {log.description}"
            )


if __name__ == "__main__":
    run()
