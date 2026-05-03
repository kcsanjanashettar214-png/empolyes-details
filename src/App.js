import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Loading from './components/Loading';
import Login from './pages/Login';
import EmployeeDashboard from './pages/EmployeeDashboard';
import ManagerDashboard from './pages/ManagerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import SecurityDashboard from './pages/SecurityDashboard';
import PromptDashboard from './pages/PromptDashboard';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setIsLoggedIn(true);
      setUser(JSON.parse(storedUser));
    }

    // Add a small delay to show the loading animation
    setTimeout(() => {
      setLoading(false);
    }, 3000);
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsLoggedIn(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <Router>
      <div className="App">
        {isLoggedIn && (
          <nav className="navbar">
            <div className="navbar-brand">
              🔐 CipherAI Protection System
            </div>
            <div className="navbar-menu">
              <a href="/" className="nav-item">
                Dashboard
              </a>
              {user?.role === 'admin' && (
                <a href="/security" className="nav-item">
                  Security
                </a>
              )}
              <a href="/prompt" className="nav-item">
                AI Chat
              </a>
            </div>
            <div className="navbar-user">
              <span>{user?.username}</span>
              <span className="role-badge">{user?.role.toUpperCase()}</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </nav>
        )}
        
        <Routes>
          <Route path="/login" element={
            isLoggedIn ? <Navigate to="/" /> : <Login onLogin={handleLogin} />
          } />
          
          <Route path="/" element={
            isLoggedIn ? (
              user?.role === 'employee' ? <EmployeeDashboard user={user} /> :
              user?.role === 'manager' ? <ManagerDashboard user={user} /> :
              user?.role === 'admin' ? <AdminDashboard user={user} /> :
              <Navigate to="/login" />
            ) : <Navigate to="/login" />
          } />
          
          <Route path="/security" element={
            isLoggedIn && user?.role === 'admin' ? <SecurityDashboard user={user} /> : <Navigate to="/login" />
          } />

          <Route path="/prompt" element={
            isLoggedIn ? <PromptDashboard user={user} /> : <Navigate to="/login" />
          } />
          
          <Route path="*" element={<Navigate to={isLoggedIn ? "/" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
