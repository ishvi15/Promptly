import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // 60 seconds for model generation
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Generate content using the Promptly API
 * @param {Object} payload - Generation parameters
 * @param {string} payload.text - User's content idea
 * @param {string} payload.platform - Target platform
 * @param {number} payload.temperature - Generation temperature
 * @param {number} payload.max_tokens - Maximum tokens to generate
 * @param {boolean} payload.use_legacy - Use legacy API endpoint
 * @returns {Promise<Object>} Generated content and metadata
 */
export async function generateContent(payload) {
  try {
    const response = await api.post('/generate', payload);
    return response.data;
  } catch (error) {
    console.error('Content generation failed:', error);
    
    // Provide more detailed error information
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.data?.message || error.response.statusText}`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network Error: Unable to connect to server. Please check if backend is running.');
    } else {
      // Something else happened
      throw new Error(`Request Error: ${error.message}`);
    }
  }
}

/**
 * Check if the backend API is healthy
 * @returns {Promise<boolean>} Health status
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}
