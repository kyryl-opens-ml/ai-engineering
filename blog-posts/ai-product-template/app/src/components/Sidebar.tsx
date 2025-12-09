import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useWorkspace } from '../hooks/useWorkspace';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { user } = useAuth();
  const { workspaces, currentWorkspace, setCurrentWorkspace } = useWorkspace();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">{collapsed ? '✦' : '✦ App'}</div>
        <button className="toggle-btn" onClick={onToggle}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {!collapsed && (
        <div className="workspace-dropdown">
          <button className="dropdown-trigger" onClick={() => setDropdownOpen(!dropdownOpen)}>
            <span>{currentWorkspace?.name || 'Select Workspace'}</span>
            <span className="dropdown-arrow">{dropdownOpen ? '▲' : '▼'}</span>
          </button>
          {dropdownOpen && (
            <div className="dropdown-menu">
              {workspaces.map((ws) => (
                <button
                  key={ws.id}
                  className={`dropdown-item ${ws.id === currentWorkspace?.id ? 'active' : ''}`}
                  onClick={() => {
                    setCurrentWorkspace(ws);
                    setDropdownOpen(false);
                  }}
                >
                  {ws.name}
                </button>
              ))}
              <NavLink to="/workspaces" className="dropdown-item view-all" onClick={() => setDropdownOpen(false)}>
                View all →
              </NavLink>
            </div>
          )}
        </div>
      )}

      <nav className="sidebar-nav">
        <div className="nav-section">
          <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Home" end>
            <span className="nav-icon">⌂</span>
            {!collapsed && <span>Home</span>}
          </NavLink>
        </div>

        <div className="nav-section">
          {!collapsed && <div className="nav-label">Features</div>}
          <NavLink to="/agent" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Agentic feature">
            <span className="nav-icon">◈</span>
            {!collapsed && <span>Agentic feature</span>}
          </NavLink>
          <NavLink to="/deterministic" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Deterministic feature">
            <span className="nav-icon">◇</span>
            {!collapsed && <span>Deterministic feature</span>}
          </NavLink>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="nav-section">
          {!collapsed && <div className="nav-label">Admin</div>}
          <NavLink to="/workspaces" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Workspaces">
            <span className="nav-icon">⊞</span>
            {!collapsed && <span>Workspaces</span>}
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Settings">
            <span className="nav-icon">⚙</span>
            {!collapsed && <span>Settings</span>}
          </NavLink>
          <NavLink to="/billing" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Billing">
            <span className="nav-icon">⊡</span>
            {!collapsed && <span>Billing</span>}
          </NavLink>
          <NavLink to="/api-status" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="API Status">
            <span className="nav-icon">↔</span>
            {!collapsed && <span>API Status</span>}
          </NavLink>
        </div>
        <div className="user-info">
          <div className="user-avatar">{user?.email?.[0]?.toUpperCase() || 'U'}</div>
          {!collapsed && (
            <div className="user-details">
              <div className="user-name">{user?.email?.split('@')[0] || 'User'}</div>
              <div className="user-email">{user?.email}</div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
