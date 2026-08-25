import uuid
import re
from fastapi import UploadFile, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logging import logger
from app.storage.minio_client import minio_client
from app.models.document import Document, DocumentStatus
from app.models.processing import ProcessingJob, JobStatus

def sanitize_filename(filename: str) -> str:
    # Basic sanitization to prevent path traversal
    if not filename:
        return "unnamed_file"
    filename = re.sub(r"[^\w\-\.]", "_", filename)
    return filename.strip("_")

async def process_document_upload(file: UploadFile, db: AsyncSession):
    # Validate MIME type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(settings.ALLOWED_MIME_TYPES)}"
        )

    # Read and Validate Size
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size allowed is {settings.MAX_UPLOAD_SIZE} bytes."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty."
        )

    # Generate IDs and Paths
    document_id = uuid.uuid4()
    safe_filename = sanitize_filename(file.filename)
    storage_key = f"documents/{document_id}/original/{safe_filename}"

    # 1. Upload to MinIO (Run in threadpool to prevent blocking)
    try:
        await run_in_threadpool(
            minio_client.upload_object,
            object_name=storage_key,
            data=file_bytes,
            length=file_size,
            content_type=file.content_type
        )
    except Exception as e:
        logger.error(f"Storage upload failed for {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store document."
        )

    # 2. Database Transaction
    try:
        new_doc = Document(
            id=document_id,
            original_filename=safe_filename,
            storage_key=storage_key,
            content_type=file.content_type,
            file_size=file_size,
            status=DocumentStatus.UPLOADED,
        )
        
        new_job = ProcessingJob(
            document_id=document_id,
            status=JobStatus.PENDING
        )
        
        db.add(new_doc)
        db.add(new_job)
        
        await db.commit()
        await db.refresh(new_doc)
        await db.refresh(new_job)
        
        return new_doc, new_job
        
    except SQLAlchemyError as e:
        logger.error(f"Database insertion failed for {document_id}: {e}")
        await db.rollback()
        
        # Compensating action: Delete from MinIO
        try:
            await run_in_threadpool(minio_client.delete_object, storage_key)
        except Exception as cleanup_err:
            logger.error(f"Failed to cleanup orphaned MinIO object {storage_key}: {cleanup_err}")
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed. Upload rolled back."
        )
