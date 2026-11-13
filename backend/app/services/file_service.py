import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from fastapi import UploadFile, HTTPException
from app.config import settings

class FileServiceException(HTTPException):
    def __init__(self, code: str, message: str, suggestion: str = "", status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": code,
                    "message": message,
                    "suggestion": suggestion
                }
            }
        )

class FileService:
    @staticmethod
    def validate_file(file: UploadFile, content: bytes) -> str:
        """
        Validates filename, extension, file size and non-empty content.
        Returns the lowercase extension.
        """
        if not file.filename:
            raise FileServiceException(
                code="INVALID_FILENAME",
                message="File name is missing or invalid.",
                suggestion="Please provide a valid file."
            )
            
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            allowed_str = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
            raise FileServiceException(
                code="UNSUPPORTED_FILE_TYPE",
                message=f"File extension '{ext}' is not supported.",
                suggestion=f"Please upload one of the supported formats: {allowed_str}."
            )

        # Check for empty file
        if len(content) == 0:
            raise FileServiceException(
                code="EMPTY_FILE",
                message="The uploaded file contains no data (0 bytes).",
                suggestion="Please upload a valid document containing readable content."
            )

        # Check file size limit
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise FileServiceException(
                code="FILE_TOO_LARGE",
                message=f"File size exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
                suggestion=f"Please compress your file or upload a document under {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        return ext

    @staticmethod
    def read_text_file(content: bytes) -> str:
        """
        Safely decodes UTF-8 / ASCII / common encodings text file.
        """
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                text = content.decode(encoding)
                text = text.strip()
                if not text:
                    raise FileServiceException(
                        code="EMPTY_TEXT_FILE",
                        message="The text file does not contain any readable text.",
                        suggestion="Please upload a text file with non-empty content."
                    )
                return text
            except UnicodeDecodeError:
                continue

        raise FileServiceException(
            code="TEXT_DECODE_FAILED",
            message="Could not decode text file with supported encodings.",
            suggestion="Please ensure your text file is UTF-8 encoded."
        )

    @staticmethod
    def save_temp_file(content: bytes, suffix: str) -> str:
        """
        Creates a temporary file outside public directories and returns the absolute path.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        return tmp_path

    @staticmethod
    def remove_temp_file(path: str):
        """
        Safely removes a temporary file if it exists.
        """
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
