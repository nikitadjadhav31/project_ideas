import { useEffect, useState } from "react";
import { api } from "../api";
import type { ApproverRequest, ReplyResult } from "../types";

function ResultStrip({ result }: { result: ReplyResult }) {
  return (
    <div className="result-strip">
      <div className="result-title">Last reply interpreted as</div>
      <div className="result-intent">
        Detected intent: <b>{result.intent}</b> · applied to {result.applied_count} item
        {result.applied_count === 1 ? "" : "s"}, {result.skipped_count} skipped
      </div>
      <div className="result-cols">
        {result.items.map((item, i) => {
          const denied = item.outcome === "not_authorised";
          const label =
            item.outcome === "approved"
              ? "Approved"
              : item.outcome === "rejected"
              ? "Blocked"
              : "Skipped";
          const pill = item.outcome === "approved" ? "provisioned" : item.outcome === "rejected" ? "blocked" : "escalated";
          return (
            <div key={i} className={`result-item ${denied ? "deny" : "ok"}`}>
              <div className="ri-head">
                <span className={`pill ${pill}`}>
                  <span className="dot" />
                  {label}
                </span>{" "}
                {item.tool}
              </div>
              <div className="ri-scope">
                {item.scope} · for {item.hire_name}
              </div>
              <div className="ri-note">{item.note}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ApproverCard({ request }: { request: ApproverRequest }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState<ReplyResult | null>(null);
  const [sending, setSending] = useState(false);

  async function send() {
    if (!text.trim()) return;
    setSending(true);
    try {
      // The reply is applied server-side; the result strip below is the
      // feedback. Dashboard and Audit fetch fresh on navigation, so they
      // reflect the change when you switch to them.
      const res = await api.reply(request.approver_email, text);
      setResult(res);
      setText("");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="approval-card">
      <div className="approval-head">
        <div className="who">
          <div className="who-avatar">{request.initials}</div>
          <div>
            <div className="name">{request.approver_name}</div>
            <div className="email">{request.approver_email}</div>
          </div>
        </div>
        <div className="batch-count">
          {request.items.length} item{request.items.length === 1 ? "" : "s"} batched
        </div>
      </div>

      {request.items.map((item) => (
        <div className="item-row" key={item.id}>
          <div>
            <div className="item-tool">{item.tool}</div>
            <div className="item-scope">{item.scope}</div>
          </div>
          <div className="item-for">
            <span className="lbl">For hire</span>
            {item.hire_name}
          </div>
          <div className="item-flags">
            {item.requires_manual && (
              <span className="tag-manual">
                <span className="dot" />
                Needs manual approval
              </span>
            )}
            {item.step && <span className="step-indicator">{item.step}</span>}
          </div>
          <div className="item-wait">{item.waiting_label}</div>
        </div>
      ))}

      <div className="reply-box">
        <label htmlFor={`reply-${request.approver_email}`}>Reply as approver</label>
        <textarea
          id={`reply-${request.approver_email}`}
          placeholder="e.g. approved for GroundCover"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="actions-right">
          <button className="btn-primary" onClick={send} disabled={sending || !text.trim()}>
            {sending ? "Sending…" : "Send reply"}
          </button>
        </div>
      </div>

      {result && <ResultStrip result={result} />}
    </div>
  );
}

export function Approvals() {
  const [requests, setRequests] = useState<ApproverRequest[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.approvals().then(setRequests).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="panel">
      <h1 className="page-title">Approvals</h1>
      <p className="page-subtitle">Items waiting on you, grouped into one request.</p>
      <hr className="header-divider" />

      {error && <div className="loading">Couldn’t load approvals: {error}</div>}
      {!requests && !error && <div className="loading">Loading…</div>}
      {requests && requests.length === 0 && (
        <div className="empty-note">Nothing waiting on you right now.</div>
      )}

      {requests?.map((req) => (
        <ApproverCard key={req.approver_email} request={req} />
      ))}
    </div>
  );
}
