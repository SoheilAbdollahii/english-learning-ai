# Initial Data Model

Status: proposed logical model. Field-level schema and migrations are not implemented yet.

## Design rules
- Use a custom Django user model from the first migration.
- Give every private learner record explicit ownership.
- Store timestamps in UTC.
- Use database constraints as well as application validation.
- Version assessment content and AI schemas where historical interpretation depends on them.
- Define data retention and deletion before production launch.

## Core entities

### Accounts and placement
- User: authentication identity.
- Profile: interface locale, learning preferences, optional goals.
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
