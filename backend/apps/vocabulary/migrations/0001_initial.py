import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="VocabularyCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("word", models.CharField(max_length=100)),
                ("definition", models.CharField(max_length=500)),
                ("example_sentence", models.CharField(blank=True, max_length=500)),
                ("translation", models.CharField(blank=True, max_length=150)),
                ("status", models.CharField(choices=[("new", "New"), ("learning", "Learning"), ("review", "In review"), ("mastered", "Mastered")], default="new", max_length=10)),
                ("repetitions", models.PositiveIntegerField(default=0)),
                ("interval_days", models.PositiveIntegerField(default=0)),
                ("ease_factor", models.DecimalField(decimal_places=2, default=2.5, max_digits=4)),
                ("due_at", models.DateTimeField()),
                ("last_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vocabulary_cards", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("due_at", "-updated_at")},
        ),
        migrations.AddConstraint(
            model_name="vocabularycard",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("word"),
                models.F("user"),
                name="unique_vocabulary_word_per_user_ci",
            ),
        ),
    ]
