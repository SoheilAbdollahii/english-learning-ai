import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
User = get_user_model()
GENERIC_RESET_MESSAGE = "If an eligible account matches that email address, instructions will be sent shortly."
GENERIC_VERIFY_MESSAGE = "If an account matches that email address and still needs verification, instructions will be sent shortly."


def _frontend_url(path):
    base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
    return f"{base}{path}"


def _send_account_email(*, user, subject, body):
    try:
        sent = send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return sent == 1
    except Exception:
        logger.exception("Account email delivery failed (user_id=%s)", user.pk)
        return False


def _account_token_url(user, path):
    uid = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
    token = default_token_generator.make_token(user)
    return _frontend_url(f"{path}?uid={uid}&token={token}")


def _send_verification(user):
    if not user.email or user.is_active:
        return False
    url = _account_token_url(user, "/verify-email")
    return _send_account_email(
        user=user,
        subject="Verify your Wordwise email",
        body=(
            f"Hello {user.get_username()},\n\n"
            "Verify your email address to activate your Wordwise account:\n"
            f"{url}\n\n"
            "If you did not create this account, you can ignore this message."
        ),
    )


def _find_user(uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoValidationError):
        return None


class PasswordResetThrottle(AnonRateThrottle):
    scope = "password_reset"


class EmailVerificationThrottle(AnonRateThrottle):
    scope = "email_verification"


@method_decorator(csrf_protect, name="dispatch")
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        email = request.data.get("email") if isinstance(request.data, dict) else None
        if isinstance(email, str) and email.strip():
            user = User.objects.filter(email__iexact=email.strip(), is_active=True).first()
            if user:
                url = _account_token_url(user, "/password-reset/confirm")
                _send_account_email(
                    user=user,
                    subject="Reset your Wordwise password",
                    body=(
                        f"Hello {user.get_username()},\n\n"
                        "Use the link below to choose a new password. The link expires after the configured token lifetime "
                        "and can only be used while it remains valid:\n"
                        f"{url}\n\n"
                        "If you did not request this, you can ignore this message."
                    ),
                )
        # Do not disclose whether an account exists, is active, or has email configured.
        return Response({"detail": GENERIC_RESET_MESSAGE}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        user = _find_user(data.get("uid", ""))
        token = data.get("token")
        password = data.get("password")
        if (
            user is None
            or not user.is_active
            or not isinstance(token, str)
            or not default_token_generator.check_token(user, token)
            or not isinstance(password, str)
        ):
            return Response({"detail": "This password reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            return Response({"password": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"status": "password_reset"}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class VerifyEmailConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerificationThrottle]

    def post(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        user = _find_user(data.get("uid", ""))
        token = data.get("token")
        if user is None or user.is_active or not user.email or not isinstance(token, str):
            return Response({"detail": "This verification link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "This verification link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"status": "email_verified"}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class VerificationResendView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [EmailVerificationThrottle]

    def post(self, request):
        email = request.data.get("email") if isinstance(request.data, dict) else None
        if isinstance(email, str) and email.strip():
            user = User.objects.filter(email__iexact=email.strip(), is_active=False).first()
            if user and user.email:
                _send_verification(user)
        return Response({"detail": GENERIC_VERIFY_MESSAGE}, status=status.HTTP_200_OK)
