import React, { useState } from 'react';
import { executeQuery } from '../services/api';
import '../styles/QueryBox.css';

function QueryBox({ user, onResponse }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await executeQuery(query, token);
      onResponse(response, response.security_status);
      setQuery('');
    } catch (err) {
      const errorMessage = err.message || 'Unknown error';
      if (errorMessage.includes('Invalid or expired token') || 
          errorMessage.includes('Unauthorized') || 
          errorMessage.includes('401')) {
        // Token expired, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }
      setError(errorMessage);
      onResponse(
        { success: false, message: errorMessage },
        null
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="query-box">
      <div className="input-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask me anything about your data..."
          disabled={loading}
          className="query-input"
        />
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? (
            <div className="query-loading">
              <div className="mini-gemini">
                <div className="mini-circle mini-circle-1"></div>
                <div className="mini-circle mini-circle-2"></div>
              </div>
              <span>Processing...</span>
            </div>
          ) : (
            '🔍 Query'
          )}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </form>
  );
}

export default QueryBox;
