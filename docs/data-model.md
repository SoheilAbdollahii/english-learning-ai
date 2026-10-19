# Initial Data Model

Status: logical model plus first implemented profile schema. Remaining domain entities are proposals until implemented with migrations and tests.

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

### Reading
- Passage: content, level, language, source/license metadata, content version, publication state.
- Question: passage, prompt, options, explanation, type and version.
- ReadingAttempt: user, passage version, score, start and completion timestamps.
- ReadingAnswer: attempt, question version, submitted answer, correctness, optional explanation snapshot.

### Vocabulary
- Word: lemma, part of speech, definitions, examples, level, locale, source/license metadata.
- VocabularyState: user, word, learning status, due date, interval/ease or equivalent algorithm state, last review.
- VocabularyReview: user, word, review type, response grade, review time.

Displaying a word is not evidence of mastery. Only recorded review outcomes update spaced-repetition state. The initial algorithm must be deterministic and unit-tested.

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
