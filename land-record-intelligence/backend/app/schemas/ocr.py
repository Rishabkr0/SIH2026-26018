from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class OCRBlockSchema(BaseModel):
    id: UUID
    page_id: UUID
    text: str
    confidence: Optional[float] = None
    x1: Optional[int] = None
    y1: Optional[int] = None
    x2: Optional[int] = None
    y2: Optional[int] = None
    block_index: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class OCRPageResultSchema(BaseModel):
    id: UUID
    ocr_document_result_id: UUID
    page_number: int
    raw_text: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    blocks: List[OCRBlockSchema] = []

    model_config = ConfigDict(from_attributes=True)

class OCRDocumentResultSchema(BaseModel):
    id: UUID
    document_id: UUID
    provider: str
    provider_version: Optional[str] = None
    language_config: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata_json: Optional[Dict[str, Any]] = None
    pages: List[OCRPageResultSchema] = []

    model_config = ConfigDict(from_attributes=True)
