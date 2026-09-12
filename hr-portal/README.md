# HR Portal

An internal onboarding tool that tracks access provisioning for new hires.
Extends the existing **New Hire Intake** screen with three new screens —
**Dashboard**, **Approvals**, and **Audit log** — reusing the same design
system (dark navy sidebar, indigo accents, inset white panel on light lavender,
Poppins geometric sans).

## Tech stack

| Layer      | Choice                                             |
| ---------- | -------------------------------------------------- |
| Frontend   | React 18 + Vite + TypeScript (SPA, React Router)   |
| Backend    | Python + FastAPI + SQLAlchemy                      |
| Database   | SQLite (swap `DATABASE_URL` for Postgres)          |

```
hr-portal/
├── frontend/     React + Vite + TS single-page app
├── backend/      FastAPI + SQLAlchemy API
└── prototype/    Original static HTML/CSS mockups (design reference)
```

## Screens

- **Dashboard** — three stat cards (active hires, tasks awaiting approval,
  escalated) and per-hire cards with a readiness bar and an access-task table.
  Status is a soft pill with a coloured dot: Pending, Awaiting approval,
  Escalated, Provisioned, Blocked.
- **Approvals** — open items grouped per approver. Sensitive items show a
  "Needs manual approval" tag and a "Step 1 of 2" indicator. A free-text
  **Reply as approver** box is interpreted server-side: intent detection plus an
  authority check, so an approver can only approve items they own. The result
  strip shows what was applied vs. refused ("Not authorised — you don't own
  this item").
- **Audit log** — every request, nudge, approval and refusal, newest first.
  Agent actors (Orchestrator, Provisioner, Follow-up agent) carry an "agent"
  tag; refused rows are styled red. Replies and hire creation write new rows
  live.

## Running locally

Two processes. The Vite dev server proxies `/api` to the backend, so start both.

### 1. Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first start the database is created and seeded with the reference
onboarding story (two hires, their access tasks, and the audit trail). Delete
`backend/hr_portal.db` to reseed from scratch. Interactive API docs are at
`http://localhost:8000/docs`.

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API

| Method | Path                     | Purpose                                    |
| ------ | ------------------------ | ------------------------------------------ |
| GET    | `/api/dashboard`         | Stats + hires with access tasks            |
| GET    | `/api/approvals`         | Open items grouped per approver            |
| POST   | `/api/approvals/reply`   | Interpret a free-text approver reply       |
| GET    | `/api/audit`             | Audit events, newest first                 |
| POST   | `/api/hires`             | Create a hire (Intake form)                |

### Try the approver reply

From the **Approvals** screen, reply as Priya Nair with
`approved for GroundCover and Databricks`. GroundCover (which she owns) is
approved and provisioned; the Databricks items (owned by Rohan Desai) are
refused for authority. Both outcomes appear in the result strip and as new
rows in the audit log.
