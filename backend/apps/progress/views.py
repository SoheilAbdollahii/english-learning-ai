from datetime import timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.placement.models import PlacementAttempt
from apps.reading.models import ReadingAttempt
from apps.vocabulary.models import VocabularyCard
from apps.writing.models import WritingSubmission
from .models import LearningActivity


def _learner_timezone(user):
    try:
        timezone_name = user.profile.timezone
    except ObjectDoesNotExist:
        timezone_name = "UTC"
    try:
        return ZoneInfo(timezone_name)
    except (ValueError, ZoneInfoNotFoundError):
        return ZoneInfo("UTC")


def _current_streak(timestamps, tz):
    active_dates = {timezone.localtime(timestamp, tz).date() for timestamp in timestamps}
    today = timezone.localdate(timezone=tz)
    cursor = today if today in active_dates else today - timedelta(days=1)
    if cursor not in active_dates:
        return 0
    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


class ProgressSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        activities = LearningActivity.objects.filter(user=user)
        recent = list(activities[:8])
        tz = _learner_timezone(user)
        timestamps = list(activities.filter(created_at__gte=now - timedelta(days=370)).order_by("-created_at").values_list("created_at", flat=True)[:5000])
        local_today = timezone.localdate(timezone=tz)
        weekly_start = local_today - timedelta(days=6)
        weekly_counts = {}
        for timestamp in activities.filter(created_at__gte=now - timedelta(days=8)).values_list("created_at", flat=True):
            activity_date = timezone.localtime(timestamp, tz).date()
            if weekly_start <= activity_date <= local_today:
                weekly_counts[activity_date] = weekly_counts.get(activity_date, 0) + 1
        weekly_activity = [
            {
                "date": (weekly_start + timedelta(days=offset)).isoformat(),
                "count": weekly_counts.get(weekly_start + timedelta(days=offset), 0),
            }
            for offset in range(7)
        ]
        return Response({
            "sessions_completed": activities.count(),
            "words_reviewed": activities.filter(activity_type=LearningActivity.Type.VOCABULARY).count(),
            "reading_attempts": ReadingAttempt.objects.filter(user=user).count(),
            "writing_submissions": WritingSubmission.objects.filter(user=user).count(),
            "placement_attempts": PlacementAttempt.objects.filter(user=user).count(),
            "due_words": VocabularyCard.objects.filter(user=user, due_at__lte=now).count(),
            "mastered_words": VocabularyCard.objects.filter(user=user, status=VocabularyCard.Status.MASTERED).count(),
            "current_streak_days": _current_streak(timestamps, tz),
            "weekly_activity": weekly_activity,
            "recent_activity": [
                {
                    "type": item.activity_type,
                    "label": item.get_activity_type_display(),
                    "created_at": item.created_at,
                }
                for item in recent
            ],
        })


class ProgressRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .recommendations import build_recommendations

        return Response({"recommendations": build_recommendations(request.user)})
