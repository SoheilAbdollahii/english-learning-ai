"""Offline metrics for manually reviewed Writing evaluation cases.

This module never calls a live AI provider. Predictions should be generated and
reviewed separately, then passed in keyed by case id.
"""


def evaluate_predictions(cases, predictions):
    expected_ids = {case["id"] for case in cases}
    missing = expected_ids - set(predictions)
    if missing:
        raise ValueError(f"Missing predictions for cases: {', '.join(sorted(missing))}")

    accepted = 0
    unchanged_cases = 0
    false_positives = 0
    true_positive_spans = 0
    predicted_span_count = 0
    reference_span_count = 0

    for case in cases:
        prediction = predictions[case["id"]]
        corrected_text = prediction.get("corrected_text")
        predicted_errors = prediction.get("errors", [])
        if corrected_text in case["acceptable_corrected_texts"]:
            accepted += 1

        if not case["should_change"]:
            unchanged_cases += 1
            if corrected_text != case["original_text"] or predicted_errors:
                false_positives += 1

        reference_spans = {
            (item["category"], item["start"], item["end"], item["original"])
            for item in case["reference_errors"]
        }
        predicted_spans = {
            (item.get("category"), item.get("start"), item.get("end"), item.get("original"))
            for item in predicted_errors
        }
        true_positive_spans += len(reference_spans & predicted_spans)
        predicted_span_count += len(predicted_spans)
        reference_span_count += len(reference_spans)

    precision = true_positive_spans / predicted_span_count if predicted_span_count else (1.0 if not reference_span_count else 0.0)
    recall = true_positive_spans / reference_span_count if reference_span_count else (1.0 if not predicted_span_count else 0.0)
    return {
        "case_count": len(cases),
        "acceptable_correction_rate": accepted / len(cases) if cases else 0.0,
        "false_positive_correction_rate": false_positives / unchanged_cases if unchanged_cases else 0.0,
        "span_precision": precision,
        "span_recall": recall,
        "unchanged_case_count": unchanged_cases,
        "note": "Draft synthetic set only; metrics are not a validated educational effectiveness claim.",
    }
