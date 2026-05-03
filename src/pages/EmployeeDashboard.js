import React, { useState } from 'react';
import QueryBox from '../components/QueryBox';
import SecurityPanel from '../components/SecurityPanel';
import '../styles/EmployeeDashboard.css';

function EmployeeDashboard({ user }) {
  const [lastResponse, setLastResponse] = useState(null);
  const [securityStatus, setSecurityStatus] = useState(null);

  const handleQueryResponse = (response, security) => {
    setLastResponse(response);
    setSecurityStatus(security);
  };

  return (
    <div className="emp-dashboard">
      <div className="emp-header">
        <h1>👤 Employee Dashboard</h1>
        <p>Welcome, {user?.username} ({user?.department})</p>
        <div className="access-level-badge">
          <span className="access-label">Access Level:</span>
          <span className="access-value">EMPLOYEE (LIMITED)</span>
        </div>
      </div>

      <div className="emp-content">
        <div className="emp-main">
          <div className="access-notice">
            <div className="notice-header">
              🔒 <strong>Data Access Restrictions</strong>
            </div>
            <div className="access-info">
              <div className="allowed-section">
                <h4>✅ You CAN Access:</h4>
                <ul>
                  <li>📍 Your attendance records</li>
                  <li>👤 Your profile information</li>
                  <li>📊 Your department information</li>
                  <li>📅 Your leave balance</li>
                  <li>🏆 Your performance metrics</li>
                </ul>
              </div>
              <div className="blocked-section">
                <h4>❌ You CANNOT Access:</h4>
                <ul>
                  <li>💰 Salary data (yours or others')</li>
                  <li>🏢 Company financial data</li>
                  <li>👥 Other employees' personal records</li>
                  <li>📋 Confidential documents</li>
                  <li>🔑 System administration data</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Secure Query Assistant</h2>
            <p className="info-text">
              Ask about your personal data, attendance, and department information. 
              Any queries for restricted data will be automatically blocked.
            </p>
            <QueryBox user={user} onResponse={handleQueryResponse} />
          </div>

          {lastResponse && (
            <div className={`card response-card ${lastResponse.success ? 'success' : 'blocked'}`}>
              <h3>{lastResponse.success ? '✅ Response' : '🚫 Access Blocked'}</h3>
              <div className="response-content">
                {lastResponse.success ? (
                  <div>
                    <p className="response-text">{lastResponse.response}</p>
                  </div>
                ) : (
                  <div className="blocked-response">
                    <strong>⚠️ {lastResponse.message}</strong>
                    <p className="reason">This query contains restricted data that you do not have access to.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="emp-sidebar">
          <SecurityPanel securityStatus={securityStatus} />

          <div className="card">
            <h3>📝 Example Queries</h3>
            <div className="query-suggestions">
              <p><strong>Allowed:</strong></p>
              <ul>
                <li>"Show my attendance"</li>
                <li>"What is my profile"</li>
                <li>"My department info"</li>
              </ul>
              <p style={{marginTop: '12px'}}><strong>Will be Blocked:</strong></p>
              <ul>
                <li>"Show my salary"</li>
                <li>"List all employee salaries"</li>
                <li>"Company budget data"</li>
              </ul>
            </div>
          </div>

          <div className="card security-reminder">
            <h4>🛡️ Security Reminder</h4>
            <p>All your queries are logged and monitored. Do not attempt to bypass access restrictions.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmployeeDashboard;
