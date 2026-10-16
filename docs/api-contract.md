# Initial REST API Contract

Status: partially implemented. Session CSRF/login/logout and the current-user profile endpoint are implemented and covered by tests. Reading, Writing, Vocabulary, progress, and usage endpoints below remain proposals until implemented and tested.

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
- A six-question starter assessment is seeded by the initial migration. The Next.js /placement page fetches the public question set, validates that all answers are selected client-side, retrieves a CSRF token, and submits the answers through the same-origin API proxy. The server scores and persists the attempt; the result screen displays the returned score and provisional level.
- CEFR estimates use a documented-in-code percentage threshold heuristic and are provisional, not a validated adaptive placement instrument. The browser never receives answer keys or calculates the official score.

## Planned endpoint inventory

### Writing
- POST /api/v1/writing/submissions/
- GET /api/v1/writing/submissions/ — paginated owner-only history
- GET /api/v1/writing/submissions/{submission_id}/ — validated result/status

Start with synchronous processing and a strict timeout. Add background jobs only if latency or retry requirements justify them. A failed or malformed AI response must never be represented as a successful analysis.

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

## Writing result logical schema
A validated result should contain schema version, status, corrected text, a list of errors (category, original span, correction, explanation), general feedback, and limitations. This is a logical contract, not a production schema yet.

Offsets require a documented convention (Unicode code points vs UTF-16, exclusive vs inclusive end). Validate that each span maps to the submitted text. Define behavior when corrected text and error list disagree.

## Contract acceptance checklist
- OpenAPI generated from actual implementation.
- Auth and object permissions tested.
- Request size, pagination, and validation bounded.
- Consistent error codes and status codes.
- Answer keys and private fields protected.
- Explicit behavior for AI timeout, provider failure, malformed output, and exhausted quota.
