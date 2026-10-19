import pytest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.db import close_old_connections, connection
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import AIUsageRecord
from .services import reserve_writing_usage

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
    assert summary.data["cost_tracking"] == "no_provider_usage_available"


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


@pytest.mark.django_db
def test_provider_token_usage_and_configured_cost_estimate_are_persisted(monkeypatch):
    monkeypatch.setenv("WRITING_SUBMISSIONS_PER_DAY", "3")
    monkeypatch.setenv("GEMINI_INPUT_COST_MICROUNITS_PER_MILLION_TOKENS", "2000000")
    monkeypatch.setenv("GEMINI_OUTPUT_COST_MICROUNITS_PER_MILLION_TOKENS", "4000000")
    monkeypatch.setenv("GEMINI_API_KEY", "configured-for-provider-selection")
    import apps.writing.views as writing_views

    result = {
        "schema_version": 1,
        "corrected_text": "She goes to school.",
        "errors": [],
        "general_feedback": "Clear sentence.",
        "limitations": [],
    }
    monkeypatch.setattr(
        writing_views,
        "analyze_writing",
        lambda _text: (
            "gemini",
            result,
            {"promptTokenCount": 123, "candidatesTokenCount": 45, "totalTokenCount": 168},
        ),
    )
    user = User.objects.create_user(username="usage-tokens", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/writing/submissions/",
        {"text": "She go to school."},
        format="json",
    )
    assert response.status_code == 201

    usage = AIUsageRecord.objects.get(user=user)
    assert usage.provider == "gemini"
    assert usage.input_tokens == 123
    assert usage.output_tokens == 45
    assert usage.estimated_cost_microunits == 426
    assert usage.metadata == {"total_tokens": 168}

    summary = client.get("/api/v1/usage/")
    assert summary.status_code == 200
    assert summary.data["input_tokens"] == 123
    assert summary.data["output_tokens"] == 45
    assert summary.data["estimated_cost_microunits"] == 426
    assert summary.data["cost_tracking"] == "estimated_from_configured_rates"


@pytest.mark.django_db
def test_token_usage_is_reported_without_fabricating_cost_when_rates_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_INPUT_COST_MICROUNITS_PER_MILLION_TOKENS", raising=False)
    monkeypatch.delenv("GEMINI_OUTPUT_COST_MICROUNITS_PER_MILLION_TOKENS", raising=False)
    user = User.objects.create_user(username="usage-no-prices", password="Strong-test-pass-123")
    AIUsageRecord.objects.create(
        user=user,
        provider="gemini",
        status=AIUsageRecord.Status.SUCCEEDED,
        input_characters=40,
        input_tokens=20,
        output_tokens=10,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    summary = client.get("/api/v1/usage/")
    assert summary.data["input_tokens"] == 20
    assert summary.data["output_tokens"] == 10
    assert summary.data["estimated_cost_microunits"] is None
    assert summary.data["cost_tracking"] == "token_usage_available_rates_not_configured"



@pytest.mark.django_db(transaction=True)
def test_concurrent_daily_quota_reservations_are_serialized_on_postgresql(monkeypatch):
    if connection.vendor != "postgresql":
        pytest.skip("Row-lock concurrency guarantee is verified on PostgreSQL only.")

    monkeypatch.setenv("WRITING_SUBMISSIONS_PER_DAY", "1")
    user = User.objects.create_user(
        username="usage-concurrent", password="Strong-test-pass-123",
    )
    barrier = Barrier(2)

    def reserve_slot():
        close_old_connections()
        try:
            learner = User.objects.get(pk=user.pk)
            barrier.wait(timeout=10)
            record, _limit, _used = reserve_writing_usage(learner, input_characters=24)
            return record is not None
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _index: reserve_slot(), range(2)))

    assert sum(outcomes) == 1
    assert AIUsageRecord.objects.filter(
        user=user,
        operation="writing_analysis",
        status=AIUsageRecord.Status.RESERVED,
    ).count() == 1
