import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboardStats, getSecurityEvents } from '../services/api';
import '../styles/AdminDashboard.css';

function AdminDashboard({ user }) {
  const [stats, setStats] = useState({
    totalUsers: 0,
    promptRequests: 0,
    dummyQueries: 0,
    avgTrustScore: 0,
    systemHealth: 100,
    threatsDetected: 0,
    requestsAllowed: 0,
  });
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    loadData(token);
    const interval = setInterval(() => loadData(token), 15000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async (token) => {
    try {
      const [statsRes, eventsRes] = await Promise.all([
        getDashboardStats(token),
        getSecurityEvents(token),
      ]);

      const s = statsRes.stats || statsRes;
      const events = eventsRes.security_events || eventsRes;

      setStats({
        totalUsers: 128,
        promptRequests: s.prompt_requests || 0,
        dummyQueries: s.dummy_queries || 0,
        avgTrustScore: s.avg_trust_score || 0,
        systemHealth: Math.max(0, 100 - (s.high_severity_threats || 0) * 2),
        threatsDetected: s.total_threats_detected || 0,
        requestsAllowed: s.requests_allowed || 0,
      });

      setRecentEvents(events.slice(0, 8));
    } catch (err) {
      const errorMessage = err.message || 'Unknown error';
      if (errorMessage.includes('Invalid or expired token') || 
          errorMessage.includes('Unauthorized') || 
          errorMessage.includes('401')) {
        // Token expired, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
        return;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-dashboard-page">
      <header className="admin-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>System Overview & Operations Control</p>
        </div>
        <div className="header-actions">
          <button className="nav-btn" onClick={() => navigate('/security')}>
            Security Dashboard
          </button>
          <button className="nav-btn" onClick={() => navigate('/prompt')}>
            Prompt Lab
          </button>
        </div>
      </header>

      {error && <div className="error-alert">{error}</div>}

      <section className="kpi-section">
        <div className="kpi-card kpi-primary">
          <div className="kpi-icon">👥</div>
          <div className="kpi-content">
            <p className="kpi-label">Total Users</p>
            <h2>{stats.totalUsers}</h2>
            <span className="kpi-change">+ 8 this week</span>
          </div>
        </div>

        <div className="kpi-card kpi-secondary">
          <div className="kpi-icon">💬</div>
          <div className="kpi-content">
            <p className="kpi-label">Prompt Requests</p>
            <h2>{stats.promptRequests}</h2>
            <span className="kpi-change">+ {Math.floor(stats.promptRequests * 0.05)} today</span>
          </div>
        </div>

        <div className="kpi-card kpi-warning">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-content">
            <p className="kpi-label">Dummy Queries</p>
            <h2>{stats.dummyQueries}</h2>
            <span className="kpi-change">Flagged by model</span>
          </div>
        </div>

        <div className="kpi-card kpi-success">
          <div className="kpi-icon">📈</div>
          <div className="kpi-content">
            <p className="kpi-label">Avg Trust</p>
            <h2>{stats.avgTrustScore}%</h2>
            <span className="kpi-change">Higher is safer</span>
          </div>
        </div>

        <div className={`kpi-card ${stats.systemHealth > 80 ? 'kpi-success' : 'kpi-danger'}`}>
          <div className="kpi-icon">💡</div>
          <div className="kpi-content">
            <p className="kpi-label">System Health</p>
            <h2>{stats.systemHealth}%</h2>
            <div className="health-bar">
              <div className="health-fill" style={{ width: `${stats.systemHealth}%` }}></div>
            </div>
          </div>
        </div>
      </section>

      <div className="admin-grid">
        <section className="admin-panel">
          <div className="panel-header">
            <h2>?? Recent Security Events</h2>
            <button className="view-all-btn" onClick={() => navigate('/security')}>
              View All ?
            </button>
          </div>

          {loading ? (
            <div className="panel-loading">Loading events...</div>
          ) : recentEvents.length === 0 ? (
            <div className="panel-empty">No recent events</div>
          ) : (
            <div className="events-list">
              {recentEvents.map((event, idx) => (
                <div key={idx} className="event-item">
                  <div className="event-icon">
                    {event.status === 'blocked' ? '?' : '?'}
                  </div>
                  <div className="event-content">
                    <p className="event-title">{event.event_type}</p>
                    <p className="event-user">User: {event.user}</p>
                    {event.meta?.trust_score !== undefined && (
                      <p className="event-meta">
                        Trust: {event.meta.trust_score}% • {event.meta.real_or_dummy}
                      </p>
                    )}
                    {event.meta?.src_ip && (
                      <p className="event-meta">IP: {event.meta.src_ip} • {event.meta.location}</p>
                    )}
                  </div>
                  <div className={`event-badge ${event.status}`}>
                    {event.status?.toUpperCase() || 'LOGGED'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="admin-panel quick-summary">
          <div className="panel-header">
            <h2>??? Security Summary</h2>
          </div>

          <div className="summary-stats">
            <div className="summary-stat">
              <span className="stat-label">Threats Today</span>
              <span className="stat-value threat">{stats.threatsDetected}</span>
            </div>
            <div className="summary-stat">
              <span className="stat-label">Requests Allowed</span>
              <span className="stat-value safe">{stats.requestsAllowed}</span>
            </div>
          </div>

          <div className="security-layers">
            <h3>Active Security Layers</h3>
            <ul className="layers-list">
              <li className="layer-item active">
                <span className="dot"></span>
                <span>Input Sanitization</span>
              </li>
              <li className="layer-item active">
                <span className="dot"></span>
                <span>Threat Detection</span>
              </li>
              <li className="layer-item active">
                <span className="dot"></span>
                <span>AI Guard (RBAC)</span>
              </li>
              <li className="layer-item active">
                <span className="dot"></span>
                <span>Encryption (Fernet)</span>
              </li>
              <li className="layer-item active">
                <span className="dot"></span>
                <span>Blockchain Audit</span>
              </li>
            </ul>
          </div>

          <div className="quick-actions">
            <button className="action-btn" onClick={() => navigate('/security')}>
              Deep Dive Security ?
            </button>
          </div>
        </section>
      </div>

      <section className="user-management">
        <div className="panel-header">
          <h2>?? User Management</h2>
          <button className="action-btn-small">+ Add User</button>
        </div>

        <div className="users-table">
          <div className="table-header">
            <div className="col-name">Name</div>
            <div className="col-role">Role</div>
            <div className="col-status">Status</div>
            <div className="col-actions">Actions</div>
          </div>

          {[
            { name: 'John Doe', role: 'admin', status: 'active' },
            { name: 'Sarah Smith', role: 'manager', status: 'active' },
            { name: 'Mike Johnson', role: 'employee', status: 'active' },
            { name: 'Lisa Chen', role: 'employee', status: 'inactive' },
            { name: 'Alex Kumar', role: 'manager', status: 'active' },
          ].map((u, idx) => (
            <div key={idx} className="table-row">
              <div className="col-name">{u.name}</div>
              <div className="col-role">
                <span className={`role-badge ${u.role}`}>{u.role}</span>
              </div>
              <div className="col-status">
                <span className={`status-badge ${u.status}`}>
                  {u.status}
                </span>
              </div>
              <div className="col-actions">
                <button className="row-action">Edit</button>
                <button className="row-action">Disable</button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default AdminDashboard;
