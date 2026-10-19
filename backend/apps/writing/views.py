from rest_framework import permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from apps.progress.models import LearningActivity
from apps.progress.services import record_activity
from apps.usage.models import AIUsageRecord
from apps.usage.services import finish_usage, reserve_writing_usage
from .models import WritingSubmission
from .serializers import WritingSubmissionCreateSerializer, WritingSubmissionSerializer
from .services import WritingProviderError, analyze_writing, get_provider


class WritingSubmissionThrottle(UserRateThrottle):
    scope = "writing_submission"


class WritingSubmissionCollectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_throttles(self):
        # Bound write requests; the durable daily quota is enforced in the POST handler.
        if self.request.method == "POST":
            return [WritingSubmissionThrottle()]
        return []

    def get(self, request):
        paginator = LimitOffsetPagination()
        paginator.default_limit = 20
        paginator.max_limit = 100
        queryset = WritingSubmission.objects.filter(user=request.user)
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = WritingSubmissionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = WritingSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usage_record, daily_limit, used = reserve_writing_usage(request.user, len(serializer.validated_data["text"]))
        if usage_record is None:
            return Response(
                {
                    "code": "usage_limit_exceeded",
                    "detail": "Your rolling 24-hour writing submission limit has been reached. Please try again later.",
                    "limit": daily_limit,
                    "used": used,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        provider_hint = get_provider().name
        submission = WritingSubmission.objects.create(
            user=request.user,
            original_text=serializer.validated_data["text"],
            status=WritingSubmission.Status.PENDING,
        )
        try:
            provider_name, result = analyze_writing(submission.original_text)
        except WritingProviderError:
            finish_usage(usage_record, provider_hint, AIUsageRecord.Status.FAILED, "analysis_unavailable")
            submission.status = WritingSubmission.Status.FAILED
            submission.failure_category = "analysis_unavailable"
            submission.save(update_fields=("status", "failure_category", "updated_at"))
            return Response(
                {
                    "id": submission.id,
                    "status": submission.status,
                    "code": "analysis_unavailable",
                    "detail": "Writing analysis is temporarily unavailable. Your submission was saved; please try again later.",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        submission.status = WritingSubmission.Status.SUCCEEDED
        submission.provider = provider_name
        submission.result = result
        submission.save(update_fields=("status", "provider", "result", "updated_at"))
        finish_usage(usage_record, provider_name, AIUsageRecord.Status.SUCCEEDED)
        record_activity(request.user, LearningActivity.Type.WRITING, submission.pk)
        return Response(WritingSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)


class WritingSubmissionDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WritingSubmissionSerializer

    def get_queryset(self):
        return WritingSubmission.objects.filter(user=self.request.user)
