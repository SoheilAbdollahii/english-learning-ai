# Phase 1 — Architecture Decisions and Integration Plan

Status: approved for implementation planning; product-code changes remain subject to their phase-specific review.
Date: 2026-10-19

## 1. Executive decision

Keep the existing product as a modular monolith. Do not rewrite the repository or split services. The implementation already contains Django/DRF domain apps, a Next.js/TypeScript client, PostgreSQL support, versioned REST endpoints, session/CSRF authentication, provider-isolated Writing analysis, and automated tests. The highest-risk issue is integration: the feature work is held in a stacked PR chain while `main` currently contains only the README.

This document is a decision proposal, not a claim that the product is production-ready.

## 2. Architecture decisions

| Area | Decision | Reason / condition |
|---|---|---|
| Application shape | Modular monolith | Appropriate operational complexity for the current MVP; preserve domain app boundaries. |
| Backend | Django + Django REST Framework | Existing implementation supports permissions, serializers, server-side scoring, and API tests. |
| Frontend | Next.js + TypeScript | Existing routes and typed client; retain same-origin `/api/*` proxy. |
| Persistence | PostgreSQL in integration/production; SQLite for quick local setup only | Use PostgreSQL for locking, constraints, and production-like integration tests. |
| API | REST under `/api/v1/` | Keep the current contract; document changes and avoid breaking clients. |
| Authentication | Django session + CSRF | Keep for the same-origin browser proxy; re-evaluate only if deployment topology changes. |
| AI Writing | Backend-only provider adapter, validated schema, bounded input/output, quotas | Never expose provider credentials to the browser; fake/demo provider in CI. |
| Personalization | Explainable deterministic rules | Avoid unsupported claims and ML complexity until sufficient evaluated data exists. |
| AI retrieval / RAG | Deferred | No evidenced MVP requirement justifies the extra retrieval, evaluation, and data-governance complexity yet. |
| Background jobs | Not required by default | Introduce a queue only if latency/load measurements justify it. |
| Deployment | Containerized services; controlled one-off migration in production | Do not run migrations concurrently from each production replica. |

## 3. Current architecture and domain boundaries

- `accounts`: Django identity, profile, session authentication and registration.
- `placement`: assessment content, server-side scoring, placement attempts.
- `writing`: submissions, provider adapter, result validation and history.
- `reading`: published passages, comprehension questions, attempts and result snapshots.
- `vocabulary`: learner-owned cards and review scheduling.
- `progress`: persisted activity and explainable recommendations.
- `usage`: durable AI quota reservation, provider token metadata and optional cost estimates.
- `frontend`: learner routes, locale/RTL support and same-origin API proxy.
- `docs` and GitHub Actions: API contract, release gates, evaluation guidance and automated checks.

Cross-app operations should use narrow service functions and database transactions where a single learner action updates multiple records. Avoid a generic event-sourcing layer or microservices.

## 4. Integration topology

The currently open PRs form this dependency chain:

`#1 architecture → #2 dashboard shell → #3 session auth → #4 placement → #5 Writing → #6 vocabulary → #7 Reading → #8 progress → #9 recommendations → #10 usage ledger → #11 registration → #12 Writing evaluation hardening → #13 release readiness → #14 locale/RTL → #16 Reading history → #17 learning-flow integration → #18 token/cost accounting → #19 evaluation guardrails → #20 release gates → #21 production security settings`.

PR #15 is not in the currently observed chain and must be inspected separately if it remains relevant. Do not merge a downstream PR directly to `main` before its required base changes have landed. Before each merge, re-check the live base/head SHAs, review unresolved comments and run CI on the candidate merge commit.

Recommended order: validate #1 into `main`, then advance one dependent PR at a time in the observed order. If repository permissions or branch protections prevent this, prepare a reviewed integration branch and open a single explicit integration PR; do not silently retarget or merge the stack.

## 5. Confirmed risks and required actions

### P0 — No integrated release branch on main
Observed: `main` contains only `README.md`; the feature implementation is held in the stacked PRs.
Action: safely integrate the chain in dependency order and run the full CI suite on the final candidate commit.

### P1 — Frontend dependency installation is not pinned
Observed: `frontend/package.json` defines semver ranges and the repository tree inspected at the latest stack head did not contain `frontend/package-lock.json`; CI runs `npm install`.
Action: generate and commit a lockfile, switch CI to `npm ci`, and verify clean-install/build reproducibility. Do not hand-edit lockfile contents.

### P1 — Rate-limit deployment assumption needs verification
Observed: DRF throttles are configured, but the inspected Django settings do not define a shared cache backend. Django's default local-memory cache is process-local.
Action: configure a shared production cache (for example Redis) or enforce edge-level limits, and test limits across multiple application workers. Keep a simple local cache for local development if needed.

### P1 — Writing educational validity is not established
Observed: schema and span validation exist; the nine-case evaluation fixture is explicitly draft-only pending qualified human review.
Action: approve annotations, test the exact configured model/prompt against the reviewed set, inspect false positives and meaning changes, and set numerical thresholds only after a measured baseline.

### P1 — Public account lifecycle is incomplete
Observed: registration and session authentication exist; email verification and account recovery are not available.
Action: either implement and test recovery/verification before a broad public launch or explicitly restrict launch scope and communicate the limitation.

### P1 — Production environment is not verified
Observed: security settings are configurable, but proxy topology, shared cache, HTTPS/cookies, backup restore, and deployment smoke tests require real-environment evidence.
Action: treat `docs/release-checklist.md` as a mandatory gate; CI success alone is insufficient.

### P2 — Cross-record consistency and concurrency
Observed: some flows use atomic transactions (placement, Reading, vocabulary review), while Writing submission, usage accounting and activity recording are separate operations.
Action: define the expected failure semantics; add tests for partial failure and concurrent quota reservation on PostgreSQL before changing transaction boundaries.

## 6. Quality gates

Before a release candidate can be called integrated:
1. Every PR in the selected chain has been reviewed and merged in dependency order, or its changes are intentionally excluded and documented.
2. The final candidate commit passes backend `manage.py check` and `pytest`, frontend lint/typecheck/tests/build, Compose validation, and container builds.
3. Tests cover private-record ownership, CSRF/session behavior, server-side scoring, hidden answer keys, vocabulary transaction behavior, Writing provider failure and quota concurrency.
4. Frontend installation is reproducible with a committed lockfile and `npm ci`.
5. Production throttling uses a shared/edge-enforced mechanism and has multi-worker coverage.
6. Writing evaluation data is human-reviewed; the demo provider is visibly labelled and never presented as real grammar analysis.
7. Security, backup/restore, migration, retention/deletion, and post-deployment smoke-test evidence is recorded.

## 7. Explicitly out of scope for this phase

- Rewriting the existing app.
- Merging PRs or changing their bases without reviewing the live dependency graph.
- Adding RAG, payments, microservices, or a background queue without evidence.
- Claiming educational effectiveness based on the draft fixture.
- Claiming production readiness from a single successful CI run.

## 8. Next implementation sequence

1. Re-check the live dependency graph and integrate the PR stack in order, with review and CI evidence at each step.
2. Add a committed frontend lockfile and use `npm ci`.
3. Configure and test shared rate limiting for production.
4. Run the full test suite against the integrated candidate and fix verified failures.
5. Complete the human-reviewed Writing evaluation and remaining release gates.
