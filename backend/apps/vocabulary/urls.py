from django.urls import path

from .views import VocabularyCardListCreateView, VocabularyReviewView

urlpatterns = [
    path("cards/", VocabularyCardListCreateView.as_view(), name="vocabulary-cards"),
    path("cards/<int:pk>/review/", VocabularyReviewView.as_view(), name="vocabulary-card-review"),
]
