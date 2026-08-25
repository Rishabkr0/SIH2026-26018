from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class OCRBlockData(BaseModel):
    text: str
    confidence: Optional[float] = None
    x1: Optional[int] = None
    y1: Optional[int] = None
    x2: Optional[int] = None
    y2: Optional[int] = None
    block_index: Optional[int] = None

class OCRPageResultData(BaseModel):
    raw_text: str
    confidence: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    blocks: List[OCRBlockData] = []

class OCRProvider(ABC):
    """
    Abstract interface for OCR Providers (e.g. Tesseract, PaddleOCR).
    Allows switching OCR engines without modifying the orchestrator pipeline.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_version(self) -> str:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Returns True if the engine is available and loaded."""
        pass

    @abstractmethod
    async def recognize_page(self, image_path: str, language: str = "eng") -> OCRPageResultData:
        """
        Process a single image page and extract text and bounding boxes.
        image_path: Path to the preprocessed local image file.
        language: Language configuration string.
        """
        pass
