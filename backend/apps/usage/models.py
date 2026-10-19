from django.conf import settings
from django.db import models


class AIUsageRecord(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Reserved"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_usage_records")
    operation = models.CharField(max_length=32, default="writing_analysis")
    provider = models.CharField(max_length=40, default="pending")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RESERVED)
    input_characters = models.PositiveIntegerField(default=0)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    estimated_cost_microunits = models.PositiveBigIntegerField(null=True, blank=True)
    failure_category = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=("user", "operation", "-created_at"), name="usage_user_op_recent_idx"),
        ]

    def __str__(self):
        return f"AIUsageRecord(id={self.pk}, user_id={self.user_id}, status={self.status})"
