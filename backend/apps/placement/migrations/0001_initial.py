import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_assessment(apps, schema_editor):
    Assessment = apps.get_model("placement", "Assessment")
    Question = apps.get_model("placement", "Question")
    assessment = Assessment.objects.create(title="English placement starter", version=1, is_published=True)
    questions = [
        ("She ___ to school every day.", {"a": "go", "b": "goes", "c": "going", "d": "gone"}, "b", "Choose the present simple form for she."),
        ("We have lived here ___ 2020.", {"a": "for", "b": "during", "c": "since", "d": "from"}, "c", "Use since with a starting point in time."),
        ("If I had known, I ___ earlier.", {"a": "will come", "b": "would have come", "c": "came", "d": "would come"}, "b", "This is a third conditional sentence."),
        ("The report ___ by the team yesterday.", {"a": "completed", "b": "was completed", "c": "has completing", "d": "is complete"}, "b", "Use the past simple passive for a completed past action."),
        ("Choose the closest meaning of 'reluctant'.", {"a": "unwilling", "b": "delighted", "c": "careless", "d": "certain"}, "a", "Reluctant means hesitant or unwilling."),
        ("Not only ___ the deadline, but she also improved the result.", {"a": "she met", "b": "did she meet", "c": "she did met", "d": "met she"}, "b", "Negative fronting requires subject-auxiliary inversion."),
    ]
    for order, (prompt, options, correct, explanation) in enumerate(questions, start=1):
        Question.objects.create(assessment=assessment, prompt=prompt, options=options, correct_option=correct, explanation=explanation, points=1, order=order)


def unseed_assessment(apps, schema_editor):
    apps.get_model("placement", "Assessment").objects.filter(title="English placement starter", version=1).delete()


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Assessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("version", models.PositiveSmallIntegerField(default=1)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.CharField(max_length=500)),
                ("options", models.JSONField()),
                ("correct_option", models.CharField(max_length=32)),
                ("explanation", models.CharField(blank=True, max_length=1000)),
                ("points", models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="placement.assessment")),
            ],
            options={"ordering": ("order", "id")},
        ),
        migrations.CreateModel(
            name="PlacementAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answers", models.JSONField()),
                ("score", models.PositiveSmallIntegerField()),
                ("max_score", models.PositiveSmallIntegerField()),
                ("estimated_level", models.CharField(max_length=7)),
                ("scoring_version", models.PositiveSmallIntegerField(default=1)),
                ("completed_at", models.DateTimeField(auto_now_add=True)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attempts", to="placement.assessment")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="placement_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-completed_at", "-id")},
        ),
        migrations.AddConstraint(model_name="assessment", constraint=models.UniqueConstraint(fields=("title", "version"), name="unique_assessment_title_version")),
        migrations.AddConstraint(model_name="question", constraint=models.UniqueConstraint(fields=("assessment", "order"), name="unique_question_order_per_assessment")),
        migrations.RunPython(seed_assessment, unseed_assessment),
    ]
