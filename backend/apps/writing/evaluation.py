"""Offline metrics for manually reviewed Writing evaluation cases.

This module never calls a live AI provider. Predictions should be generated and
reviewed separately, then passed in keyed by case id. Exact-span metrics are
strict diagnostics, not a substitute for human review.
"""


def evaluate_predictions(cases, predictions):
    if not isinstance(cases, list):
        raise ValueError("Cases must be a list")
    if not isinstance(predictions, dict):
        raise ValueError("Predictions must be an object keyed by case id")

    case_ids = [case.get("id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        raise ValueError("Every case must have a non-empty string id")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate case ids are not allowed")

    expected_ids = set(case_ids)
    supplied_ids = set(predictions)
    missing = expected_ids - supplied_ids
    unexpected = supplied_ids - expected_ids
    if missing:
        raise ValueError(f"Missing predictions for cases: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"Unexpected predictions for cases: {', '.join(sorted(unexpected))}")

    accepted = 0
    unchanged_cases = 0
    false_positives = 0
    true_positive_spans = 0
    predicted_span_count = 0
    reference_span_count = 0

    for case in cases:
        case_id = case["id"]
        for field in ("original_text", "should_change", "acceptable_corrected_texts", "reference_errors"):
            if field not in case:
                raise ValueError(f"Case {case_id} is missing required field: {field}")
        if not isinstance(case["original_text"], str):
            raise ValueError(f"Case {case_id} original_text must be a string")
        if not isinstance(case["should_change"], bool):
            raise ValueError(f"Case {case_id} should_change must be a boolean")
        if not isinstance(case["acceptable_corrected_texts"], list):
            raise ValueError(f"Case {case_id} acceptable_corrected_texts must be a list")
        if not isinstance(case["reference_errors"], list):
            raise ValueError(f"Case {case_id} reference_errors must be a list")

        prediction = predictions[case_id]
        if not isinstance(prediction, dict):
            raise ValueError(f"Prediction for {case_id} must be an object")
        corrected_text = prediction.get("corrected_text")
        predicted_errors = prediction.get("errors", [])
        if not isinstance(corrected_text, str):
            raise ValueError(f"Prediction for {case_id} needs string corrected_text")
        if not isinstance(predicted_errors, list):
            raise ValueError(f"Prediction for {case_id} errors must be a list")

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
        predicted_spans = set()
        for item in predicted_errors:
            if not isinstance(item, dict):
                raise ValueError(f"Predicted error for {case_id} must be an object")
            predicted_spans.add(
                (item.get("category"), item.get("start"), item.get("end"), item.get("original"))
            )
        true_positive_spans += len(reference_spans & predicted_spans)
        predicted_span_count += len(predicted_spans)
        reference_span_count += len(reference_spans)

    precision = (
        true_positive_spans / predicted_span_count
        if predicted_span_count
        else (1.0 if not reference_span_count else 0.0)
    )
    recall = (
        true_positive_spans / reference_span_count
        if reference_span_count
        else (1.0 if not predicted_span_count else 0.0)
    )
    return {
        "case_count": len(cases),
        "acceptable_correction_rate": accepted / len(cases) if cases else 0.0,
        "false_positive_correction_rate": false_positives / unchanged_cases if unchanged_cases else 0.0,
        "span_precision": precision,
        "span_recall": recall,
        "unchanged_case_count": unchanged_cases,
        "note": "Draft synthetic set only; metrics are not a validated educational effectiveness claim.",
    }
