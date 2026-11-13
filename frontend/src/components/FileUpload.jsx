import React, { useState, useRef } from 'react';
import { UploadCloud, File, X, Sparkles, AlertCircle } from 'lucide-react';

const ALLOWED_EXTS = ['.pdf', '.txt', '.png', '.jpg', '.jpeg'];
const MAX_SIZE_MB = 15;

export default function FileUpload({ onFileSubmit, disabled }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [validationError, setValidationError] = useState('');
  const inputRef = useRef(null);

  const validateFile = (file) => {
    setValidationError('');
    if (!file) return false;

    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      setValidationError(`Unsupported file type '${ext}'. Please upload a PDF, TXT, or Image.`);
      return false;
    }

    if (file.size === 0) {
      setValidationError('The selected file is empty (0 bytes).');
      return false;
    }

    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_SIZE_MB) {
      setValidationError(`File size (${sizeMb.toFixed(1)} MB) exceeds the ${MAX_SIZE_MB}MB limit.`);
      return false;
    }

    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setValidationError('');
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile) {
      onFileSubmit(selectedFile);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="upload-card">
      <form onSubmit={handleSubmit}>
        <div
          className={`dropzone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            style={{ display: 'none' }}
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            onChange={handleChange}
            disabled={disabled}
          />

          <UploadCloud className="dropzone-icon" />
          <h3>Drag and drop your document here</h3>
          <p>or click to browse your local computer</p>

          <div className="file-tags">
            <span className="file-tag">PDF (Direct Text & OCR)</span>
            <span className="file-tag">TXT</span>
            <span className="file-tag">PNG</span>
            <span className="file-tag">JPG / JPEG</span>
            <span className="file-tag">Up to 15MB</span>
          </div>
        </div>

        {validationError && (
          <div style={{ color: '#dc2626', fontSize: '0.88rem', marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle size={16} />
            {validationError}
          </div>
        )}

        {selectedFile && (
          <div className="file-preview">
            <div className="file-info">
              <File size={28} color="#2563eb" />
              <div>
                <div className="file-name">{selectedFile.name}</div>
                <div className="file-size">{formatFileSize(selectedFile.size)}</div>
              </div>
            </div>
            <button
              type="button"
              className="btn-secondary"
              onClick={handleRemove}
              disabled={disabled}
              title="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        )}

        <button
          type="submit"
          className="btn-primary"
          disabled={!selectedFile || disabled}
        >
          <Sparkles size={18} />
          <span>Simplify Document with AI</span>
        </button>
      </form>
    </div>
  );
}
