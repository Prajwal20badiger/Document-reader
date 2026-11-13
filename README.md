# AI Document Simplifier

An end-to-end intelligent document processing web application that takes complex documents (PDFs, Images, Text files), extracts the text (with OCR fallback for scanned pages), and generates a plain-language simplification, executive summary, key takeaways, and a technical glossary using AI.

## Features
- **Intelligent Extraction**: Direct text extraction from PDFs using PyMuPDF; seamless automatic OCR fallback using Tesseract for scanned PDFs and image files (PNG, JPG, JPEG).
- **AI-Powered Simplification**: Retains factual integrity, numbers, dates, and obligations while lowering reading difficulty.
- **Comprehensive Breakdown**:
  - Concise Executive Summary
  - Full Simplified Text
  - Bulleted Key Points
  - Unfamiliar Term Glossary
- **Clean Modern UI**: Drag-and-drop file upload, file validation, real-time loading feedback, and structured result tabs.
- **Robust Error Handling**: Actionable messages for unsupported file formats, oversized files, missing OCR engine, or missing AI credentials.

## Prerequisites
- Node.js (v18+) and npm
- Python (3.10+)
- Tesseract OCR (Optional for text PDFs and TXT, required for images & scanned PDFs)

## Setup & Running

### Backend
```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the backend API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vite development server
npm run dev
```

The frontend will run at `http://localhost:5173` and communicate with the backend at `http://localhost:8000`.
