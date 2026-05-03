import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';
import '../styles/Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await loginUser(username, password);
      onLogin(response.access_token, response.user);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (role) => {
    const credentials = {
      employee: { username: 'employee', password: 'employee123' },
      manager: { username: 'manager', password: 'manager123' },
      admin: { username: 'admin', password: 'admin123' }
    };
    const cred = credentials[role];
    setUsername(cred.username);
    setPassword(cred.password);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>🔐 Secure Enterprise Dashboard</h1>
          <p>7-Layer Security Architecture</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="login-btn">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="demo-section">
          <p>Demo Credentials:</p>
          <div className="demo-buttons">
            <button onClick={() => fillCredentials('employee')} className="demo-btn employee">
              👤 Employee
            </button>
            <button onClick={() => fillCredentials('manager')} className="demo-btn manager">
              👔 Manager
            </button>
            <button onClick={() => fillCredentials('admin')} className="demo-btn admin">
              👨‍💼 Admin
            </button>
          </div>
        </div>

        <div className="security-info">
          <h3>Security Features:</h3>
          <ul>
            <li>✓ 7-Layer Security Pipeline</li>
            <li>✓ Role-Based Access Control</li>
            <li>✓ Real-Time Threat Detection</li>
            <li>✓ End-to-End Encryption</li>
            <li>✓ Blockchain Audit Logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Login;
