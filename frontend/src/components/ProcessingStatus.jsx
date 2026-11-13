import React from 'react';
import { Loader2, CheckCircle2, Clock } from 'lucide-react';

export default function ProcessingStatus({ step }) {
  const steps = [
    { id: 1, title: 'Validating & Uploading' },
    { id: 2, title: 'Text Extraction / OCR Fallback' },
    { id: 3, title: 'AI Simplification & Structuring' },
  ];

  return (
    <div className="progress-card">
      <div className="spinner"></div>
      <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.4rem' }}>
        Simplifying your document...
      </h3>
      <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '500px', margin: '0 auto' }}>
        Please wait while we extract text, clarify technical terms, and produce an easy-to-read summary.
      </p>

      <div className="progress-steps">
        {steps.map((s) => {
          const isDone = step > s.id;
          const isCurrent = step === s.id;
          return (
            <div
              key={s.id}
              className={`step-item ${isCurrent ? 'active' : ''}`}
            >
              {isDone ? (
                <CheckCircle2 size={16} color="#10b981" />
              ) : isCurrent ? (
                <Loader2 size={16} className="spin-icon" color="#2563eb" />
              ) : (
                <Clock size={16} color="#94a3b8" />
              )}
              <span>{s.title}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
