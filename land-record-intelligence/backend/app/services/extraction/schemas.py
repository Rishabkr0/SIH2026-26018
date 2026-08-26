from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ExtractedFieldData(BaseModel):
    field_name: str
    extracted_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: Optional[float] = None
    source_reference: Optional[str] = None
    bounding_box: Optional[Dict[str, int]] = None
    extraction_method: str

class ExtractionResultData(BaseModel):
    document_id: str
    fields: List[ExtractedFieldData] = []
    
    def get_field(self, field_name: str) -> Optional[ExtractedFieldData]:
        for f in self.fields:
            if f.field_name == field_name:
                return f
        return None
