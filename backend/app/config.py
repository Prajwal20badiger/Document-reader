import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in project root or current directory
root_dir = Path(__file__).resolve().parent.parent.parent
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-2.5-flash")
    
    # OCR settings
    TESSERACT_CMD: str = os.getenv(
        "TESSERACT_CMD", 
        r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else "tesseract"
    )
    TESSDATA_PREFIX: str = os.getenv(
        "TESSDATA_PREFIX",
        str(root_dir / "tessdata")
    )
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
    OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "eng")
    OCR_DPI: int = int(os.getenv("OCR_DPI", "200"))
    OCR_MAX_PAGES: int = int(os.getenv("OCR_MAX_PAGES", "10"))
    
    # Text quality threshold: average minimum chars per page to consider selectable PDF text sufficient
    MIN_CHARS_PER_PAGE: int = int(os.getenv("MIN_CHARS_PER_PAGE", "40"))

    # Allowed extensions
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}
    ALLOWED_MIME_TYPES: set = {
        "application/pdf",
        "text/plain",
        "image/png",
        "image/jpeg",
        "image/jpg",
    }

settings = Settings()
