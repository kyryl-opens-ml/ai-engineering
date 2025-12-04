import { NavLink } from 'react-router-dom';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
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
          <NavLink to="/feature-2" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title="Items">
            <span className="nav-icon">◇</span>
            {!collapsed && <span>Items</span>}
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
          <div className="user-avatar">K</div>
          {!collapsed && (
            <div className="user-details">
              <div className="user-name">Kyryl</div>
              <div className="user-email">kyryl@example.com</div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
