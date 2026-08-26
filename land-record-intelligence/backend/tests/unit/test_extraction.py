import pytest
from app.services.extraction.rules_provider import RulesProvider
from app.services.extraction.ollama_adapter import OllamaAdapter
from app.services.extraction.layered_service import LayeredExtractionService
from app.models.ocr import OCRPageResult, OCRBlock
from app.core.config import settings

@pytest.fixture
def sample_pages():
    page = OCRPageResult(page_number=1, raw_text="Khasra No: 1234\nArea: 1.5 hectares\nOwner Name: Ram Kumar")
    page.blocks = [
        OCRBlock(text="Khasra No: 1234", confidence=0.9, block_index=1),
        OCRBlock(text="Area: 1.5 hectares", confidence=0.85, block_index=2),
        OCRBlock(text="Owner Name: Ram Kumar", confidence=0.95, block_index=3),
    ]
    return [page]

@pytest.mark.asyncio
async def test_rules_provider_success(sample_pages):
    provider = RulesProvider()
    result = await provider.extract("doc_1", sample_pages, ["khasra_number", "land_area", "owner_name", "khata_number"])
    
    assert len(result.fields) == 3
    extracted_dict = {f.field_name: f for f in result.fields}
    assert extracted_dict["khasra_number"].extracted_value == "1234"
    assert extracted_dict["khasra_number"].confidence is None
    assert extracted_dict["land_area"].extracted_value == "1.5 hectares"
    assert extracted_dict["owner_name"].extracted_value == "Ram Kumar"
    
    # khata_number should be missing
    assert "khata_number" not in extracted_dict

@pytest.mark.asyncio
async def test_ollama_adapter_unavailable_fallback(sample_pages):
    # Temporarily set to a bogus URL to force failure
    original_url = settings.OLLAMA_URL
    settings.OLLAMA_URL = "http://localhost:99999" # invalid port
    
    provider = OllamaAdapter()
    result = await provider.extract("doc_1", sample_pages, ["khata_number"])
    
    # Should safely return empty without crashing
    assert len(result.fields) == 0
    
    settings.OLLAMA_URL = original_url

@pytest.mark.asyncio
async def test_layered_service(sample_pages, monkeypatch):
    service = LayeredExtractionService()
    
    # Mock the ollama provider to simulate a successful fallback
    async def mock_extract(doc_id, pages, fields):
        from app.services.extraction.schemas import ExtractionResultData, ExtractedFieldData
        res = ExtractionResultData(document_id=doc_id)
        if "khata_number" in fields:
            res.fields.append(ExtractedFieldData(
                field_name="khata_number",
                extracted_value="5678",
                confidence=None,
                extraction_method="OLLAMA"
            ))
        return res
        
    monkeypatch.setattr(service.ollama_provider, "extract", mock_extract)
    
    result = await service.extract_fields("doc_1", sample_pages, ["khasra_number", "khata_number"])
    
    extracted_dict = {f.field_name: f for f in result.fields}
    assert extracted_dict["khasra_number"].extracted_value == "1234"
    assert extracted_dict["khasra_number"].extraction_method == "RULES"
    assert extracted_dict["khata_number"].extracted_value == "5678"
    assert extracted_dict["khata_number"].extraction_method == "OLLAMA"
