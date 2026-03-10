import uuid
from datetime import datetime, timezone

import grpc
from sqlalchemy.orm import Session

from ceramicraft_log_mservice.models.audit_log import AuditLogEntry
from ceramicraft_log_mservice.pb import audit_log_pb2, audit_log_pb2_grpc


class AuditLogService(audit_log_pb2_grpc.AuditLogServiceServicer):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def RecordAuditLog(
        self,
        request: audit_log_pb2.RecordAuditLogRequest,
        context: grpc.ServicerContext,
    ) -> audit_log_pb2.RecordAuditLogResponse:
        db: Session = self.session_factory()
        try:
            # Simple hash chain logic:
            # 1. Get the last record's hash
            # 2. Assign to previous_hash of the new record
            # 3. Calculate new record's hash

            # Find the most recently created log entry
            last_entry = (
                db.query(AuditLogEntry)
                .order_by(AuditLogEntry.created_at.desc(), AuditLogEntry.previous_hash)
                .first()
            )

            # If no genesis entry, use a "0000..." hash
            prev_hash = last_entry.current_hash if last_entry else "0" * 64

            role_name = audit_log_pb2.Role.Name(request.role)

            new_entry = AuditLogEntry(
                id=str(uuid.uuid4()),
                actor_id=request.actor_id,
                role=role_name,
                description=request.description,
                created_at=datetime.now(timezone.utc),
                previous_hash=prev_hash,
            )

            # calculate the hash before adding to session since current_hash is NOT NULL
            new_entry.current_hash = new_entry.calculate_hash()

            db.add(new_entry)
            db.commit()

            return audit_log_pb2.RecordAuditLogResponse(
                success=True, event_id=str(new_entry.id)
            )

        except Exception as e:
            db.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return audit_log_pb2.RecordAuditLogResponse(success=False)
        finally:
            db.close()
