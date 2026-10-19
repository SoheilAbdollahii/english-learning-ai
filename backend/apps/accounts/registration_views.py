import json

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions, status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class RegistrationThrottle(AnonRateThrottle):
    scope = "registration"


@method_decorator(csrf_protect, name="dispatch")
class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        payload = request.data
        if not isinstance(payload, dict):
            return Response({"detail": "Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        username = payload.get("username")
        password = payload.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        username = username.strip().lower()
        if not username or len(username) > 150:
            return Response({"username": ["Enter a username of 1 to 150 characters."]}, status=status.HTTP_400_BAD_REQUEST)
        username_field = User._meta.get_field("username")
        try:
            username_field.run_validators(username)
        except DjangoValidationError as exc:
            return Response({"username": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"username": ["This username is already taken."]}, status=status.HTTP_400_BAD_REQUEST)

        candidate = User(username=username)
        try:
            validate_password(password, user=candidate)
        except DjangoValidationError as exc:
            return Response({"password": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
        except IntegrityError:
            return Response({"username": ["This username is already taken."]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": user.pk, "username": user.get_username(), "status": "created"},
            status=status.HTTP_201_CREATED,
        )
