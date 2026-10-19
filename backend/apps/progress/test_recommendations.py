import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.vocabulary.models import VocabularyCard
from .models import LearningActivity

User = get_user_model()


@pytest.mark.django_db
def test_recommendations_explain_their_evidence_and_prioritize_due_words():
    user = User.objects.create_user(username="recommend-owner", password="Strong-test-pass-123")
    VocabularyCard.objects.create(user=user, word="timely", definition="At the right time.", due_at=timezone.now())
    LearningActivity.objects.create(user=user, activity_type=LearningActivity.Type.VOCABULARY, metadata={"quality": 4})
    client = APIClient()
    assert client.get("/api/v1/progress/recommendations/").status_code == 403
    client.force_authenticate(user=user)
    response = client.get("/api/v1/progress/recommendations/")
    assert response.status_code == 200
    items = response.data["recommendations"]
    assert items[0]["code"] == "review_due_words"
    assert "1 vocabulary card" in items[0]["reason"]
    assert all(item["reason"] and item["href"].startswith("/") for item in items)
    assert len(items) <= 3


@pytest.mark.django_db
def test_recommendations_change_when_reading_history_exists():
    from apps.reading.models import Passage, ReadingAttempt

    user = User.objects.create_user(username="recommend-reader", password="Strong-test-pass-123")
    passage = Passage.objects.create(slug="recommend-reading", title="Reading", body="Text.", level="A2", is_published=True)
    ReadingAttempt.objects.create(user=user, passage=passage, passage_version=1, submitted_answers={}, result_details=[], score=1, max_score=1, percentage=100)
    client = APIClient()
    client.force_authenticate(user=user)
    codes = [item["code"] for item in client.get("/api/v1/progress/recommendations/").data["recommendations"]]
    assert "start_reading" not in codes
