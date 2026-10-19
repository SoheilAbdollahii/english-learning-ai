import json

import pytest
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.mark.django_db
def test_login_requires_csrf_token():
    user = User.objects.create_user(username="login-user", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": user.username, "password": "Strong-test-pass-123"}),
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_login_and_logout_session_flow():
    user = User.objects.create_user(username="session-user", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)
    token_response = client.get("/api/v1/auth/csrf/")
    token = token_response.json()["csrfToken"]
    login_response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": user.username, "password": "Strong-test-pass-123"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert login_response.status_code == 200
    assert client.get("/api/v1/me/").status_code == 200

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    logout_response = client.post(
        "/api/v1/auth/logout/",
        data="{}",
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert logout_response.status_code == 200
    assert client.get("/api/v1/me/").status_code == 403


@pytest.mark.django_db
def test_login_rejects_wrong_password():
    User.objects.create_user(username="wrong-password-user", password="Strong-test-pass-123")
    client = Client(enforce_csrf_checks=True)
    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "wrong-password-user", "password": "incorrect"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_registration_requires_csrf_and_creates_normalized_username():
    client = Client(enforce_csrf_checks=True)
    denied = client.post(
        "/api/v1/auth/register/",
        data=json.dumps({"username": "NewLearner", "email": "newlearner@example.com", "password": "Strong-test-pass-123"}),
        content_type="application/json",
    )
    assert denied.status_code == 403

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    response = client.post(
        "/api/v1/auth/register/",
        data=json.dumps({"username": "NewLearner", "email": "newlearner@example.com", "password": "Strong-test-pass-123"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newlearner"
    assert response.json()["status"] == "verification_sent"
    user = User.objects.get(username="newlearner")
    assert user.check_password("Strong-test-pass-123")
    assert user.email == "newlearner@example.com"
    assert not user.is_active
    assert client.get("/api/v1/me/").status_code == 403


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_registration_rejects_weak_password_and_case_insensitive_duplicate():
    client = Client(enforce_csrf_checks=True)
    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    weak = client.post(
        "/api/v1/auth/register/",
        data=json.dumps({"username": "weak-password", "email": "weak@example.com", "password": "short"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert weak.status_code == 400
    assert "password" in weak.json()
    assert not User.objects.filter(username="weak-password").exists()

    User.objects.create_user(username="existinguser", password="Strong-test-pass-123")
    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    duplicate = client.post(
        "/api/v1/auth/register/",
        data=json.dumps({"username": "ExistingUser", "email": "existing@example.com", "password": "Another-strong-pass-456"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert duplicate.status_code == 400
    assert "username" in duplicate.json()
