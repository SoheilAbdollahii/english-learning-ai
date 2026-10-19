from django.urls import path

from .views import UsageSummaryView

urlpatterns = [
    path("", UsageSummaryView.as_view(), name="usage-summary"),
]
