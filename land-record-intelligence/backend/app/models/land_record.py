from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy.orm import relationship

from app.db.base import Base

class RecordStatus(str, enum.Enum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    CONFLICT = "CONFLICT"

class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Core domain fields
    record_identifier = Column(String, index=True, nullable=True)
    owner_name = Column(String, index=True, nullable=True)
    khasra_number = Column(String, index=True, nullable=True)
    khata_number = Column(String, index=True, nullable=True)
    village = Column(String, index=True, nullable=True)
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    land_area = Column(String, nullable=True)
    land_classification = Column(String, nullable=True)
    
    status = Column(Enum(RecordStatus), nullable=False, default=RecordStatus.PENDING_VERIFICATION, index=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", back_populates="land_records")
    extracted_fields = relationship("ExtractedField", back_populates="land_record", cascade="all, delete-orphan")
    validation_findings = relationship("ValidationFinding", back_populates="land_record", cascade="all, delete-orphan")
    corrections = relationship("FieldCorrection", back_populates="land_record", cascade="all, delete-orphan")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    land_record_id = Column(UUID(as_uuid=True), ForeignKey("land_records.id", ondelete="CASCADE"), nullable=False)
    
    field_name = Column(String, nullable=False)
    extracted_value = Column(String, nullable=True)
    normalized_value = Column(String, nullable=True)
    
    confidence = Column(Float, nullable=False, default=0.0)
    source_reference = Column(String, nullable=True)
    bounding_box = Column(JSONB, nullable=True)
    extraction_method = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    land_record = relationship("LandRecord", back_populates="extracted_fields")
