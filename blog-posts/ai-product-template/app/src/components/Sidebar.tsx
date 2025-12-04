type Page = 'home' | 'feature-1' | 'feature-2' | 'feature-3' | 'settings' | 'billing';

interface SidebarProps {
  activePage: Page;
  onNavigate: (page: Page) => void;
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ activePage, onNavigate, collapsed, onToggle }: SidebarProps) {
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
          <button 
            className={`nav-item ${activePage === 'home' ? 'active' : ''}`}
            onClick={() => onNavigate('home')}
            title="Home"
          >
            <span className="nav-icon">⌂</span>
            {!collapsed && <span>Home</span>}
          </button>
        </div>

        <div className="nav-section">
          {!collapsed && <div className="nav-label">Features</div>}
          <button 
            className={`nav-item ${activePage === 'feature-1' ? 'active' : ''}`}
            onClick={() => onNavigate('feature-1')}
            title="Feature 1"
          >
            <span className="nav-icon">◈</span>
            {!collapsed && <span>Feature 1</span>}
          </button>
          <button 
            className={`nav-item ${activePage === 'feature-2' ? 'active' : ''}`}
            onClick={() => onNavigate('feature-2')}
            title="Feature 2"
          >
            <span className="nav-icon">◇</span>
            {!collapsed && <span>Feature 2</span>}
          </button>
        </div>

      </nav>

      <div className="sidebar-footer">
        <div className="nav-section">
          {!collapsed && <div className="nav-label">Admin</div>}
          <button 
            className={`nav-item ${activePage === 'settings' ? 'active' : ''}`}
            onClick={() => onNavigate('settings')}
            title="Settings"
          >
            <span className="nav-icon">⚙</span>
            {!collapsed && <span>Settings</span>}
          </button>
          <button 
            className={`nav-item ${activePage === 'billing' ? 'active' : ''}`}
            onClick={() => onNavigate('billing')}
            title="Billing"
          >
            <span className="nav-icon">⊡</span>
            {!collapsed && <span>Billing</span>}
          </button>
          <button 
            className={`nav-item ${activePage === 'feature-3' ? 'active' : ''}`}
            onClick={() => onNavigate('feature-3')}
            title="API Status"
          >
            <span className="nav-icon">↔</span>
            {!collapsed && <span>API Status</span>}
          </button>
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

export type { Page };

