import httpx
import json
from typing import List
from app.services.extraction.provider import ExtractionProvider
from app.services.extraction.schemas import ExtractionResultData, ExtractedFieldData
from app.models.ocr import OCRPageResult
from app.core.config import settings
from app.core.logging import logger

class OllamaAdapter(ExtractionProvider):
    @property
    def provider_name(self) -> str:
        return "OLLAMA"

    async def extract(self, document_id: str, pages: List[OCRPageResult], target_fields: List[str]) -> ExtractionResultData:
        result = ExtractionResultData(document_id=document_id, fields=[])
        if not target_fields:
            return result
            
        full_text = "\n".join([page.raw_text for page in pages if page.raw_text])
        if not full_text.strip():
            return result

        prompt = (
            "Extract the following fields from the document text provided below.\n"
            f"Fields to extract: {', '.join(target_fields)}\n"
            "Return ONLY a valid JSON object where keys are the field names and values are the extracted strings. "
            "If a field is not found, leave the value as null.\n\n"
            f"Document Text:\n{full_text}"
        )
        
        ollama_url = getattr(settings, "OLLAMA_URL", "http://localhost:11434")
        ollama_model = getattr(settings, "OLLAMA_MODEL", "mistral")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                response_text = data.get("response", "{}")
                extracted_json = json.loads(response_text)
                
                for field in target_fields:
                    val = extracted_json.get(field)
                    if val is not None and str(val).strip() and str(val).lower() != "null":
                        result.fields.append(ExtractedFieldData(
                            field_name=field,
                            extracted_value=str(val).strip(),
                            confidence=None,
                            extraction_method=self.provider_name,
                            source_reference="llm_inference"
                        ))
                        
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.warning(f"Ollama extraction failed: API connection error - {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"Ollama extraction failed: Invalid JSON response - {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama extraction: {e}")
            
        return result
