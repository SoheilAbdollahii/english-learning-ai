import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Passage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=100)),
                ("title", models.CharField(max_length=180)),
                ("body", models.TextField(max_length=5000)),
                ("level", models.CharField(choices=[("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1"), ("C2", "C2")], default="A2", max_length=2)),
                ("content_version", models.PositiveSmallIntegerField(default=1)),
                ("source_note", models.CharField(default="Original Wordwise content", max_length=300)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("level", "id")},
        ),
        migrations.CreateModel(
            name="ReadingQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.CharField(max_length=500)),
                ("options", models.JSONField()),
                ("correct_option", models.CharField(max_length=32)),
                ("explanation", models.CharField(blank=True, max_length=1000)),
                ("points", models.PositiveSmallIntegerField(default=1)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("passage", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="reading.passage")),
            ],
            options={"ordering": ("order", "id")},
        ),
        migrations.CreateModel(
            name="ReadingAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("passage_version", models.PositiveSmallIntegerField()),
                ("submitted_answers", models.JSONField()),
                ("result_details", models.JSONField(default=list)),
                ("score", models.PositiveSmallIntegerField()),
                ("max_score", models.PositiveSmallIntegerField()),
                ("percentage", models.PositiveSmallIntegerField()),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                ("passage", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attempts", to="reading.passage")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reading_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-completed_at", "-id")},
        ),
        migrations.AddConstraint(
            model_name="passage",
            constraint=models.UniqueConstraint(fields=("slug", "content_version"), name="unique_passage_slug_version"),
        ),
        migrations.AddConstraint(
            model_name="readingquestion",
            constraint=models.UniqueConstraint(fields=("passage", "order"), name="unique_reading_question_order"),
        ),
    ]
