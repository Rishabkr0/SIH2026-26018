from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy.orm import relationship

from app.db.base import Base

class OCRStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class OCRDocumentResult(Base):
    __tablename__ = "ocr_document_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    provider = Column(String, nullable=False)
    provider_version = Column(String, nullable=True)
    language_config = Column(String, nullable=True)
    status = Column(Enum(OCRStatus), nullable=False, default=OCRStatus.PENDING)
    
    error_message = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    document = relationship("Document")
    pages = relationship("OCRPageResult", back_populates="document_result", cascade="all, delete-orphan")

class OCRPageResult(Base):
    __tablename__ = "ocr_page_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ocr_document_result_id = Column(UUID(as_uuid=True), ForeignKey("ocr_document_results.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    
    raw_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True) # Normalized 0.0 to 1.0
    processing_time_seconds = Column(Float, nullable=True)
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document_result = relationship("OCRDocumentResult", back_populates="pages")
    blocks = relationship("OCRBlock", back_populates="page_result", cascade="all, delete-orphan")

class OCRBlock(Base):
    __tablename__ = "ocr_blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("ocr_page_results.id", ondelete="CASCADE"), nullable=False)
    
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True) # Normalized 0.0 to 1.0
    
    x1 = Column(Integer, nullable=True)
    y1 = Column(Integer, nullable=True)
    x2 = Column(Integer, nullable=True)
    y2 = Column(Integer, nullable=True)
    
    block_index = Column(Integer, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    page_result = relationship("OCRPageResult", back_populates="blocks")
