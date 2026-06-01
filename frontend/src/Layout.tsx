import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/", label: "Élő", end: true },
  { to: "/settings", label: "Beállítások" },
  { to: "/history", label: "Előzmények" },
];

export default function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">◆</span>
          <div>
            <strong>Bitunix</strong>
            <span>Trading Platform</span>
          </div>
        </div>
        <nav className="nav">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
      <style>{`
        .shell { display: flex; min-height: 100vh; }
        .sidebar {
          width: 220px;
          background: var(--bg-elevated);
          border-right: 1px solid var(--border);
          padding: 1.5rem 1rem;
          flex-shrink: 0;
        }
        .brand {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 2rem;
          padding: 0 0.5rem;
        }
        .brand-icon {
          color: var(--accent);
          font-size: 1.25rem;
        }
        .brand strong { display: block; font-size: 0.95rem; }
        .brand span { font-size: 0.7rem; color: var(--text-muted); }
        .nav { display: flex; flex-direction: column; gap: 0.25rem; }
        .nav-link {
          padding: 0.65rem 0.85rem;
          border-radius: 8px;
          color: var(--text-muted);
          font-weight: 500;
          font-size: 0.9rem;
        }
        .nav-link:hover { color: var(--text); background: rgba(255,255,255,0.03); }
        .nav-link.active {
          color: var(--accent);
          background: rgba(61, 255, 168, 0.08);
        }
        .main {
          flex: 1;
          padding: 1.75rem 2rem;
          overflow: auto;
          max-width: 1100px;
        }
        @media (max-width: 768px) {
          .shell { flex-direction: column; }
          .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--border); }
          .nav { flex-direction: row; flex-wrap: wrap; }
        }
      `}</style>
    </div>
  );
}
