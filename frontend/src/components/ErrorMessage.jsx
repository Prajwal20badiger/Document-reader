import React from 'react';
import { AlertCircle, X, Settings, Zap } from 'lucide-react';

export default function ErrorMessage({ error, onDismiss, onOpenSettings, onUseDemoMode }) {
  if (!error) return null;

  const isAuthError = error.code === 'AI_UNAVAILABLE' || error.code === 'AI_AUTH_FAILED';

  return (
    <div className="error-banner">
      <AlertCircle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1 }}>
        <div className="error-title">
          <span>Processing Notice</span>
          {error.code && <span className="error-code">{error.code}</span>}
        </div>
        <div className="error-msg">{error.message || 'An unexpected error occurred.'}</div>
        {error.suggestion && (
          <div className="error-suggestion">
            <span style={{ fontWeight: '600' }}>Option:</span> {error.suggestion}
          </div>
        )}

        {isAuthError && (
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.85rem', flexWrap: 'wrap' }}>
            {onOpenSettings && (
              <button
                type="button"
                className="btn-secondary"
                style={{ borderColor: '#f87171', color: '#991b1b' }}
                onClick={onOpenSettings}
              >
                <Settings size={14} />
                <span>Configure AI API Key</span>
              </button>
            )}

            {onUseDemoMode && (
              <button
                type="button"
                className="btn-secondary"
                style={{ borderColor: '#2563eb', color: '#1d4ed8', background: '#eff6ff', fontWeight: '600' }}
                onClick={onUseDemoMode}
              >
                <Zap size={14} color="#2563eb" />
                <span>Switch to Offline Demo Mode (No Key Needed)</span>
              </button>
            )}
          </div>
        )}
      </div>

      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{ background: 'none', border: 'none', color: '#991b1b', cursor: 'pointer', padding: '4px' }}
          title="Dismiss"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}
