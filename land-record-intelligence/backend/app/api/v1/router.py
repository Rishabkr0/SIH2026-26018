from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.db.redis_client import redis_client
from app.storage.minio_client import minio_client

from app.models.document import Document
from app.models.land_record import LandRecord, RecordStatus
from app.schemas.document import DocumentResponse
from app.schemas.land_record import LandRecordResponse, LandRecordDetailResponse

router = APIRouter()

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
