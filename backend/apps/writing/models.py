from django.conf import settings
from django.db import models


class WritingSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="writing_submissions",
    )
    original_text = models.TextField(max_length=5000)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    schema_version = models.PositiveSmallIntegerField(default=1)
    provider = models.CharField(max_length=40, default="demo")
    result = models.JSONField(null=True, blank=True)
    failure_category = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self):
        return f"WritingSubmission(id={self.pk}, user_id={self.user_id}, status={self.status})"
