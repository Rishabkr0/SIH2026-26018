import tempfile
import os
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import io
from PIL import Image

from app.models.processing import ProcessingJob
from app.models.document import Document
from app.models.ocr import OCRDocumentResult, OCRPageResult, OCRBlock, OCRStatus
from app.processing.stages.base import ProcessingStage
from app.services.ocr.provider import OCRProvider
from app.services.preprocessing import DocumentPreprocessor
from app.storage.minio_client import minio_client
from app.core.config import settings
from app.core.logging import logger

class OCRStage(ProcessingStage):
    """
    Downloads source document, preprocesses pages, runs configured OCR engine, 
    and persists structured OCR results to Postgres.
    """
    
    def __init__(self, ocr_provider: OCRProvider, language: str = "eng"):
        self.ocr_provider = ocr_provider
        self.language = language

    @property
    def name(self) -> str:
        return f"ocr_{self.ocr_provider.provider_name}"
        
    async def execute(self, session: AsyncSession, job: ProcessingJob, document: Document) -> Dict[str, Any]:
        logger.info(f"Starting OCRStage for document {document.id} using {self.ocr_provider.provider_name}")
        
        # 1. Idempotency Check: Do we already have an OCR result for this document?
        result = await session.execute(
            select(OCRDocumentResult).where(OCRDocumentResult.document_id == document.id)
        )
        existing_ocr = result.scalar_one_or_none()
        
        if existing_ocr:
            if existing_ocr.status == OCRStatus.COMPLETED:
                logger.info(f"OCR already completed for document {document.id}. Skipping.")
                return {"status": "skipped", "reason": "already completed"}
            else:
                # Clear out partial/failed run to retry cleanly
                await session.delete(existing_ocr)
                await session.flush()
        
        # 2. Initialize new OCR Document Result
        doc_result = OCRDocumentResult(
            document_id=document.id,
            provider=self.ocr_provider.provider_name,
            provider_version=self.ocr_provider.provider_version,
            language_config=self.language,
            status=OCRStatus.PROCESSING
        )
        session.add(doc_result)
        await session.flush()
        
        # 3. Retrieve document bytes from MinIO
        import urllib3
        response = None
        try:
            response = minio_client.get_object(document.storage_key)
            file_bytes = response.read()
        finally:
            if response:
                response.close()
                response.release_conn()
            
        if not file_bytes:
            raise ValueError("Document file is empty or missing from storage.")
            
        # 4. Preprocess: Get PIL Images for each page
        pages: List[Image.Image] = []
        if document.content_type == "application/pdf":
            logger.info(f"Converting PDF {document.id} to images...")
            pages = await DocumentPreprocessor.pdf_to_images(file_bytes)
        else:
            # Assume image
            img = Image.open(io.BytesIO(file_bytes))
            pages = [img]
            
        logger.info(f"Document {document.id} yielded {len(pages)} pages.")
        
        page_results = []
        failed_pages = 0
        
        # Create a temporary directory to save images for Tesseract to read from disk
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, page_img in enumerate(pages):
                page_num = i + 1
                try:
                    logger.info(f"Processing page {page_num}/{len(pages)}")
                    
                    # Normalize image
                    norm_img = await DocumentPreprocessor.normalize_image(page_img)
                    
                    # Save temporarily
                    temp_path = os.path.join(temp_dir, f"page_{page_num}.png")
                    norm_img.save(temp_path, format="PNG")
                    
                    start_time = datetime.now(timezone.utc)
                    # Run OCR
                    ocr_data = await self.ocr_provider.recognize_page(temp_path, self.language)
                    end_time = datetime.now(timezone.utc)
                    duration = (end_time - start_time).total_seconds()
                    
                    # Persist Page Result
                    page_record = OCRPageResult(
                        ocr_document_result_id=doc_result.id,
                        page_number=page_num,
                        raw_text=ocr_data.raw_text,
                        confidence=ocr_data.confidence,
                        processing_time_seconds=duration,
                        width=ocr_data.width,
                        height=ocr_data.height
                    )
                    session.add(page_record)
                    await session.flush()
                    
                    # Persist Blocks
                    if ocr_data.blocks:
                        db_blocks = [
                            OCRBlock(
                                page_id=page_record.id,
                                text=b.text,
                                confidence=b.confidence,
                                x1=b.x1, y1=b.y1, x2=b.x2, y2=b.y2,
                                block_index=b.block_index
                            )
                            for b in ocr_data.blocks
                        ]
                        session.add_all(db_blocks)
                        
                    page_results.append({
                        "page_number": page_num,
                        "status": "success",
                        "confidence": ocr_data.confidence
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to process page {page_num} of document {document.id}: {e}")
                    failed_pages += 1
                    page_results.append({
                        "page_number": page_num,
                        "status": "failed",
                        "error": str(e)
                    })
        
        # 5. Finalize Document Result Status
        if failed_pages == 0:
            doc_result.status = OCRStatus.COMPLETED
        elif failed_pages < len(pages):
            doc_result.status = OCRStatus.PARTIAL
        else:
            doc_result.status = OCRStatus.FAILED
            doc_result.error_message = "All pages failed OCR processing."
            
        doc_result.completed_at = datetime.now(timezone.utc)
        doc_result.metadata_json = {
            "total_pages": len(pages),
            "failed_pages": failed_pages,
            "page_details": page_results
        }
        
        session.add(doc_result)
        
        # If all pages failed, raise an exception to fail the overarching ProcessingJob
        if failed_pages == len(pages) and len(pages) > 0:
            raise RuntimeError("OCR Stage failed for all pages.")
            
        return {
            "status": doc_result.status.value,
            "provider": self.ocr_provider.provider_name,
            "total_pages": len(pages),
            "failed_pages": failed_pages
        }
