# Initial Data Model

Status: implemented profile, placement, writing, and initial vocabulary card schemas; Reading and progress entities remain proposals until implemented with migrations and tests.

## Design rules
- The current scaffold uses Django's built-in User model to avoid premature custom-auth complexity. Revisit any custom-user requirement before production data exists; changing user models after launch is a high-cost migration.
- Give every private learner record explicit ownership.
- Store timestamps in UTC.
- Use database constraints as well as application validation.
- Version assessment content and AI schemas where historical interpretation depends on them.
- Define data retention and deletion before production launch.

## Implemented: Profile
- One-to-one relation to the authenticated Django user.
- locale: en or fa, default en.
- target_level: A1-C2 or unknown, default unknown.
- daily_goal_minutes: integer from 5 to 180, default 15.
- timezone: string, default UTC.
- Creation and update timestamps.
- Profile creation is lazy on GET /api/v1/me/ and the endpoint only addresses the authenticated user.

## Proposed core entities

### Accounts and placement
- User: Django authentication identity.
- PlacementAttempt: user, assessment version, answers, score, estimated level, completion time, scoring version.

### Writing
- WritingSubmission: owner, original text, status, creation time, optional context.
- WritingAnalysis: submission, schema version, validated result, safe provider/model metadata, latency and usage metadata when available, failure category.
- WritingError: analysis, category, source span, original text, suggested correction, explanation, and confidence only if meaningfully calibrated.

Keep a canonical validated analysis result. Add normalized error records only where querying or analytics need them. Raw model output is not trusted application data.

### Reading (initial implementation)
- Passage: slug, title, original passage body, CEFR level, content version, source note, publication state, and creation timestamp. The public API only lists published passages.
- ReadingQuestion: passage, prompt, options, correct option, explanation, points, and order. Public serializers intentionally omit correct options and explanations until an attempt is submitted.
- ReadingAttempt: user, passage reference and version, submitted answers, result/explanation snapshots, server-calculated score and percentage, and completion timestamp.
- Original A2 and B1 sample passages are seeded through a data migration. Follow-up work: enforce immutable published content versions and add normalized per-question answer-event records if analytics require them.

### Vocabulary (initial implementation)
- VocabularyCard: user, word, English definition, optional example and translation, status, repetitions, interval, ease factor, due timestamp, last review timestamp, and created/updated timestamps.
- A case-insensitive database uniqueness constraint prevents the same learner from saving duplicate words.
- The review endpoint accepts a grade from 0 to 5 and applies a deterministic SM-2-inspired scheduling function. Grades below 3 restart the interval; successful reviews grow intervals. A card is not marked mastered merely because it is displayed.
- Automated tests cover owner isolation, duplicate prevention, due filtering, input bounds, and interval transitions.
- Follow-up: immutable VocabularyReview event records and curated word content with source/license metadata.

### Progress and usage
- LearningActivity: optional domain event for timeline and summary; do not build a generic event-sourcing platform.
- Recommendation: compute on demand initially unless persistence is needed for history or reproducibility.
- UsageRecord: user, operation, timestamp, outcome, and provider usage/cost metadata where available.
- Plan/UsagePolicy: optional quota configuration; real payments remain out of initial MVP.

## Key constraints
- Test cross-user access denial.
- Use transactions for completed attempts and their answers.
- Add uniqueness constraints for per-user vocabulary state.
- Define deletion behavior to avoid accidental loss of audit/evaluation records.
- Keep a stable writing-error taxonomy and document changes.
- Do not expose answer keys before submission.
- Use decimal or integer minor units for monetary accounting, not floating-point arithmetic.
