# Initial REST API Contract

Status: core MVP endpoints are implemented with automated tests. Session CSRF/login/logout, email verification and password reset, profile, placement, Writing, vocabulary review, Reading comprehension, progress, and usage summary are present. The Writing flow uses a provider-neutral adapter with a demo fallback and optional Gemini Developer API integration when `GEMINI_API_KEY` is configured. Token usage and optional configured-rate cost estimates are persisted; educational quality remains unverified until educator review and a measured live-provider evaluation are complete.

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
- GET /api/v1/health/ — public liveness response; confirms the process is serving but does not check dependencies.
- GET /api/v1/ready/ — public readiness response; checks database connectivity and unapplied migrations and returns generic failure details without exposing driver internals.

### Current learner profile
- GET /api/v1/me/ — authenticated user's id, username, email, name fields, and profile preferences.
- PATCH /api/v1/me/ — updates first/last name and/or profile preferences; username, email, and id are read-only.
- Profile preferences: locale (en/fa), target_level (A1-C2/unknown), daily_goal_minutes (5-180), timezone.
- Unauthenticated requests are denied. The endpoint always resolves the current authenticated user; callers cannot supply another user's ID.
- Authentication currently uses Django session authentication. For browser clients, production deployment must use HTTPS and correctly configure CSRF and cookie settings.

### Authentication
- GET /api/v1/auth/csrf/ — implemented; returns a CSRF token and sets the CSRF cookie.
- POST /api/v1/auth/login/ — implemented; accepts username/password and creates a Django session; CSRF header/cookie required.
- POST /api/v1/auth/register/ — creates an inactive account with username, unique email, and password; CSRF required, password validators enforced, and anonymous requests throttled (default 5/hour via `REGISTRATION_RATE_LIMIT`).
- POST /api/v1/auth/logout/ — implemented; ends the authenticated session; CSRF header/cookie required.
- Login rotates the CSRF token; browser clients should obtain a fresh token after login before a subsequent unsafe request.
- The Next.js frontend proxies `/api/*` to `BACKEND_API_URL` (default `http://127.0.0.1:8000`) so browser requests remain same-origin. Add the frontend origin to `DJANGO_CSRF_TRUSTED_ORIGINS`; production origins must be configured explicitly.
- The frontend login and registration forms are available at `/login` and `/register`. Registration does not automatically sign the learner in; it directs the learner to the login flow.
- Email verification and password-reset request/confirmation/resend endpoints are implemented with CSRF protection and throttles. Real SMTP delivery and end-to-end production-origin verification remain environment-specific release checks.

### Placement (implemented backend and frontend flow)
- GET /api/v1/placement/assessments/ — published assessments only.
- GET /api/v1/placement/assessments/{assessment_id}/ — public question fields only; answer keys and explanations are withheld.
- POST /api/v1/placement/attempts/ — authenticated; validates complete answer sets and calculates score on the server.
- GET /api/v1/placement/attempts/{attempt_id}/ — authenticated owner-only result.
- A six-question starter assessment is seeded by the initial migration. The Next.js /placement page fetches the public question set, validates that all answers are selected, retrieves a CSRF token, and submits the answers through the same-origin API proxy. The server scores and persists the attempt; the result screen displays the returned score and provisional level.
- CEFR estimates use a documented-in-code percentage threshold heuristic and are provisional, not a validated adaptive placement instrument. The browser never receives answer keys or calculates the official score.

### Writing (MVP API; demo fallback and optional Gemini provider)
- POST /api/v1/writing/submissions/ — authenticated; accepts `{ "text": "..." }` with 3–5000 characters, persists the submission, and returns a versioned result from the configured adapter.
- GET /api/v1/writing/submissions/ — authenticated, paginated owner-only history (`limit`/`offset`).
- GET /api/v1/writing/submissions/{submission_id}/ — authenticated owner-only submission and result.
- Result schema v1 includes `corrected_text`, `errors`, `general_feedback`, and `limitations`. Error offsets use Python Unicode code points; `start` is inclusive and `end` exclusive, and the original span must match the submitted text.
- The demo provider deliberately performs no grammar evaluation and makes this limitation explicit; when Gemini is configured, the provider-backed result is validated before it is returned. The Writing Studio shows corrected text, error spans, suggested corrections, explanations, provider status, and limitations. Provider failures and invalid/overlapping result spans are not reported as successful analyses. Provider-backed submissions are rate-limited per authenticated learner (default 10/hour, configurable with `WRITING_SUBMISSIONS_PER_HOUR`) and constrained by a durable rolling-24-hour quota (`WRITING_SUBMISSIONS_PER_DAY`). Gemini output is capped at 2,048 tokens. The provider-reported prompt/output token counts are stored in the usage ledger; only aggregate token metadata is stored there, not the learner's text or the raw provider payload. `GET /api/v1/usage/` reports token totals and optional estimated cost. To enable cost estimates, set BOTH `GEMINI_INPUT_COST_MICROUNITS_PER_MILLION_TOKENS` and `GEMINI_OUTPUT_COST_MICROUNITS_PER_MILLION_TOKENS` using the active provider price sheet; a micro-unit is one millionth of the billing currency unit. The application deliberately assumes no default price. Cost estimates are configuration-based estimates, not invoices. The demo provider has no provider token usage, and its cost is not fabricated. Human-reviewed provider evaluation, production pricing verification, and deployment-specific HTTPS/proxy configuration remain follow-up work.

### Vocabulary (initial review MVP)
- GET /api/v1/vocabulary/cards/ — authenticated; returns only the current learner's cards ordered by due date. Add `?due=true` to return cards due now.
- POST /api/v1/vocabulary/cards/ — authenticated; creates a card with word, English definition, optional example and translation. A learner cannot save the same word twice, ignoring case.
- POST /api/v1/vocabulary/cards/{card_id}/review/ — authenticated owner-only; accepts `quality` from 0 to 5 and returns the updated schedule. Each successful review atomically appends a review-event snapshot.
- GET /api/v1/vocabulary/reviews/?limit=20&offset=0 — authenticated, paginated owner-only review-event history. Optional `card` filters by numeric card ID. Each event preserves the word and before/after scheduling state as recorded at review time; the API exposes no edit/delete operation.
- Review scheduling is a deterministic SM-2-inspired rule set: grades below 3 reset the interval to one day; successful reviews progress through 1 day, 6 days, then ease-adjusted intervals. Five successful repetitions and a minimum 21-day interval mark a card mastered. Displaying a card alone does not change mastery.
- The current card model stores a single owner-scoped card and its scheduling state; separate immutable review-event history and curated licensed vocabulary content are future work.

### Reading (initial comprehension MVP)
- GET /api/v1/reading/passages/ — public list of published original passages with level, content version, and question count.
- GET /api/v1/reading/passages/{passage_id}/ — published passage and public question options. Correct options and explanations are omitted before submission.
- POST /api/v1/reading/attempts/ — authenticated; accepts a passage ID and exactly one valid option per question; server calculates weighted score and percentage.
- GET /api/v1/reading/attempts/?limit=10&offset=0 — authenticated, paginated owner-only attempt history (maximum page size 50).
- GET /api/v1/reading/attempts/{attempt_id}/ — authenticated owner-only result including answer feedback, explanation snapshots, and an immutable `question_snapshots` array (prompt, options, answer key, explanation, points, order, selected option, and correctness as recorded at submission). Existing attempts are backfilled with available feedback fields; historical option text cannot be reconstructed for attempts created before this snapshot field.
- Two original sample passages (A2 and B1) are seeded by migration. Content is original starter content, not externally licensed material. The current MVP does not yet include passage authoring workflows or immutable question version snapshots; the learner-facing attempt-history UI is being added in PR #16 and remains subject to CI verification.

### Progress (initial persisted summary)
- GET /api/v1/progress/summary/ — authenticated; returns completed activity count, vocabulary reviews, reading/writing/placement totals, due/mastered vocabulary counts, current consecutive-day streak, and the latest eight activity events.
- Activity events are recorded after successful writing submissions, completed reading attempts, placement attempts, and vocabulary review outcomes. Event metadata avoids storing submitted writing text.
- Study duration is intentionally not reported because the current product does not collect reliable session-duration data.

## Planned endpoint inventory

### Recommendations and usage
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
