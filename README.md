# English Learning AI

An AI-powered English learning web application.

> **Project status:** early scaffold. Architecture and delivery documentation are in place, with minimal Django and Next.js starter applications. Writing analysis, Reading exercises, Vocabulary review, authentication flows, and dashboard metrics are not implemented yet.

## Technology stack

- Backend: Python, Django, Django REST Framework
- Frontend: Next.js, React, TypeScript
- Database: PostgreSQL for local/production configuration; SQLite is used as a zero-setup fallback when `DATABASE_URL` is omitted
- Testing: pytest / pytest-django and Node's built-in test runner
- CI: GitHub Actions

## Repository map

- `backend/` — Django API starter and health endpoint
- `frontend/` — Next.js landing page scaffold
- `docs/architecture.md` — architecture decisions
- `docs/data-model.md` — proposed learning data model
- `docs/api-contract.md` — initial endpoint inventory
- `docs/security-testing.md` — security and test baseline
- `docs/evaluation-plan.md` — AI Writing evaluation plan
- `docs/development-plan.md` — phases and acceptance criteria

## Local setup

Requirements: Python 3.12+, Node.js 22+, npm, and optionally PostgreSQL.

1. Copy `.env.example` to `.env` and replace local placeholder values. Never commit real secrets.
2. Backend:

   ```bash
   cd backend
   python -m venv .venv
   # Activate the virtual environment, then:
   pip install -r requirements.txt
   python manage.py check
   python manage.py migrate
   python manage.py runserver
   ```

   Health endpoint: `http://127.0.0.1:8000/api/v1/health/`

3. Frontend, in a separate terminal:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:3000`.

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

## Development status

See [the development roadmap](docs/development-plan.md) and [architecture baseline](docs/architecture.md). Features should be marked verified only after tests or documented manual checks pass.
