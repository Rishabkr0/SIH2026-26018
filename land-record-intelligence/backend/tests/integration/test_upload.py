import pytest
import io
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_invalid_mime_type(async_client: AsyncClient):
    file_content = b"This is a fake text file."
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    response = await async_client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_oversized_file(async_client: AsyncClient):
    # Simulate a file larger than 10MB
    # We don't actually need to send 11MB over the test client to test the logic
    # But since FastAPI reads it into memory or spools it, we can send a large dummy payload
    file_content = b"0" * (11 * 1024 * 1024)
    files = {"file": ("large.pdf", io.BytesIO(file_content), "application/pdf")}
    
    response = await async_client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_valid_file(async_client: AsyncClient, test_pdf: bytes):
    files = {"file": ("test.pdf", test_pdf, "application/pdf")}
    
    response = await async_client.post("/api/v1/documents", files=files)
    
    assert response.status_code == 201
    assert "document" in response.json()
    assert "processing_job_id" in response.json()
