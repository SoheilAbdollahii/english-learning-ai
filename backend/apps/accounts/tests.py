import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Profile

User = get_user_model()


@pytest.mark.django_db
def test_me_requires_authentication():
    response = APIClient().get("/api/v1/me/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_me_returns_authenticated_users_profile():
    user = User.objects.create_user(username="learner-one", password="Strong-test-pass-123")
    Profile.objects.create(user=user, locale="fa", target_level="B1")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/me/")
    assert response.status_code == 200
    assert response.data["username"] == "learner-one"
    assert response.data["profile"]["locale"] == "fa"
    assert response.data["profile"]["target_level"] == "B1"


@pytest.mark.django_db
def test_me_patch_updates_profile_preferences():
    user = User.objects.create_user(username="learner-two", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(
        "/api/v1/me/",
        {"profile": {"locale": "fa", "daily_goal_minutes": 30}},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["profile"]["locale"] == "fa"
    assert response.data["profile"]["daily_goal_minutes"] == 30
    profile = Profile.objects.get(user=user)
    assert profile.locale == "fa"
    assert profile.daily_goal_minutes == 30


@pytest.mark.django_db
def test_me_rejects_out_of_range_daily_goal():
    user = User.objects.create_user(username="learner-three", password="Strong-test-pass-123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(
        "/api/v1/me/",
        {"profile": {"daily_goal_minutes": 500}},
        format="json",
    )
    assert response.status_code == 400
