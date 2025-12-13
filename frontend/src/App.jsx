import React, { useState } from 'react';
import Generator from './components/Generator';
import Output from './components/Output';
import { generateContent } from './services/api';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await generateContent(formData);
      setResult(response);
    } catch (err) {
      setError(err.message);
      console.error('Generation failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <span className="logo-icon">✨</span>
              <h1 className="logo-text">Promptly</h1>
            </div>
            <p className="tagline">AI-Powered Content Generation Platform</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
              <button onClick={handleReset} className="error-dismiss">×</button>
            </div>
          )}

          <div className="app-grid">
            <div className="input-section">
              <Generator onGenerate={handleGenerate} isLoading={isLoading} />
            </div>
            <div className="output-section">
              <Output result={result} isLoading={isLoading} />
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>Built with React + FastAPI | Powered by HuggingFace Models</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
