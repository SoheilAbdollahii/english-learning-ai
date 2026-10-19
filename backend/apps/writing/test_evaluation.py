import json
from pathlib import Path

import pytest

from .evaluation import evaluate_predictions
from .services import WritingProviderError, validate_result


DATASET_PATH = Path(__file__).with_name("evaluation_cases.json")


def test_synthetic_evaluation_dataset_has_aligned_reference_spans():
    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    assert len(cases) >= 8
    assert {case["level"] for case in cases} >= {"A2", "B1"}
    assert any(not case["should_change"] for case in cases)
    for case in cases:
        assert case["annotation_status"] == "draft_requires_human_review"
        for error in case["reference_errors"]:
            assert case["original_text"][error["start"]:error["end"]] == error["original"]


def test_offline_evaluation_metrics_report_false_positives_and_span_scores():
    cases = [
        {"id": "fix", "original_text": "She go.", "should_change": True, "acceptable_corrected_texts": ["She goes."], "reference_errors": [{"category": "grammar", "start": 4, "end": 6, "original": "go"}]},
        {"id": "keep", "original_text": "Hello there.", "should_change": False, "acceptable_corrected_texts": ["Hello there."], "reference_errors": []},
    ]
    predictions = {
        "fix": {"corrected_text": "She goes.", "errors": [{"category": "grammar", "start": 4, "end": 6, "original": "go"}]},
        "keep": {"corrected_text": "Hello there!", "errors": []},
    }
    metrics = evaluate_predictions(cases, predictions)
    assert metrics["case_count"] == 2
    assert metrics["acceptable_correction_rate"] == 0.5
    assert metrics["false_positive_correction_rate"] == 1.0
    assert metrics["span_precision"] == 1.0
    assert metrics["span_recall"] == 1.0


def test_evaluation_rejects_missing_predictions():
    with pytest.raises(ValueError, match="Missing predictions"):
        evaluate_predictions([{"id": "required"}], {})


def test_evaluation_rejects_unexpected_predictions():
    case = {"id": "expected", "original_text": "Hi.", "should_change": False, "acceptable_corrected_texts": ["Hi."], "reference_errors": []}
    with pytest.raises(ValueError, match="Unexpected predictions"):
        evaluate_predictions([case], {"expected": {"corrected_text": "Hi.", "errors": []}, "typo-id": {"corrected_text": "Hi.", "errors": []}})


def test_evaluation_rejects_duplicate_case_ids():
    case = {"id": "duplicate", "original_text": "Hi.", "should_change": False, "acceptable_corrected_texts": ["Hi."], "reference_errors": []}
    with pytest.raises(ValueError, match="Duplicate case ids"):
        evaluate_predictions([case, case], {})


def test_evaluation_rejects_malformed_prediction_shapes():
    case = {"id": "case", "original_text": "Hi.", "should_change": False, "acceptable_corrected_texts": ["Hi."], "reference_errors": []}
    with pytest.raises(ValueError, match="corrected_text"):
        evaluate_predictions([case], {"case": {"errors": []}})
    with pytest.raises(ValueError, match="errors must be a list"):
        evaluate_predictions([case], {"case": {"corrected_text": "Hi.", "errors": {}}})


def test_result_validation_rejects_unknown_category_and_oversized_feedback():
    base = {
        "schema_version": 1,
        "corrected_text": "I am happy.",
        "errors": [{"category": "made_up", "start": 0, "end": 1, "original": "I", "correction": "I", "explanation": "Example."}],
        "general_feedback": "Feedback.",
        "limitations": [],
    }
    with pytest.raises(WritingProviderError, match="category"):
        validate_result("I am happy.", base)
    base["errors"] = []
    base["general_feedback"] = "x" * 2001
    with pytest.raises(WritingProviderError, match="feedback"):
        validate_result("I am happy.", base)


def test_gemini_provider_rejects_oversized_http_response(monkeypatch):
    from .services import GeminiWritingProvider

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, size=-1):
            return b"x" * (size + 1)

    monkeypatch.setattr("apps.writing.services.urlopen", lambda *_args, **_kwargs: FakeResponse())
    with pytest.raises(WritingProviderError, match="maximum allowed size"):
        GeminiWritingProvider(api_key="test-secret").analyze("A sample sentence.")



def test_draft_dataset_metrics_never_claim_quality_gate_passed():
    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    predictions = {
        case["id"]: {
            "corrected_text": case["acceptable_corrected_texts"][0],
            "errors": case["reference_errors"],
        }
        for case in cases
    }
    metrics = evaluate_predictions(cases, predictions)
    assert metrics["case_count"] == len(cases)
    assert metrics["quality_gate_passed"] is False
    assert metrics["annotation_statuses"] == ["draft_requires_human_review"]
    assert "diagnostics only" in metrics["note"]


def test_evaluation_rejects_prediction_span_that_does_not_match_source():
    case = {
        "id": "case",
        "original_text": "She go.",
        "should_change": True,
        "acceptable_corrected_texts": ["She goes."],
        "reference_errors": [{"category": "grammar", "start": 4, "end": 6, "original": "go"}],
    }
    predictions = {
        "case": {
            "corrected_text": "She goes.",
            "errors": [{"category": "grammar", "start": 4, "end": 6, "original": "XX"}],
        }
    }
    with pytest.raises(ValueError, match="does not match"):
        evaluate_predictions([case], predictions)


def test_evaluation_rejects_overlapping_predicted_spans():
    case = {
        "id": "case",
        "original_text": "She goes.",
        "should_change": True,
        "acceptable_corrected_texts": ["She goes."],
        "reference_errors": [{"category": "grammar", "start": 4, "end": 8, "original": "goes"}],
    }
    predictions = {
        "case": {
            "corrected_text": "She goes.",
            "errors": [
                {"category": "grammar", "start": 4, "end": 6, "original": "go"},
                {"category": "grammar", "start": 5, "end": 8, "original": "oes"},
            ],
        }
    }
    with pytest.raises(ValueError, match="overlap"):
        evaluate_predictions([case], predictions)


def test_evaluation_rejects_invalid_reference_spans():
    case = {
        "id": "case",
        "original_text": "Hello.",
        "should_change": True,
        "acceptable_corrected_texts": ["Hello!"],
        "reference_errors": [{"category": "grammar", "start": 0, "end": 1, "original": "X"}],
    }
    with pytest.raises(ValueError, match="does not match"):
        evaluate_predictions([case], {"case": {"corrected_text": "Hello!", "errors": []}})
