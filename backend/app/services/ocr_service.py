import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import pytesseract
from app.config import settings

class OCRException(Exception):
    def __init__(self, code: str, message: str, suggestion: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion

class OCRService:
    def __init__(self):
        self._setup_tesseract()

    def _setup_tesseract(self):
        """
        Configures pytesseract command and TESSDATA_PREFIX environment variable.
        """
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            
        if settings.TESSDATA_PREFIX and os.path.exists(settings.TESSDATA_PREFIX):
            os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX

    def check_availability(self) -> Tuple[bool, str]:
        """
        Verifies that tesseract binary is callable and target language is installed.
        Returns (is_available, error_or_info_message).
        """
        self._setup_tesseract()
        cmd = pytesseract.pytesseract.tesseract_cmd

        # Check binary existence
        if not shutil.which(cmd) and not os.path.exists(cmd):
            return False, f"Tesseract executable not found at '{cmd}' or in system PATH."

        try:
            # Check version
            version = pytesseract.get_tesseract_version()
            # Check available languages
            langs = pytesseract.get_languages(config="")
            if settings.OCR_LANGUAGE not in langs:
                return False, (
                    f"Language pack '{settings.OCR_LANGUAGE}' not found in Tesseract. "
                    f"Available languages: {langs or 'None'}. Checked TESSDATA_PREFIX: '{os.environ.get('TESSDATA_PREFIX')}'"
                )
            return True, f"Tesseract v{version} ready with language '{settings.OCR_LANGUAGE}'."
        except Exception as e:
            return False, f"Failed to run Tesseract: {str(e)}"

    def recognize_image(self, image: Image.Image) -> str:
        """
        Performs OCR on a PIL Image object with timeout and error handling.
        """
        available, msg = self.check_availability()
        if not available:
            raise OCRException(
                code="OCR_UNAVAILABLE",
                message="OCR engine is not properly configured or available.",
                suggestion=f"Server details: {msg}. Please ensure Tesseract and traineddata are present."
            )

        try:
            # Basic preprocessing: convert to grayscale (L) or RGB
            if image.mode not in ("L", "RGB"):
                image = image.convert("RGB")
            
            # Execute OCR with timeout (30s)
            custom_config = f"-l {settings.OCR_LANGUAGE} --oem 3 --psm 3"
            extracted_text = pytesseract.image_to_string(
                image, 
                config=custom_config,
                timeout=30
            )
            
            return self._normalize_text(extracted_text)
        except pytesseract.pytesseract.TesseractTimeoutError:
            raise OCRException(
                code="OCR_TIMEOUT",
                message="OCR text extraction timed out.",
                suggestion="The image may be too complex or large. Try a smaller or lower resolution image."
            )
        except Exception as e:
            raise OCRException(
                code="OCR_PROCESSING_FAILED",
                message=f"OCR processing failed: {str(e)}",
                suggestion="Please provide a cleaner scan or supported image."
            )

    def recognize_image_file(self, file_path: str) -> str:
        """
        Opens an image file and runs OCR.
        """
        try:
            with Image.open(file_path) as img:
                return self.recognize_image(img)
        except Exception as e:
            if isinstance(e, OCRException):
                raise
            raise OCRException(
                code="INVALID_IMAGE_FILE",
                message=f"Could not load image: {str(e)}",
                suggestion="Please ensure the uploaded image is a valid PNG or JPEG."
            )

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalizes whitespace while preserving paragraphs.
        """
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines()]
        # Remove excessive empty lines
        cleaned_lines = []
        consecutive_empty = 0
        for line in lines:
            if not line:
                consecutive_empty += 1
                if consecutive_empty <= 1:
                    cleaned_lines.append("")
            else:
                consecutive_empty = 0
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

ocr_service = OCRService()
