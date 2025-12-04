import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { fetchHealth } from './api';
import './App.css';

interface HealthData {
  status: string;
  version: string;
}

function Home() {
  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="page-subtitle">Overview of your application</p>
    </div>
  );
}

function Feature1() {
  return (
    <div className="page">
      <h1>Feature 1</h1>
      <p className="page-subtitle">Feature 1 content goes here</p>
    </div>
  );
}

function Feature2() {
  return (
    <div className="page">
      <h1>Feature 2</h1>
      <p className="page-subtitle">Feature 2 content goes here</p>
    </div>
  );
}

function ApiStatus() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="page">
      <h1>API Status</h1>
      <p className="page-subtitle">Check API connection and version</p>
      <div className="status-card">
        {loading && <p>Checking...</p>}
        {error && (
          <div className="status-error">
            <span className="status-dot error"></span>
            <span>Error: {error}</span>
          </div>
        )}
        {health && (
          <div className="status-ok">
            <div className="status-row">
              <span className="status-dot ok"></span>
              <span>Status: {health.status}</span>
            </div>
            <div className="status-row">
              <span>Version: {health.version}</span>
            </div>
            <div className="status-row">
              <span className="status-muted">API: {import.meta.env.VITE_API_URL}</span>
            </div>
          </div>
        )}
        <button className="refresh-btn" onClick={checkHealth} disabled={loading}>
          Refresh
        </button>
      </div>
    </div>
  );
}

function Settings() {
  return (
    <div className="page">
      <h1>Settings</h1>
      <p className="page-subtitle">Manage your account settings</p>
    </div>
  );
}

function Billing() {
  return (
    <div className="page">
      <h1>Billing</h1>
      <p className="page-subtitle">Manage your subscription and payments</p>
    </div>
  );
}

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar 
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/feature-1" element={<Feature1 />} />
          <Route path="/feature-2" element={<Feature2 />} />
          <Route path="/api-status" element={<ApiStatus />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/billing" element={<Billing />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
