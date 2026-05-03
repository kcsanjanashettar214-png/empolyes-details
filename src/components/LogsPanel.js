import React from 'react';

function LogsPanel({ logs, title, type }) {
  return (
    <div className="card logs-panel">
      <h3>{title}</h3>
      {logs && logs.length > 0 ? (
        <div className="logs-list">
          {logs.map((log, idx) => (
            <div key={idx} className={`log-entry ${type}`}>
              <div className="log-time">
                {new Date(log.timestamp).toLocaleTimeString()}
              </div>
              <div className="log-content">
                {typeof log.message === 'string' ? log.message : JSON.stringify(log)}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No logs available</p>
      )}
    </div>
  );
}

export default LogsPanel;
