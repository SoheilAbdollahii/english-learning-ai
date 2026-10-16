from django.urls import path

from .views import (
    WritingSubmissionCreateView,
    WritingSubmissionDetailView,
    WritingSubmissionListView,
)

urlpatterns = [
    path("submissions/", WritingSubmissionCreateView.as_view(), name="writing-submissions-create"),
    path("submissions/history/", WritingSubmissionListView.as_view(), name="writing-submissions-list"),
    path("submissions/<int:pk>/", WritingSubmissionDetailView.as_view(), name="writing-submissions-detail"),
]
