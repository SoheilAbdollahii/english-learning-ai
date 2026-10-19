import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="WritingSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_text", models.TextField(max_length=5000)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("succeeded", "Succeeded"), ("failed", "Failed")], default="pending", max_length=12)),
                ("schema_version", models.PositiveSmallIntegerField(default=1)),
                ("provider", models.CharField(default="demo", max_length=40)),
                ("result", models.JSONField(blank=True, null=True)),
                ("failure_category", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="writing_submissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
    ]
