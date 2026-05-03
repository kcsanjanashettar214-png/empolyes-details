import React, { useState, useEffect } from 'react';
import { getBlockchainLogs, getThreatLogs, getSecurityEvents, getDashboardStats, getNetworkThreats, getNetworkDataset } from '../services/api';
import '../styles/SecurityDashboard.css';

function SecurityDashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [blockchainLogs, setBlockchainLogs] = useState([]);
  const [threatLogs, setThreatLogs] = useState([]);
  const [securityEvents, setSecurityEvents] = useState([]);
  const [networkEvents, setNetworkEvents] = useState([]);
  const [networkSummary, setNetworkSummary] = useState(null);
  const [datasetRows, setDatasetRows] = useState([]);
  const [datasetSummary, setDatasetSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('threats');

  useEffect(() => {
    loadSecurityData();
    const interval = setInterval(loadSecurityData, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadSecurityData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const [statsRes, bcRes, threatRes, eventRes, networkRes, datasetRes] = await Promise.all([
        getDashboardStats(token),
        getBlockchainLogs(token),
        getThreatLogs(token),
        getSecurityEvents(token),
        getNetworkThreats(token),
        getNetworkDataset(token)
      ]);

      setStats(statsRes.stats);
      setBlockchainLogs(bcRes.blockchain_logs || []);
      setThreatLogs(threatRes.threat_logs || []);
      setSecurityEvents(eventRes.security_events || []);
      setNetworkEvents(networkRes.network_events || []);
      setNetworkSummary(networkRes.summary || null);
      setDatasetRows(datasetRes.dataset_rows || []);
      setDatasetSummary(datasetRes.summary || null);
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
      setError('Failed to load security data: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="security-loading">Loading security dashboard...</div>;
  }

  return (
    <div className="security-page">
      <header className="sec-header">
        <div>
          <h1>Security Dashboard</h1>
          <p>Real-time attack detection, threat analysis, and blockchain audit</p>
        </div>
        <button className="refresh-btn-sec" onClick={loadSecurityData}>
          Refresh
        </button>
      </header>

      {error && <div className="sec-error">{error}</div>}

      {stats && (
        <section className="sec-metrics">
          <div className="sec-metric-card threat-count">
            <span className="metric-num">{stats.total_threats_detected}</span>
            <span className="metric-label">Total Threats</span>
          </div>
          <div className="sec-metric-card alert-count">
            <span className="metric-num">{stats.high_severity_threats}</span>
            <span className="metric-label">High Severity</span>
          </div>
          <div className="sec-metric-card blocked-count">
            <span className="metric-num">{stats.requests_blocked}</span>
            <span className="metric-label">Blocked Requests</span>
          </div>
          <div className="sec-metric-card allowed-count">
            <span className="metric-num">{stats.requests_allowed}</span>
            <span className="metric-label">Allowed Requests</span>
          </div>
          <div className="sec-metric-card blockchain-count">
            <span className="metric-num">{stats.blockchain_blocks}</span>
            <span className="metric-label">Blockchain Blocks</span>
          </div>
          <div className={`sec-metric-card integrity-status ${stats.blockchain_integrity ? 'verified' : 'compromised'}`}>
            <span className="metric-num">
              {stats.blockchain_integrity ? '✓' : '✗'}
            </span>
            <span className="metric-label">
              {stats.blockchain_integrity ? 'Verified' : 'Compromised'}
            </span>
          </div>
        </section>
      )}

      {networkSummary && (
        <section className="sec-network-summary">
          <div className="network-metric-card">
            <span className="metric-num">{networkSummary.total_samples}</span>
            <span className="metric-label">Model Training Rows</span>
          </div>
          <div className="network-metric-card safe-count">
            <span className="metric-num">{networkSummary.benign_predicted}</span>
            <span className="metric-label">Predicted Benign</span>
          </div>
          <div className="network-metric-card malicious-count">
            <span className="metric-num">{networkSummary.malicious_predicted}</span>
            <span className="metric-label">Predicted Malicious</span>
          </div>
        </section>
      )}

      {datasetSummary && datasetRows.length > 0 && (
        <section className="sec-dataset-sample">
          <div className="dataset-panel-header">
            <h2>Dataset Sample</h2>
            <p>CSV dataset loaded from backend and used for model training / threat detection.</p>
          </div>
          <div className="dataset-summary-row">
            <div className="dataset-summary-card">
              <span>Total Rows</span>
              <strong>{datasetSummary.total_rows}</strong>
            </div>
            <div className="dataset-summary-card">
              <span>Sample Malicious</span>
              <strong>{datasetSummary.malicious_sample_count}</strong>
            </div>
            <div className="dataset-summary-card">
              <span>Sample Benign</span>
              <strong>{datasetSummary.benign_sample_count}</strong>
            </div>
          </div>
          <div className="dataset-table">
            <div className="dataset-row dataset-head">
              <div>Time</div>
              <div>Src IP</div>
              <div>Dst IP</div>
              <div>Port</div>
              <div>Protocol</div>
              <div>Label</div>
            </div>
            {datasetRows.slice(0, 8).map((row, idx) => (
              <div key={idx} className="dataset-row">
                <div>{row.timestamp}</div>
                <div>{row.src_ip}</div>
                <div>{row.dst_ip}</div>
                <div>{row.dst_port}</div>
                <div>{row.protocol}</div>
                <div className={`dataset-label ${row.label}`}>
                  {row.label?.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {networkEvents.length > 0 && (
        <section className="sec-network-events">
          <div className="network-panel-header">
            <h2>Network Threat Feed</h2>
            <p>Sample event predictions generated from the backend model and dataset.</p>
          </div>
          <div className="network-table">
            <div className="network-head-row">
              <div>Timestamp</div>
              <div>Source</div>
              <div>Destination</div>
              <div>Port</div>
              <div>Protocol</div>
              <div>Prediction</div>
            </div>
            {networkEvents.map((event, idx) => (
              <div key={idx} className="network-row">
                <div>{event.timestamp}</div>
                <div>{event.src_ip}</div>
                <div>{event.dst_ip}</div>
                <div>{event.dst_port}</div>
                <div>{event.protocol}</div>
                <div className={`prediction-badge ${event.predicted_label === 'MALICIOUS' ? 'malicious' : 'benign'}`}>
                  {event.predicted_label}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="sec-tabs">
        <button 
          className={`sec-tab ${activeTab === 'threats' ? 'active' : ''}`}
          onClick={() => setActiveTab('threats')}
        >
          Attack Logs
        </button>
        <button 
          className={`sec-tab ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          Security Events
        </button>
        <button 
          className={`sec-tab ${activeTab === 'blockchain' ? 'active' : ''}`}
          onClick={() => setActiveTab('blockchain')}
        >
          Blockchain Logs
        </button>
      </div>

      <section className="sec-content">
        {activeTab === 'threats' && (
          <div className="logs-view">
            <div className="logs-table">
              <div className="table-head threat-row">
                <div className="col-type">Type</div>
                <div className="col-message">Message</div>
                <div className="col-user">User</div>
                <div className="col-time">Timestamp</div>
                <div className="col-status">Status</div>
              </div>
              {threatLogs.length === 0 ? (
                <div className="no-logs">No threat logs</div>
              ) : (
                threatLogs.map((threat, idx) => (
                  <div key={idx} className={`table-row threat-row ${threat.severity}`}>
                    <div className="col-type">
                      <span className="type-badge">{threat.type}</span>
                    </div>
                    <div className="col-message">{threat.message}</div>
                    <div className="col-user">{threat.user}</div>
                    <div className="col-time">
                      {new Date(threat.timestamp).toLocaleString()}
                    </div>
                    <div className="col-status">
                      <span className={`status-badge ${threat.blocked ? 'blocked' : 'allowed'}`}>
                        {threat.blocked ? 'BLOCKED' : 'ALLOWED'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="logs-view">
            <div className="logs-table">
              <div className="table-head event-row">
                <div className="col-event">Event Type</div>
                <div className="col-details">Details</div>
                <div className="col-user">User</div>
                <div className="col-time">Timestamp</div>
                <div className="col-status">Status</div>
              </div>
              {securityEvents.length === 0 ? (
                <div className="no-logs">No security events</div>
              ) : (
                securityEvents.map((event, idx) => (
                  <div key={idx} className={`table-row event-row ${event.status}`}>
                    <div className="col-event">{event.event_type}</div>
                    <div className="col-details">{event.details}</div>
                    <div className="col-user">{event.user}</div>
                    <div className="col-time">
                      {new Date(event.timestamp).toLocaleString()}
                    </div>
                    <div className="col-status">
                      <span className={`status-badge ${event.status}`}>
                        {event.status?.toUpperCase() || 'LOGGED'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'blockchain' && (
          <div className="logs-view">
            <div className="logs-table">
              <div className="table-head blockchain-row">
                <div className="col-block">Block #</div>
                <div className="col-hash">Hash</div>
                <div className="col-data">Data</div>
                <div className="col-time">Timestamp</div>
              </div>
              {blockchainLogs.length === 0 ? (
                <div className="no-logs">No blockchain logs</div>
              ) : (
                blockchainLogs.map((block, idx) => (
                  <div key={idx} className="table-row blockchain-row">
                    <div className="col-block">#{block.index}</div>
                    <div className="col-hash">
                      <code>{block.hash.slice(0, 32)}...</code>
                    </div>
                    <div className="col-data">
                      <code>{typeof block.data === 'string' ? block.data : JSON.stringify(block.data).slice(0, 60)}...</code>
                    </div>
                    <div className="col-time">
                      {new Date(block.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default SecurityDashboard;
