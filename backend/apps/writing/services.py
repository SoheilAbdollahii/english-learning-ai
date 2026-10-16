"""Provider-neutral writing analysis adapter and result validation.

The demo provider intentionally does not claim to correct grammar. It exercises
persistence, API contracts, and UI integration until a real provider is selected.
"""

from typing import Any


class WritingProviderError(Exception):
    """Raised when a writing provider cannot produce a usable result."""


class DemoWritingProvider:
    name = "demo"

    def analyze(self, text: str) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "corrected_text": text,
            "errors": [],
            "general_feedback": "The demo provider is connected. No grammar corrections have been generated yet.",
            "limitations": [
                "Demo mode does not evaluate grammar, spelling, or writing quality.",
                "Connect and evaluate a real provider before using this result for learning decisions.",
            ],
        }


def get_provider():
    """Return the configured provider; production provider selection is intentionally deferred."""
    return DemoWritingProvider()


def validate_result(original_text: str, result: Any) -> dict[str, Any]:
    """Validate the versioned result and ensure error spans match the submitted text.

    Offsets use Python Unicode code points with an inclusive start and exclusive end.
    """
    if not isinstance(result, dict):
        raise WritingProviderError("Provider returned an invalid result.")
    if result.get("schema_version") != 1:
        raise WritingProviderError("Provider returned an unsupported result schema.")
    if not isinstance(result.get("corrected_text"), str):
        raise WritingProviderError("Provider returned an invalid corrected text field.")
    if not isinstance(result.get("general_feedback"), str):
        raise WritingProviderError("Provider returned invalid feedback.")
    limitations = result.get("limitations")
    errors = result.get("errors")
    if not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations):
        raise WritingProviderError("Provider returned invalid limitations.")
    if not isinstance(errors, list):
        raise WritingProviderError("Provider returned an invalid error list.")

    validated_errors = []
    for error in errors:
        if not isinstance(error, dict):
            raise WritingProviderError("Provider returned an invalid error item.")
        category = error.get("category")
        start = error.get("start")
        end = error.get("end")
        original = error.get("original")
        correction = error.get("correction")
        explanation = error.get("explanation")
        if not isinstance(category, str) or not category.strip():
            raise WritingProviderError("Provider returned an invalid error category.")
        if type(start) is not int or type(end) is not int:
            raise WritingProviderError("Provider returned invalid error offsets.")
        if start < 0 or end <= start or end > len(original_text):
            raise WritingProviderError("Provider returned out-of-range error offsets.")
        if not isinstance(original, str) or original_text[start:end] != original:
            raise WritingProviderError("Provider returned an error span that does not match the submitted text.")
        if not isinstance(correction, str) or not isinstance(explanation, str):
            raise WritingProviderError("Provider returned an invalid correction or explanation.")
        validated_errors.append({
            "category": category,
            "start": start,
            "end": end,
            "original": original,
            "correction": correction,
            "explanation": explanation,
        })

    return {
        "schema_version": 1,
        "corrected_text": result["corrected_text"],
        "errors": validated_errors,
        "general_feedback": result["general_feedback"],
        "limitations": limitations,
    }


def analyze_writing(text: str) -> tuple[str, dict[str, Any]]:
    provider = get_provider()
    try:
        raw_result = provider.analyze(text)
    except Exception as exc:
        raise WritingProviderError("Writing analysis provider failed.") from exc
    return provider.name, validate_result(text, raw_result)
