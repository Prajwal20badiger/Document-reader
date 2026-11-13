from fastapi import APIRouter
from app.config import settings
from app.schemas.document import HealthResponse
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    ocr_available, _ = ocr_service.check_availability()
    ai_configured = ai_service.is_configured()

    return HealthResponse(
        status="healthy",
        ocr_available=ocr_available,
        ocr_language=settings.OCR_LANGUAGE,
        ai_configured=ai_configured,
        ai_model=settings.AI_MODEL,
        max_upload_size_mb=settings.MAX_UPLOAD_SIZE_MB,
        allowed_extensions=sorted(list(settings.ALLOWED_EXTENSIONS))
    )
