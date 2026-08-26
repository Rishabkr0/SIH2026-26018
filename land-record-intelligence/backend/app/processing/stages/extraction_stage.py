from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.processing import ProcessingJob
from app.models.document import Document
from app.models.ocr import OCRDocumentResult, OCRPageResult
from app.models.land_record import LandRecord, ExtractedField, RecordStatus
from app.processing.stages.base import ProcessingStage
from app.services.extraction.layered_service import LayeredExtractionService
from app.core.config import settings

class ExtractionStage(ProcessingStage):
    @property
    def name(self) -> str:
        return "ExtractionStage"
        
    def __init__(self):
        self.extraction_service = LayeredExtractionService()
        self.target_fields = [
            "record_identifier",
            "owner_name",
            "khasra_number",
            "khata_number",
            "village",
            "district",
            "state",
            "land_area",
            "land_classification"
        ]

    async def execute(self, session: AsyncSession, job: ProcessingJob, document: Document) -> Dict[str, Any]:
        # 1. Fetch OCR Results
        stmt = (
            select(OCRDocumentResult)
            .where(OCRDocumentResult.document_id == document.id)
            .options(
                selectinload(OCRDocumentResult.pages)
                .selectinload(OCRPageResult.blocks)
            )
        )
        result = await session.execute(stmt)
        ocr_result = result.scalars().first()
        
        if not ocr_result:
            raise Exception("Cannot run extraction: No OCR results found for document.")
            
        # 2. Run Layered Extraction
        extraction_data = await self.extraction_service.extract_fields(
            document_id=str(document.id),
            pages=ocr_result.pages,
            target_fields=self.target_fields
        )
        
        # 3. Assess status based on confidence
        extracted_dict = {}
        for field in extraction_data.fields:
            extracted_dict[field.field_name] = field.extracted_value

        # Count fields that are missing entirely or have no extracted value
        unresolved_count = 0
        for field_name in self.target_fields:
            field_data = next((f for f in extraction_data.fields if f.field_name == field_name), None)
            if field_data is None or not field_data.extracted_value:
                unresolved_count += 1

        # Mark as PENDING_VERIFICATION (i.e. REVIEW_REQUIRED) if any field is unresolved
        final_status = RecordStatus.VERIFIED if unresolved_count == 0 else RecordStatus.PENDING_VERIFICATION
        
        # 4. Create LandRecord
        land_record = LandRecord(
            document_id=document.id,
            record_identifier=extracted_dict.get("record_identifier"),
            owner_name=extracted_dict.get("owner_name"),
            khasra_number=extracted_dict.get("khasra_number"),
            khata_number=extracted_dict.get("khata_number"),
            village=extracted_dict.get("village"),
            district=extracted_dict.get("district"),
            state=extracted_dict.get("state"),
            land_area=extracted_dict.get("land_area"),
            land_classification=extracted_dict.get("land_classification"),
            status=final_status
        )
        session.add(land_record)
        await session.flush() # flush to get land_record.id
        
        # 5. Create ExtractedField records for provenance
        for field_data in extraction_data.fields:
            if field_data.extracted_value:
                ext_field = ExtractedField(
                    land_record_id=land_record.id,
                    field_name=field_data.field_name,
                    extracted_value=field_data.extracted_value,
                    normalized_value=field_data.normalized_value,
                    confidence=field_data.confidence if field_data.confidence is not None else 0.0,
                    extraction_method=field_data.extraction_method,
                    source_reference=field_data.source_reference,
                    bounding_box=field_data.bounding_box
                )
                session.add(ext_field)
        
        # Flush so that test assertions can observe inserted rows within same session
        await session.flush()
                
        # 6. Return metadata
        return {
            "unresolved_fields": unresolved_count,
            "status": final_status.value,
            "fields_extracted": len([f for f in extraction_data.fields if f.extracted_value])
        }
