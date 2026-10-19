import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="AIUsageRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("operation", models.CharField(default="writing_analysis", max_length=32)),
                ("provider", models.CharField(default="pending", max_length=40)),
                ("status", models.CharField(choices=[("reserved", "Reserved"), ("succeeded", "Succeeded"), ("failed", "Failed"), ("rejected", "Rejected")], default="reserved", max_length=10)),
                ("input_characters", models.PositiveIntegerField(default=0)),
                ("input_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("output_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("estimated_cost_microunits", models.PositiveBigIntegerField(blank=True, null=True)),
                ("failure_category", models.CharField(blank=True, max_length=64)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_usage_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.AddIndex(
            model_name="aiusagerecord",
            index=models.Index(fields=["user", "operation", "-created_at"], name="usage_user_op_recent_idx"),
        ),
    ]
