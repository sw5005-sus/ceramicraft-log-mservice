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


if __name__ == "__main__":
    run()
