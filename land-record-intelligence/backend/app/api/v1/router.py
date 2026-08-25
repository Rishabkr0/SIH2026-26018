from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.db.redis_client import redis_client
from app.storage.minio_client import minio_client

from app.models.document import Document
from app.models.processing import ProcessingJob
from app.models.land_record import LandRecord, RecordStatus
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.schemas.processing import ProcessingJobResponse
from app.schemas.land_record import LandRecordResponse, LandRecordDetailResponse
from app.services.document_service import process_document_upload

from app.api.v1.endpoints import ocr

router = APIRouter()
router.include_router(ocr.router, tags=["ocr"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    redis_status = "ok"
    minio_status = "ok"
    overall_status = "ok"

    # Check DB
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "failed"
        overall_status = "failed"

    # Check Redis
    is_redis_up = await redis_client.ping()
    if not is_redis_up:
        redis_status = "failed"
        overall_status = "failed"

    # Check MinIO
    is_minio_up = minio_client.verify_connection()
    if not is_minio_up:
        minio_status = "failed"
        overall_status = "failed"

    payload = {
        "status": overall_status,
        "services": {
            "database": db_status,
            "redis": redis_status,
            "storage": minio_status
        }
    }

    if overall_status == "failed":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=payload)

    return payload

@router.post("/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    doc, job = await process_document_upload(file, db)
    return DocumentUploadResponse(
        document=doc,
        processing_job_id=job.id
    )

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc

@router.get("/documents/{document_id}/file")
async def get_document_file(document_id: UUID, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    try:
        response = await run_in_threadpool(minio_client.get_object, doc.storage_key)
        
        def iterfile():
            try:
                for chunk in response.stream(32 * 1024):
                    yield chunk
            finally:
                response.release_conn()
                
        return StreamingResponse(
            iterfile(),
            media_type=doc.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{doc.original_filename}"'
            }
        )
    except Exception as e:
        # Minio error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")

@router.get("/documents/{document_id}/processing", response_model=ProcessingJobResponse)
async def get_processing_job(document_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(ProcessingJob).where(ProcessingJob.document_id == document_id)
    result = await db.execute(query)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processing job not found")
    return job

@router.post("/documents/{document_id}/process", response_model=ProcessingJobResponse)
async def manually_process_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Manually enqueue an existing document for processing.
    """
    from datetime import datetime, timezone
    from app.processing.queue import ProcessingQueue
    from app.models.processing import JobStatus
    
    # 1. Check if document exists
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    # 2. Check existing job
    query = select(ProcessingJob).where(ProcessingJob.document_id == document_id)
    result = await db.execute(query)
    job = result.scalars().first()
    
    if not job:
        # Create one if missing
        job = ProcessingJob(
            document_id=document_id,
            status=JobStatus.PENDING
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
    # 3. If already queued or processing, return conflict
    if job.status in [JobStatus.QUEUED, JobStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Job is already in {job.status.value} state."
        )
        
    # 4. Enqueue
    enqueue_success = await ProcessingQueue.enqueue_job(str(job.id))
    
    if enqueue_success:
        job.status = JobStatus.QUEUED
        job.queued_at = datetime.now(timezone.utc)
        job.error_message = None # Reset error if it was FAILED
    else:
        job.status = JobStatus.FAILED
        job.failed_at = datetime.now(timezone.utc)
        job.error_message = "Failed to manually enqueue job to Redis."
        
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

@router.get("/records", response_model=List[LandRecordResponse])
async def list_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    owner: Optional[str] = None,
    khasra: Optional[str] = None,
    khata: Optional[str] = None,
    village: Optional[str] = None,
    record_status: Optional[RecordStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(LandRecord)
    
    if owner:
        query = query.where(LandRecord.owner_name.ilike(f"%{owner}%"))
    if khasra:
        query = query.where(LandRecord.khasra_number == khasra)
    if khata:
        query = query.where(LandRecord.khata_number == khata)
    if village:
        query = query.where(LandRecord.village.ilike(f"%{village}%"))
    if record_status:
        query = query.where(LandRecord.status == record_status)
        
    query = query.order_by(LandRecord.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/records/{record_id}", response_model=LandRecordDetailResponse)
async def get_record(record_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(LandRecord).where(LandRecord.id == record_id).options(
        selectinload(LandRecord.extracted_fields),
        selectinload(LandRecord.validation_findings)
    )
    result = await db.execute(query)
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record
