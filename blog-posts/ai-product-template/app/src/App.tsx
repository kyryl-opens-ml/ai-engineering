import { useState, useEffect } from 'react';
import { Sidebar, type Page } from './components/Sidebar';
import { fetchHealth } from './api';
import './App.css';

interface HealthData {
  status: string;
  version: string;
}

function App() {
  const [activePage, setActivePage] = useState<Page>('home');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = async () => {
    setLoading(true);
    setHealthError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      setHealthError(err instanceof Error ? err.message : 'Failed to connect');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activePage === 'feature-3') {
      checkHealth();
    }
  }, [activePage]);

  return (
    <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar 
        activePage={activePage} 
        onNavigate={setActivePage}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <main className="main-content">
        {activePage === 'home' && (
          <div className="page">
            <h1>Dashboard</h1>
            <p className="page-subtitle">Overview of your application</p>
          </div>
        )}
        {activePage === 'feature-1' && (
          <div className="page">
            <h1>Feature 1</h1>
            <p className="page-subtitle">Feature 1 content goes here</p>
          </div>
        )}
        {activePage === 'feature-2' && (
          <div className="page">
            <h1>Feature 2</h1>
            <p className="page-subtitle">Feature 2 content goes here</p>
          </div>
        )}
        {activePage === 'feature-3' && (
          <div className="page">
            <h1>API Status</h1>
            <p className="page-subtitle">Check API connection and version</p>
            <div className="status-card">
              {loading && <p>Checking...</p>}
              {healthError && (
                <div className="status-error">
                  <span className="status-dot error"></span>
                  <span>Error: {healthError}</span>
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
        )}
        {activePage === 'settings' && (
          <div className="page">
            <h1>Settings</h1>
            <p className="page-subtitle">Manage your account settings</p>
          </div>
        )}
        {activePage === 'billing' && (
          <div className="page">
            <h1>Billing</h1>
            <p className="page-subtitle">Manage your subscription and payments</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
