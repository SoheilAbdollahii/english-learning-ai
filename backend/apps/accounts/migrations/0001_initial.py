import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Profile", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("locale", models.CharField(choices=[("en", "English"), ("fa", "Persian")], default="en", max_length=2)),
        ("target_level", models.CharField(choices=[("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1"), ("C2", "C2"), ("unknown", "Not assessed")], default="unknown", max_length=7)),
        ("daily_goal_minutes", models.PositiveSmallIntegerField(default=15, validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(180)])),
        ("timezone", models.CharField(default="UTC", max_length=64)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
    ])]
