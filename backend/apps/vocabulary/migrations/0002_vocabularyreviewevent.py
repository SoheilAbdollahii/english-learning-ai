import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vocabulary", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="VocabularyReviewEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("word_snapshot", models.CharField(max_length=100)),
                ("quality", models.PositiveSmallIntegerField()),
                ("repetitions_before", models.PositiveIntegerField()),
                ("repetitions_after", models.PositiveIntegerField()),
                ("interval_days_before", models.PositiveIntegerField()),
                ("interval_days_after", models.PositiveIntegerField()),
                ("ease_factor_before", models.DecimalField(decimal_places=2, max_digits=4)),
                ("ease_factor_after", models.DecimalField(decimal_places=2, max_digits=4)),
                ("status_before", models.CharField(choices=[("new", "New"), ("learning", "Learning"), ("review", "In review"), ("mastered", "Mastered")], max_length=10)),
                ("status_after", models.CharField(choices=[("new", "New"), ("learning", "Learning"), ("review", "In review"), ("mastered", "Mastered")], max_length=10)),
                ("reviewed_at", models.DateTimeField()),
                ("card", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="review_events", to="vocabulary.vocabularycard")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vocabulary_review_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-reviewed_at", "-id")},
        ),
    ]
