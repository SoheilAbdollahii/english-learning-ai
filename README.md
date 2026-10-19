# English Learning AI

An AI-powered English learning web application.

> **Project status:** active MVP development. Session authentication/profile, placement assessment, Writing Studio, Vocabulary spaced repetition, Reading comprehension, persisted progress metrics, and transparent rule-based recommendations are implemented on a stacked set of open pull requests. The dashboard and learning flows are under automated CI verification; they are not yet a production release. Without `GEMINI_API_KEY`, Writing uses an explicitly labelled demo adapter and does not evaluate grammar.

## Technology stack

- Backend: Python, Django, Django REST Framework
- Frontend: Next.js, React, TypeScript
- Database: PostgreSQL for local/production configuration; SQLite is used as a zero-setup fallback when `DATABASE_URL` is omitted
- Testing: pytest / pytest-django and Node's built-in test runner
- CI: GitHub Actions

## Repository map

- `backend/` — Django REST API for accounts, placement, writing, vocabulary, reading, and progress
- `frontend/` — Next.js learner dashboard, session sign-in, placement quiz, Writing Studio, Vocabulary review, and Reading Room
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

Open `http://localhost:3000`. Sign in at `http://localhost:3000/login` using the Django superuser you created. The frontend proxies `/api/*` to `http://127.0.0.1:8000` by default; set `BACKEND_API_URL` if your backend runs elsewhere. The dashboard's progress summary is derived from saved activities; study duration is intentionally not shown because reliable session-duration tracking is not yet implemented. For a different frontend origin, set `DJANGO_CSRF_TRUSTED_ORIGINS` to comma-separated origins including `https://` in production. Create a user through Django admin or `createsuperuser`; public registration is not yet available.

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
- Session login/logout, profile, owner-scoped learning records, server-side placement/reading scoring, vocabulary review scheduling, Writing result validation, production-mode secret enforcement, and basic AI request throttling and a database-backed rolling-24-hour Writing quota are implemented in the current PR stack.
- Writing uses a demo provider unless a Gemini API key is configured; the demo provider is not a tutor and must not be presented as real grammar feedback.
- Before production: complete and merge the stacked PRs in dependency order; configure HTTPS/proxy settings and secure cookies for the actual deployment; add account recovery/registration policy, immutable content/version controls, provider token/cost accounting, privacy/retention policy, backup/restore drills, and an evaluated writing dataset. Run the full release checklist and CI on the final merge commit.

## Development status

See [the development roadmap](docs/development-plan.md) and [architecture baseline](docs/architecture.md). Features should be marked verified only after tests or documented manual checks pass.
