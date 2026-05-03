import React from 'react';
import '../styles/Loading.css';

const Loading = () => {
  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="loading-logo">
          <div className="gemini-icon">
            <div className="gemini-circle gemini-circle-1"></div>
            <div className="gemini-circle gemini-circle-2"></div>
            <div className="gemini-circle gemini-circle-3"></div>
          </div>
          <h1 className="team-name">Team Gemini</h1>
        </div>

        <div className="loading-animation">
          <div className="loading-bar">
            <div className="loading-progress"></div>
          </div>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div className="loading-text">
          <p>Initializing Secure Enterprise Dashboard</p>
          <p className="loading-subtitle">7-Layer Security Architecture</p>
        </div>
      </div>
    </div>
  );
};

export default Loading;