from django.urls import path

from .views import (
    AssessmentDetailView,
    AssessmentListView,
    PlacementAttemptCreateView,
    PlacementAttemptDetailView,
)

urlpatterns = [
    path("assessments/", AssessmentListView.as_view(), name="placement-assessments"),
    path("assessments/<int:pk>/", AssessmentDetailView.as_view(), name="placement-assessment-detail"),
    path("attempts/", PlacementAttemptCreateView.as_view(), name="placement-attempts"),
    path("attempts/<int:pk>/", PlacementAttemptDetailView.as_view(), name="placement-attempt-detail"),
]
