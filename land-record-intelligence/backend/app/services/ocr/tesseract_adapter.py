import pytesseract
from PIL import Image
import asyncio
from typing import List

from .provider import OCRProvider, OCRPageResultData, OCRBlockData
from app.core.logging import logger

class TesseractAdapter(OCRProvider):
    def __init__(self):
        self._provider_name = "tesseract"
        self._provider_version = "unknown"
        try:
            self._provider_version = pytesseract.get_tesseract_version()
        except Exception:
            pass

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def provider_version(self) -> str:
        return str(self._provider_version)

    def health_check(self) -> bool:
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    async def recognize_page(self, image_path: str, language: str = "eng") -> OCRPageResultData:
        """
        Extracts text and TSV blocks using Tesseract OCR.
        Runs in an asyncio threadpool to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self._recognize_sync, image_path, language)

    def _recognize_sync(self, image_path: str, language: str) -> OCRPageResultData:
        img = Image.open(image_path)
        width, height = img.size
        
        # 1. Get raw string
        raw_text = pytesseract.image_to_string(img, lang=language)
        
        # 2. Get detailed data (TSV)
        # Columns: level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text
        data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
        
        blocks: List[OCRBlockData] = []
        total_conf = 0.0
        conf_count = 0
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text:
                continue
                
            conf_val = float(data['conf'][i])
            if conf_val >= 0: # -1 means no confidence for this level
                total_conf += conf_val
                conf_count += 1
                
            normalized_conf = conf_val / 100.0 if conf_val >= 0 else None
            
            blocks.append(OCRBlockData(
                text=text,
                confidence=normalized_conf,
                x1=data['left'][i],
                y1=data['top'][i],
                x2=data['left'][i] + data['width'][i],
                y2=data['top'][i] + data['height'][i],
                block_index=i
            ))
            
        page_confidence = (total_conf / conf_count / 100.0) if conf_count > 0 else None
        
        return OCRPageResultData(
            raw_text=raw_text,
            confidence=page_confidence,
            width=width,
            height=height,
            blocks=blocks
        )
