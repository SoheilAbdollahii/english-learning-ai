import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import AIUsageRecord

User = get_user_model()


@pytest.mark.django_db
def test_writing_daily_quota_is_enforced_and_usage_is_visible(monkeypatch):
    monkeypatch.setenv("WRITING_SUBMISSIONS_PER_DAY", "1")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    user = User.objects.create_user(username="usage-quota", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/v1/writing/submissions/", {"text": "A first practice sentence."}, format="json")
    second = client.post("/api/v1/writing/submissions/", {"text": "A second practice sentence."}, format="json")
    assert first.status_code == 201
    assert second.status_code == 429
    assert second.data["code"] == "usage_limit_exceeded"
    assert AIUsageRecord.objects.filter(user=user, status=AIUsageRecord.Status.SUCCEEDED).count() == 1
    assert AIUsageRecord.objects.filter(user=user).count() == 1

    summary = client.get("/api/v1/usage/")
    assert summary.status_code == 200
    assert summary.data["limit"] == 1
    assert summary.data["used"] == 1
    assert summary.data["remaining"] == 0
    assert summary.data["input_characters"] == len("A first practice sentence.")
    assert summary.data["cost_tracking"].startswith("unavailable")


@pytest.mark.django_db
def test_failed_provider_attempt_is_recorded_and_consumes_quota(monkeypatch):
    monkeypatch.setenv("WRITING_SUBMISSIONS_PER_DAY", "1")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    import apps.writing.views as writing_views
    from apps.writing.services import WritingProviderError

    def fail(_text):
        raise WritingProviderError("private provider details")

    monkeypatch.setattr(writing_views, "analyze_writing", fail)
    user = User.objects.create_user(username="usage-failure", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/writing/submissions/", {"text": "A provider failure sentence."}, format="json")
    assert response.status_code == 502
    usage = AIUsageRecord.objects.get(user=user)
    assert usage.status == AIUsageRecord.Status.FAILED
    assert usage.failure_category == "analysis_unavailable"
    assert "private provider details" not in str(usage.metadata)
    assert client.post("/api/v1/writing/submissions/", {"text": "Retry sentence."}, format="json").status_code == 429


@pytest.mark.django_db
def test_usage_summary_requires_authentication_and_is_user_scoped():
    owner = User.objects.create_user(username="usage-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="usage-other", password="Strong-test-pass-123")
    AIUsageRecord.objects.create(user=owner, operation="writing_analysis", provider="demo", status="succeeded", input_characters=20)
    client = APIClient()
    assert client.get("/api/v1/usage/").status_code == 403
    client.force_authenticate(user=other)
    assert client.get("/api/v1/usage/").data["used"] == 0
