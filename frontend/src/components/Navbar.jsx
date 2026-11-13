import React from 'react';
import { FileText, Settings as SettingsIcon, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react';

export default function Navbar({ health, onOpenSettings }) {
  const isHealthy = health?.status === 'healthy';
  const ocrReady = health?.ocr_available;
  const aiReady = health?.ai_configured;

  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <FileText size={20} />
        </div>
        <div>
          <span className="brand-title">AI Document Simplifier</span>
        </div>
        <span className="brand-badge">MVP</span>
      </div>

      <div className="nav-actions">
        <div 
          className={`status-pill ${isHealthy ? 'status-healthy' : 'status-offline'}`}
          title={isHealthy ? 'Backend API connected' : 'Backend API disconnected'}
        >
          {isHealthy ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
          <span>{isHealthy ? 'Backend Connected' : 'Offline'}</span>
        </div>

        {isHealthy && (
          <div 
            className="status-pill" 
            style={{ 
              background: ocrReady ? '#f0fdf4' : '#fff7ed', 
              color: ocrReady ? '#166534' : '#9a3412',
              borderColor: ocrReady ? '#bbf7d0' : '#fed7aa'
            }}
            title={ocrReady ? 'Tesseract OCR engine ready' : 'OCR not available'}
          >
            {ocrReady ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
            <span>{ocrReady ? 'OCR Ready' : 'OCR Disabled'}</span>
          </div>
        )}

        <button 
          className="btn-secondary" 
          onClick={onOpenSettings} 
          title="Configure AI API Key & Model"
        >
          <SettingsIcon size={15} />
          <span>Settings</span>
        </button>
      </div>
    </header>
  );
}
