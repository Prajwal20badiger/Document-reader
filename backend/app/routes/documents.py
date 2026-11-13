from typing import Optional
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.document import DocumentAnalyzeResponse
from app.services.file_service import FileService, FileServiceException
from app.services.pdf_service import pdf_service, PDFServiceException
from app.services.ocr_service import ocr_service, OCRException
from app.services.ai_service import ai_service, AIServiceException

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_document(
    file: UploadFile = File(...),
    x_ai_api_key: Optional[str] = Header(None),
    x_ai_model: Optional[str] = Header(None)
):
    temp_path: Optional[str] = None
    try:
        content = await file.read()
        
        # 1. Validate file extension, size and non-empty
        ext = FileService.validate_file(file, content)
        
        extracted_text = ""
        extraction_method = ""
        page_count: Optional[int] = None
        warnings = []

        # 2. Routing based on format
        if ext == ".txt":
            extracted_text = FileService.read_text_file(content)
            extraction_method = "txt"
            page_count = 1
        elif ext in (".png", ".jpg", ".jpeg"):
            temp_path = FileService.save_temp_file(content, suffix=ext)
            extracted_text = ocr_service.recognize_image_file(temp_path)
            extraction_method = "image_ocr"
            page_count = 1
        elif ext == ".pdf":
            extracted_text, extraction_method, page_count, pdf_warnings = (
                pdf_service.extract_text_from_pdf(content)
            )
            warnings.extend(pdf_warnings)
        else:
            raise FileServiceException(
                code="UNSUPPORTED_FORMAT",
                message=f"Unsupported format '{ext}'.",
                suggestion="Please upload a PDF, TXT, or Image (PNG/JPEG)."
            )

        # 3. Check for empty extraction
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "TEXT_EXTRACTION_FAILED",
                        "message": "We could not read text from this document.",
                        "suggestion": "Try a clearer scan or another supported file."
                    }
                }
            )

        # 4. AI Simplification and structuring
        ai_result = await ai_service.analyze_document(
            text=extracted_text,
            document_name=file.filename,
            extraction_method=extraction_method,
            custom_key=x_ai_api_key,
            custom_model=x_ai_model
        )

        # 5. Build response
        return DocumentAnalyzeResponse(
            document_name=file.filename,
            extraction_method=extraction_method,
            summary=ai_result["summary"],
            simplified_text=ai_result["simplified_text"],
            key_points=ai_result["key_points"],
            glossary=ai_result["glossary"],
            source_text_sample=extracted_text[:600] + ("..." if len(extracted_text) > 600 else ""),
            page_count=page_count,
            warnings=warnings
        )

    except FileServiceException as e:
        return JSONResponse(status_code=e.status_code, content=e.detail)
    except PDFServiceException as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "suggestion": e.suggestion
                }
            }
        )
    except OCRException as e:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "suggestion": e.suggestion
                }
            }
        )
    except AIServiceException as e:
        status_code = 503 if e.code in ("AI_UNAVAILABLE", "AI_TIMEOUT", "AI_NETWORK_ERROR") else 400
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "suggestion": e.suggestion
                }
            }
        )
    except HTTPException as e:
        if isinstance(e.detail, dict) and "error" in e.detail:
            return JSONResponse(status_code=e.status_code, content=e.detail)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": "REQUEST_ERROR",
                    "message": str(e.detail),
                    "suggestion": "Please review the request parameters."
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred during document processing.",
                    "suggestion": "Please try again later."
                }
            }
        )
    finally:
        if temp_path:
            FileService.remove_temp_file(temp_path)
