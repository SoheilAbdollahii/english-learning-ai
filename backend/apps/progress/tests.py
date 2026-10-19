import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.vocabulary.models import VocabularyCard
from .models import LearningActivity

User = get_user_model()


@pytest.mark.django_db
def test_progress_summary_is_private_and_counts_persisted_activity():
    user = User.objects.create_user(username="progress-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="progress-other", password="Strong-test-pass-123")
    now = timezone.now()
    first = LearningActivity.objects.create(user=user, activity_type=LearningActivity.Type.VOCABULARY, object_id=3)
    second = LearningActivity.objects.create(user=user, activity_type=LearningActivity.Type.READING, object_id=7)
    LearningActivity.objects.filter(pk=first.pk).update(created_at=now - timedelta(days=1))
    LearningActivity.objects.filter(pk=second.pk).update(created_at=now)
    VocabularyCard.objects.create(user=user, word="dueword", definition="A due word.", due_at=now - timedelta(minutes=1))
    VocabularyCard.objects.create(user=user, word="masteredword", definition="A mastered word.", due_at=now + timedelta(days=10), status=VocabularyCard.Status.MASTERED)

    client = APIClient()
    assert client.get("/api/v1/progress/summary/").status_code == 403
    client.force_authenticate(user=other)
    assert client.get("/api/v1/progress/summary/").data["sessions_completed"] == 0

    client.force_authenticate(user=user)
    response = client.get("/api/v1/progress/summary/")
    assert response.status_code == 200
    assert response.data["sessions_completed"] == 2
    assert response.data["words_reviewed"] == 1
    assert response.data["reading_attempts"] == 0
    assert response.data["due_words"] == 1
    assert response.data["mastered_words"] == 1
    assert response.data["current_streak_days"] == 2
    assert [item["type"] for item in response.data["recent_activity"]] == ["reading", "vocabulary"]


@pytest.mark.django_db
def test_learning_activity_does_not_store_submitted_text_by_default():
    user = User.objects.create_user(username="progress-minimal", password="Strong-test-pass-123")
    activity = LearningActivity.objects.create(user=user, activity_type=LearningActivity.Type.WRITING, object_id=22)
    assert activity.metadata == {}
    assert "original_text" not in activity.metadata
