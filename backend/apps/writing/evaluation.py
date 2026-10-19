"""Offline metrics for manually reviewed Writing evaluation cases.

The helper is intentionally provider-agnostic and never calls an AI API. Metrics
from draft annotations are diagnostics only; they are not a quality gate.
"""

ALLOWED_CATEGORIES = {"grammar", "spelling", "punctuation", "word_choice", "style"}


def _validate_case(case, index):
    if not isinstance(case, dict):
        raise ValueError(f"Case at index {index} must be an object")
    case_id = case.get("id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("Every case must have a non-empty string id")
    for field in ("original_text", "should_change", "acceptable_corrected_texts", "reference_errors"):
        if field not in case:
            raise ValueError(f"Case {case_id} is missing required field: {field}")
    if not isinstance(case["original_text"], str) or not case["original_text"]:
        raise ValueError(f"Case {case_id} original_text must be a non-empty string")
    if not isinstance(case["should_change"], bool):
        raise ValueError(f"Case {case_id} should_change must be a boolean")
    acceptable = case["acceptable_corrected_texts"]
    if not isinstance(acceptable, list) or not acceptable or not all(isinstance(item, str) for item in acceptable):
        raise ValueError(f"Case {case_id} acceptable_corrected_texts must be a non-empty list of strings")
    errors = case["reference_errors"]
    if not isinstance(errors, list):
        raise ValueError(f"Case {case_id} reference_errors must be a list")
    spans = []
    for error in errors:
        if not isinstance(error, dict):
            raise ValueError(f"Reference error for {case_id} must be an object")
        category, start, end, original = (error.get(key) for key in ("category", "start", "end", "original"))
        if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Reference error for {case_id} has an invalid category")
        if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(case["original_text"]):
            raise ValueError(f"Reference error for {case_id} has invalid offsets")
        if not isinstance(original, str) or case["original_text"][start:end] != original:
            raise ValueError(f"Reference error for {case_id} does not match the source text")
        spans.append((start, end))
    for previous, current in zip(sorted(spans), sorted(spans)[1:]):
        if current[0] < previous[1]:
            raise ValueError(f"Reference errors overlap for case {case_id}")
    if case["should_change"] != bool(errors):
        # Some corrections may be whole-sentence/register decisions, but those must
        # be explicitly documented rather than silently misrepresented as span errors.
        if not case.get("spanless_change_reason"):
            raise ValueError(f"Case {case_id} should document spanless changes or align should_change with reference_errors")
    status = case.get("annotation_status", "unmarked")
    if not isinstance(status, str) or not status:
        raise ValueError(f"Case {case_id} annotation_status must be a non-empty string")


def evaluate_predictions(cases, predictions):
    if not isinstance(cases, list):
        raise ValueError("Cases must be a list")
    if not isinstance(predictions, dict):
        raise ValueError("Predictions must be an object keyed by case id")

    for index, case in enumerate(cases):
        _validate_case(case, index)
    case_ids = [case["id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate case ids are not allowed")

    expected_ids = set(case_ids)
    supplied_ids = set(predictions)
    missing = expected_ids - supplied_ids
    unexpected = supplied_ids - expected_ids
    if missing:
        raise ValueError(f"Missing predictions for cases: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"Unexpected predictions for cases: {', '.join(sorted(unexpected))")

    accepted = 0
    unchanged_cases = 0
    false_positives = 0
    true_positive_spans = 0
    predicted_span_count = 0
    reference_span_count = 0

    for case in cases:
        case_id = case["id"]
        prediction = predictions[case_id]
        if not isinstance(prediction, dict):
            raise ValueError(f"Prediction for {case_id} must be an object")
        corrected_text = prediction.get("corrected_text")
        predicted_errors = prediction.get("errors")
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
        offsets = []
        for item in predicted_errors:
            if not isinstance(item, dict):
                raise ValueError(f"Predicted error for {case_id} must be an object")
            category, start, end, original = (item.get(key) for key in ("category", "start", "end", "original"))
            if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
                raise ValueError(f"Predicted error for {case_id} has an invalid category")
            if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(case["original_text"]):
                raise ValueError(f"Predicted error for {case_id} has invalid offsets")
            if not isinstance(original, str) or case["original_text"][start:end] != original:
                raise ValueError(f"Predicted error for {case_id} does not match the source text")
            predicted_spans.add((category, start, end, original))
            offsets.append((start, end))
        if len(predicted_spans) != len(predicted_errors):
            raise ValueError(f"Prediction for {case_id} contains duplicate error spans")
        ordered_offsets = sorted(offsets)
        for previous, current in zip(ordered_offsets, ordered_offsets[1:]):
            if current[0] < previous[1]:
                raise ValueError(f"Predicted error spans overlap for case {case_id}")
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
    annotation_statuses = sorted({case.get("annotation_status", "unmarked") for case in cases})
    reviewed = bool(cases) and all(
        case.get("annotation_status") in {"reviewed", "adjudicated", "approved"}
        for case in cases
    )
    return {
        "case_count": len(cases),
        "acceptable_correction_rate": accepted / len(cases) if cases else 0.0,
        "false_positive_correction_rate": false_positives / unchanged_cases if unchanged_cases else 0.0,
        "span_precision": precision,
        "span_recall": recall,
        "unchanged_case_count": unchanged_cases,
        "annotation_statuses": annotation_statuses,
        "quality_gate_passed": reviewed,
        "note": (
            "Reviewed annotations detected; this result still requires human review of meaning preservation and explanations."
            if reviewed
            else "Draft/unreviewed annotations: metrics are diagnostics only and cannot be used as a quality or release claim."
        ),
    }
