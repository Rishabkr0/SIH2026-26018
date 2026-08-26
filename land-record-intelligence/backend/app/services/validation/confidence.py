import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.land_record import ExtractedField
from app.models.ocr import OCRDocumentResult, OCRPageResult, OCRBlock

class ConfidenceEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_ocr_confidence(self, document_id: str, source_reference: str) -> Optional[float]:
        if not source_reference:
            return None
            
        # source_reference format: "page_1_block_0"
        match = re.match(r"page_(\d+)_block_(\d+)", source_reference)
        if not match:
            return None
            
        page_num = int(match.group(1))
        block_idx = int(match.group(2))
        
        stmt = select(OCRBlock).join(OCRPageResult).join(OCRDocumentResult).filter(
            OCRDocumentResult.document_id == document_id,
            OCRPageResult.page_number == page_num,
            OCRBlock.block_index == block_idx
        )
        result = await self.db.execute(stmt)
        block = result.scalars().first()
        
        if block:
            return block.confidence
        return None

    async def calculate_derived_confidence(self, document_id: str, field: ExtractedField) -> Optional[float]:
        """
        Calculates the numeric confidence score for a given extracted field.
        Only uses explicitly observed evidence (e.g. OCR block confidence).
        Returns None (UNKNOWN) if sufficient numeric evidence does not exist.
        """
        if not field.extracted_value:
            return None
            
        derived = None
        
        if field.extraction_method == "RULES":
            # Legitimate Numeric Generation from OCR Block
            ocr_confidence = await self._get_ocr_confidence(document_id, field.source_reference)
            if ocr_confidence is not None:
                derived = ocr_confidence
                
        # If extraction_method is OLLAMA or if OCR confidence is missing,
        # we do not invent a fabricated baseline or penalty. It remains None (UNKNOWN).
        
        return derived
