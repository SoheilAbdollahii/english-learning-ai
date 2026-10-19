from django.urls import path

from .views import ProgressSummaryView

urlpatterns = [
    path("summary/", ProgressSummaryView.as_view(), name="progress-summary"),
]
