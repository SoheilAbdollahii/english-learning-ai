# Architecture Baseline

Status: proposed MVP design. This document describes intended architecture, not implemented application code.

## Product scope
The MVP includes accounts and learner profile, placement assessment, AI-assisted writing feedback, levelled reading comprehension, vocabulary review with spaced repetition, evidence-based progress summaries, bilingual-ready UI with RTL/LTR, server-side AI usage controls, tests, CI, and setup documentation.

Defer real payments, RAG/vector search, custom ML, microservices, and enterprise features until measurable requirements justify them.

## System design
- Frontend: Next.js and TypeScript.
- Backend: Django and Django REST Framework.
- Database: PostgreSQL.
- AI: provider-neutral adapter called only by the backend.
- API: versioned REST endpoints under /api/v1/.
- CI: GitHub Actions for backend and frontend quality checks.

The backend owns authorization, scoring, learning rules, persistence, AI orchestration, and quota enforcement. Provider credentials must never be exposed to the browser.

## Proposed layout
- backend/config: Django settings and root URLs
- backend/apps/accounts: identity and profile
- backend/apps/placement: assessment and scoring
- backend/apps/writing: submissions, AI orchestration, validated results
- backend/apps/reading: passages, questions, attempts
- backend/apps/vocabulary: word state and reviews
- backend/apps/progress: metrics and rule-based recommendations
- backend/apps/usage: server-enforced quotas and usage records
- frontend/src/app: Next.js routes
- frontend/src/features: feature-oriented UI
- docs: architecture, data model, API, security, evaluation, roadmap
- .github/workflows: automated checks

Use a modular monolith: one Django deployment with domain-oriented apps. Avoid cross-module access to another app's internals; use explicit service interfaces. Do not create generic abstractions before multiple concrete use cases require them.

## Architecture decisions (proposed)
1. Modular monolith: lower operational overhead than microservices for a small team.
2. DRF: mature validation, permissions, serializers, and API testing.
3. PostgreSQL: relational integrity and transactions fit learning records.
4. Next.js + TypeScript: structured routes and typed UI interfaces.
5. Versioned REST API: controlled contract evolution.
6. AI provider adapter: centralizes timeouts, usage tracking, and provider replacement.
7. Rule-based personalization: explainable and testable without training data.
8. No RAG in initial MVP: add only after a concrete use case and evaluation.
9. Session authentication with secure HttpOnly cookies and CSRF is the default if frontend/backend deployment topology supports it. Confirm domain topology before implementation; choose and document a different mechanism if necessary.
10. Tests and CI are foundational, not post-release cleanup.

## Cross-cutting requirements
- Enforce ownership and permissions server-side for every private record.
- Validate inputs and AI output at trust boundaries.
- Bound request size, latency, and AI usage.
- Keep secrets out of source control and redact sensitive data from logs.
- Make dashboard metrics traceable to persisted activity.
- Support keyboard access, accessible errors, and RTL/LTR layouts.
- Mark features verified only after relevant tests or documented manual checks pass.

## Open assumptions
AI provider, budget, hosting, domain topology, content sources/licensing, and retention policy are not yet fixed. Background jobs are not mandatory at the start; add a queue only if measured latency or workload requires it.
