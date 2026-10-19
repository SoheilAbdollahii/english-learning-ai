import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Passage, ReadingAttempt, ReadingQuestion

User = get_user_model()


@pytest.mark.django_db
def test_published_passages_hide_answer_keys_until_attempt_is_submitted():
    passage = Passage.objects.create(
        slug="test-routine", title="A Test Routine", body="A short passage about a useful routine.",
        level="A2", is_published=True,
    )
    question = ReadingQuestion.objects.create(
        passage=passage, prompt="What is useful?", options={"a": "A routine", "b": "A storm"},
        correct_option="a", explanation="The text supports this answer.", order=1,
    )
    client = APIClient()
    detail = client.get(f"/api/v1/reading/passages/{passage.pk}/")
    assert detail.status_code == 200
    assert detail.data["questions"][0]["id"] == question.id
    assert "correct_option" not in detail.data["questions"][0]
    assert "explanation" not in detail.data["questions"][0]


@pytest.mark.django_db
def test_reading_attempt_is_scored_by_server_and_returns_explanations():
    user = User.objects.create_user(username="reader", password="Strong-test-pass-123")
    passage = Passage.objects.create(slug="test-city", title="A Test City", body="A short passage.", level="A2", is_published=True)
    q1 = ReadingQuestion.objects.create(passage=passage, prompt="Question one?", options={"a": "Correct", "b": "Wrong"}, correct_option="a", explanation="Because it is stated.", order=1, points=2)
    q2 = ReadingQuestion.objects.create(passage=passage, prompt="Question two?", options={"a": "Wrong", "b": "Correct"}, correct_option="b", explanation="The second option is supported.", order=2, points=1)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/reading/attempts/", {
        "passage_id": passage.pk,
        "answers": {str(q1.pk): "a", str(q2.pk): "a"},
    }, format="json")
    assert response.status_code == 201
    assert response.data["score"] == 2
    assert response.data["max_score"] == 3
    assert response.data["percentage"] == 67
    assert response.data["result_details"][0]["correct"] is True
    assert response.data["result_details"][1]["correct"] is False
    assert ReadingAttempt.objects.get(pk=response.data["id"]).user == user


@pytest.mark.django_db
def test_reading_attempt_requires_exact_valid_answers_and_authentication():
    passage = Passage.objects.create(slug="test-exact", title="Exact Answers", body="A short passage.", level="A1", is_published=True)
    question = ReadingQuestion.objects.create(passage=passage, prompt="Choose.", options={"a": "One", "b": "Two"}, correct_option="a", order=1)
    client = APIClient()
    payload = {"passage_id": passage.pk, "answers": {str(question.pk): "z"}}
    assert client.post("/api/v1/reading/attempts/", payload, format="json").status_code == 403
    user = User.objects.create_user(username="reader-invalid", password="Strong-test-pass-123")
    client.force_authenticate(user=user)
    assert client.post("/api/v1/reading/attempts/", payload, format="json").status_code == 400
    assert client.post("/api/v1/reading/attempts/", {"passage_id": passage.pk, "answers": {}}, format="json").status_code == 400


@pytest.mark.django_db
def test_reading_attempt_detail_is_owner_scoped():
    owner = User.objects.create_user(username="reader-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="reader-other", password="Strong-test-pass-123")
    passage = Passage.objects.create(slug="private-attempt", title="Private Attempt", body="A short passage.", level="A1", is_published=True)
    attempt = ReadingAttempt.objects.create(user=owner, passage=passage, passage_version=1, submitted_answers={}, result_details=[], score=0, max_score=1, percentage=0)
    client = APIClient()
    client.force_authenticate(user=other)
    assert client.get(f"/api/v1/reading/attempts/{attempt.pk}/").status_code == 404


@pytest.mark.django_db
def test_unpublished_passages_are_not_listed_or_retrievable():
    passage = Passage.objects.create(slug="draft-passage", title="Draft", body="Not yet published.", level="A1", is_published=False)
    client = APIClient()
    assert passage.id not in [item["id"] for item in client.get("/api/v1/reading/passages/").data]
    assert client.get(f"/api/v1/reading/passages/{passage.pk}/").status_code == 404


@pytest.mark.django_db
def test_reading_attempt_history_is_paginated_and_owner_scoped():
    owner = User.objects.create_user(username="history-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="history-other", password="Strong-test-pass-123")
    passage = Passage.objects.create(slug="history-passage", title="History Passage", body="Text.", level="A2", is_published=True)
    for index in range(12):
        ReadingAttempt.objects.create(
            user=owner, passage=passage, passage_version=1,
            submitted_answers={}, result_details=[], score=index % 2,
            max_score=1, percentage=(index % 2) * 100,
        )
    client = APIClient()
    assert client.get("/api/v1/reading/attempts/").status_code == 403
    client.force_authenticate(user=owner)
    response = client.get("/api/v1/reading/attempts/?limit=2")
    assert response.status_code == 200
    assert response.data["count"] == 12
    assert len(response.data["results"]) == 2
    client.force_authenticate(user=other)
    assert client.get("/api/v1/reading/attempts/").data["count"] == 0
