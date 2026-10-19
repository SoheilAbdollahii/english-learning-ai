from django.urls import path

from .auth_views import csrf_token, session_login, session_logout
from .registration_views import RegistrationView
from .recovery_views import PasswordResetConfirmView, PasswordResetRequestView, VerificationResendView, VerifyEmailConfirmView
from .views import MeView

urlpatterns = [
    path("auth/csrf/", csrf_token, name="csrf-token"),
    path("auth/login/", session_login, name="session-login"),
    path("auth/register/", RegistrationView.as_view(), name="session-register"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("auth/verify-email/", VerifyEmailConfirmView.as_view(), name="verify-email-confirm"),
    path("auth/verify-email/resend/", VerificationResendView.as_view(), name="verify-email-resend"),
    path("auth/logout/", session_logout, name="session-logout"),
    path("me/", MeView.as_view(), name="me"),
]
