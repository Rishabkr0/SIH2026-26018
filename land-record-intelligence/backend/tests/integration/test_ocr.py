import pytest
import os
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image

from app.models.document import Document
from app.models.ocr import OCRDocumentResult, OCRStatus
from app.services.ocr.tesseract_adapter import TesseractAdapter
from app.services.preprocessing import DocumentPreprocessor
from app.processing.stages.ocr import OCRStage
from app.models.processing import ProcessingJob, JobStatus

@pytest.fixture
def sample_image_path(tmp_path):
    img_path = tmp_path / "test_img.png"
    # Create a small dummy image with some text
    img = Image.new('RGB', (100, 30), color = (255, 255, 255))
    img.save(img_path)
    return str(img_path)

@pytest.mark.asyncio
async def test_tesseract_adapter_health():
    adapter = TesseractAdapter()
    # Assuming tesseract is installed in the test environment (which it should be via Docker)
    is_healthy = adapter.health_check()
    assert is_healthy is True

@pytest.mark.asyncio
async def test_tesseract_adapter_recognize(sample_image_path):
    adapter = TesseractAdapter()
    result = await adapter.recognize_page(sample_image_path, "eng")
    assert result.width == 100
    assert result.height == 30
    assert result.raw_text is not None
    # For a blank image, text might be empty, but that's fine. We just check structure.
    assert isinstance(result.blocks, list)

@pytest.mark.asyncio
async def test_ocr_endpoints(async_client: AsyncClient, db_session: AsyncSession):
    # Setup dummy document and OCR results
    doc = Document(
        id=uuid4(),
        original_filename="test.pdf",
        content_type="application/pdf",
        storage_key="test/test.pdf",
        file_size=1024
    )
    db_session.add(doc)
    
    ocr_doc = OCRDocumentResult(
        id=uuid4(),
        document_id=doc.id,
        provider="tesseract",
        status=OCRStatus.COMPLETED
    )
    db_session.add(ocr_doc)
    await db_session.commit()
    
    # Test GET /documents/{id}/ocr
    response = await async_client.get(f"/api/v1/documents/{doc.id}/ocr")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(ocr_doc.id)
    assert data["status"] == "COMPLETED"
    
    # Test 404
    fake_id = uuid4()
    response_404 = await async_client.get(f"/api/v1/documents/{fake_id}/ocr")
    assert response_404.status_code == 404
