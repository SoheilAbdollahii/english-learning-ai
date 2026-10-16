from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Profile(models.Model):
    class Locale(models.TextChoices):
        ENGLISH = "en", "English"
        PERSIAN = "fa", "Persian"
    class Level(models.TextChoices):
        A1 = "A1", "A1"
        A2 = "A2", "A2"
        B1 = "B1", "B1"
        B2 = "B2", "B2"
        C1 = "C1", "C1"
        C2 = "C2", "C2"
        UNKNOWN = "unknown", "Not assessed"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    locale = models.CharField(max_length=2, choices=Locale.choices, default=Locale.ENGLISH)
    target_level = models.CharField(max_length=7, choices=Level.choices, default=Level.UNKNOWN)
    daily_goal_minutes = models.PositiveSmallIntegerField(default=15, validators=[MinValueValidator(5), MaxValueValidator(180)])
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Profile(user_id={self.user_id})"
