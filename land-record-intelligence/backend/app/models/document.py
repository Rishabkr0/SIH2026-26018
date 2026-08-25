from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy.orm import relationship

from app.db.base import Base

class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String, nullable=True)
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED)
    
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    processing_jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")
    land_records = relationship("LandRecord", back_populates="document", cascade="all, delete-orphan")
