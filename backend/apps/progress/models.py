from django.conf import settings
from django.db import models


class LearningActivity(models.Model):
    class Type(models.TextChoices):
        WRITING = "writing", "Writing submission"
        READING = "reading", "Reading attempt"
        VOCABULARY = "vocabulary", "Vocabulary review"
        PLACEMENT = "placement", "Placement attempt"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_activities",
    )
    activity_type = models.CharField(max_length=16, choices=Type.choices)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=("user", "-created_at"), name="progress_user_recent_idx"),
            models.Index(fields=("user", "activity_type"), name="progress_user_type_idx"),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} (user_id={self.user_id})"
