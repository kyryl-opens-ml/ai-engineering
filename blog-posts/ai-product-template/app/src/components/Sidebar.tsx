import { NavLink } from 'react-router-dom';
import { useAuth } from '../auth';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { user, signOut } = useAuth();
  const email = user?.email || '';
  const initial = email.charAt(0).toUpperCase() || '?';

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">{collapsed ? '✦' : '✦ App'}</div>
        <button className="toggle-btn" onClick={onToggle}>
          {collapsed ? '→' : '←'}
        </button>
      </div>
      
      <nav className="sidebar-nav">
        <div className="nav-section">
          <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Home" end>
            <span className="nav-icon">⌂</span>
            {!collapsed && <span>Home</span>}
          </NavLink>
        </div>

        <div className="nav-section">
          {!collapsed && <div className="nav-label">Features</div>}
          <NavLink to="/feature-1" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Feature 1">
            <span className="nav-icon">◈</span>
            {!collapsed && <span>Feature 1</span>}
          </NavLink>
          <NavLink to="/feature-2" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Feature 2">
            <span className="nav-icon">◇</span>
            {!collapsed && <span>Feature 2</span>}
          </NavLink>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="nav-section">
          {!collapsed && <div className="nav-label">Admin</div>}
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
          <div className="user-avatar">{initial}</div>
          {!collapsed && (
            <div className="user-details">
              <div className="user-email">{email}</div>
              <button className="signout-btn" onClick={signOut}>Sign out</button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
