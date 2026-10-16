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


from django.test import Client


@pytest.mark.django_db
def test_session_login_requires_csrf_and_creates_authenticated_session():
    user = User.objects.create_user(username="session-learner", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)

    rejected = client.post(
        "/api/v1/auth/login/",
        data='{"username":"session-learner","password":"Strong-test-pass-123"}',
        content_type="application/json",
    )
    assert rejected.status_code == 403

    csrf_response = client.get("/api/v1/auth/csrf/")
    assert csrf_response.status_code == 200
    csrf_token = csrf_response.json()["csrfToken"]
    login_response = client.post(
        "/api/v1/auth/login/",
        data='{"username":"session-learner","password":"Strong-test-pass-123"}',
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert login_response.status_code == 200
    assert login_response.json()["username"] == user.username

    me_response = client.get("/api/v1/me/")
    assert me_response.status_code == 200
    assert me_response.json()["username"] == user.username


@pytest.mark.django_db
def test_session_login_rejects_invalid_credentials():
    User.objects.create_user(username="login-check", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)
    csrf_token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    response = client.post(
        "/api/v1/auth/login/",
        data='{"username":"login-check","password":"not-the-password"}',
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password."


@pytest.mark.django_db
def test_session_logout_ends_session_and_requires_csrf():
    User.objects.create_user(username="logout-learner", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)
    csrf_token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    client.post(
        "/api/v1/auth/login/",
        data='{"username":"logout-learner","password":"Strong-test-pass-123"}',
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    fresh_csrf = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    response = client.post(
        "/api/v1/auth/logout/",
        content_type="application/json",
        HTTP_X_CSRFTOKEN=fresh_csrf,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert client.get("/api/v1/me/").status_code in (401, 403)
