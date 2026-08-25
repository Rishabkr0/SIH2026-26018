from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.land_record import RecordStatus
from app.models.validation import FindingStatus, FindingSeverity

class ExtractedFieldResponse(BaseModel):
    id: UUID
    field_name: str
    extracted_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float
    source_reference: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None
    extraction_method: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ValidationFindingResponse(BaseModel):
    id: UUID
    field_name: Optional[str] = None
    finding_type: str
    severity: FindingSeverity
    message: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    status: FindingStatus
    
    model_config = ConfigDict(from_attributes=True)

class LandRecordBase(BaseModel):
    document_id: UUID
    record_identifier: Optional[str] = None
    owner_name: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    land_area: Optional[str] = None
    land_classification: Optional[str] = None
    status: RecordStatus

class LandRecordResponse(LandRecordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LandRecordDetailResponse(LandRecordResponse):
    extracted_fields: List[ExtractedFieldResponse] = []
    validation_findings: List[ValidationFindingResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
