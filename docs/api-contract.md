# Initial REST API Contract

Status: proposed endpoint inventory. Exact serializers, status codes, and OpenAPI schema must be tested against the implementation before the contract is stable.

## Conventions
- Prefix routes with /api/v1/.
- Use JSON and ISO 8601 UTC timestamps.
- Validate all inputs server-side.
- Enforce authorization for every private object.
- Do not expose provider credentials, stack traces, internal prompts, or another user's data.
- Document pagination and filtering when list endpoints are implemented.
- Generate OpenAPI from actual serializers and views.

## Endpoint inventory

### Authentication and profile
- POST /auth/login/
- POST /auth/logout/
- GET /me/
- PATCH /me/profile/

Default proposal is session authentication with secure cookies and CSRF, contingent on deployment topology.

### Placement
- GET /placement/assessments/
- GET /placement/assessments/{assessment_id}/ — public question fields only
- POST /placement/attempts/ — server calculates score
- GET /placement/attempts/{attempt_id}/ — owner-only result

### Writing
- POST /writing/submissions/
- GET /writing/submissions/ — paginated owner-only history
- GET /writing/submissions/{submission_id}/ — validated result/status

Start with synchronous processing and a strict timeout. Add background jobs only if latency or retry requirements justify them. A failed or malformed AI response must never be represented as a successful analysis.

### Reading
- GET /reading/passages/
- GET /reading/passages/{passage_id}/
- POST /reading/attempts/ — server calculates score
- GET /reading/attempts/{attempt_id}/ — owner-only result

### Vocabulary
- GET /vocabulary/review/
- POST /vocabulary/reviews/
- GET /vocabulary/progress/

### Progress and usage
- GET /progress/summary/
- GET /progress/recommendations/
- GET /usage/

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
