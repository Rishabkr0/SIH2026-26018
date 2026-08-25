from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    original_filename: str
    content_type: str
    file_size: int
    status: DocumentStatus

class DocumentResponse(DocumentBase):
    id: UUID
    storage_key: str
    checksum: Optional[str] = None
    uploaded_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
