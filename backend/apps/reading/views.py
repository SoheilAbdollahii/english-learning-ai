from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Passage, ReadingAttempt
from .serializers import (
    PassageDetailSerializer,
    PassageListSerializer,
    ReadingAttemptCreateSerializer,
    ReadingAttemptSerializer,
)


class PassageListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PassageListSerializer
    queryset = Passage.objects.filter(is_published=True).order_by("level", "id")


class PassageDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PassageDetailSerializer
    queryset = Passage.objects.filter(is_published=True).prefetch_related("questions")


class ReadingAttemptCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReadingAttemptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        passage = serializer.validated_data["passage"]
        answers = serializer.validated_data["answers"]
        questions = serializer.validated_data["questions"]
        score = sum(question.points for question in questions if answers[str(question.pk)] == question.correct_option)
        max_score = sum(question.points for question in questions)
        details = [
            {
                "question_id": question.pk,
                "prompt": question.prompt,
                "selected_option": answers[str(question.pk)],
                "correct_option": question.correct_option,
                "correct": answers[str(question.pk)] == question.correct_option,
                "explanation": question.explanation,
            }
            for question in questions
        ]
        with transaction.atomic():
            attempt = ReadingAttempt.objects.create(
                user=request.user,
                passage=passage,
                passage_version=passage.content_version,
                submitted_answers=answers,
                result_details=details,
                score=score,
                max_score=max_score,
                percentage=round(score * 100 / max_score) if max_score else 0,
            )
        return Response(ReadingAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class ReadingAttemptDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReadingAttemptSerializer

    def get_queryset(self):
        return ReadingAttempt.objects.filter(user=self.request.user).select_related("passage")
