import io
from typing import Tuple, List
import fitz  # PyMuPDF
from PIL import Image
from app.config import settings
from app.services.ocr_service import ocr_service, OCRException

class PDFServiceException(Exception):
    def __init__(self, code: str, message: str, suggestion: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion

class PDFService:
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> Tuple[str, str, int, List[str]]:
        """
        Extracts text from PDF bytes.
        Returns: (extracted_text, extraction_method, page_count, warnings)
        extraction_method is either 'pdf_text' or 'pdf_ocr'.
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise PDFServiceException(
                code="INVALID_PDF",
                message=f"Could not open or parse PDF document: {str(e)}",
                suggestion="Please ensure the file is an uncorrupted PDF document."
            )

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            raise PDFServiceException(
                code="EMPTY_PDF",
                message="The PDF file has 0 pages.",
                suggestion="Please provide a valid PDF document with pages."
            )

        warnings: List[str] = []
        pages_to_process = min(page_count, settings.OCR_MAX_PAGES)
        if page_count > settings.OCR_MAX_PAGES:
            warnings.append(
                f"PDF has {page_count} pages; processing was capped to the first {settings.OCR_MAX_PAGES} pages."
            )

        # 1. Attempt direct text extraction first
        direct_text_pages = []
        for i in range(pages_to_process):
            page = doc[i]
            page_text = page.get_text()
            if page_text:
                direct_text_pages.append(page_text.strip())

        total_direct_text = "\n\n".join(direct_text_pages).strip()
        avg_chars = len(total_direct_text) / max(pages_to_process, 1)

        # If usable text exists (average chars per page >= threshold), use direct text
        if avg_chars >= settings.MIN_CHARS_PER_PAGE and len(total_direct_text) > 20:
            doc.close()
            return total_direct_text, "pdf_text", page_count, warnings

        # 2. Scanned or low-text PDF: Fall back to OCR
        warnings.append("Direct text extraction found insufficient text. Switched to OCR fallback.")
        
        # Verify OCR is available before expensive rendering
        ocr_ready, ocr_msg = ocr_service.check_availability()
        if not ocr_ready:
            doc.close()
            raise PDFServiceException(
                code="OCR_FALLBACK_UNAVAILABLE",
                message="PDF contains scanned pages or non-selectable text, and OCR engine is unavailable.",
                suggestion=f"OCR status: {ocr_msg}. Please provide a selectable-text PDF or configure Tesseract."
            )

        ocr_pages_text = []
        dpi = settings.OCR_DPI
        # Matrix for DPI scaling (72 standard dpi in PDF)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for i in range(pages_to_process):
            page = doc[i]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")
            with Image.open(io.BytesIO(img_bytes)) as pil_img:
                try:
                    page_ocr_text = ocr_service.recognize_image(pil_img)
                    if page_ocr_text:
                        ocr_pages_text.append(f"--- Page {i + 1} ---\n{page_ocr_text}")
                except OCRException as e:
                    warnings.append(f"OCR warning on page {i + 1}: {e.message}")

        doc.close()
        combined_ocr_text = "\n\n".join(ocr_pages_text).strip()

        if not combined_ocr_text or len(combined_ocr_text) < 10:
            raise PDFServiceException(
                code="TEXT_EXTRACTION_FAILED",
                message="We could not read text from this document.",
                suggestion="Try a clearer scan or another supported file."
            )

        return combined_ocr_text, "pdf_ocr", page_count, warnings

pdf_service = PDFService()
