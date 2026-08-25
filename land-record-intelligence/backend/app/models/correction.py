from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

from app.db.base import Base

class FieldCorrection(Base):
    __tablename__ = "field_corrections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    land_record_id = Column(UUID(as_uuid=True), ForeignKey("land_records.id", ondelete="CASCADE"), nullable=False)
    extracted_field_id = Column(UUID(as_uuid=True), ForeignKey("extracted_fields.id", ondelete="SET NULL"), nullable=True)
    
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    
    corrected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    land_record = relationship("LandRecord", back_populates="corrections")
