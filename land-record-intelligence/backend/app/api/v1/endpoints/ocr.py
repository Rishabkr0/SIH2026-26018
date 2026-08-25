from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.db.session import get_db
from app.models.ocr import OCRDocumentResult, OCRPageResult
from app.schemas.ocr import OCRDocumentResultSchema, OCRPageResultSchema

router = APIRouter()

@router.get("/documents/{document_id}/ocr", response_model=OCRDocumentResultSchema)
async def get_document_ocr_result(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the OCR results for a specific document.
    """
    stmt = (
        select(OCRDocumentResult)
        .where(OCRDocumentResult.document_id == document_id)
        .options(
            selectinload(OCRDocumentResult.pages).selectinload(OCRPageResult.blocks)
        )
    )
    result = await db.execute(stmt)
    ocr_result = result.scalar_one_or_none()
    
    if not ocr_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR result not found for this document"
        )
        
    return ocr_result

@router.get("/documents/{document_id}/ocr/pages/{page_number}", response_model=OCRPageResultSchema)
async def get_document_ocr_page_result(
    document_id: UUID,
    page_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed OCR results and blocks for a specific page.
    """
    stmt = (
        select(OCRPageResult)
        .join(OCRDocumentResult)
        .where(
            OCRDocumentResult.document_id == document_id,
            OCRPageResult.page_number == page_number
        )
        .options(
            selectinload(OCRPageResult.blocks)
        )
    )
    result = await db.execute(stmt)
    page_result = result.scalar_one_or_none()
    
    if not page_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OCR page result not found for page {page_number}"
        )
        
    return page_result
