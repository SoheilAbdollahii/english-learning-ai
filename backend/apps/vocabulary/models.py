from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class VocabularyCard(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        LEARNING = "learning", "Learning"
        REVIEW = "review", "In review"
        MASTERED = "mastered", "Mastered"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vocabulary_cards",
    )
    word = models.CharField(max_length=100)
    definition = models.CharField(max_length=500)
    example_sentence = models.CharField(max_length=500, blank=True)
    translation = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    repetitions = models.PositiveIntegerField(default=0)
    interval_days = models.PositiveIntegerField(default=0)
    ease_factor = models.DecimalField(max_digits=4, decimal_places=2, default=2.50)
    due_at = models.DateTimeField()
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_at", "-updated_at")
        constraints = [
            models.UniqueConstraint(
                Lower("word"), "user", name="unique_vocabulary_word_per_user_ci"
            ),
        ]

    def __str__(self):
        return f"{self.word} (user_id={self.user_id})"
