# Initial REST API Contract

Status: partially implemented. The current-user profile endpoint is implemented and covered by tests; remaining endpoints are proposals until implemented and tested.

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

## Planned endpoint inventory

### Authentication
- GET /api/v1/auth/csrf/ — returns a CSRF token and sets the CSRF cookie.
- POST /api/v1/auth/login/ — accepts username/password and creates a Django session; CSRF header/cookie required.
- POST /api/v1/auth/logout/ — ends the authenticated session; CSRF header/cookie required.
- Login rotates the CSRF token; browser clients should obtain a fresh token after login before a subsequent unsafe request.
- Registration policy and endpoint remain to be designed before public launch.

### Placement
- GET /api/v1/placement/assessments/
- GET /api/v1/placement/assessments/{assessment_id}/ — public question fields only
- POST /api/v1/placement/attempts/ — server calculates score
- GET /api/v1/placement/attempts/{attempt_id}/ — owner-only result

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
