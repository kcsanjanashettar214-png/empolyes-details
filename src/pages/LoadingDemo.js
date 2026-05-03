import React, { useState } from 'react';
import QueryBox from '../components/QueryBox';
import SecurityPanel from '../components/SecurityPanel';

function LoadingDemo() {
  const [response, setResponse] = useState(null);
  const [securityStatus, setSecurityStatus] = useState(null);

  const handleResponse = (resp, status) => {
    setResponse(resp);
    setSecurityStatus(status);
  };

  const user = { username: 'demo', role: 'admin' };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Team Gemini Loading Animation Demo</h1>

      <div style={{ marginBottom: '2rem' }}>
        <h2>Query Loading Animation</h2>
        <p>Click "Query" to see the mini Team Gemini loading animation in the button:</p>
        <QueryBox user={user} onResponse={handleResponse} />
      </div>

      {response && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Response:</h3>
          <pre style={{
            background: '#f5f5f5',
            padding: '1rem',
            borderRadius: '5px',
            overflow: 'auto'
          }}>
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}

      {securityStatus && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Security Status:</h3>
          <SecurityPanel securityStatus={securityStatus} />
        </div>
      )}
    </div>
  );
}

export default LoadingDemo;