from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_usage_summary


class UsageSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(get_usage_summary(request.user))
