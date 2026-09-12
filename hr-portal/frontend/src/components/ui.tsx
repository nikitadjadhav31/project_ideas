import type { Status } from "../types";

const STATUS_LABEL: Record<Status, string> = {
  pending: "Pending",
  awaiting_approval: "Awaiting approval",
  escalated: "Escalated",
  provisioned: "Provisioned",
  blocked: "Blocked",
};

export function StatusPill({ status }: { status: Status }) {
  return (
    <span className={`pill ${status}`}>
      <span className="dot" />
      {STATUS_LABEL[status]}
    </span>
  );
}

export function AgentTag() {
  return (
    <span className="tag-agent">
      <span className="dot" />
      agent
    </span>
  );
}
