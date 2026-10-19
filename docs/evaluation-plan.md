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

## Starter fixture and local metric runner

A nine-case synthetic starter fixture lives at `backend/apps/writing/evaluation_cases.json`. It covers A2/B1 grammar, spelling, punctuation, word choice, correct sentences, ambiguity, informal register, and a run-on sentence. Its `annotation_status` is deliberately `draft_requires_human_review`: the spans and acceptable alternatives must be reviewed by qualified English educators before the fixture can be treated as a gold set or used for release claims.

The offline metric helper and CLI are available in `backend/apps/writing/evaluation.py` and `backend/apps/writing/evaluate_cli.py`. From the `backend/` directory, pass a JSON object keyed by case ID:

```bash
python -m apps.writing.evaluate_cli --predictions /path/to/predictions.json
```

The runner reports acceptable-correction rate, false-positive correction rate on no-change cases, and exact span precision/recall. It rejects missing or unexpected prediction IDs and malformed prediction shapes to reduce accidental evaluation of the wrong sample set. Exact span matching is intentionally strict; it may mark valid alternate spans as mismatches. The runner does not score meaning preservation or explanation quality automatically; those require human review. Never include identifiable learner writing in a public fixture.

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
