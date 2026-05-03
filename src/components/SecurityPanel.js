import React from 'react';
import '../styles/SecurityPanel.css';

function SecurityPanel({ securityStatus }) {
  if (!securityStatus) {
    return (
      <div className="card security-panel">
        <h3>🛡️ Security Status</h3>
        <p className="no-data">No query processed yet</p>
      </div>
    );
  }

  const layers = [
    { id: '1_access_control', name: 'Access Control', icon: '👤' },
    { id: '2_api_security', name: 'API Security', icon: '🔐' },
    { id: '2_rate_limiting', name: 'Rate Limiting', icon: '⏱️' },
    { id: '3_input_sanitization', name: 'Input Sanitization', icon: '🧹' },
    { id: '4_threat_detection', name: 'Threat Detection', icon: '⚠️' },
    { id: '5_ai_guard', name: 'AI Guard', icon: '🤖' },
    { id: '6_encryption', name: 'Encryption', icon: '🔒' },
    { id: '7_blockchain_logging', name: 'Blockchain', icon: '🔗' },
  ];

  const layerStatus = securityStatus.layers || {};
  const blockedAt = securityStatus.blocked_at_layer;

  return (
    <div className="card security-panel">
      <h3>🛡️ 7-Layer Security Pipeline</h3>
      
      <div className={`overall-status ${securityStatus.passed ? 'passed' : 'blocked'}`}>
        {securityStatus.passed ? '✅ ALL LAYERS PASSED' : '🚫 BLOCKED'}
      </div>

      <div className="layers-list">
        {layers.map((layer, index) => {
          const layerData = layerStatus[layer.id];
          if (!layerData) return null;

          const isPassed = layerData.passed !== false;
          const isBlocked = blockedAt === index + 1;

          return (
            <div
              key={layer.id}
              className={`layer-item ${isPassed ? 'passed' : 'blocked'} ${isBlocked ? 'blocked-at' : ''}`}
            >
              <div className="layer-header">
                <span className="layer-icon">{layer.icon}</span>
                <span className="layer-name">Layer {index + 1}: {layer.name}</span>
                <span className="layer-status">
                  {isPassed ? '✓' : '✗'}
                </span>
              </div>
              <div className="layer-details">
                {layerData.message && (
                  <p className="layer-message">{layerData.message}</p>
                )}
                {layerData.threat_score !== undefined && (
                  <p className="layer-info">Threat Score: {(layerData.threat_score * 100).toFixed(0)}%</p>
                )}
                {layerData.classification && (
                  <p className="layer-info">Classification: {layerData.classification}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {securityStatus.threat_detected && (
        <div className="threat-warning">
          <strong>⚠️ THREAT DETECTED & BLOCKED</strong>
        </div>
      )}
    </div>
  );
}

export default SecurityPanel;
