# Security and Testing Baseline

## Security

### Authentication and authorization
- Session authentication uses CSRF protection; secure-cookie flags are enabled when `DJANGO_DEBUG=false`.
- Configure exact allowed hosts, CSRF trusted origins, HTTPS termination, and any trusted proxy headers for the real deployment topology.
- Enforce ownership on the server; frontend hiding is not authorization.
- Test unauthenticated requests and cross-user read/update attempts.
- Public registration has CSRF protection, password validators, normalized unique usernames, unique email addresses, and an anonymous request throttle. Email verification and password recovery endpoints are implemented and tested; production SMTP delivery and abuse monitoring remain deployment tasks.

### Secrets and data handling
- Commit only `.env.example` with placeholders; ignore real environment files.
- Store AI and production credentials in deployment secrets.
- Never log raw writing submissions, passwords, tokens, session IDs, or provider secrets.
- Define retention, export, and deletion policy before production.
- Use HTTPS in deployed environments, secure database credentials, private database networking, and tested backups.
- Production deployment settings, proxy trust, HSTS policy, and cookie behavior must be verified at the actual edge; repository CI does not prove infrastructure security.

### AI-specific controls
- Enforce input limits, timeouts, and server-side quotas. The Writing flow uses a per-hour DRF throttle plus a database-backed rolling-24-hour reservation quota; concurrency behavior still needs validation against production PostgreSQL.
- Treat user text and model output as untrusted; validate model responses against a versioned schema.
- Never use AI output to decide permissions, account state, billing, or trusted scoring.
- Send only necessary personal data to providers and document the provider's data processing before public launch.
- The usage ledger can persist actual provider token counts when returned and can calculate an optional estimate from configured rates. It avoids storing raw provider payloads or learner text. Estimates are operational approximations, not invoices.
- The offline Writing evaluation harness validates source spans, categories, overlap, missing/unexpected prediction IDs, and malformed predictions. It explicitly marks draft annotations as diagnostic-only and can enforce a reviewed-dataset gate. The synthetic cases remain draft-only until reviewed by qualified educators; no educational-effectiveness claim is currently justified.
- Without a configured Gemini API key, Writing uses a demo adapter; it does not provide genuine grammar analysis and must be labelled accordingly.

## Testing strategy

### Backend
- Unit tests: scoring, writing-result validation, vocabulary scheduling, quotas, recommendations, usage/token-cost accounting, and offline evaluation input validation.
- API tests: auth, ownership, validation, pagination, status and error behavior.
- Integration tests: PostgreSQL constraints, transaction boundaries, and concurrent quota reservations.
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
- Smoke-test the production origin, CSRF/session cookies, readiness endpoint, and provider failure state after deployment.

### CI baseline
- Backend checks/tests, frontend lint/TypeScript/tests/production build, Compose validation, and container image builds run in GitHub Actions.
- Review the exact workflow run for the final merge commit before release; a successful CI run is not a substitute for human review or production smoke tests.
