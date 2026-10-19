# Production Release Checklist

This checklist is a release gate, not a statement that deployment has already happened. Complete it against the final merged commit and record evidence in the release issue.

## 1. Source and CI
- [ ] Merge stacked pull requests in dependency order only after review; verify each base/head relationship before merging.
- [ ] Run the complete GitHub Actions CI suite on the final merge commit (backend tests, frontend lint/typecheck/tests/build, Compose validation, image builds).
- [ ] Review unresolved comments, security findings, dependency alerts, and migration diffs.
- [ ] Tag the exact commit intended for release and retain the previous known-good image/tag for rollback.

## 2. Secrets and environment
- [ ] Set a high-entropy `DJANGO_SECRET_KEY` through the deployment secret manager; never use the local placeholder.
- [ ] Set `DJANGO_DEBUG=false`, exact `DJANGO_ALLOWED_HOSTS`, and production `DJANGO_CSRF_TRUSTED_ORIGINS` values.
- [ ] Configure database credentials independently of the sample Compose defaults and restrict database network access.
- [ ] Store `GEMINI_API_KEY` only in server-side secrets if provider-backed Writing is enabled. Rotate any key that may have been exposed.
- [ ] Choose explicit per-hour and per-day Writing quotas. Configure input/output cost rates only from the active provider price sheet; estimates are not invoices.
- [ ] Configure `REDIS_URL` to a shared, authenticated/private Redis service for multi-worker throttling; verify throttles across workers and failover behavior.
- [ ] Confirm the deployed frontend's backend URL and that no provider key is bundled into client assets.

## 3. HTTPS and edge configuration
- [ ] Terminate HTTPS at a trusted reverse proxy/load balancer and redirect HTTP to HTTPS there.
- [ ] Verify Django sees the correct scheme behind the proxy before enabling proxy SSL headers; trust forwarded headers only from controlled infrastructure.
- [ ] Verify secure session and CSRF cookies in a real browser on the deployed origin.
- [ ] Configure HSTS only after HTTPS works across every covered hostname; start conservatively and expand policy only after validation.
- [ ] Restrict inbound ports; do not expose PostgreSQL or internal service ports publicly.
- [ ] Check allowed hosts, CSRF origins, CORS policy (if introduced), content security policy, and security headers for the actual topology.

## 4. Data, migrations, and recovery
- [ ] Take a database backup and test restore to a separate environment before first release and before risky migrations.
- [ ] Run migrations as a controlled one-off release task; do not allow each application replica to migrate concurrently.
- [ ] Verify migrations are backward-compatible with the rollout/rollback strategy and review destructive operations.
- [ ] Define data retention, account deletion, export, and provider data-processing disclosures before accepting real learner data.
- [ ] Confirm database encryption, access audit, monitoring, and backup retention appropriate to the deployment.

## 5. AI Writing quality, safety, and cost
- [ ] Decide whether the product may launch with the demo Writing adapter. If so, make its non-evaluating behavior unmistakable in the UI and marketing.
- [ ] Have qualified English educators review the synthetic fixture, offsets, categories, acceptable corrections, and no-change examples; document disagreements and adjudication.
- [ ] Run the same reviewed cases against the exact configured provider/model/prompt and archive predictions/metrics without personal learner data.
- [ ] Human-review false positives, meaning preservation, explanation correctness, ambiguous/register-sensitive inputs, and a sample of failures.
- [ ] Set release thresholds after measuring a baseline; do not present the current draft metrics as validated educational effectiveness.
- [ ] Verify quotas under concurrent requests against PostgreSQL, provider timeout/error handling, output limits, token accounting, and cost estimates.
- [ ] Establish provider outage alerts and a safe user-facing fallback. Never imply demo output is genuine grammar analysis.

## 6. Product acceptance and operations
- [ ] Complete signup/login/logout, CSRF, profile, placement, Writing, vocabulary review, reading attempt, progress, and cross-user authorization smoke tests.
- [ ] Verify Persian/English switching, RTL/LTR layout, keyboard navigation, accessible labels, and responsive layouts.
- [ ] Add email verification, account recovery, abuse handling, and support/contact process before a broad public launch.
- [ ] Confirm liveness and readiness endpoints, logs without secrets/raw learner text, error monitoring, latency/error dashboards, and provider-cost monitoring.
- [ ] Verify a rollback procedure and rehearse it; document the person responsible for incident response.
- [ ] Record the deployment URL, release commit, CI run, migration result, smoke-test evidence, and unresolved risks.

## Current known blockers before broad public launch
- Human-reviewed Writing evaluation and a measured run against the configured live provider are not yet complete.
- Email verification and password recovery are not implemented.
- Production infrastructure, HTTPS/proxy configuration, backup/restore, monitoring, privacy/retention policy, and a real deployment have not been verified by repository CI.
- Stacked pull requests must be reviewed and merged in dependency order before their features are in the default branch.
