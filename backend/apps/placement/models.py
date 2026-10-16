from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Assessment(models.Model):
    title = models.CharField(max_length=160)
    version = models.PositiveSmallIntegerField(default=1)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("title", "version"), name="unique_assessment_title_version")]
        ordering = ("id",)

    def __str__(self):
        return f"{self.title} v{self.version}"


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")
    prompt = models.CharField(max_length=500)
    options = models.JSONField()
    correct_option = models.CharField(max_length=32)
    explanation = models.CharField(max_length=1000, blank=True)
    points = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")
        constraints = [models.UniqueConstraint(fields=("assessment", "order"), name="unique_question_order_per_assessment")]

    def __str__(self):
        return self.prompt[:80]


class PlacementAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="placement_attempts")
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT, related_name="attempts")
    answers = models.JSONField()
    score = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField()
    estimated_level = models.CharField(max_length=7)
    scoring_version = models.PositiveSmallIntegerField(default=1)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-completed_at", "-id")

    def __str__(self):
        return f"PlacementAttempt(id={self.pk}, user_id={self.user_id})"
