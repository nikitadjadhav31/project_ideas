import { useEffect, useState } from "react";
import { api } from "../api";
import type { AuditEvent } from "../types";
import { AgentTag } from "../components/ui";

function formatTs(iso: string): string {
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  const date = d.toLocaleDateString("en-GB", { month: "short", day: "numeric" });
  const time = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  return `${date} · ${time}`;
}

export function AuditLog() {
  const [events, setEvents] = useState<AuditEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.audit().then(setEvents).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="panel">
      <h1 className="page-title">Audit log</h1>
      <p className="page-subtitle">Every request, nudge, approval and refusal.</p>
      <hr className="header-divider" />

      {error && <div className="loading">Couldn’t load audit log: {error}</div>}
      {!events && !error && <div className="loading">Loading…</div>}

      {events && (
        <table className="audit-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id} className={e.refused ? "refused" : ""}>
                <td className="ts">{formatTs(e.timestamp)}</td>
                <td className="actor">
                  {e.actor} {e.is_agent && <AgentTag />}
                </td>
                <td className="action">{e.action}</td>
                <td>{e.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
