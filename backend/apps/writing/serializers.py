from rest_framework import serializers

from .models import WritingSubmission


class WritingSubmissionCreateSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=3, max_length=5000, trim_whitespace=True)


class WritingSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingSubmission
        fields = (
            "id",
            "original_text",
            "status",
            "schema_version",
            "provider",
            "result",
            "failure_category",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
