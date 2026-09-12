import type { Dashboard, ApproverRequest, ReplyResult, AuditEvent, Hire } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/api/dashboard"),
  approvals: () => request<ApproverRequest[]>("/api/approvals"),
  audit: () => request<AuditEvent[]>("/api/audit"),
  reply: (approver_email: string, text: string) =>
    request<ReplyResult>("/api/approvals/reply", {
      method: "POST",
      body: JSON.stringify({ approver_email, text }),
    }),
  createHire: (name: string, department: string, start_label: string) =>
    request<Hire>("/api/hires", {
      method: "POST",
      body: JSON.stringify({ name, department, start_label }),
    }),
};
