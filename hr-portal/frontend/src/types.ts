// API contract — mirrors the FastAPI Pydantic schemas.

export type Status =
  | "pending"
  | "awaiting_approval"
  | "escalated"
  | "provisioned"
  | "blocked";

export interface Task {
  id: number;
  tool: string;
  scope: string;
  approver_name: string | null;
  approver_email: string | null;
  status: Status;
  nudge_count: number;
  escalated: boolean;
  sensitive: boolean;
  requires_manual: boolean;
  step: string | null;
  last_nudge: string;
  waiting_label: string;
}

export interface Hire {
  id: number;
  name: string;
  department: string;
  start_label: string;
  readiness: number;
  tasks: Task[];
}

export interface Stats {
  active_hires: number;
  awaiting_approval: number;
  escalated: number;
}

export interface Dashboard {
  stats: Stats;
  hires: Hire[];
}

export interface ApprovalItem {
  id: number;
  tool: string;
  scope: string;
  hire_name: string;
  waiting_label: string;
  sensitive: boolean;
  requires_manual: boolean;
  step: string | null;
}

export interface ApproverRequest {
  approver_name: string;
  approver_email: string;
  initials: string;
  items: ApprovalItem[];
}

export type Outcome = "approved" | "rejected" | "not_authorised";

export interface ReplyResultItem {
  tool: string;
  scope: string;
  hire_name: string;
  outcome: Outcome;
  note: string;
}

export interface ReplyResult {
  intent: string;
  applied_count: number;
  skipped_count: number;
  items: ReplyResultItem[];
}

export interface AuditEvent {
  id: number;
  timestamp: string;
  actor: string;
  is_agent: boolean;
  action: string;
  detail: string;
  refused: boolean;
}
