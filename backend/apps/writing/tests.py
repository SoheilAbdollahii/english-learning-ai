import pytest
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import WritingSubmission
from .services import WritingProviderError, validate_result

User = get_user_model()


@pytest.mark.django_db
def test_writing_submission_uses_demo_provider_and_persists_result():
    user = User.objects.create_user(username="writing-learner", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/writing/submissions/",
        {"text": "I enjoy learning English."},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "succeeded"
    assert response.data["provider"] == "demo"
    assert response.data["result"]["schema_version"] == 1
    assert "does not evaluate grammar" in response.data["result"]["limitations"][0]
    submission = WritingSubmission.objects.get(pk=response.data["id"])
    assert submission.user == user
    assert submission.original_text == "I enjoy learning English."


@pytest.mark.django_db
def test_writing_endpoints_require_authentication():
    client = APIClient()
    assert client.post("/api/v1/writing/submissions/", {"text": "Hello world."}, format="json").status_code == 403
    assert client.get("/api/v1/writing/submissions/").status_code == 403


@pytest.mark.django_db
def test_writing_submission_rejects_too_short_and_too_long_text():
    user = User.objects.create_user(username="writing-invalid", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.post("/api/v1/writing/submissions/", {"text": "  "}, format="json").status_code == 400
    assert client.post("/api/v1/writing/submissions/", {"text": "x" * 5001}, format="json").status_code == 400


@pytest.mark.django_db
def test_writing_history_and_details_are_owner_scoped():
    owner = User.objects.create_user(username="writing-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="writing-other", password="Strong-test-pass-123")
    submission = WritingSubmission.objects.create(user=owner, original_text="A sample sentence.")

    client = APIClient()
    client.force_authenticate(user=other)
    assert client.get(f"/api/v1/writing/submissions/{submission.id}/").status_code == 404
    assert client.get("/api/v1/writing/submissions/").data["results"] == []

    client.force_authenticate(user=owner)
    response = client.get("/api/v1/writing/submissions/")
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


def test_result_validation_rejects_spans_that_do_not_match_source_text():
    bad_result = {
        "schema_version": 1,
        "corrected_text": "I am happy.",
        "errors": [{"category": "grammar", "start": 0, "end": 1, "original": "X", "correction": "I", "explanation": "Example."}],
        "general_feedback": "Feedback.",
        "limitations": [],
    }
    with pytest.raises(WritingProviderError):
        validate_result("I am happy.", bad_result)


def test_result_validation_accepts_unicode_code_point_offsets():
    result = {
        "schema_version": 1,
        "corrected_text": "Café is nice.",
        "errors": [{"category": "spelling", "start": 0, "end": 4, "original": "Café", "correction": "Cafe", "explanation": "Example."}],
        "general_feedback": "Feedback.",
        "limitations": [],
    }
    validated = validate_result("Café is nice.", result)
    assert validated["errors"][0]["original"] == "Café"


@pytest.mark.django_db
def test_provider_failure_is_reported_as_failure_not_success(monkeypatch):
    import apps.writing.views as writing_views

    def fail(_text):
        raise WritingProviderError("private internal detail")

    monkeypatch.setattr(writing_views, "analyze_writing", fail)
    user = User.objects.create_user(username="writing-failure", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/writing/submissions/", {"text": "A sample sentence."}, format="json")
    assert response.status_code == 502
    assert response.data["code"] == "analysis_unavailable"
    assert "private internal detail" not in str(response.data)
    assert WritingSubmission.objects.get(pk=response.data["id"]).status == "failed"


def test_provider_selection_uses_demo_without_api_key(monkeypatch):
    from .services import DemoWritingProvider, get_provider

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert isinstance(get_provider(), DemoWritingProvider)


def test_gemini_provider_sends_key_in_header_and_parses_json(monkeypatch):
    import json
    from .services import GeminiWritingProvider

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": json.dumps({
                                "schema_version": 1,
                                "corrected_text": "I go to school.",
                                "errors": [{
                                    "category": "grammar",
                                    "start": 0,
                                    "end": 2,
                                    "original": "I ",
                                    "correction": "I",
                                    "explanation": "Example correction.",
                                }],
                                "general_feedback": "Good start.",
                                "limitations": [],
                            })
                        }]
                    }
                }]
            }).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("apps.writing.services.urlopen", fake_urlopen)
    provider = GeminiWritingProvider(api_key="test-secret", timeout=9)
    result = provider.analyze("I go to school.")
    assert result["schema_version"] == 1
    assert captured["request"].get_header("X-goog-api-key") == "test-secret"
    assert captured["timeout"] == 9
    assert "test-secret" not in captured["request"].full_url


def test_gemini_provider_reports_unreadable_output_safely(monkeypatch):
    from .services import GeminiWritingProvider, WritingProviderError

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b'{"candidates": []}'

    monkeypatch.setattr("apps.writing.services.urlopen", lambda *_args, **_kwargs: FakeResponse())
    with pytest.raises(WritingProviderError, match="unreadable"):
        GeminiWritingProvider(api_key="test-secret").analyze("I am learning English.")


def test_production_security_defaults_do_not_use_insecure_cookie_settings():
    from django.conf import settings

    assert settings.SECRET_KEY != "unsafe-local-development-key-change-me"
    assert settings.SESSION_COOKIE_SECURE is (not settings.DEBUG)
    assert settings.CSRF_COOKIE_SECURE is (not settings.DEBUG)
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True


@pytest.mark.django_db
def test_writing_submission_rate_limit_applies_only_to_provider_calls(monkeypatch):
    from apps.writing.views import WritingSubmissionThrottle

    monkeypatch.setattr(WritingSubmissionThrottle, "THROTTLE_RATES", {"writing_submission": "1/hour"})
    cache.clear()
    user = User.objects.create_user(username="writing-throttled", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/v1/writing/submissions/", {"text": "First sentence."}, format="json")
    second = client.post("/api/v1/writing/submissions/", {"text": "Second sentence."}, format="json")
    history = client.get("/api/v1/writing/submissions/")

    assert first.status_code == 201
    assert second.status_code == 429
    assert history.status_code == 200
    cache.clear()
