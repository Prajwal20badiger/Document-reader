import React, { useState } from 'react';
import {
  FileText,
  ListOrdered,
  BookOpen,
  Copy,
  Check,
  RotateCcw,
  AlertTriangle,
  Eye,
  Search,
  Sparkles
} from 'lucide-react';

export default function ResultsView({ result, onReset }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [copied, setCopied] = useState(false);
  const [showSource, setShowSource] = useState(false);
  const [glossaryFilter, setGlossaryFilter] = useState('');

  if (!result) return null;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getMethodBadge = (method) => {
    switch (method) {
      case 'pdf_text':
        return <span className="method-badge badge-pdf-text">PDF Direct Text</span>;
      case 'pdf_ocr':
        return <span className="method-badge badge-pdf-ocr">Scanned PDF (OCR)</span>;
      case 'image_ocr':
        return <span className="method-badge badge-image-ocr">Image OCR</span>;
      case 'txt':
        return <span className="method-badge badge-txt">Plain Text</span>;
      default:
        return <span className="method-badge badge-pdf-text">{method}</span>;
    }
  };

  const filteredGlossary = (result.glossary || []).filter(item =>
    item.term.toLowerCase().includes(glossaryFilter.toLowerCase()) ||
    item.definition.toLowerCase().includes(glossaryFilter.toLowerCase())
  );

  return (
    <div className="results-container">
      {/* Header */}
      <div className="results-header">
        <div className="doc-meta">
          <FileText size={22} color="#2563eb" />
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: '700' }}>{result.document_name}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '3px' }}>
              {getMethodBadge(result.extraction_method)}
              {result.page_count && (
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  {result.page_count} {result.page_count === 1 ? 'page' : 'pages'}
                </span>
              )}
            </div>
          </div>
        </div>

        <button className="btn-secondary" onClick={onReset}>
          <RotateCcw size={15} />
          <span>New Document</span>
        </button>
      </div>

      {/* Warnings Banner if any */}
      {result.warnings && result.warnings.length > 0 && (
        <div style={{ background: '#fffbeb', borderBottom: '1px solid #fef3c7', padding: '0.75rem 1.75rem', display: 'flex', alignItems: 'center', gap: '8px', color: '#92400e', fontSize: '0.85rem' }}>
          <AlertTriangle size={16} flexShrink={0} />
          <div>
            {result.warnings.map((w, idx) => (
              <span key={idx} style={{ marginRight: '10px' }}>• {w}</span>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          <Sparkles size={16} />
          <span>Overview</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'simplified' ? 'active' : ''}`}
          onClick={() => setActiveTab('simplified')}
        >
          <FileText size={16} />
          <span>Simplified Document</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'key_points' ? 'active' : ''}`}
          onClick={() => setActiveTab('key_points')}
        >
          <ListOrdered size={16} />
          <span>Key Points ({result.key_points?.length || 0})</span>
        </button>

        <button
          className={`tab-btn ${activeTab === 'glossary' ? 'active' : ''}`}
          onClick={() => setActiveTab('glossary')}
        >
          <BookOpen size={16} />
          <span>Glossary ({result.glossary?.length || 0})</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="tab-content">
        {/* TAB 1: Summary Overview */}
        {activeTab === 'summary' && (
          <div>
            <div className="card-box" style={{ background: '#f8fafc', borderColor: '#cbd5e1' }}>
              <div className="card-title">
                <Sparkles size={18} color="#2563eb" /> Executive Summary
              </div>
              <div className="prose" style={{ fontSize: '1.05rem', fontWeight: '500', color: '#1e293b' }}>
                {result.summary}
              </div>
            </div>

            {result.key_points && result.key_points.length > 0 && (
              <div className="card-box">
                <div className="card-title">
                  <ListOrdered size={18} color="#2563eb" /> Key Takeaways
                </div>
                <ul className="points-list">
                  {result.key_points.slice(0, 4).map((point, idx) => (
                    <li key={idx} className="point-item">
                      <span className="point-number">{idx + 1}</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Full Simplified Document */}
        {activeTab === 'simplified' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginBottom: '1rem' }}>
              <button
                className="btn-secondary"
                onClick={() => setShowSource(!showSource)}
              >
                <Eye size={15} />
                <span>{showSource ? 'Hide Extracted Source' : 'Compare Source Text'}</span>
              </button>

              <button
                className="btn-secondary"
                onClick={() => handleCopy(result.simplified_text)}
              >
                {copied ? <Check size={15} color="#16a34a" /> : <Copy size={15} />}
                <span>{copied ? 'Copied!' : 'Copy Text'}</span>
              </button>
            </div>

            {showSource && result.source_text_sample && (
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#64748b', marginBottom: '0.4rem' }}>
                  Extracted Raw Source Text Sample (First 600 characters)
                </div>
                <pre className="source-box">{result.source_text_sample}</pre>
              </div>
            )}

            <div className="card-box">
              <div className="prose">
                {result.simplified_text}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: Key Points */}
        {activeTab === 'key_points' && (
          <div>
            <div className="card-title" style={{ marginBottom: '1rem' }}>
              Essential Points & Constraints
            </div>
            {result.key_points && result.key_points.length > 0 ? (
              <ul className="points-list">
                {result.key_points.map((point, idx) => (
                  <li key={idx} className="point-item">
                    <span className="point-number">{idx + 1}</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ color: '#64748b' }}>No key points extracted.</p>
            )}
          </div>
        )}

        {/* TAB 4: Glossary */}
        {activeTab === 'glossary' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <div className="card-title" style={{ marginBottom: 0 }}>
                Glossary of Difficult Terms
              </div>
              <div style={{ position: 'relative', width: '250px' }}>
                <Search size={15} style={{ position: 'absolute', left: '10px', top: '10px', color: '#94a3b8' }} />
                <input
                  type="text"
                  placeholder="Filter terms..."
                  className="form-input"
                  style={{ paddingLeft: '32px', paddingBottom: '0.4rem', paddingTop: '0.4rem' }}
                  value={glossaryFilter}
                  onChange={(e) => setGlossaryFilter(e.target.value)}
                />
              </div>
            </div>

            {filteredGlossary.length > 0 ? (
              <div className="glossary-grid">
                {filteredGlossary.map((item, idx) => (
                  <div key={idx} className="glossary-item">
                    <div className="glossary-term">{item.term}</div>
                    <div className="glossary-def">{item.definition}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#64748b' }}>
                {result.glossary?.length === 0
                  ? 'No unfamiliar technical terms were detected in this document.'
                  : 'No terms match your search filter.'}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
