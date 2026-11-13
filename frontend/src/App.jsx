import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import ResultsView from './components/ResultsView';
import ErrorMessage from './components/ErrorMessage';
import SettingsModal from './components/SettingsModal';
import { checkHealth, analyzeDocument } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Settings
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [apiKey, setApiKey] = useState(
    () => localStorage.getItem('doc_simplifier_api_key') || ''
  );
  const [model, setModel] = useState(
    () => localStorage.getItem('doc_simplifier_model') || 'gemini-2.5-flash'
  );

  useEffect(() => {
    checkHealth().then((data) => setHealth(data));
    const interval = setInterval(() => {
      checkHealth().then((data) => setHealth(data));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSubmit = async (file) => {
    setError(null);
    setResult(null);
    setLoading(true);
    setLoadingStep(1);

    // Simulate step progression for UX
    const t1 = setTimeout(() => setLoadingStep(2), 700);
    const t2 = setTimeout(() => setLoadingStep(3), 1600);

    try {
      const data = await analyzeDocument(file, apiKey, model);
      setResult(data);
    } catch (err) {
      setError({
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || 'An error occurred during analysis.',
        suggestion: err.suggestion || 'Please try again or check server logs.'
      });
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setLoading(false);
  };

  return (
    <div className="app-container">
      <Navbar
        health={health}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      <main className="main-content">
        {!result && (
          <section className="hero">
            <h1>Understand Any Document in Seconds</h1>
            <p>
              Upload dense PDFs, technical reports, scans, or text documents.
              Get plain-language explanations, executive summaries, key points, and definitions.
            </p>
          </section>
        )}

        <ErrorMessage
          error={error}
          onDismiss={() => setError(null)}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />

        {loading && <ProcessingStatus step={loadingStep} />}

        {!loading && !result && (
          <FileUpload
            onFileSubmit={handleFileSubmit}
            disabled={loading}
          />
        )}

        {!loading && result && (
          <ResultsView
            result={result}
            onReset={handleReset}
          />
        )}
      </main>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        apiKey={apiKey}
        setApiKey={setApiKey}
        model={model}
        setModel={setModel}
        health={health}
      />
    </div>
  );
}
