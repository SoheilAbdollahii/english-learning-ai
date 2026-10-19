from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assessment, PlacementAttempt
from .serializers import (
    AssessmentDetailSerializer,
    AssessmentListSerializer,
    AttemptCreateSerializer,
    AttemptResultSerializer,
)


class AssessmentListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AssessmentListSerializer
    queryset = Assessment.objects.filter(is_published=True).order_by("id")


class AssessmentDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AssessmentDetailSerializer
    queryset = Assessment.objects.filter(is_published=True).prefetch_related("questions")


def estimate_level(score: int, max_score: int) -> str:
    """Return a deterministic provisional CEFR estimate from the percentage score."""
    percentage = (score / max_score) * 100 if max_score else 0
    if percentage < 40:
        return "A1"
    if percentage < 55:
        return "A2"
    if percentage < 70:
        return "B1"
    if percentage < 85:
        return "B2"
    if percentage < 95:
        return "C1"
    return "C2"


class PlacementAttemptCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AttemptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = serializer.validated_data["assessment"]
        answers = serializer.validated_data["answers"]
        questions = serializer.validated_data["questions"]
        score = sum(
            question.points
            for question in questions
            if answers[str(question.pk)] == question.correct_option
        )
        max_score = sum(question.points for question in questions)
        with transaction.atomic():
            attempt = PlacementAttempt.objects.create(
                user=request.user,
                assessment=assessment,
                answers=answers,
                score=score,
                max_score=max_score,
                estimated_level=estimate_level(score, max_score),
                scoring_version=1,
            )
        return Response(AttemptResultSerializer(attempt).data, status=status.HTTP_201_CREATED)


class PlacementAttemptDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttemptResultSerializer

    def get_queryset(self):
        return PlacementAttempt.objects.filter(user=self.request.user).select_related("assessment")
