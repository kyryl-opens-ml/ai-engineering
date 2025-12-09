import { useState, useEffect, useRef } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { useAuth } from './hooks/useAuth';
import { useWorkspace } from './hooks/useWorkspace';
import { fetchHealth, fetchWorkspaceMembers, addWorkspaceMember, removeWorkspaceMember, visualizePdf } from './api';
import './App.css';

interface HealthData {
  status: string;
  version: string;
}

interface Member {
  id: string;
  user_id: string;
  role: string;
  email: string | null;
}

function Home() {
  const { currentWorkspace } = useWorkspace();
  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="page-subtitle">
        {currentWorkspace ? `Workspace: ${currentWorkspace.name}` : 'Select a workspace'}
      </p>
    </div>
  );
}

function Agent() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [d3Code, setD3Code] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setD3Code(null);
    try {
      const result = await visualizePdf(file);
      setD3Code(result.d3_code);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process PDF');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (d3Code && iframeRef.current) {
      const html = `<!DOCTYPE html>
<html>
<head>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; }
    #container { width: 100%; min-height: 400px; }
  </style>
</head>
<body>
  <div id="container"></div>
  <script>
    const container = document.getElementById('container');
    try {
      ${d3Code}
    } catch (e) {
      container.innerHTML = '<p style="color: red;">Error: ' + e.message + '</p>';
    }
  </script>
</body>
</html>`;
      iframeRef.current.srcdoc = html;
    }
  }, [d3Code]);

  return (
    <div className="page">
      <h1>Agentic feature</h1>
      <p className="page-subtitle">Upload a PDF to generate a D3.js visualization</p>
      <form onSubmit={handleSubmit} className="upload-form">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="file-input"
        />
        <button type="submit" disabled={!file || loading} className="submit-btn">
          {loading ? 'Processing...' : 'Generate Visualization'}
        </button>
      </form>
      {error && <p className="form-error">{error}</p>}
      {d3Code && (
        <div className="visualization-container">
          <iframe
            ref={iframeRef}
            title="D3 Visualization"
            sandbox="allow-scripts"
            className="d3-iframe"
          />
        </div>
      )}
    </div>
  );
}

function Deterministic() {
  return (
    <div className="page">
      <h1>Deterministic feature</h1>
      <p className="page-subtitle">Deterministic feature content goes here</p>
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

function Workspaces() {
  const { workspaces, currentWorkspace, createWorkspace } = useWorkspace();
  const [newName, setNewName] = useState('');
  const [members, setMembers] = useState<Member[]>([]);
  const [newEmail, setNewEmail] = useState('');

  useEffect(() => {
    if (currentWorkspace) {
      fetchWorkspaceMembers(currentWorkspace.id).then(setMembers).catch(() => setMembers([]));
    }
  }, [currentWorkspace]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    await createWorkspace(newName);
    setNewName('');
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace || !newEmail.trim()) return;
    try {
      await addWorkspaceMember(currentWorkspace.id, newEmail);
      setNewEmail('');
      const updated = await fetchWorkspaceMembers(currentWorkspace.id);
      setMembers(updated);
    } catch {
      alert('Failed to add member');
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!currentWorkspace) return;
    await removeWorkspaceMember(currentWorkspace.id, memberId);
    const updated = await fetchWorkspaceMembers(currentWorkspace.id);
    setMembers(updated);
  };

  return (
    <div className="page">
      <h1>Workspaces</h1>
      <p className="page-subtitle">Manage your workspaces</p>

      <div className="section">
        <h2>Your Workspaces</h2>
        <ul className="workspace-list">
          {workspaces.map((ws) => (
            <li key={ws.id} className={ws.id === currentWorkspace?.id ? 'active' : ''}>
              {ws.name} <span className="role-badge">{ws.role}</span>
            </li>
          ))}
        </ul>
        <form onSubmit={handleCreate} className="inline-form">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="New workspace name"
          />
          <button type="submit">Create</button>
        </form>
      </div>

      {currentWorkspace && currentWorkspace.role === 'owner' && (
        <div className="section">
          <h2>Members of {currentWorkspace.name}</h2>
          <ul className="member-list">
            {members.map((m) => (
              <li key={m.id || m.user_id}>
                {m.email || 'Unknown'} <span className="role-badge">{m.role}</span>
                {m.role !== 'owner' && (
                  <button onClick={() => handleRemove(m.id)} className="remove-btn">Remove</button>
                )}
              </li>
            ))}
          </ul>
          <form onSubmit={handleAddMember} className="inline-form">
            <input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="Member email"
            />
            <button type="submit">Add</button>
          </form>
        </div>
      )}
    </div>
  );
}

function Settings() {
  const { user, signOut } = useAuth();
  return (
    <div className="page">
      <h1>Settings</h1>
      <p className="page-subtitle">Manage your account settings</p>
      <div className="section">
        <p>Signed in as: {user?.email}</p>
        <button onClick={signOut} className="submit-btn">Sign Out</button>
      </div>
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
  const { user, loading } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/agent" element={<Agent />} />
          <Route path="/deterministic" element={<Deterministic />} />
          <Route path="/workspaces" element={<Workspaces />} />
          <Route path="/api-status" element={<ApiStatus />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/billing" element={<Billing />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
