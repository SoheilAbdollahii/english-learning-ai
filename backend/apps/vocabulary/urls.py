from django.urls import path

from .views import VocabularyCardListCreateView, VocabularyReviewHistoryView, VocabularyReviewView

urlpatterns = [
    path("cards/", VocabularyCardListCreateView.as_view(), name="vocabulary-cards"),
    path("reviews/", VocabularyReviewHistoryView.as_view(), name="vocabulary-review-history"),
    path("cards/<int:pk>/review/", VocabularyReviewView.as_view(), name="vocabulary-card-review"),
]
