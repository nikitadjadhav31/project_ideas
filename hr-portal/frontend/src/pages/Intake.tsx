import { useState } from "react";
import { api } from "../api";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function Intake() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [role, setRole] = useState("");
  const [manager, setManager] = useState("Priya Nair");
  const [startDate, setStartDate] = useState("");
  const [sending, setSending] = useState(false);
  const [confirmed, setConfirmed] = useState<string | null>(null);

  const canSubmit = name.trim() && department && startDate && !sending;

  async function submit() {
    if (!canSubmit) return;
    setSending(true);
    setConfirmed(null);
    try {
      const startLabel = startDate ? WEEKDAYS[new Date(startDate).getDay()] : "TBD";
      const hire = await api.createHire(name.trim(), department, startLabel);
      setConfirmed(`Hire confirmed and sent — ${hire.name} added.`);
      setName("");
      setEmail("");
      setDepartment("");
      setRole("");
      setStartDate("");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="panel">
      <h1 className="page-title">New Hire Intake</h1>
      <p className="page-subtitle">Confirm a new hire and generate their hire ID.</p>
      <hr className="header-divider" />

      <div className="section">
        <div>
          <p className="section-label">Candidate</p>
          <p className="section-desc">Who is joining, and where to reach them today.</p>
        </div>
        <div>
          <div className="field">
            <label htmlFor="cand-name">Candidate name</label>
            <input id="cand-name" type="text" placeholder="e.g. Jane Doe" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="cand-email">
              Candidate’s personal email <span className="hint">(official email isn’t provisioned yet)</span>
            </label>
            <input id="cand-email" type="text" placeholder="jane@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
        </div>
      </div>

      <div className="section">
        <div>
          <p className="section-label">Assignment</p>
          <p className="section-desc">Team, role and the manager who owns onboarding.</p>
        </div>
        <div>
          <div className="field">
            <label htmlFor="dept">Department</label>
            <select id="dept" value={department} onChange={(e) => setDepartment(e.target.value)}>
              <option value="">Select department</option>
              <option>Engineering</option>
              <option>Product</option>
              <option>Design</option>
              <option>Sales</option>
              <option>Operations</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="role">Role</label>
            <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="">Select role</option>
              <option>Software Engineer</option>
              <option>Product Manager</option>
              <option>Designer</option>
              <option>Account Executive</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="mgr">Manager</label>
            <select id="mgr" value={manager} onChange={(e) => setManager(e.target.value)}>
              <option>Priya Nair</option>
              <option>Rohan Desai</option>
              <option>Kavya Rao</option>
            </select>
          </div>
        </div>
      </div>

      <div className="section">
        <div>
          <p className="section-label">Timing</p>
          <p className="section-desc">Day one must be in the future.</p>
        </div>
        <div>
          <div className="field">
            <label htmlFor="start">Start date</label>
            <input id="start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
        </div>
      </div>

      <div className="actions-right">
        {confirmed && <span className="sent-note">{confirmed}</span>}
        <button className="btn-primary" onClick={submit} disabled={!canSubmit}>
          {sending ? "Confirming…" : "Confirm hire"}
        </button>
      </div>
    </div>
  );
}
