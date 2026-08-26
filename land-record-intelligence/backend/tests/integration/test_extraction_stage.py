import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus
from app.models.processing import ProcessingJob, JobStatus
from app.models.ocr import OCRDocumentResult, OCRPageResult, OCRBlock, OCRStatus
from app.models.land_record import LandRecord, ExtractedField, RecordStatus
from app.processing.stages.extraction_stage import ExtractionStage
from sqlalchemy import select

@pytest.mark.asyncio
async def test_extraction_stage_integration(db_session: AsyncSession):
    # 1. Setup Document and Job
    doc_id = uuid.uuid4()
    doc = Document(id=doc_id, original_filename="test.pdf", storage_key="test", content_type="application/pdf", file_size=100, status=DocumentStatus.UPLOADED)
    job = ProcessingJob(document_id=doc_id, status=JobStatus.PROCESSING)
    
    db_session.add(doc)
    db_session.add(job)
    await db_session.flush()
    
    # 2. Setup OCR Results
    ocr_res = OCRDocumentResult(document_id=doc_id, provider="test", status=OCRStatus.COMPLETED)
    db_session.add(ocr_res)
    await db_session.flush()
    
    page = OCRPageResult(ocr_document_result_id=ocr_res.id, page_number=1, raw_text="Khasra No: 999\nVillage: TestPur")
    db_session.add(page)
    await db_session.flush()
    
    block1 = OCRBlock(page_id=page.id, text="Khasra No: 999", confidence=0.9, block_index=1)
    block2 = OCRBlock(page_id=page.id, text="Village: TestPur", confidence=0.9, block_index=2)
    db_session.add_all([block1, block2])
    await db_session.flush()
    
    # 3. Execute ExtractionStage
    stage = ExtractionStage()
    result = await stage.execute(db_session, job, doc)
    
    # 4. Assertions
    assert "status" in result
    
    # Check if LandRecord was created
    stmt = select(LandRecord).where(LandRecord.document_id == doc_id)
    res = await db_session.execute(stmt)
    land_record = res.scalar_one()
    
    assert land_record is not None
    assert land_record.khasra_number == "999"
    assert land_record.village == "TestPur"
    
    # Check ExtractedFields
    stmt = select(ExtractedField).where(ExtractedField.land_record_id == land_record.id)
    res = await db_session.execute(stmt)
    fields = res.scalars().all()
    
    assert len(fields) >= 2
    field_names = [f.field_name for f in fields]
    assert "khasra_number" in field_names
    assert "village" in field_names
    
    # Since not all target fields were extracted, status should be PENDING_VERIFICATION
    assert land_record.status == RecordStatus.PENDING_VERIFICATION
