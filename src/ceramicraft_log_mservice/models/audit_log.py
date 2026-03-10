import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditLogEntry(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(BigInteger, nullable=False, index=True)
    role = Column(
        String(20), nullable=False
    )  # Enum or string, string is safer for cross-service
    description = Column(String(500), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Hash Chain for tamper evidence (Strict Single Chain)
    previous_hash = Column(
        String(64), nullable=False
    )  # SHA-256 hash is 64 hex characters
    current_hash = Column(String(64), nullable=False, unique=True, index=True)

    def calculate_hash(
        self,
    ) -> str:
        """
        Calculates the SHA-256 hash of the log entry content concatenated with the previous hash.
        This provides the tamper-evident property.
        """
        # Ensure consistent ordering for hashing
        content = (
            f"{self.actor_id}|{self.role}|{self.description}|"
            f"{self.created_at.isoformat()}|"
            f"{self.previous_hash}"
        )
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
