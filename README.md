# English Learning AI

An AI-powered English learning web application.

> **Project status:** early MVP. Architecture and delivery documentation, a Django API starter, a responsive learner dashboard, and a CSRF-protected frontend session login/logout flow are in place. The current-user profile API is integrated for session status. Progress values remain placeholders; public registration, persisted learner activity, Writing analysis, Reading exercises, Vocabulary review, and real dashboard metrics are not implemented yet.

## Technology stack

- Backend: Python, Django, Django REST Framework
- Frontend: Next.js, React, TypeScript
- Database: PostgreSQL for local/production configuration; SQLite is used as a zero-setup fallback when `DATABASE_URL` is omitted
- Testing: pytest / pytest-django and Node's built-in test runner
- CI: GitHub Actions

## Repository map

- `backend/` — Django API starter and health endpoint
- `frontend/` — Next.js learner dashboard UI and session sign-in screen
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

The sample file documents the expected environment values but Django does not automatically load `.env`; export the variables in your shell or configure your local environment manager. Never commit real secrets. For a quick local run, leave `DATABASE_URL` unset to use SQLite, or configure a running PostgreSQL instance.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py createsuperuser
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

Open `http://localhost:3000`. Sign in at `http://localhost:3000/login` using the Django superuser you created. The frontend proxies `/api/*` to `http://127.0.0.1:8000` by default; set `BACKEND_API_URL` if your backend runs elsewhere. The dashboard progress values remain placeholders and its learning-area links do not yet launch working lessons. For a different frontend origin, set `DJANGO_CSRF_TRUSTED_ORIGINS` to comma-separated origins including `https://` in production.

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
- Session login/logout and the current-user profile endpoint are implemented and tested, but public registration, account recovery, production cookie/security settings, object-level permissions for future learning records, AI output validation, and quotas still need implementation before production use.
- Dashboard metrics are intentionally shown as placeholders until they can be derived from persisted activity records.

## Development status

See [the development roadmap](docs/development-plan.md) and [architecture baseline](docs/architecture.md). Features should be marked verified only after tests or documented manual checks pass.
