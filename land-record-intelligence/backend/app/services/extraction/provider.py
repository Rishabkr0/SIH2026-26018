from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.services.extraction.schemas import ExtractionResultData
from app.models.ocr import OCRPageResult, OCRBlock

class ExtractionProvider(ABC):
    """
    Abstract interface for field extraction providers.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider."""
        pass
        
    @abstractmethod
    async def extract(self, document_id: str, pages: List[OCRPageResult], target_fields: List[str]) -> ExtractionResultData:
        """
        Extract target fields from OCR pages and blocks.
        :param document_id: The ID of the document being processed.
        :param pages: A list of OCRPageResult objects (which contain associated OCRBlock objects).
        :param target_fields: A list of field names to extract.
        :return: ExtractionResultData containing the extracted fields.
        """
        pass
