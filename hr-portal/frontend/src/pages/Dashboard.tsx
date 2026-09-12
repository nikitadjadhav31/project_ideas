import { useEffect, useState } from "react";
import { api } from "../api";
import type { Dashboard as DashboardData, Hire } from "../types";
import { StatusPill } from "../components/ui";

function HireCard({ hire }: { hire: Hire }) {
  return (
    <div className="hire-card">
      <div className="hire-head">
        <div>
          <div className="hire-name">{hire.name}</div>
          <div className="hire-meta">
            {hire.department} · Starts {hire.start_label}
          </div>
        </div>
        <div className="readiness">
          <div className="readiness-top">
            <span>Readiness</span>
            <b>{hire.readiness}%</b>
          </div>
          <div className="bar">
            <span style={{ width: `${hire.readiness}%` }} />
          </div>
        </div>
      </div>

      {hire.tasks.length > 0 && (
        <table className="task-table">
          <thead>
            <tr>
              <th>Tool</th>
              <th>Scope</th>
              <th>Approver</th>
              <th>Status</th>
              <th>Last nudge</th>
            </tr>
          </thead>
          <tbody>
            {hire.tasks.map((t) => (
              <tr key={t.id}>
                <td className="tool">{t.tool}</td>
                <td>{t.scope}</td>
                <td className={t.approver_name ? "" : "dim"}>{t.approver_name ?? "—"}</td>
                <td>
                  <StatusPill status={t.status} />
                </td>
                <td className={t.last_nudge === "—" ? "dim" : ""}>{t.last_nudge}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="panel">
      <h1 className="page-title">Onboarding dashboard</h1>
      <p className="page-subtitle">Access provisioning status across active hires.</p>
      <hr className="header-divider" />

      {error && <div className="loading">Couldn’t load dashboard: {error}</div>}
      {!data && !error && <div className="loading">Loading…</div>}

      {data && (
        <>
          <div className="stat-row">
            <div className="stat-card">
              <div className="stat-label">Active hires</div>
              <div className="stat-value">{data.stats.active_hires}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Tasks awaiting approval</div>
              <div className="stat-value warn">{data.stats.awaiting_approval}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Escalated</div>
              <div className="stat-value danger">{data.stats.escalated}</div>
            </div>
          </div>

          {data.hires.map((hire) => (
            <HireCard key={hire.id} hire={hire} />
          ))}
        </>
      )}
    </div>
  );
}
