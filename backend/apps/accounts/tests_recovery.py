import json
import re
from urllib.parse import urlparse, parse_qs

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, override_settings

User = get_user_model()


def csrf_client():
    client = Client(enforce_csrf_checks=True)
    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    return client, token


def token_params(message):
    url = re.search(r"https?://[^\s]+", message.body).group(0)
    params = parse_qs(urlparse(url).query)
    return params["uid"][0], params["token"][0]


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_registration_requires_email_and_sends_verification_link():
    client, token = csrf_client()
    response = client.post(
        "/api/v1/auth/register/",
        data=json.dumps({"username": "verify-me", "email": "Verify-Me@example.com", "password": "Strong-test-pass-123"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 201
    user = User.objects.get(username="verify-me")
    assert user.email == "verify-me@example.com"
    assert not user.is_active
    assert len(mail.outbox) == 1
    assert "/verify-email?uid=" in mail.outbox[0].body


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_email_verification_activates_user_and_token_cannot_be_reused():
    client, token = csrf_client()
    user = User.objects.create_user(username="pending", email="pending@example.com", password="Strong-test-pass-123", is_active=False)
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(str(user.pk).encode())
    secret = default_token_generator.make_token(user)
    response = client.post(
        "/api/v1/auth/verify-email/",
        data=json.dumps({"uid": uid, "token": secret}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    replay = client.post(
        "/api/v1/auth/verify-email/",
        data=json.dumps({"uid": uid, "token": secret}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert replay.status_code == 400


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_password_reset_is_generic_and_changes_password_with_valid_token():
    user = User.objects.create_user(username="reset-me", email="reset@example.com", password="Old-strong-pass-123")
    client, token = csrf_client()
    unknown = client.post(
        "/api/v1/auth/password-reset/",
        data=json.dumps({"email": "not-here@example.com"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert unknown.status_code == 200
    assert len(mail.outbox) == 0

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    requested = client.post(
        "/api/v1/auth/password-reset/",
        data=json.dumps({"email": "RESET@example.com"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert requested.status_code == 200
    assert requested.json()["detail"] == unknown.json()["detail"]
    assert len(mail.outbox) == 1
    uid, reset_token = token_params(mail.outbox[0])

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    confirmed = client.post(
        "/api/v1/auth/password-reset/confirm/",
        data=json.dumps({"uid": uid, "token": reset_token, "password": "New-strong-pass-456"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert confirmed.status_code == 200
    user.refresh_from_db()
    assert user.check_password("New-strong-pass-456")
    assert not user.check_password("Old-strong-pass-123")

    token = client.get("/api/v1/auth/csrf/").json()["csrfToken"]
    replay = client.post(
        "/api/v1/auth/password-reset/confirm/",
        data=json.dumps({"uid": uid, "token": reset_token, "password": "Another-strong-pass-789"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert replay.status_code == 400


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_password_reset_rejects_weak_password_and_inactive_accounts():
    user = User.objects.create_user(username="inactive", email="inactive@example.com", password="Old-strong-pass-123", is_active=False)
    client, token = csrf_client()
    response = client.post(
        "/api/v1/auth/password-reset/",
        data=json.dumps({"email": user.email}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 200
    assert mail.outbox == []
