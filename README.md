# English Learning AI

An AI-powered English learning web application.

> **Project status:** early MVP. Architecture and delivery documentation, a Django API starter, and a responsive learner dashboard UI shell are in place. The dashboard currently uses placeholder progress values; authentication, persisted learner activity, Writing analysis, Reading exercises, Vocabulary review, and dashboard metrics are not implemented yet.

## Technology stack

- Backend: Python, Django, Django REST Framework
- Frontend: Next.js, React, TypeScript
- Database: PostgreSQL for local/production configuration; SQLite is used as a zero-setup fallback when `DATABASE_URL` is omitted
- Testing: pytest / pytest-django and Node's built-in test runner
- CI: GitHub Actions

## Repository map

- `backend/` — Django API starter and health endpoint
- `frontend/` — Next.js learner dashboard UI preview
- `frontend/tests/` — frontend dashboard smoke tests
- `docs/architecture.md` — architecture decisions
- `docs/data-model.md` — proposed learning data model
- `docs/api-contract.md` — initial endpoint inventory
- `docs/security-testing.md` — security and test baseline
- `docs/evaluation-plan.md` — AI Writing evaluation plan
- `docs/development-plan.md` — phases and acceptance criteria

## Local setup

Requirements: Python 3.12+, Node.js 22+, npm, and optionally PostgreSQL.

From the repository root, create a local environment file if needed:

```bash
cp .env.example .env
```

Replace local placeholder values as appropriate. Never commit real secrets. For a quick local run, the backend can use SQLite when `DATABASE_URL` is omitted.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```

Health endpoint: `http://127.0.0.1:8000/api/v1/health/`

### Frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The dashboard is a UI preview; its progress values are placeholders and its learning-area links do not yet launch working lessons.

## Checks

Backend:

```bash
cd backend
python manage.py check
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm test
npm run build
```

The checks above are configured in CI but must be observed running successfully before calling the branch verified.

## Security notes

- Do not commit `.env` or provider API keys.
- The current health endpoint is a scaffold, not a production readiness check.
- Authentication, object-level permissions, AI output validation, quotas, and production settings still need implementation and tests before handling real learner data.
- Dashboard metrics are intentionally shown as placeholders until they can be derived from persisted activity records.

## Development status

See [the development roadmap](docs/development-plan.md) and [architecture baseline](docs/architecture.md). Features should be marked verified only after tests or documented manual checks pass.
