# IssueHub - Lightweight Bug Tracker

IssueHub is a minimal bug tracker built for team-based project and issue management.

It supports:
- authentication (signup/login/logout)
- project creation and membership management
- issue CRUD with role-based permissions
- comments and issue status tracking
- filtering/search/sorting/pagination

## Assignment Requirement Coverage

### Core MVP
- Backend: Python + FastAPI -> implemented
- DB: PostgreSQL with migrations (Alembic) -> implemented
- Frontend: React (Vite) -> implemented
- Auth: email/password + JWT + signup/login/logout -> implemented
- Testing: backend unit/integration tests -> implemented
- Docs: this README includes setup/run/test/architecture/trade-offs/limitations -> implemented
- API: REST JSON + CORS -> implemented

### User Roles
- User:
  - create/read/update issues they reported -> implemented
  - comment -> implemented
  - view issues in joined projects -> implemented
- Project Maintainer:
  - update/assign/close any issue in project -> implemented
  - manage project membership -> implemented

### Required Features
- Auth & Projects:
  - signup/login/logout -> implemented
  - create project (creator becomes maintainer) -> implemented
  - invite/add members by email -> implemented
- Issues:
  - CRUD -> implemented
  - filter/search by status/priority/assignee/title -> implemented
  - sort by created_at/priority/status -> implemented
- Issue Details:
  - metadata (status/priority/assignee/reporter/timestamps) -> implemented
  - comment thread + add comment -> implemented
  - status/assignee controls visible and actionable only for maintainers -> implemented
- UX:
  - navigation flow Projects -> Issues -> Issue Detail -> implemented
  - basic validation + user feedback (spinners/toasts) -> implemented
  - New Issue modal -> implemented

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL (SQLite can be used for local dev by changing `DATABASE_URL`)
- Passlib (`bcrypt`) for password hashing
- `python-jose` for JWT
- Pytest + HTTPX for tests

### Frontend
- React + Vite
- React Router
- Axios
- local component state (`useState`, `useEffect`)

## Architecture and Module Separation

Backend follows layered separation:
- `app/api/` -> route handlers/controllers
- `app/services/` -> business rules + authorization logic
- `app/dao/` -> database access/query layer
- `app/models/` -> SQLAlchemy models
- `app/schemas/` -> request/response validation with Pydantic
- `app/core/` -> config/security/dependencies

Frontend:
- `src/pages/` -> route-level pages
- `src/components/` -> reusable UI pieces
- `src/api/axios.js` -> API client + auth header interceptor

## Project Structure (High Level)

```txt
issuehub/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── dao/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── core/
│   │   └── main.py
│   ├── tests/
│   ├── seed.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   ├── api/
    │   └── App.jsx
    └── package.json
```

## Setup

## 1. Prerequisites
- Python 3.11+
- PostgreSQL
- Node.js 18+

## 2. Clone and enter project
```bash
git clone <your-repo-url>
cd issuehub
```

## 3. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/issuehub
SECRET_KEY=replace_with_secure_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run migrations:
```bash
alembic upgrade head
```

Seed demo data:
```bash
python seed.py
```

Run API:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger:
- `http://127.0.0.1:8000/docs`

## 4. Frontend setup
```bash
cd ../frontend
npm install
npm run dev
```

Frontend URL:
- `http://localhost:5173`

## How to Run Tests

From project root:
```bash
python -m pytest backend/tests -q
```

## API Contract Notes

Primary API base in frontend is:
- `/api/...`

Versioned aliases are also available:
- `/api/v1/...`

Contract compatibility highlights:
- `POST /api/auth/signup` -> JSON `{name,email,password}`
- `POST /api/auth/login` -> supports JSON `{email,password}` and form login
- `GET /api/me` -> current user profile
- `GET /api/projects/{id}/issues` supports `assignee` (and also `assignee_id` for compatibility)

Errors are structured as:
```json
{
  "error": {
    "code": "HTTP_400",
    "message": "Some message",
    "details": []
  }
}
```

## Seed Data

Seed script creates:
- 4 users
- 2 projects
- project memberships with maintainer/member roles
- 12 issues (within 10-20 suggested range)
- comments on selected issues

It is idempotent, so re-running seed does not create duplicates for the same records.

Demo credentials:
- `ali@test.com / password123`
- `zulfiqar@test.com / 123456`
- `ayesha@test.com / password123`
- `rahul@test.com / password123`

## Tech Choices and Trade-offs

- FastAPI + SQLAlchemy chosen for rapid API development and clear typing.
- JWT bearer auth chosen for stateless API auth and simple SPA integration.
- React local state chosen for simplicity and speed over introducing global state libs.
- Route/service/dao layering added for maintainability and interview-ready code separation.

Trade-offs:
- Kept implementation minimal and assignment-focused rather than adding heavy infrastructure.
- Chose compatibility paths (`/api` and `/api/v1`) to preserve existing clients while matching assignment examples.

## Known Limitations and Future Improvements

- No refresh-token flow (access token only).
- No CI/CD pipeline yet.
- No Docker setup yet.
- Test suite can be expanded further for edge-case and frontend coverage.
- Sorting by enum fields uses DB enum ordering; custom explicit semantic ordering could be refined further.
- Observability (structured logs/metrics/tracing) is minimal.

## Optional Submission Add-ons

- Live deployment URL (optional).
- Demo walkthrough video (optional).

