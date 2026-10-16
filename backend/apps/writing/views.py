from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WritingSubmission
from .serializers import WritingSubmissionCreateSerializer, WritingSubmissionSerializer
from .services import WritingProviderError, analyze_writing


class WritingSubmissionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WritingSubmissionSerializer

    def get_queryset(self):
        return WritingSubmission.objects.filter(user=self.request.user)


class WritingSubmissionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WritingSubmissionSerializer

    def get_queryset(self):
        return WritingSubmission.objects.filter(user=self.request.user)


class WritingSubmissionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WritingSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = WritingSubmission.objects.create(
            user=request.user,
            original_text=serializer.validated_data["text"],
            status=WritingSubmission.Status.PENDING,
        )
        try:
            provider_name, result = analyze_writing(submission.original_text)
        except WritingProviderError:
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
        return Response(WritingSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
