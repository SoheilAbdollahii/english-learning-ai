from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok", "service": "english-learning-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health, name="health"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/placement/", include("apps.placement.urls")),
    path("api/v1/writing/", include("apps.writing.urls")),
    path("api/v1/vocabulary/", include("apps.vocabulary.urls")),
    path("api/v1/reading/", include("apps.reading.urls")),
]
