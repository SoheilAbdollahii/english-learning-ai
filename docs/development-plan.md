# Development Roadmap and Acceptance Criteria

Status: initial estimate. Schedule depends on weekly availability, AI budget, hosting, and academic deadlines.

## Phases

### Phase 1 — Design
- [x] Initial architecture decisions.
- [x] Logical data model and endpoint inventory.
- [x] Security/testing baseline.
- [x] Writing evaluation methodology.
- [ ] Confirm remaining assumptions and numerical acceptance thresholds.

### Phase 2 — Development foundation
Create backend/frontend skeletons, environment configuration, PostgreSQL local setup, lint/tests/CI, and repeatable developer documentation.

### Phase 3 — Accounts and placement
Custom user model, profile, authentication, cross-user authorization tests, versioned placement assessment, server-side scoring.

### Phase 4 — Writing MVP
Provider-neutral adapter, fake provider for tests, versioned result schema, span validation, history, timeout/failure handling, usage accounting, evaluation baseline.

Current status: **In progress — implemented but unverified.** The branch includes the provider-neutral demo adapter, schema-v1 validation, owner-scoped submissions/history, and safe failure responses. The demo adapter is not a grammar evaluator. Real-provider timeouts, usage accounting, and an evaluation baseline are still outstanding.

### Phase 5 — Reading and Vocabulary
Curated licensed/versioned content, server-side Reading scoring, vocabulary review state and tested spaced-repetition rules.

### Phase 6 — Progress and personalization
Defined metrics from persisted records and transparent rule-based recommendations.

### Phase 7 — Frontend integration
Complete learner flows, RTL/LTR and accessibility checks, E2E scenarios, production build checks.

### Phase 8 — Usage controls
Server-enforced quotas and clear limit behavior. Defer payment integration until provider, market, and compliance needs are known.

### Phase 9 — Optional RAG
Proceed only with a concrete use case; evaluate source rights, retrieval quality, answer quality, and evidence attribution separately.

### Phase 10 — Release
Production configuration, migrations, backup strategy, privacy/logging review, deployment guide, and regression run.

## MVP acceptance criteria
- AC-01 Accounts: users authenticate and access only their own private records.
- AC-02 Placement: server-calculated score is saved with assessment/scoring version.
- AC-03 Writing: output is schema-validated; provider failure is not reported as success.
- AC-04 Reading: user submits answers and sees server-calculated score and explanations.
- AC-05 Vocabulary: review outcome updates scheduling; exposure alone does not imply mastery.
- AC-06 Progress: dashboard metrics are defined and derived from recorded activity.
- AC-07 Internationalization: supported locales render with correct language and direction.
- AC-08 Usage: AI limits are enforced server-side and tested.
- AC-09 CI: backend/frontend checks run automatically and fail the workflow on failure.
- AC-10 Documentation: a new developer can configure, run, and test the project.

## Initial backlog
| ID | Priority | Item | Dependency | Acceptance signal |
|---|---|---|---|---|
| FOUNDATION-01 | P0 | Local development skeleton | Design | Both apps start from documented setup |
| FOUNDATION-02 | P0 | PostgreSQL and migrations | Backend skeleton | Clean migrations pass |
| FOUNDATION-03 | P0 | CI and quality checks | App skeletons | Checks run on push and PR |
| ACCOUNTS-01 | P0 | User/profile/auth | Foundation | Auth and cross-user tests pass |
| PLACEMENT-01 | P1 | Placement assessment | Accounts | Versioned scoring tests pass |
| WRITING-01 | P0 | AI provider adapter | Foundation | Fake provider tests pass offline |
| WRITING-02 | P0 | Writing schema validation | WRITING-01 | Invalid output rejected safely |
| WRITING-03 | P0 | Evaluation dataset | Annotation | Baseline metrics and limitations documented |
| READING-01 | P1 | Reading flow | Accounts/content | Scoring and history tests pass |
| VOCAB-01 | P1 | Vocabulary review | Accounts/word content | Scheduling has deterministic tests |
| PROGRESS-01 | P1 | Metrics/recommendations | Learning records | Recommendations trace to evidence |
| FRONTEND-01 | P0 | UI/API integration | API contract | Main journeys pass E2E tests |
| USAGE-01 | P1 | AI quotas | AI adapter | Quota bypass attempts fail |
| RELEASE-01 | P1 | Deployment checklist | MVP | Repeatable deployment/regression |
| RAG-01 | P2 | Retrieval research | Evaluation evidence | Proceed only with measured need |

## Status discipline
Use Not started, In progress, Implemented — unverified, and Verified. Code changes alone do not prove a feature works; verification requires relevant tests or a documented manual check.
