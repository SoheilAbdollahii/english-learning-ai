import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Assessment, PlacementAttempt
from .views import estimate_level

User = get_user_model()


@pytest.mark.django_db
def test_published_assessment_does_not_expose_answer_key():
    response = APIClient().get("/api/v1/placement/assessments/")
    assert response.status_code == 200
    assert len(response.data) >= 1
    assessment_id = response.data[0]["id"]
    detail = APIClient().get(f"/api/v1/placement/assessments/{assessment_id}/")
    assert detail.status_code == 200
    assert len(detail.data["questions"]) == 6
    assert "correct_option" not in detail.data["questions"][0]
    assert "explanation" not in detail.data["questions"][0]


@pytest.mark.django_db
def test_attempt_score_is_calculated_server_side_and_saved():
    user = User.objects.create_user(username="placement-learner", password="Strong-test-pass-123")
    assessment = Assessment.objects.get(is_published=True)
    from .models import Question
    questions = list(Question.objects.filter(assessment=assessment))
    answers = {str(question.id): question.correct_option for question in questions}
    answers[str(questions[0].id)] = "a" if questions[0].correct_option != "a" else "b"
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/placement/attempts/", {"assessment_id": assessment.id, "answers": answers}, format="json")
    assert response.status_code == 201
    assert response.data["score"] == len(questions) - 1
    assert response.data["max_score"] == len(questions)
    assert PlacementAttempt.objects.filter(user=user, assessment=assessment).count() == 1


@pytest.mark.django_db
def test_attempt_rejects_missing_or_invalid_answers():
    user = User.objects.create_user(username="placement-invalid", password="Strong-test-pass-123")
    assessment = Assessment.objects.get(is_published=True)
    client = APIClient()
    client.force_authenticate(user=user)
    missing = client.post("/api/v1/placement/attempts/", {"assessment_id": assessment.id, "answers": {}}, format="json")
    assert missing.status_code == 400
    from .models import Question
    question = Question.objects.filter(assessment=assessment).first()
    invalid = client.post("/api/v1/placement/attempts/", {"assessment_id": assessment.id, "answers": {str(question.id): "not-an-option"}}, format="json")
    assert invalid.status_code == 400


@pytest.mark.django_db
def test_attempt_results_are_private_to_owner():
    assessment = Assessment.objects.get(is_published=True)
    owner = User.objects.create_user(username="placement-owner", password="Strong-test-pass-123")
    other = User.objects.create_user(username="placement-other", password="Strong-test-pass-123")
    attempt = PlacementAttempt.objects.create(user=owner, assessment=assessment, answers={}, score=0, max_score=6, estimated_level="A1")
    client = APIClient()
    client.force_authenticate(user=other)
    assert client.get(f"/api/v1/placement/attempts/{attempt.id}/").status_code == 404


def test_estimate_level_boundaries():
    assert estimate_level(0, 6) == "A1"
    assert estimate_level(4, 6) == "B1"
    assert estimate_level(6, 6) == "C2"
