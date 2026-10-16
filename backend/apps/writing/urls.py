from django.urls import path

from .views import WritingSubmissionCollectionView, WritingSubmissionDetailView

urlpatterns = [
    path("submissions/", WritingSubmissionCollectionView.as_view(), name="writing-submissions"),
    path("submissions/<int:pk>/", WritingSubmissionDetailView.as_view(), name="writing-submission-detail"),
]
