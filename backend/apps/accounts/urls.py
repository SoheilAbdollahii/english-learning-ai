from django.urls import path

from .auth_views import csrf_token, session_login, session_logout
from .views import MeView

urlpatterns = [
    path("auth/csrf/", csrf_token, name="csrf-token"),
    path("auth/login/", session_login, name="session-login"),
    path("auth/logout/", session_logout, name="session-logout"),
    path("me/", MeView.as_view(), name="me"),
]
