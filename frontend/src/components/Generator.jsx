import React, { useState } from 'react';
import './Generator.css';

const platforms = [
  { value: 'General', label: 'General' },
  { value: 'Instagram', label: 'Instagram' },
  { value: 'LinkedIn', label: 'LinkedIn' },
  { value: 'YouTube Script', label: 'YouTube Script' },
];

const Generator = ({ onGenerate, isLoading }) => {
  const [formData, setFormData] = useState({
    text: '',
    platform: 'General',
    temperature: 0.7,
    max_tokens: 256,
    use_legacy: false,
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.text.trim()) {
      alert('Please enter your content idea');
      return;
    }
    onGenerate(formData);
  };

  return (
    <div className="generator-container">
      <h2 className="generator-title">Create Your Content</h2>
      
      <form onSubmit={handleSubmit} className="generator-form">
        <div className="form-group">
          <label htmlFor="text">Content Idea / Topic *</label>
          <textarea
            id="text"
            name="text"
            value={formData.text}
            onChange={handleInputChange}
            placeholder="Enter your content idea, topic, or concept..."
            rows={4}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="platform">Platform</label>
            <select
              id="platform"
              name="platform"
              value={formData.platform}
              onChange={handleInputChange}
            >
              {platforms.map(platform => (
                <option key={platform.value} value={platform.value}>
                  {platform.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="max_tokens">Max Tokens</label>
            <input
              type="number"
              id="max_tokens"
              name="max_tokens"
              value={formData.max_tokens}
              onChange={handleInputChange}
              min="50"
              max="1024"
              step="16"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="temperature">
            Temperature: {formData.temperature}
          </label>
          <input
            type="range"
            id="temperature"
            name="temperature"
            value={formData.temperature}
            onChange={handleInputChange}
            min="0"
            max="1"
            step="0.1"
          />
          <div className="temperature-labels">
            <span>Focused</span>
            <span>Creative</span>
          </div>
        </div>

        <div className="form-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="use_legacy"
              checked={formData.use_legacy}
              onChange={handleInputChange}
            />
            <span className="checkbox-custom"></span>
            Use Legacy API
          </label>
        </div>

        <button
          type="submit"
          className="generate-button"
          disabled={isLoading || !formData.text.trim()}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Generating...
            </>
          ) : (
            'Generate Content'
          )}
        </button>
      </form>
    </div>
  );
};

export default Generator;
