import React, { useState } from 'react';
import { X, Key, Cpu, Info, Check } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  apiKey,
  setApiKey,
  model,
  setModel,
  health
}) {
  const [localKey, setLocalKey] = useState(apiKey);
  const [localModel, setLocalModel] = useState(model);
  const [savedAlert, setSavedAlert] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    setApiKey(localKey);
    setModel(localModel);
    localStorage.setItem('doc_simplifier_api_key', localKey);
    localStorage.setItem('doc_simplifier_model', localModel);
    setSavedAlert(true);
    setTimeout(() => {
      setSavedAlert(false);
      onClose();
    }, 800);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700' }}>AI Configuration</h2>
          <button 
            className="btn-secondary" 
            style={{ padding: '4px 8px', border: 'none' }} 
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSave}>
          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <Key size={14} /> AI API Key
              </span>
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="Paste Google Gemini or OpenAI API Key"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
            />
            <p className="form-help">
              You can set `AI_API_KEY` in the backend `.env` file or provide your key here. Keys are stored locally in your browser.
            </p>
          </div>

          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <Cpu size={14} /> Model Name
              </span>
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="gemini-2.5-flash"
              value={localModel}
              onChange={(e) => setLocalModel(e.target.value)}
            />
            <p className="form-help">
              Examples: <code>gemini-2.5-flash</code>, <code>gemini-1.5-flash</code>, <code>gpt-4o-mini</code>
            </p>
          </div>

          <div className="form-group" style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '600', marginBottom: '4px' }}>
              <Info size={14} color="#3b82f6" /> Backend Environment Info
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
              <div>Max file size: <strong>{health?.max_upload_size_mb || 15} MB</strong></div>
              <div>OCR Language: <strong>{health?.ocr_language || 'eng'}</strong></div>
              <div>OCR Engine: <strong>{health?.ocr_available ? 'Available (Tesseract)' : 'Unavailable'}</strong></div>
              <div>Server AI configured: <strong>{health?.ai_configured ? 'Yes (via .env)' : 'No (client key used)'}</strong></div>
            </div>
          </div>

          {savedAlert && (
            <div style={{ color: '#16a34a', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Check size={16} /> Settings saved successfully!
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" style={{ width: 'auto', marginTop: 0 }}>
              Save Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
