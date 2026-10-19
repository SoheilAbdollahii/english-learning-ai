from django.urls import path

from .views import ProgressRecommendationsView, ProgressSummaryView

urlpatterns = [
    path("summary/", ProgressSummaryView.as_view(), name="progress-summary"),
    path("recommendations/", ProgressRecommendationsView.as_view(), name="progress-recommendations"),
]
