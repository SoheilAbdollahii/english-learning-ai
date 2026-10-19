from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="LearningActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_type", models.CharField(choices=[("writing", "Writing submission"), ("reading", "Reading attempt"), ("vocabulary", "Vocabulary review"), ("placement", "Placement attempt")], max_length=16)),
                ("object_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learning_activities", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.AddIndex(
            model_name="learningactivity",
            index=models.Index(fields=["user", "-created_at"], name="progress_user_recent_idx"),
        ),
        migrations.AddIndex(
            model_name="learningactivity",
            index=models.Index(fields=["user", "activity_type"], name="progress_user_type_idx"),
        ),
    ]
