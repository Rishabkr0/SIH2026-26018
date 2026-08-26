import re
from typing import List
from app.services.extraction.provider import ExtractionProvider
from app.services.extraction.schemas import ExtractionResultData, ExtractedFieldData
from app.models.ocr import OCRPageResult, OCRBlock

class RulesProvider(ExtractionProvider):
    @property
    def provider_name(self) -> str:
        return "RULES"

    async def extract(self, document_id: str, pages: List[OCRPageResult], target_fields: List[str]) -> ExtractionResultData:
        result = ExtractionResultData(document_id=document_id, fields=[])
        
        patterns = {
            "khasra_number": r"(?i)(?:khasra\s*(?:no\.?|number)?\s*[:-]?\s*)(\d+[/\w]*)",
            "khata_number": r"(?i)(?:khata\s*(?:no\.?|number)?\s*[:-]?\s*)(\d+[/\w]*)",
            "land_area": r"(?i)(?:area\s*[:-]?\s*)(\d+(?:\.\d+)?\s*(?:sq\.?\s*m|hectares?|acres?|ha))",
            "owner_name": r"(?i)(?:owner|name of owner|owner name)\s*[:-]?\s*([A-Za-z\s]{3,30})(?=\n|$)",
            "district": r"(?i)(?:district|zilla)\s*[:-]?\s*([A-Za-z]+)",
            "village": r"(?i)(?:village|gaon)\s*[:-]?\s*([A-Za-z]+)",
            "state": r"(?i)(?:state)\s*[:-]?\s*([A-Za-z]+)",
            "record_identifier": r"(?i)(?:record\s*(?:id|no|identifier)|id)\s*[:-]?\s*([A-Za-z0-9\-]+)",
            "land_classification": r"(?i)(?:classification|type)\s*[:-]?\s*([A-Za-z\s]+)"
        }
        
        extracted_keys = set()
        
        for page in pages:
            # A simple block-by-block heuristic
            for block in page.blocks:
                text = block.text or ""
                for field in target_fields:
                    if field in extracted_keys:
                        continue
                        
                    if field in patterns:
                        match = re.search(patterns[field], text)
                        if match:
                            value = match.group(1).strip()
                            
                            bbox = None
                            if block.x1 is not None and block.y1 is not None and block.x2 is not None and block.y2 is not None:
                                bbox = {
                                    "x1": block.x1,
                                    "y1": block.y1,
                                    "x2": block.x2,
                                    "y2": block.y2
                                }
                            
                            result.fields.append(ExtractedFieldData(
                                field_name=field,
                                extracted_value=value,
                                confidence=None,
                                extraction_method=self.provider_name,
                                source_reference=f"page_{page.page_number}_block_{block.block_index}",
                                bounding_box=bbox
                            ))
                            extracted_keys.add(field)

        return result
