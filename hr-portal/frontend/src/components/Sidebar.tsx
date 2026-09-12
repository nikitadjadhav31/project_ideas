import { NavLink } from "react-router-dom";

const items = [
  {
    to: "/",
    label: "Dashboard",
    end: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    to: "/intake",
    label: "Intake form",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5M9 13h6M9 17h4" />
      </svg>
    ),
  },
  {
    to: "/approvals",
    label: "Approvals",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12h4l2 3h6l2-3h4" /><path d="M5 5h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z" />
      </svg>
    ),
  },
  {
    to: "/audit",
    label: "Audit log",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8 6h12M8 12h12M8 18h12" /><circle cx="3.5" cy="6" r="1" /><circle cx="3.5" cy="12" r="1" /><circle cx="3.5" cy="18" r="1" />
      </svg>
    ),
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <rect x="5" y="4" width="14" height="17" rx="2.5" />
            <path d="M9 4a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 4v1H9V4z" />
            <path d="M9 11h6M9 15h4" />
          </svg>
        </div>
        <span className="brand-name">HR Portal</span>
      </div>

      <nav className="nav">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="user-card">
        <div className="avatar">SK</div>
        <div>
          <div className="user-name">Suraj Khanna</div>
          <div className="user-role">HR Manager</div>
        </div>
      </div>
    </aside>
  );
}
