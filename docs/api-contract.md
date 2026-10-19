# Initial REST API Contract

Status: partially implemented. Session CSRF/login/logout and the current-user profile endpoint are implemented and covered by tests. Reading, Vocabulary, progress, and usage endpoints below remain proposals until implemented and tested. The Writing API and frontend Writing Studio are implemented on the `feat/writing-mvp-api` branch. Gemini Developer API integration is optional and enabled only when the backend environment has a configured `GEMINI_API_KEY`; without it, the clearly labelled demo provider remains active. CI for the latest hardening changes is pending.

## Conventions
- Prefix routes with /api/v1/.
- Use JSON and ISO 8601 UTC timestamps.
- Validate all inputs server-side.
- Enforce authorization for every private object.
- Do not expose provider credentials, stack traces, internal prompts, or another user's data.
- Document pagination and filtering when list endpoints are implemented.
- Generate OpenAPI from actual serializers and views.

## Implemented endpoints

### Health
- GET /api/v1/health/ — public process-level health response; not a database/dependency readiness check.

### Current learner profile
- GET /api/v1/me/ — authenticated user's id, username, email, name fields, and profile preferences.
- PATCH /api/v1/me/ — updates first/last name and/or profile preferences; username, email, and id are read-only.
- Profile preferences: locale (en/fa), target_level (A1-C2/unknown), daily_goal_minutes (5-180), timezone.
- Unauthenticated requests are denied. The endpoint always resolves the current authenticated user; callers cannot supply another user's ID.
- Authentication currently uses Django session authentication. For browser clients, production deployment must use HTTPS and correctly configure CSRF and cookie settings.

### Authentication
- GET /api/v1/auth/csrf/ — implemented; returns a CSRF token and sets the CSRF cookie.
- POST /api/v1/auth/login/ — implemented; accepts username/password and creates a Django session; CSRF header/cookie required.
- POST /api/v1/auth/logout/ — implemented; ends the authenticated session; CSRF header/cookie required.
- Login rotates the CSRF token; browser clients should obtain a fresh token after login before a subsequent unsafe request.
- The Next.js frontend proxies `/api/*` to `BACKEND_API_URL` (default `http://127.0.0.1:8000`) so browser requests remain same-origin. Add the frontend origin to `DJANGO_CSRF_TRUSTED_ORIGINS`; production origins must be configured explicitly.
- The frontend login form is available at `/login`. Public registration is intentionally not available yet; create users through the Django admin or `createsuperuser` for local testing.
- Registration policy and endpoint remain to be designed before public launch.

### Placement (implemented backend and frontend flow)
- GET /api/v1/placement/assessments/ — published assessments only.
- GET /api/v1/placement/assessments/{assessment_id}/ — public question fields only; answer keys and explanations are withheld.
- POST /api/v1/placement/attempts/ — authenticated; validates complete answer sets and calculates score on the server.
- GET /api/v1/placement/attempts/{attempt_id}/ — authenticated owner-only result.
- A six-question starter assessment is seeded by the initial migration. The Next.js /placement page fetches the public question set, validates that all answers are selected, retrieves a CSRF token, and submits the answers through the same-origin API proxy. The server scores and persists the attempt; the result screen displays the returned score and provisional level.
- CEFR estimates use a documented-in-code percentage threshold heuristic and are provisional, not a validated adaptive placement instrument. The browser never receives answer keys or calculates the official score.

### Writing (MVP API; demo provider only)
- POST /api/v1/writing/submissions/ — authenticated; accepts `{ "text": "..." }` with 3–5000 characters, persists the submission, and returns a versioned result from the configured adapter.
- GET /api/v1/writing/submissions/ — authenticated, paginated owner-only history (`limit`/`offset`).
- GET /api/v1/writing/submissions/{submission_id}/ — authenticated owner-only submission and result.
- Result schema v1 includes `corrected_text`, `errors`, `general_feedback`, and `limitations`. Error offsets use Python Unicode code points; `start` is inclusive and `end` exclusive, and the original span must match the submitted text.
- The current demo provider deliberately performs no grammar evaluation and makes this limitation explicit. It is an integration/test scaffold, not an AI writing tutor. Provider failures and invalid result schemas are not reported as successful analyses. Provider-backed submissions are rate-limited per authenticated learner (default 10/hour, configurable with `WRITING_SUBMISSIONS_PER_HOUR`). This throttle limits request frequency but is not a billing-grade usage ledger; durable quota accounting, provider evaluation data, and deployment-specific HTTPS/proxy configuration remain follow-up work.

## Planned endpoint inventory

### Reading
- GET /api/v1/reading/passages/
- GET /api/v1/reading/passages/{passage_id}/
- POST /api/v1/reading/attempts/ — server calculates score
- GET /api/v1/reading/attempts/{attempt_id}/ — owner-only result

### Vocabulary
- GET /api/v1/vocabulary/review/
- POST /api/v1/vocabulary/reviews/
- GET /api/v1/vocabulary/progress/

### Progress and usage
- GET /api/v1/progress/summary/
- GET /api/v1/progress/recommendations/
- GET /api/v1/usage/

## Error response example
The consistent error envelope should include a stable code, safe user-facing message, field details where relevant, and an opaque request ID. Internal exception details belong in protected logs with sensitive values redacted.

## Contract acceptance checklist
- OpenAPI generated from actual serializers and views.
- Auth and object permissions tested.
- Request size, pagination, and validation bounded.
- Consistent error codes and status codes.
- Answer keys and private fields protected.
- Explicit behavior for AI timeout, provider failure, malformed output, and exhausted quota.
