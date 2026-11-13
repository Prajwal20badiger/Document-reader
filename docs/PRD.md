# AI Document Simplifier - Product Requirements Document (PRD)

## 1. Executive Summary & Vision
AI Document Simplifier is a web application that helps users comprehend complex information in documents, reports, and scans. Users upload a supported file (PDF, TXT, PNG/JPG), the backend extracts or OCRs the content, sends bounded text to an AI service, and returns structured plain-language explanations, concise summaries, key points, and a glossary of terms.

## 2. Target Users
- Students navigating complex academic or technical material.
- Non-technical professionals reading policies, compliance manuals, or technical reports.
- General users requiring fast clarity on lengthy documents.

## 3. Scope & MVP Boundaries
### In Scope:
- Drag-and-drop & file selection for PDF, PNG/JPEG, and TXT files (up to 15MB).
- Selectable text PDF extraction via PyMuPDF.
- Automatic OCR fallback via Tesseract for scanned/low-text PDFs and images.
- AI simplification returning:
  - Concise plain-language summary
  - Simplified readable version preserving critical facts, numbers, dates, and warnings
  - Actionable key points list
  - Glossary of technical/unfamiliar terms with plain-English definitions
- Real-time processing indicators and granular error feedback.

### Out of Scope (MVP):
- Persistent multi-user authentication and database storage.
- Payment systems or usage limits beyond rate limiting/timeouts.
- Full document authoring, annotation, and editing tools.

## 4. Functional Requirements
- **FR-01**: Document upload (drag-and-drop or picker) supporting PDF, TXT, PNG, JPG, JPEG.
- **FR-02**: File validation (extension, MIME type, size limit <= 15MB, non-empty check).
- **FR-03**: Selectable PDF text extraction via PyMuPDF without running OCR if usable text exists.
- **FR-04**: OCR fallback for scanned PDFs and image files via Tesseract OCR engine.
- **FR-05**: AI simplification producing faithful plain-language content without hallucination.
- **FR-06**: Separate executive summary section.
- **FR-07**: Extracted key points as a structured bulleted list.
- **FR-08**: Difficult terms explained in a structured glossary (term + plain definition).
- **FR-09**: Clean, responsive, accessible UI displaying summary, simplified text, key points, and glossary.
- **FR-10**: Actionable error states (unsupported format, file too large, OCR missing, AI not configured).
- **FR-11**: Extracted source text preserved for comparison and debugging.
- **FR-12**: Plain text (.txt) direct UTF-8 extraction support.

## 5. Non-Functional Requirements
- **Usability**: Responsive, intuitive UI with clear loading status and structured results.
- **Performance**: Bypass OCR when direct text extraction succeeds; cap OCR to max 10 pages.
- **Reliability & Safety**: Clean error boundaries between file extraction, OCR, and AI services.
- **Privacy**: In-memory transient processing; no persistent user document retention.
