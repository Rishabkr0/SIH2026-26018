from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from fastapi.concurrency import run_in_threadpool

from app.models.processing import ProcessingJob
from app.models.document import Document
from app.processing.stages.base import ProcessingStage
from app.storage.minio_client import minio_client
from app.core.config import settings

class DevelopmentValidationStage(ProcessingStage):
    """
    A placeholder stage used to validate the orchestration pipeline.
    It does not perform real OCR or extraction.
    """

    @property
    def name(self) -> str:
        return "development_validation"

    async def execute(self, session: AsyncSession, job: ProcessingJob, document: Document) -> Dict[str, Any]:
        """
        Validates that the document and storage object are accessible.
        """
        # 1. Verify database document existence
        if not document or not document.storage_key:
            raise ValueError("Document or storage_key missing.")

        # 2. Verify MinIO object existence via threadpool (since minio is sync)
        try:
            stat = await run_in_threadpool(
                minio_client.client.stat_object, 
                settings.MINIO_BUCKET, 
                document.storage_key
            )
        except Exception as e:
            raise RuntimeError(f"Storage object inaccessible: {e}")

        # Provide a small simulated delay for realistic orchestration observation
        await asyncio.sleep(2)

        return {
            "document_accessible": True,
            "storage_object_accessible": True,
            "file_size": stat.size,
            "development_stage": True
        }
