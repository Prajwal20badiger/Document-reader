# AI Document Simplifier - System Architecture

## 1. High-Level Architecture

The system uses a decoupled architecture featuring:
1. **Frontend**: React + Vite single page application with modern UI components, real-time loading feedback, and multi-tab results view.
2. **Backend**: FastAPI REST service providing structured validation, modular service orchestration, and predictable JSON error contracts.
3. **Extraction Services**:
   - `file_service`: Enforces extension, MIME type, size limit checks, and temporary safe handling.
   - `pdf_service`: Inspects PDF using PyMuPDF (fitz), extracts text directly if text quality threshold is met, or renders page pixmaps for OCR fallback.
   - `ocr_service`: Manages Tesseract OCR integration, executable and language data detection, image preprocessing, and page bounding.
   - `ai_service`: Formulates structured prompts, interacts with LLM API (supporting Gemini / OpenAI-compatible or local AI), enforces output JSON schemas, and handles configuration errors.

```
+-------------------------------------------------------------+
|                      React + Vite UI                        |
|  - Drag & Drop Upload                                       |
|  - Live Processing Indicator                                |
|  - Results: Summary | Simplified | Key Points | Glossary     |
+------------------------------+------------------------------+
                               |
                        HTTP Multipart
                               v
+-------------------------------------------------------------+
|                       FastAPI API                           |
|  - GET /health                                              |
|  - POST /api/documents/analyze                              |
+------------------------------+------------------------------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
+-----------------+   +-----------------+   +-----------------+
|  File & TXT Svc |   | PDF & OCR Svc   |   |   AI Service    |
| - Validation    |   | - PyMuPDF       |   | - Gemini / LLM  |
| - Safe temp     |   | - Tesseract OCR |   | - Schema check  |
+-----------------+   +-----------------+   +-----------------+
```

## 2. API Contract Specification

### `GET /health`
Returns configuration status and dependency health without exposing credentials.
```json
{
  "status": "healthy",
  "ocr_available": true,
  "ai_configured": true,
  "max_upload_size_mb": 15
}
```

### `POST /api/documents/analyze`
Accepts `multipart/form-data` with `file: UploadFile`.

#### Success Response (`200 OK`)
```json
{
  "document_name": "quarterly-report.pdf",
  "extraction_method": "pdf_text",
  "summary": "Plain-language summary of the document...",
  "simplified_text": "Detailed simplified text preserving factual constraints...",
  "key_points": [
    "Key finding or takeaway 1",
    "Key finding or takeaway 2"
  ],
  "glossary": [
    {
      "term": "EBITDA",
      "definition": "Earnings before interest, taxes, depreciation, and amortization—a measure of core operating profit."
    }
  ],
  "source_text_sample": "First 500 chars of extracted text...",
  "warnings": []
}
```

#### Error Response (`4xx / 5xx`)
```json
{
  "error": {
    "code": "OCR_DEPENDENCY_MISSING",
    "message": "Tesseract OCR binary or language data is unavailable on the server.",
    "suggestion": "Please provide selectable-text PDFs or configure Tesseract."
  }
}
```

## 3. Decision Pipeline for Text Extraction
```
Upload Document
      |
Validate Format & Size
      |
Format Check:
  - TXT   --> Read UTF-8 string directly
  - Image --> Send directly to Tesseract OCR
  - PDF   --> Direct text extraction with PyMuPDF
                |
                +-> Usable characters >= threshold (50 chars/page average) -> Return text
                +-> Low/No text (scanned) -> Render pages (max 10, 200 DPI) -> Tesseract OCR
```
