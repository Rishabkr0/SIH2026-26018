from typing import List, Dict, Optional
from app.services.extraction.provider import ExtractionProvider
from app.services.extraction.rules_provider import RulesProvider
from app.services.extraction.ollama_adapter import OllamaAdapter
from app.services.extraction.schemas import ExtractionResultData, ExtractedFieldData
from app.models.ocr import OCRPageResult
from app.core.config import settings
from app.core.logging import logger

class LayeredExtractionService:
    def __init__(self):
        self.rules_provider = RulesProvider()
        self.ollama_provider = OllamaAdapter()
        
    async def extract_fields(self, document_id: str, pages: List[OCRPageResult], target_fields: List[str]) -> ExtractionResultData:
        logger.info(f"Starting layered extraction for document {document_id}")
        
        # 1. Deterministic Extraction
        rules_result = await self.rules_provider.extract(document_id, pages, target_fields)
        
        extracted_dict: Dict[str, ExtractedFieldData] = {}
        for field in rules_result.fields:
            extracted_dict[field.field_name] = field
            
        # 2. Identify unresolved fields (where deterministic rules produced no candidate value)
        unresolved_fields = []
        for field in target_fields:
            if field not in extracted_dict or not extracted_dict[field].extracted_value:
                unresolved_fields.append(field)
                
        # 3. Local Model Fallback for unresolved fields
        if unresolved_fields:
            logger.info(f"Document {document_id}: Falling back to Ollama for fields: {unresolved_fields}")
            ollama_result = await self.ollama_provider.extract(document_id, pages, unresolved_fields)
            
            for field in ollama_result.fields:
                # If rules already provided a low-confidence value, we overwrite it with Ollama's if it's not empty
                if field.extracted_value:
                    extracted_dict[field.field_name] = field
        
        final_fields = list(extracted_dict.values())
        return ExtractionResultData(document_id=document_id, fields=final_fields)
