import pytest
from app.processing.stages.validation_stage import ValidationStage
from app.models.land_record import LandRecord, ExtractedField, RecordStatus
from app.models.document import Document, DocumentStatus
from app.models.processing import ProcessingJob, JobStatus
from app.models.validation import ValidationFinding

@pytest.mark.asyncio
async def test_validation_stage_integration(db_session):
    # Create Document & Job
    doc = Document(original_filename="test.pdf", storage_key="test/key", content_type="application/pdf", file_size=1024)
    db_session.add(doc)
    await db_session.commit()
    
    job = ProcessingJob(document_id=doc.id, status=JobStatus.PROCESSING)
    db_session.add(job)
    await db_session.commit()
    
    # Create a LandRecord left in PENDING_VERIFICATION by ExtractionStage
    record = LandRecord(document_id=doc.id, status=RecordStatus.PENDING_VERIFICATION)
    db_session.add(record)
    await db_session.commit()
    
    # Add fields: Missing "village" to trigger CRITICAL finding, and unknown confidence
    f1 = ExtractedField(land_record_id=record.id, field_name="khasra_number", extracted_value="123", extraction_method="RULES")
    f2 = ExtractedField(land_record_id=record.id, field_name="owner_name", extracted_value="Ramesh", extraction_method="RULES")
    db_session.add_all([f1, f2])
    await db_session.commit()
    
    # Expire all to clear cache
    db_session.expire_all()
    
    # Refresh job and doc to prevent MissingGreenlet lazy-load errors in the stage
    await db_session.refresh(job)
    await db_session.refresh(doc)
    
    # Run the stage
    stage = ValidationStage()
    result = await stage.execute(db_session, job, doc)
    assert result.get("records_validated") == 1
    
    # Commit the session to mimic Orchestrator behavior
    await db_session.commit()
    
    # Fetch the updated record
    from sqlalchemy.future import select
    record = (await db_session.execute(select(LandRecord).filter_by(id=record.id))).scalar_one()
    
    # It should still be PENDING_VERIFICATION
    assert record.status == RecordStatus.PENDING_VERIFICATION
    
    # Assert findings were created
    findings = (await db_session.execute(select(ValidationFinding).filter_by(land_record_id=record.id))).scalars().all()
    
    assert len(findings) > 0
    assert any(f.finding_type == "MISSING_REQUIRED_FIELD" and f.field_name == "village" for f in findings)
    
    # Assert confidence was updated to 0.0 (UNKNOWN) because we don't have OCR blocks in this db_session mock
    await db_session.refresh(f1)
    assert f1.confidence == 0.0
