from django.urls import path

from .views import (
    PassageDetailView,
    PassageListView,
    ReadingAttemptCreateView,
    ReadingAttemptDetailView,
)

urlpatterns = [
    path("passages/", PassageListView.as_view(), name="reading-passages"),
    path("passages/<int:pk>/", PassageDetailView.as_view(), name="reading-passage-detail"),
    path("attempts/", ReadingAttemptCreateView.as_view(), name="reading-attempts"),
    path("attempts/<int:pk>/", ReadingAttemptDetailView.as_view(), name="reading-attempt-detail"),
]
