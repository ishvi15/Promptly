import React from 'react';
import './Output.css';

const Output = ({ result, isLoading }) => {
  if (isLoading) {
    return (
      <div className="output-container">
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Analyzing your content idea and generating platform-optimized content...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="output-container">
        <div className="empty-state">
          <div className="empty-icon">✨</div>
          <h3>Ready to Create Amazing Content</h3>
          <p>Fill in your content idea and click generate to see AI-powered, platform-optimized content tailored to your needs.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="output-container">
      <div className="output-header">
        <h2 className="output-title">Generated Content</h2>
        <div className="output-meta">
          {result.fallback_used && (
            <span className="fallback-badge">
              <span className="fallback-icon">⚠️</span>
              Fallback Used
            </span>
          )}
          <span className="time-badge">Generated in {result.time_taken}s</span>
        </div>
      </div>

      <div className="output-content">
        <div className="content-section">
          <h3>Your Content</h3>
          <div className="content-box">
            <pre>{result.content}</pre>
          </div>
        </div>

        <div className="metadata-grid">
          <div className="metadata-item">
            <label>Intent</label>
            <span className="intent-badge">{result.intent}</span>
          </div>
          
          <div className="metadata-item">
            <label>Sentiment</label>
            <span className={`sentiment-badge sentiment-${result.sentiment}`}>
              {result.sentiment}
            </span>
          </div>
        </div>

        {result.documents && result.documents.length > 0 && (
          <div className="documents-section">
            <h3>Source Insights Used</h3>
            <div className="documents-list">
              {result.documents.map((doc, index) => (
                <div key={index} className="document-item">
                  <span className="document-number">{index + 1}</span>
                  <p>{doc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {result.reason && (
          <div className="reason-section">
            <h3>Note</h3>
            <div className="reason-box">
              <p>{result.reason}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Output;
