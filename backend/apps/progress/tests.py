import pytest
from datetime import date, datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.vocabulary.models import VocabularyCard
from .models import LearningActivity
from .views import _current_streak, _learner_timezone

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
    weekly = response.data["weekly_activity"]
    assert len(weekly) == 7
    assert [day["date"] for day in weekly] == sorted(day["date"] for day in weekly)
    assert sum(day["count"] for day in weekly) == 2
    assert weekly[-1]["date"] == timezone.localdate(timezone=_learner_timezone(user)).isoformat()
    assert [item["type"] for item in response.data["recent_activity"]] == ["reading", "vocabulary"]


@pytest.mark.django_db
def test_learning_activity_does_not_store_submitted_text_by_default():
    user = User.objects.create_user(username="progress-minimal", password="Strong-test-pass-123")
    activity = LearningActivity.objects.create(user=user, activity_type=LearningActivity.Type.WRITING, object_id=22)
    assert activity.metadata == {}
    assert "original_text" not in activity.metadata


@pytest.mark.django_db
def test_learner_journey_updates_all_learning_metrics(monkeypatch):
    """Exercise the core learning APIs together and verify persisted progress."""
    from apps.placement.models import Assessment, Question, PlacementAttempt
    from apps.reading.models import Passage, ReadingQuestion, ReadingAttempt
    from apps.writing.models import WritingSubmission
    from apps.vocabulary.models import VocabularyCard

    # Keep this integration test deterministic and independent of CI secrets.
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    user = User.objects.create_user(username="journey-learner", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)

    assessment = Assessment.objects.create(title="Journey placement", version=1, is_published=True)
    placement_question = Question.objects.create(
        assessment=assessment, prompt="Choose the correct sentence.",
        options={"a": "She studies.", "b": "She study."}, correct_option="a", order=1,
    )
    placement = client.post(
        "/api/v1/placement/attempts/",
        {"assessment_id": assessment.pk, "answers": {str(placement_question.pk): "a"}},
        format="json",
    )
    assert placement.status_code == 201
    assert placement.data["estimated_level"] == "C2"
    assert PlacementAttempt.objects.filter(user=user).count() == 1

    card_response = client.post(
        "/api/v1/vocabulary/cards/",
        {"word": "consistent", "definition": "Doing something regularly."},
        format="json",
    )
    assert card_response.status_code == 201
    review = client.post(
        f"/api/v1/vocabulary/cards/{card_response.data['id']}/review/",
        {"quality": 5}, format="json",
    )
    assert review.status_code == 200
    assert review.data["repetitions"] == 1

    passage = Passage.objects.create(
        slug="journey-reading", title="A Learning Habit",
        body="A short daily habit can make learning more consistent.",
        level="A2", is_published=True,
    )
    reading_question = ReadingQuestion.objects.create(
        passage=passage, prompt="What can a daily habit do?",
        options={"a": "Support learning", "b": "Stop learning"},
        correct_option="a", explanation="The passage says a daily habit supports learning.", order=1,
    )
    reading = client.post(
        "/api/v1/reading/attempts/",
        {"passage_id": passage.pk, "answers": {str(reading_question.pk): "a"}},
        format="json",
    )
    assert reading.status_code == 201
    assert reading.data["percentage"] == 100
    assert ReadingAttempt.objects.filter(user=user).count() == 1

    writing = client.post(
        "/api/v1/writing/submissions/",
        {"text": "I practice English every day."}, format="json",
    )
    assert writing.status_code == 201
    assert writing.data["provider"] == "demo"
    assert WritingSubmission.objects.filter(user=user).count() == 1

    summary = client.get("/api/v1/progress/summary/")
    assert summary.status_code == 200
    assert summary.data["sessions_completed"] == 4
    assert summary.data["words_reviewed"] == 1
    assert summary.data["reading_attempts"] == 1
    assert summary.data["writing_submissions"] == 1
    assert summary.data["placement_attempts"] == 1
    assert summary.data["due_words"] == 0
    assert summary.data["mastered_words"] == 0
    assert {item["type"] for item in summary.data["recent_activity"]} == {
        "placement", "vocabulary", "reading", "writing",
    }



def test_current_streak_uses_learner_local_day_boundaries(monkeypatch):
    # 15:30 UTC is already the next calendar day in Tokyo.
    timestamps = [
        datetime(2026, 10, 17, 15, 30, tzinfo=dt_timezone.utc),
        datetime(2026, 10, 18, 15, 30, tzinfo=dt_timezone.utc),
    ]
    monkeypatch.setattr(
        "apps.progress.views.timezone.localdate",
        lambda timezone=None: date(2026, 10, 20),
    )
    assert _current_streak(timestamps, ZoneInfo("Asia/Tokyo")) == 2


def test_current_streak_counts_yesterday_when_today_has_no_activity(monkeypatch):
    timestamps = [
        datetime(2026, 10, 17, 12, 0, tzinfo=dt_timezone.utc),
        datetime(2026, 10, 18, 12, 0, tzinfo=dt_timezone.utc),
    ]
    monkeypatch.setattr(
        "apps.progress.views.timezone.localdate",
        lambda timezone=None: date(2026, 10, 19),
    )
    assert _current_streak(timestamps, ZoneInfo("UTC")) == 2


@pytest.mark.django_db
def test_invalid_profile_timezone_falls_back_to_utc():
    from apps.accounts.models import Profile

    user = User.objects.create_user(username="progress-invalid-timezone", password="Strong-test-pass-123")
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.timezone = "Not/A_Real_Zone"
    profile.save(update_fields=("timezone",))
    user.profile = profile
    assert str(_learner_timezone(user)) == "UTC"



@pytest.mark.django_db
def test_weekly_activity_counts_follow_profile_timezone():
    from apps.accounts.models import Profile

    user = User.objects.create_user(username="progress-weekly-tz", password="Strong-test-pass-123")
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.timezone = "Asia/Tokyo"
    profile.save(update_fields=("timezone",))
    tz = ZoneInfo("Asia/Tokyo")
    local_today = timezone.localdate(timezone=tz)
    # This UTC timestamp corresponds to local midnight in Tokyo.
    utc_timestamp = datetime.combine(local_today, datetime.min.time(), tzinfo=tz).astimezone(dt_timezone.utc)
    activity = LearningActivity.objects.create(
        user=user, activity_type=LearningActivity.Type.READING, object_id=1,
    )
    LearningActivity.objects.filter(pk=activity.pk).update(created_at=utc_timestamp)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/progress/summary/")
    assert response.status_code == 200
    weekly = response.data["weekly_activity"]
    today_bucket = next(day for day in weekly if day["date"] == local_today.isoformat())
    assert today_bucket["count"] == 1
