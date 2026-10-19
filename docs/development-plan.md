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

Status: **Core account lifecycle implemented and verified in CI.** Session auth, profile preferences, owner-scoped placement attempts, server-side scoring, email verification, verification resend, and password reset/recovery have automated tests. New accounts remain inactive until the learner explicitly confirms the verification action. Production SMTP delivery, abuse monitoring, and deployment-specific security checks remain external release gates.

### Phase 4 — Writing MVP
Provider-neutral adapter, fake provider for tests, versioned result schema, span validation, history, timeout/failure handling, usage accounting, evaluation baseline.

Current status: **Writing application flow and quality tooling are implemented; release-quality evaluation is intentionally gated.** The server-side Gemini adapter uses a bounded timeout and output ceiling, captures provider-reported token counts, validates the versioned result schema and non-overlapping source spans, and persists aggregate usage without storing raw provider payloads in the usage ledger. Optional cost estimates require explicitly configured active price-sheet rates. The Writing Studio displays corrected text, individual correction spans, explanations, provider status, and limitations. The evaluation harness validates dataset/prediction shapes and source offsets, reports correction/span metrics and false positives, and refuses to mark draft annotations as a passed quality gate. The nine synthetic cases remain `draft_requires_human_review`; a qualified educator must review them and a measured run must be performed against the configured live provider before making educational-quality claims.

### Phase 5 — Reading and Vocabulary

Vocabulary status: **Verified in CI on PR #6** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39221335506)); cross-module acceptance coverage and atomic review persistence are **verified in CI on PR #17** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39229554954)). The MVP includes owner-scoped cards, case-insensitive duplicate prevention, due-card filtering, a deterministic SM-2-inspired schedule, review grades, and a responsive review UI. Review-state changes and activity events now share a transaction, and the view locks the owned card while applying a review. Immutable vocabulary review-event snapshots and an owner-scoped paginated history endpoint are implemented in the current branch; pending CI verification. Remaining vocabulary work includes curated licensed word packs and richer progress analytics.

Reading core flow: **Verified in CI on PR #7** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39221772403)). Attempt-history UI and paginated history endpoint are covered by PR #16, with CI passing for backend, frontend, and container build. The initial flow includes two original A2/B1 passages, published-only public endpoints, hidden answer keys before submission, exact-answer validation, server-side scoring, owner-scoped saved attempts, feedback explanations, and a responsive learner page. Remaining work includes immutable question-version snapshots, authoring/content review, and more reviewed passages.

### Phase 6 — Progress and personalization

Progress status: **Verified in CI on PR #8** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39222238189)). The dashboard reads persisted session counts, vocabulary review outcomes, due/mastered word counts, reading/writing/placement totals, current streak, and recent activity from an authenticated API. Learning activity events are written by the corresponding backend flows. Study duration remains intentionally unreported until reliable duration tracking is designed.

Rule-based recommendations: **Verified in CI on PR #9** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39222517527)). Up to three next steps are selected from persisted due-word and module-history evidence, with a human-readable reason and direct route. This is a deterministic heuristic, not an AI-generated claim.

Remaining: additional timezone/history edge-case coverage and validation of quota concurrency against production PostgreSQL. Provider token/cost accounting is now implemented in PR #18; estimates require configured rates and are not billing records.

### Phase 7 — Frontend integration
Complete learner flows, RTL/LTR and accessibility checks, E2E scenarios, production build checks.

### Phase 8 — Usage controls

Usage status: **Basic durable quota verified in CI on PR #10** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39222991351)). Writing requests reserve a database-backed slot before provider work; the rolling 24-hour default is 30 submissions per learner and provider failures consume a slot. A private usage summary exposes used/remaining slots and character volume. A per-hour DRF throttle remains as an additional guard.

Provider-reported token metadata and optional rate-configured cost estimates are implemented in PR #18. A PostgreSQL-only concurrent-reservation regression test and PostgreSQL-backed backend CI service are added in PR #34 and await CI verification. Remaining: operational alerting and verification against the actual production topology. Do not use this MVP ledger for billing.

### Phase 9 — Optional RAG
Proceed only with a concrete use case; evaluate source rights, retrieval quality, answer quality, and evidence attribution separately.

### Phase 10 — Release

Release tooling status: **Verified in CI on PR #13** ([run](https://github.com/SoheilAbdollahii/english-learning-ai/actions/runs/39224375843)). Added backend/frontend Dockerfiles, a local PostgreSQL Docker Compose setup, a database/migration readiness endpoint, and a release checklist that separates local smoke tests from production requirements.

Remaining before production: execute the container smoke test in a Docker-capable environment; validate PostgreSQL quota concurrency; configure real HTTPS/proxy/cache/secrets and SMTP; complete privacy and backup/restore drills; complete educator review and live-provider Writing evaluation; and run the final release regression.

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
