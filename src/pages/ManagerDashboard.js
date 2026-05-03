import React, { useState, useEffect } from 'react';
import QueryBox from '../components/QueryBox';
import SecurityPanel from '../components/SecurityPanel';
import { getManagerDashboardStats, getManagerSecurityEvents } from '../services/api';
import '../styles/ManagerDashboard.css';

function ManagerDashboard({ user }) {
  const [lastResponse, setLastResponse] = useState(null);
  const [securityStatus, setSecurityStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [suspiciousQueries, setSuspiciousQueries] = useState([]);

  useEffect(() => {
    loadDepartmentData();
    const interval = setInterval(loadDepartmentData, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadDepartmentData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [statsRes, eventsRes] = await Promise.all([
        getManagerDashboardStats(token),
        getManagerSecurityEvents(token)
      ]);

      setStats(statsRes.stats);
      
      const suspicious = (eventsRes.security_events || [])
        .slice(0, 5);
      setSuspiciousQueries(suspicious);
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
      console.log('Failed to load department data', errorMessage);
    }
  };

  const handleQueryResponse = (response, security) => {
    setLastResponse(response);
    setSecurityStatus(security);
  };

  return (
    <div className="mgr-dashboard">
      <div className="mgr-header">
        <h1>👔 Manager Dashboard</h1>
        <p>Welcome, {user?.username} - {user?.department} Manager</p>
        <div className="scope-badge">
          <span className="scope-label">Department Scope:</span>
          <span className="scope-value">{user?.department}</span>
        </div>
      </div>

      {stats && (
        <section className="dept-analytics">
          <h3>📊 Department Analytics</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <span className="metric-num">{stats.system_health || 95}%</span>
              <span className="metric-label">Dept Health</span>
            </div>
            <div className="analytics-card">
              <span className="metric-num">{stats.ai_requests || 142}</span>
              <span className="metric-label">Total Queries</span>
            </div>
            <div className="analytics-card">
              <span className="metric-num">{stats.requests_allowed || 138}</span>
              <span className="metric-label">Allowed</span>
            </div>
            <div className="analytics-card alert">
              <span className="metric-num">{stats.requests_blocked || 4}</span>
              <span className="metric-label">Blocked</span>
            </div>
          </div>
        </section>
      )}

      <div className="mgr-content">
        <div className="mgr-main">
          <div className="card">
            <h2>Department Query Assistant</h2>
            <p className="info-text">
              Access department performance metrics, team analytics, and reports. 
              Your queries are scoped to {user?.department} data only.
            </p>
            <QueryBox user={user} onResponse={handleQueryResponse} />
          </div>

          {lastResponse && (
            <div className={`card response-card ${lastResponse.success ? 'success' : 'blocked'}`}>
              <h3>{lastResponse.success ? '✅ Response' : '🚫 Blocked'}</h3>
              <div className="response-content">
                {lastResponse.success ? (
                  <div>
                    <p className="response-text">{lastResponse.response}</p>
                  </div>
                ) : (
                  <div className="blocked-response">
                    <strong>⚠️ {lastResponse.message}</strong>
                    <p className="reason">This query is outside your department scope or contains restricted data.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="mgr-sidebar">
          <SecurityPanel securityStatus={securityStatus} />

          {suspiciousQueries.length > 0 && (
            <div className="card flagged-queries">
              <h3>🚨 Flagged Activity</h3>
              <div className="flagged-list">
                {suspiciousQueries.map((q, idx) => (
                  <div key={idx} className="flagged-item">
                    <span className="flag-icon">⚠️</span>
                    <div className="flag-details">
                      <p className="flag-type">{q.event_type}</p>
                      <p className="flag-user">User: {q.user}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <h3>📝 Query Examples</h3>
            <div className="query-suggestions">
              <p><strong>Department Scope:</strong></p>
              <ul>
                <li>"Show {user?.department} performance"</li>
                <li>"Team attendance report"</li>
                <li>"Department metrics"</li>
                <li>"Team member overview"</li>
              </ul>
            </div>
          </div>

          <div className="card security-reminder">
            <h4>🔐 Access Scope</h4>
            <p>You can only query data within your department ({user?.department}). Cross-departmental and sensitive company data will be blocked.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ManagerDashboard;
