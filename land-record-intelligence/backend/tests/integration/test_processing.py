import pytest
from httpx import AsyncClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document
from app.models.processing import ProcessingJob, JobStatus
from app.processing.queue import ProcessingQueue
from app.processing.worker import ProcessingWorker

@pytest.mark.asyncio
async def test_manual_processing_enqueue(async_client: AsyncClient, db_session: AsyncSession, test_pdf: bytes):
    # 1. Upload a document
    response = await async_client.post(
        "/api/v1/documents",
        files={"file": ("test.pdf", test_pdf, "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    doc_id = data["document"]["id"]
    job_id = data["processing_job_id"]
    
    # 2. Check the job is QUEUED initially
    job_response = await async_client.get(f"/api/v1/documents/{doc_id}/processing")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "QUEUED"
    
    # 3. Test Manual Processing conflict
    manual_response = await async_client.post(f"/api/v1/documents/{doc_id}/process")
    assert manual_response.status_code == 409
    
    # 4. Modify the DB to simulate FAILED state, so we can re-enqueue
    job = await db_session.get(ProcessingJob, job_id)
    job.status = JobStatus.FAILED
    db_session.add(job)
    await db_session.commit()
    
    # 5. Test manual processing successfully
    manual_response2 = await async_client.post(f"/api/v1/documents/{doc_id}/process")
    assert manual_response2.status_code == 200
    assert manual_response2.json()["status"] == "QUEUED"

@pytest.mark.asyncio
async def test_worker_processing(async_client: AsyncClient, db_session: AsyncSession, test_pdf: bytes):
    # This test verifies that the ProcessingWorker can pick up a QUEUED job and process it
    # 1. Upload
    response = await async_client.post(
        "/api/v1/documents",
        files={"file": ("test2.pdf", test_pdf, "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    job_id = data["processing_job_id"]
    doc_id = data["document"]["id"]
    
    # Verify it is in Redis
    queued_job_id = await ProcessingQueue.dequeue_job(timeout=1)
    assert queued_job_id == job_id
    
    # Now simulate worker consuming it, but fully contained to avoid loop/pool issues in test
    worker = ProcessingWorker(worker_id="test_worker")
    job = await worker._claim_job(job_id)
    assert job is not None
    assert job.status == JobStatus.PROCESSING
    assert job.worker_id == "test_worker"
    
    # Let orchestrator run in a fresh session to avoid asyncpg connection bound issues
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as pipeline_session:
        # reload job
        fresh_job = await pipeline_session.get(ProcessingJob, job_id)
        result = await worker.orchestrator.run_pipeline(pipeline_session, fresh_job)
        
    assert result is True
    
    # Check updated state
    async with AsyncSessionLocal() as check_session:
        final_job = await check_session.get(ProcessingJob, job_id)
        assert final_job.status == JobStatus.COMPLETED
        assert type(final_job.job_metadata) is dict
        assert "stages_executed" in final_job.job_metadata

@pytest.mark.asyncio
async def test_invalid_document_process(async_client: AsyncClient):
    bad_id = str(uuid.uuid4())
    response = await async_client.post(f"/api/v1/documents/{bad_id}/process")
    assert response.status_code == 404
