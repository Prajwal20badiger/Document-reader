import React, { useState } from 'react';
import { X, Key, Cpu, Info, Check, Zap, ExternalLink } from 'lucide-react';

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
    }, 700);
  };

  const handleSelectDemo = () => {
    setLocalKey('demo');
    setApiKey('demo');
    localStorage.setItem('doc_simplifier_api_key', 'demo');
    setSavedAlert(true);
    setTimeout(() => {
      setSavedAlert(false);
      onClose();
    }, 700);
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

        {/* Quick Demo Mode Banner */}
        <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.85rem', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontWeight: '700', fontSize: '0.9rem', color: '#1e40af', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Zap size={15} /> Don't have an API key?
              </div>
              <div style={{ fontSize: '0.78rem', color: '#3b82f6' }}>
                Use Offline Demo Mode to test summarization, key points & glossary instantly.
              </div>
            </div>
            <button
              type="button"
              className="btn-secondary"
              style={{ background: '#2563eb', color: 'white', borderColor: '#1d4ed8', fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}
              onClick={handleSelectDemo}
            >
              Enable Demo Mode
            </button>
          </div>
        </div>

        <form onSubmit={handleSave}>
          <div className="form-group">
            <label className="form-label">
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <Key size={14} /> AI API Key (Gemini or OpenAI)
              </span>
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter Gemini API key (or 'demo')"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
            />
            <p className="form-help">
              Get a free API key at{' '}
              <a 
                href="https://aistudio.google.com/app/apikey" 
                target="_blank" 
                rel="noreferrer" 
                style={{ color: '#2563eb', textDecoration: 'underline' }}
              >
                Google AI Studio <ExternalLink size={11} style={{ verticalAlign: 'middle' }} />
              </a>{' '}
              or set <code>AI_API_KEY</code> in backend <code>.env</code>.
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
              Default: <code>gemini-2.5-flash</code> (also supports <code>gemini-1.5-flash</code>, <code>gpt-4o-mini</code>)
            </p>
          </div>

          <div className="form-group" style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '600', marginBottom: '4px' }}>
              <Info size={14} color="#3b82f6" /> System Capabilities
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
              <div>OCR Engine: <strong style={{ color: health?.ocr_available ? '#16a34a' : '#dc2626' }}>{health?.ocr_available ? 'Available (Tesseract)' : 'Unavailable'}</strong></div>
              <div>Current AI Mode: <strong>{localKey === 'demo' ? 'Offline Demo Mode' : (localKey ? 'Client API Key' : 'Not configured')}</strong></div>
              <div>Max File Limit: <strong>{health?.max_upload_size_mb || 15} MB</strong></div>
            </div>
          </div>

          {savedAlert && (
            <div style={{ color: '#16a34a', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Check size={16} /> Configuration saved!
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
