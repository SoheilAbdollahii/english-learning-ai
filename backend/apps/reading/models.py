from django.conf import settings
from django.db import models


class Passage(models.Model):
    class Level(models.TextChoices):
        A1 = "A1", "A1"
        A2 = "A2", "A2"
        B1 = "B1", "B1"
        B2 = "B2", "B2"
        C1 = "C1", "C1"
        C2 = "C2", "C2"

    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=180)
    body = models.TextField(max_length=5000)
    level = models.CharField(max_length=2, choices=Level.choices, default=Level.A2)
    content_version = models.PositiveSmallIntegerField(default=1)
    source_note = models.CharField(max_length=300, default="Original Wordwise content")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("level", "id")
        constraints = [
            models.UniqueConstraint(fields=("slug", "content_version"), name="unique_passage_slug_version"),
        ]

    def __str__(self):
        return f"{self.title} ({self.level}, v{self.content_version})"


class ReadingQuestion(models.Model):
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name="questions")
    prompt = models.CharField(max_length=500)
    options = models.JSONField()
    correct_option = models.CharField(max_length=32)
    explanation = models.CharField(max_length=1000, blank=True)
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(fields=("passage", "order"), name="unique_reading_question_order"),
        ]

    def __str__(self):
        return self.prompt[:80]


class ReadingAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_attempts")
    passage = models.ForeignKey(Passage, on_delete=models.PROTECT, related_name="attempts")
    passage_version = models.PositiveSmallIntegerField()
    submitted_answers = models.JSONField()
    result_details = models.JSONField(default=list)
    question_snapshots = models.JSONField(default=list)
    score = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField()
    percentage = models.PositiveSmallIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-completed_at", "-id")

    def __str__(self):
        return f"ReadingAttempt(id={self.pk}, user_id={self.user_id})"
