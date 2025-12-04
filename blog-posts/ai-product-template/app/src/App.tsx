import { useState } from 'react';
import { Sidebar, type Page } from './components/Sidebar';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState<Page>('home');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
