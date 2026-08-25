from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.db.redis_client import redis_client
from app.storage.minio_client import minio_client

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
    # Note: MinIO verification might be blocking, but fast enough for local ping.
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
