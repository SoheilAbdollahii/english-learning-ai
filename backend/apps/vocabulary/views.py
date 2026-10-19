from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VocabularyCard, VocabularyReviewEvent
from .serializers import (
    VocabularyCardCreateSerializer,
    VocabularyCardSerializer,
    VocabularyReviewSerializer,
    VocabularyReviewEventSerializer,
)
from .services import apply_review


class VocabularyCardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = VocabularyCard.objects.filter(user=self.request.user)
        if self.request.query_params.get("due", "").lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(due_at__lte=timezone.now())
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VocabularyCardCreateSerializer
        return VocabularyCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = serializer.save()
        return Response(VocabularyCardSerializer(card).data, status=status.HTTP_201_CREATED)


class VocabularyReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        serializer = VocabularyReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                card = VocabularyCard.objects.select_for_update().get(pk=pk, user=request.user)
                card = apply_review(card, serializer.validated_data["quality"])
        except VocabularyCard.DoesNotExist:
            return Response({"detail": "Vocabulary card not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(VocabularyCardSerializer(card).data, status=status.HTTP_200_OK)



class VocabularyReviewHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VocabularyReviewEventSerializer

    def get_queryset(self):
        queryset = VocabularyReviewEvent.objects.filter(
            user=self.request.user,
        ).select_related("card")
        card_id = self.request.query_params.get("card")
        if card_id:
            queryset = queryset.filter(card_id=card_id)
        return queryset
