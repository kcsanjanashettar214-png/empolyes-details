// API Service
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

const parseResponse = async (response) => {
  const text = await response.text();
  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || data?.error || text || `Request failed (${response.status})`;
    throw new Error(detail);
  }

  return data;
};

const buildAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
});

export const loginUser = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: JSON.stringify({ username, password }),
  });

  return parseResponse(response);
};

export const executeQuery = async (query, token) => {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: buildAuthHeaders(token),
    body: JSON.stringify({ query }),
  });

  return parseResponse(response);
};

export const getBlockchainLogs = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/blockchain-logs`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getThreatLogs = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/threat-logs`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getSecurityEvents = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/security-events`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getManagerSecurityEvents = async (token) => {
  const response = await fetch(`${API_BASE_URL}/manager/security-events`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getManagerDashboardStats = async (token) => {
  const response = await fetch(`${API_BASE_URL}/manager/dashboard-stats`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getPromptEvents = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/prompt-events`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getNetworkThreats = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/network-threats`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getNetworkDataset = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/network-dataset`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};

export const getDashboardStats = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/dashboard-stats`, {
    headers: buildAuthHeaders(token),
  });
  return parseResponse(response);
};
