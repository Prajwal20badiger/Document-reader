from pydantic import BaseModel, Field
from typing import List, Optional

class GlossaryItem(BaseModel):
    term: str = Field(..., description="The technical or complex term identified")
    definition: str = Field(..., description="Plain-language definition of the term")

class DocumentAnalyzeResponse(BaseModel):
    document_name: str
    extraction_method: str = Field(..., description="e.g. 'pdf_text', 'pdf_ocr', 'image_ocr', 'txt'")
    summary: str = Field(..., description="A concise plain-language summary")
    simplified_text: str = Field(..., description="Full text rewritten in simple, clear language")
    key_points: List[str] = Field(default_factory=list, description="List of key points/takeaways")
    glossary: List[GlossaryItem] = Field(default_factory=list, description="Glossary of difficult terms")
    source_text_sample: Optional[str] = Field(None, description="Preserved sample of original extracted text")
    page_count: Optional[int] = Field(None, description="Number of pages processed")
    warnings: List[str] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str
    ocr_available: bool
    ocr_language: str
    ai_configured: bool
    ai_model: str
    max_upload_size_mb: int
    allowed_extensions: List[str]
