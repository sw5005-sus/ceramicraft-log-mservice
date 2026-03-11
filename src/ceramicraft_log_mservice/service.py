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

            new_entry = AuditLogEntry(
                id=str(uuid.uuid4()),
                service=request.service,
                actor_id=request.actor_id,
                role=request.role,
                description=request.description,
                occurred_at=datetime.fromisoformat(
                    request.occurred_at.replace("Z", "+00:00")
                ),
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

    def QueryAuditLogs(
        self,
        request: audit_log_pb2.QueryAuditLogsRequest,
        context: grpc.ServicerContext,
    ) -> audit_log_pb2.QueryAuditLogsResponse:
        db: Session = self.session_factory()
        try:
            query = db.query(AuditLogEntry)

            if request.HasField("actor_id"):
                query = query.filter(AuditLogEntry.actor_id == request.actor_id)
            if request.HasField("service") and request.service:
                query = query.filter(AuditLogEntry.service == request.service)
            if request.HasField("role") and request.role:
                query = query.filter(AuditLogEntry.role == request.role)
            if request.HasField("start_time"):
                try:
                    start_dt = datetime.fromisoformat(
                        request.start_time.replace("Z", "+00:00")
                    )
                    query = query.filter(AuditLogEntry.created_at >= start_dt)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid start_time format, expected ISO 8601")
                    return audit_log_pb2.QueryAuditLogsResponse()
            if request.HasField("end_time"):
                try:
                    end_dt = datetime.fromisoformat(
                        request.end_time.replace("Z", "+00:00")
                    )
                    query = query.filter(AuditLogEntry.created_at <= end_dt)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid end_time format, expected ISO 8601")
                    return audit_log_pb2.QueryAuditLogsResponse()
            if request.HasField("occurred_at_start"):
                try:
                    occurred_at_start_dt = datetime.fromisoformat(
                        request.occurred_at_start.replace("Z", "+00:00")
                    )
                    query = query.filter(
                        AuditLogEntry.occurred_at >= occurred_at_start_dt
                    )
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(
                        "Invalid occurred_at_start format, expected ISO 8601"
                    )
                    return audit_log_pb2.QueryAuditLogsResponse()
            if request.HasField("occurred_at_end"):
                try:
                    occurred_at_end_dt = datetime.fromisoformat(
                        request.occurred_at_end.replace("Z", "+00:00")
                    )
                    query = query.filter(
                        AuditLogEntry.occurred_at <= occurred_at_end_dt
                    )
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(
                        "Invalid occurred_at_end format, expected ISO 8601"
                    )
                    return audit_log_pb2.QueryAuditLogsResponse()

            total_count = query.count()

            query = query.order_by(AuditLogEntry.created_at.desc())

            if request.limit > 0:
                query = query.limit(request.limit)
            if request.offset > 0:
                query = query.offset(request.offset)

            entries = query.all()

            pb_logs = []
            for entry in entries:
                pb_logs.append(
                    audit_log_pb2.AuditLog(
                        id=str(entry.id),
                        service=entry.service,
                        actor_id=entry.actor_id,
                        role=entry.role,
                        description=entry.description,
                        occurred_at=entry.occurred_at.isoformat(),
                        created_at=entry.created_at.isoformat(),
                        previous_hash=entry.previous_hash,
                        current_hash=entry.current_hash,
                    )
                )

            return audit_log_pb2.QueryAuditLogsResponse(
                logs=pb_logs, total_count=total_count
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return audit_log_pb2.QueryAuditLogsResponse()
        finally:
            db.close()

    def VerifyAuditLogChain(
        self,
        request: audit_log_pb2.VerifyAuditLogChainRequest,
        context: grpc.ServicerContext,
    ) -> audit_log_pb2.VerifyAuditLogChainResponse:
        db: Session = self.session_factory()
        try:
            # Order by created_at ascending to reconstruct the chain from start to end
            query = db.query(AuditLogEntry).order_by(
                AuditLogEntry.created_at.asc(), AuditLogEntry.previous_hash.asc()
            )

            if request.HasField("start_time"):
                try:
                    start_dt = datetime.fromisoformat(
                        request.start_time.replace("Z", "+00:00")
                    )
                    query = query.filter(AuditLogEntry.created_at >= start_dt)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid start_time format, expected ISO 8601")
                    return audit_log_pb2.VerifyAuditLogChainResponse(
                        is_valid=False, message="Invalid start_time format"
                    )

            if request.HasField("end_time"):
                try:
                    end_dt = datetime.fromisoformat(
                        request.end_time.replace("Z", "+00:00")
                    )
                    query = query.filter(AuditLogEntry.created_at <= end_dt)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid end_time format, expected ISO 8601")
                    return audit_log_pb2.VerifyAuditLogChainResponse(
                        is_valid=False, message="Invalid end_time format"
                    )

            entries = query.all()

            if not entries:
                return audit_log_pb2.VerifyAuditLogChainResponse(
                    is_valid=True, message="No audit logs to verify."
                )

            # Validate each entry
            # To handle cases where we are verifying a subset of logs (via date filters),
            # we initialize expected_prev with the previous_hash of the first retrieved entry.
            expected_prev = entries[0].previous_hash

            for entry in entries:
                # 1. Chain validation: check matching previous hashes
                if entry.previous_hash != expected_prev:
                    return audit_log_pb2.VerifyAuditLogChainResponse(
                        is_valid=False,
                        failed_log_id=str(entry.id),
                        message=f"Hash chain broken. ID: {entry.id}. Expected prev hash {expected_prev}, found {entry.previous_hash}",
                    )

                # 2. Tampering validation: check if hash of current content is valid
                calculated_hash = entry.calculate_hash()
                if entry.current_hash != calculated_hash:
                    return audit_log_pb2.VerifyAuditLogChainResponse(
                        is_valid=False,
                        failed_log_id=str(entry.id),
                        message=f"Data tampered for ID {entry.id}. Calculated hash {calculated_hash} differs from stored hash {entry.current_hash}",
                    )

                # Setup check for next iteration
                expected_prev = entry.current_hash

            return audit_log_pb2.VerifyAuditLogChainResponse(
                is_valid=True, message=f"Successfully verified {len(entries)} logs."
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return audit_log_pb2.VerifyAuditLogChainResponse(
                is_valid=False, message=f"Internal error: {e}"
            )
        finally:
            db.close()
