import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.processing import ProcessingJob
from app.models.document import Document
from app.processing.stages.base import ProcessingStage
from app.services.validation.engine import ValidationEngine

logger = logging.getLogger(__name__)

class ValidationStage(ProcessingStage):
    """
    Stage to calculate confidence and run validation rules on ExtractedFields.
    Transitions LandRecord status from PENDING_VERIFICATION to VERIFIED or CONFLICT if appropriate.
    """
    
    @property
    def name(self) -> str:
        return "VALIDATION"
        
    async def execute(self, session: AsyncSession, job: ProcessingJob, document: Document) -> Dict[str, Any]:
        logger.info(f"Starting ValidationStage for job {job.id}, document {job.document_id}")
        
        # 1. Fetch LandRecords with eager-loaded extracted_fields
        from app.models.land_record import LandRecord
        result = await session.execute(
            select(LandRecord)
            .options(selectinload(LandRecord.extracted_fields))
            .filter(LandRecord.document_id == job.document_id)
        )
        records = result.scalars().all()
        
        if not records:
            logger.warning(f"No LandRecords found for document {job.document_id}. Skipping ValidationStage.")
            return {"records_validated": 0, "skipped": True}
            
        engine = ValidationEngine(session)
        
        for record in records:
            await engine.process_record(record)
            
        logger.info(f"Completed ValidationStage for document {job.document_id}. Processed {len(records)} record(s).")
        return {"records_validated": len(records)}
