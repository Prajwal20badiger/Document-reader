import io
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
import pymupdf as fitz

from app.main import app
from app.services.ai_service import ai_service, AIServiceException
from app.config import settings

client = TestClient(app)

def create_sample_pdf(text: str) -> bytes:
    """Helper to create a PDF with selectable text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_scanned_pdf(image_text: str) -> bytes:
    """Helper to create a PDF containing an image (scanned page simulation)."""
    # Create an image containing text
    img = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((30, 100), image_text, fill="black")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    doc = fitz.open()
    page = doc.new_page(width=600, height=300)
    rect = fitz.Rect(0, 0, 600, 300)
    page.insert_image(rect, stream=img_bytes)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_sample_image(text: str) -> bytes:
    """Helper to create an image file."""
    img = Image.new("RGB", (500, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_t02_valid_text_pdf():
    """T-02: Selectable text PDF extracted directly without OCR."""
    pdf_content = create_sample_pdf(
        "Quarterly Financial Report. Revenue reached 10 million dollars in Q3. Operating expenses were well controlled."
    )
    
    mock_ai_response = {
        "summary": "Revenue hit 10 million in Q3 with controlled expenses.",
        "simplified_text": "This report states that company revenue grew to $10M in the third quarter.",
        "key_points": ["Revenue reached $10 million", "Expenses stayed under control"],
        "glossary": [{"term": "Operating expenses", "definition": "Ongoing costs for running the business."}]
    }

    with patch.object(ai_service, "analyze_document", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_response
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("report.pdf", pdf_content, "application/pdf")},
            headers={"x-ai-api-key": "mock-test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_method"] == "pdf_text"
        assert data["summary"] == mock_ai_response["summary"]
        assert len(data["key_points"]) == 2
        assert len(data["glossary"]) == 1


def test_t03_scanned_pdf():
    """T-03: Scanned PDF invokes OCR fallback."""
    scanned_pdf_content = create_scanned_pdf("Notice of Lease Renewal: Tenant must notify landlord 30 days prior.")
    
    mock_ai_response = {
        "summary": "Lease renewal rules.",
        "simplified_text": "You must tell your landlord 30 days before renewing.",
        "key_points": ["Notify landlord 30 days prior"],
        "glossary": []
    }

    with patch.object(ai_service, "analyze_document", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_response
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("scanned_notice.pdf", scanned_pdf_content, "application/pdf")},
            headers={"x-ai-api-key": "mock-test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_method"] == "pdf_ocr"
        assert "OCR fallback" in str(data["warnings"])


def test_t04_image_upload():
    """T-04: Image upload is processed by Tesseract OCR."""
    img_bytes = create_sample_image("Patient must avoid driving for 24 hours after sedation.")
    
    mock_ai_response = {
        "summary": "Medical post-care instructions.",
        "simplified_text": "Do not drive for 24 hours after receiving medicine.",
        "key_points": ["No driving for 24 hours"],
        "glossary": [{"term": "Sedation", "definition": "Medicine to help you relax or sleep."}]
    }

    with patch.object(ai_service, "analyze_document", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_response
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("prescription.png", img_bytes, "image/png")},
            headers={"x-ai-api-key": "mock-test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_method"] == "image_ocr"


def test_t05_txt_upload():
    """T-05: TXT upload directly extracts UTF-8 text."""
    txt_content = (
        "Project Architecture Blueprint.\nAll backend services communicate through typed REST interfaces.\n"
        "Data persistence is not required for the initial prototype."
    ).encode("utf-8")

    mock_ai_response = {
        "summary": "Architectural guidelines for the prototype.",
        "simplified_text": "The system uses REST APIs without database storage.",
        "key_points": ["REST APIs used", "No database storage in prototype"],
        "glossary": [{"term": "REST", "definition": "A standard way for web programs to talk to each other."}]
    }

    with patch.object(ai_service, "analyze_document", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_response
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("architecture.txt", txt_content, "text/plain")},
            headers={"x-ai-api-key": "mock-test-key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_method"] == "txt"
        assert data["summary"] == mock_ai_response["summary"]


def test_t06_unsupported_extension():
    """T-06: Unsupported extension rejected with clear message."""
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("spreadsheet.xlsx", b"some binary data", "application/vnd.ms-excel")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert "xlsx" in data["error"]["message"]


def test_t07_oversized_file():
    """T-07: Oversized file rejected before expensive processing."""
    # Temporarily set max upload to 1MB for test
    orig_max = settings.MAX_UPLOAD_SIZE_MB
    try:
        settings.MAX_UPLOAD_SIZE_MB = 1
        large_bytes = b"0" * (2 * 1024 * 1024)  # 2MB
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("oversized.pdf", large_bytes, "application/pdf")}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"
    finally:
        settings.MAX_UPLOAD_SIZE_MB = orig_max


def test_t08_empty_unreadable_document():
    """T-08: Empty document results in clear extraction failure without calling AI."""
    response = client.post(
        "/api/documents/analyze",
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMPTY_FILE"


def test_t09_ai_success():
    """T-09: AI success returns structured summary, simplified text, key points and glossary."""
    raw_ai_json = (
        '{"summary": "A brief overview.", '
        '"simplified_text": "The contract explains employee rights.", '
        '"key_points": ["Employees get 20 vacation days", "Notice period is 30 days"], '
        '"glossary": [{"term": "Indemnity", "definition": "Protection against loss."}]}'
    )

    parsed = ai_service._parse_and_validate_json(raw_ai_json)
    assert parsed["summary"] == "A brief overview."
    assert len(parsed["key_points"]) == 2
    assert len(parsed["glossary"]) == 1
    assert parsed["glossary"][0]["term"] == "Indemnity"


def test_t10_ai_unavailable():
    """T-10: When AI credentials are not configured, an actionable error is returned; no fake results."""
    # Ensure AI_API_KEY is unset
    orig_key = settings.AI_API_KEY
    try:
        settings.AI_API_KEY = ""
        txt_content = b"Some valid document text to process."
        response = client.post(
            "/api/documents/analyze",
            files={"file": ("doc.txt", txt_content, "text/plain")}
        )
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "AI_UNAVAILABLE"
        assert "credentials" in data["error"]["message"].lower()
    finally:
        settings.AI_API_KEY = orig_key


def test_t11_malformed_ai_json():
    """T-11: Malformed AI JSON response is caught by schema validation."""
    malformed_json_str = "This is not JSON text at all!"
    with pytest.raises(AIServiceException) as exc_info:
        ai_service._parse_and_validate_json(malformed_json_str)
    assert exc_info.value.code == "AI_MALFORMED_JSON"

    # Missing required keys
    incomplete_json_str = '{"summary": "test"}'
    with pytest.raises(AIServiceException) as exc_info:
        ai_service._parse_and_validate_json(incomplete_json_str)
    assert exc_info.value.code == "AI_INVALID_SCHEMA"
