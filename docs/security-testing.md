# Security and Testing Baseline

## Security

### Authentication and authorization
- Use a custom Django user model from the first migration.
- Prefer session authentication with secure, HttpOnly cookies and CSRF when deployment topology permits.
- Configure allowed hosts, CORS, cookie flags, and CSRF trusted origins explicitly.
- Enforce ownership on the server; frontend hiding is not authorization.
- Test unauthenticated requests and cross-user read/update attempts.
- Public registration requires CSRF, password validators, normalized unique usernames, and an anonymous request throttle. Email verification, recovery flows, and production-grade abuse prevention remain outstanding.

### Secrets and data handling
- Commit only an .env.example with placeholders; ignore real environment files.
- Store AI and production credentials in deployment secrets.
- Never log raw writing submissions, passwords, tokens, session IDs, or provider secrets.
- Define retention and deletion policy before production.
- Use HTTPS in deployed environments and secure database credentials.

### AI-specific controls
- Enforce input limits, timeouts, and server-side quotas. The current Writing flow uses a per-hour DRF throttle plus a database-backed rolling-24-hour reservation quota; concurrent quota reservations must be validated against production PostgreSQL.
- Treat user text and model output as untrusted.
- Validate model responses against a versioned schema.
- Never use AI output to decide permissions, account state, billing, or trusted scoring.
- Send only necessary personal data to providers.
- Record safe failure and usage metadata without sensitive payloads. The initial ledger stores provider/status and input character volume; it does not yet calculate money or persist actual provider token usage.
- Do not claim calibrated confidence without empirical evaluation.

## Testing strategy

### Backend
- Unit tests: scoring, writing-result validation, vocabulary scheduling, quotas, recommendations.
- API tests: auth, ownership, validation, pagination, status and error behavior.
- Integration tests: PostgreSQL constraints and transaction boundaries.
- AI adapter tests use a fake provider; regular CI must not call a paid live API.

### Frontend
- Component tests for forms, loading/error/empty states, keyboard interaction.
- Verify RTL/LTR direction and locale switching.
- Test accessible labels, focus handling, and useful error messages.

### End-to-end
- Authentication and profile update.
- Reading attempt with server-calculated score.
- Writing submission using deterministic fake provider.
- Vocabulary review changes scheduling state.
- A user cannot access another user's history.

### CI baseline
- Backend formatting/lint, tests, and type checks if adopted.
- Frontend lint, TypeScript check, unit tests, and production build.
- Pin dependency resolution and keep tests deterministic.
- Do not claim CI passes until it has actually run successfully.
