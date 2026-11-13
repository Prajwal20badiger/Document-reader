import React from 'react';
import { AlertCircle, X, HelpCircle, Settings } from 'lucide-react';

export default function ErrorMessage({ error, onDismiss, onOpenSettings }) {
  if (!error) return null;

  const isAuthError = error.code === 'AI_UNAVAILABLE' || error.code === 'AI_AUTH_FAILED';

  return (
    <div className="error-banner">
      <AlertCircle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1 }}>
        <div className="error-title">
          <span>Processing Error</span>
          {error.code && <span className="error-code">{error.code}</span>}
        </div>
        <div className="error-msg">{error.message || 'An unexpected error occurred.'}</div>
        {error.suggestion && (
          <div className="error-suggestion">
            <span style={{ fontWeight: '600' }}>Suggestion:</span> {error.suggestion}
          </div>
        )}

        {isAuthError && onOpenSettings && (
          <button
            type="button"
            className="btn-secondary"
            style={{ marginTop: '0.75rem', borderColor: '#f87171', color: '#991b1b' }}
            onClick={onOpenSettings}
          >
            <Settings size={14} />
            <span>Open AI Settings to configure API Key</span>
          </button>
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
