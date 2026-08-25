import io
import cv2
import numpy as np
from PIL import Image
from typing import List
from pdf2image import convert_from_bytes
import asyncio

from app.core.logging import logger

class DocumentPreprocessor:
    """
    Handles PDF to Image conversion and basic image normalization for OCR.
    """
    
    @staticmethod
    async def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
        """
        Converts a PDF byte stream into a list of PIL Images.
        Runs in a threadpool to avoid blocking the event loop.
        """
        try:
            images = await asyncio.to_thread(
                convert_from_bytes,
                pdf_bytes,
                dpi=dpi,
                fmt="jpeg",
                thread_count=2
            )
            return images
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise ValueError("Invalid or corrupted PDF file.") from e

    @staticmethod
    def _normalize_sync(img: Image.Image) -> Image.Image:
        """
        Synchronous internal method for OpenCV normalization.
        """
        # Convert PIL Image to OpenCV format (numpy array)
        open_cv_image = np.array(img)
        
        # Handle grayscale vs color
        if len(open_cv_image.shape) == 3 and open_cv_image.shape[2] == 3:
            # Convert RGB to BGR 
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            # Convert to grayscale
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = open_cv_image

        # Denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=30)
        
        # Adaptive Thresholding to handle varying lighting/contrast
        # thresholded = cv2.adaptiveThreshold(
        #    denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        # )
        
        # Convert back to PIL Image
        return Image.fromarray(denoised)

    @staticmethod
    async def normalize_image(img: Image.Image) -> Image.Image:
        """
        Applies grayscale conversion and denoising to prepare image for OCR.
        Runs in a threadpool.
        """
        return await asyncio.to_thread(DocumentPreprocessor._normalize_sync, img)
