# AI Writing Evaluation Plan

The goal is educational correctness, not merely fluent output.

## Dataset
Create a small, versioned, manually reviewed dataset covering:
- Beginner through advanced writing.
- Grammar, spelling, punctuation, word choice, and sentence structure.
- Correct sentences that should remain unchanged.
- Ambiguous inputs with multiple valid corrections.
- Informal and context-dependent language.
- Examples where rewriting could change intended meaning.

Use consented or synthetic samples with appropriate rights. Do not commit identifiable student writing to a public repository. Document annotation guidance and reviewer disagreement.

## Annotation
For each sample record original text, intended meaning/context where available, reference error spans and categories, acceptable corrections, educational explanations, whether no correction is needed, ambiguity notes, and adjudication outcome.

## Metrics
1. False-positive correction rate: correct text incorrectly flagged or changed.
2. Correction acceptability: suggestions judged grammatical and context-appropriate.
3. Meaning preservation: whether intended meaning is retained.
4. Error-category precision/recall or reviewer agreement.
5. Span alignment quality under a documented offset convention.
6. Explanation quality: correctness, clarity, learner usefulness.
7. Robustness to ambiguity, malformed output, timeouts, and long inputs.
8. Median/tail latency and estimated cost per completed analysis where available.

Report sample size and uncertainty. A small convenience sample is not proof of broad educational effectiveness. Compare model/prompt changes on the same held-out examples when possible.

## Release gates
- All outputs pass schema and business-rule validation.
- No known critical security/privacy issue remains open.
- A reviewer-approved baseline dataset exists.
- False positives and meaning changes are inspected explicitly.
- Numerical product thresholds are chosen after baseline measurement, not invented beforehand.
- Provider outages and malformed output yield a recoverable failure state.

## Personalization
Recommendations must trace to persisted evidence and deterministic rules. Evaluate whether the referenced activity exists, the skill matches the observed weakness, unsupported claims are avoided, and changes in evidence lead to predictable changes in recommendations. Do not claim learning outcomes improve without an appropriate study.
