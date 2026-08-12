import { NavLink, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <NavLink to="/" className="sidebar-logo">
            <div className="sidebar-logo-icon">C</div>
            <span className="sidebar-logo-text">CourseSync</span>
          </NavLink>
        </div>
        <nav className="sidebar-nav">
          <NavLink
            to="/dashboard"
            end
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
            Dashboard
          </NavLink>
          <NavLink
            to="/add"
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
            Add Course
          </NavLink>
        </nav>
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
            CourseSync v0.1 MVP
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
