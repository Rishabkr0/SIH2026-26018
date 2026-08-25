from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy.orm import relationship

from app.db.base import Base

class FindingStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class FindingSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    land_record_id = Column(UUID(as_uuid=True), ForeignKey("land_records.id", ondelete="CASCADE"), nullable=False)
    
    field_name = Column(String, nullable=True)
    finding_type = Column(String, nullable=False)
    severity = Column(Enum(FindingSeverity), nullable=False, default=FindingSeverity.MEDIUM)
    message = Column(String, nullable=False)
    
    expected_value = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)
    
    status = Column(Enum(FindingStatus), nullable=False, default=FindingStatus.OPEN)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    land_record = relationship("LandRecord", back_populates="validation_findings")
