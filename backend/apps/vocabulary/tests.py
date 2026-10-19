import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from .models import VocabularyCard
from .services import apply_review

User = get_user_model()


@pytest.mark.django_db
def test_authenticated_learner_can_add_and_list_vocabulary_card():
    user = User.objects.create_user(username="vocab-learner", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/vocabulary/cards/", {
        "word": "resilient",
        "definition": "Able to recover after difficulty.",
        "example_sentence": "She stayed resilient during the challenge.",
        "translation": "تاب‌آور",
    }, format="json")
    assert response.status_code == 201
    assert response.data["status"] == "new"
    assert response.data["interval_days"] == 0
    assert response.data["due_at"] is not None
    listed = client.get("/api/v1/vocabulary/cards/")
    assert listed.status_code == 200
    assert listed.data[0]["word"] == "resilient"


@pytest.mark.django_db
def test_vocabulary_cards_are_private_and_review_is_owner_scoped():
    owner = User.objects.create_user(username="vocab-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="vocab-other", password="Strong-test-pass-123")
    card = VocabularyCard.objects.create(user=owner, word="curious", definition="Eager to learn.", due_at=timezone.now())
    client = APIClient()
    client.force_authenticate(user=other)
    assert client.get("/api/v1/vocabulary/cards/").data == []
    assert client.post(f"/api/v1/vocabulary/cards/{card.pk}/review/", {"quality": 5}, format="json").status_code == 404


@pytest.mark.django_db
def test_duplicate_word_is_rejected_case_insensitively_for_same_user():
    user = User.objects.create_user(username="vocab-duplicate", password="Strong-test-pass-123")
    VocabularyCard.objects.create(user=user, word="Serendipity", definition="A fortunate discovery.", due_at=timezone.now())
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/vocabulary/cards/", {"word": "serendipity", "definition": "Another definition."}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_due_filter_only_returns_cards_due_now():
    user = User.objects.create_user(username="vocab-due", password="Strong-test-pass-123")
    now = timezone.now()
    due = VocabularyCard.objects.create(user=user, word="dueword", definition="Due now.", due_at=now - timedelta(minutes=1))
    VocabularyCard.objects.create(user=user, word="laterword", definition="Due later.", due_at=now + timedelta(days=2))
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/vocabulary/cards/?due=true")
    assert [item["id"] for item in response.data] == [due.id]


@pytest.mark.django_db
def test_review_updates_interval_and_bad_grade_restarts_learning():
    user = User.objects.create_user(username="vocab-review", password="Strong-test-pass-123")
    card = VocabularyCard.objects.create(user=user, word="persistent", definition="Continuing despite difficulty.", due_at=timezone.now())
    card = apply_review(card, 5)
    assert card.repetitions == 1
    assert card.interval_days == 1
    assert card.due_at > card.last_reviewed_at
    card = apply_review(card, 5)
    assert card.repetitions == 2
    assert card.interval_days == 6
    card = apply_review(card, 2)
    assert card.repetitions == 0
    assert card.interval_days == 1
    assert card.status == VocabularyCard.Status.LEARNING


@pytest.mark.django_db
def test_review_grade_is_validated_and_anonymous_access_is_denied():
    user = User.objects.create_user(username="vocab-grade", password="Strong-test-pass-123")
    card = VocabularyCard.objects.create(user=user, word="lucid", definition="Clear.", due_at=timezone.now())
    client = APIClient()
    assert client.get("/api/v1/vocabulary/cards/").status_code == 403
    client.force_authenticate(user=user)
    assert client.post(f"/api/v1/vocabulary/cards/{card.pk}/review/", {"quality": 6}, format="json").status_code == 400
    assert client.post(f"/api/v1/vocabulary/cards/{card.pk}/review/", {"quality": -1}, format="json").status_code == 400
